import asyncio

import httpx
import pytest

from biblioteca_mais_nova.xano_diagnostics import (
    diagnose_xano,
    format_xano_diagnostic_report,
)


@pytest.mark.parametrize(
    ("profile", "expected_paths", "authenticated_paths"),
    [
        (
            "estudante",
            (
                "/catalogo/titulos",
                "/catalogo/categorias",
                "/minhas/emprestimos",
                "/minhas/solicitacoes",
                "/minhas/reservas",
            ),
            {
                "/minhas/emprestimos",
                "/minhas/solicitacoes",
                "/minhas/reservas",
            },
        ),
        (
            "bibliotecario",
            (
                "/catalogo/titulos",
                "/catalogo/categorias",
                "/admin/acervo",
                "/admin/solicitacoes",
                "/admin/reservas",
                "/admin/emprestimos",
            ),
            {
                "/admin/acervo",
                "/admin/solicitacoes",
                "/admin/reservas",
                "/admin/emprestimos",
            },
        ),
        (
            "admin",
            (
                "/catalogo/titulos",
                "/catalogo/categorias",
                "/admin/acervo",
                "/admin/solicitacoes",
                "/admin/reservas",
                "/admin/emprestimos",
                "/admin/usuarios",
            ),
            {
                "/admin/acervo",
                "/admin/solicitacoes",
                "/admin/reservas",
                "/admin/emprestimos",
                "/admin/usuarios",
            },
        ),
    ],
)
def test_diagnostic_reads_are_limited_to_the_authenticated_profile(
    monkeypatch,
    profile,
    expected_paths,
    authenticated_paths,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[])

    async def verify():
        results = await diagnose_xano(
            profile,
            "token-de-teste",
            transport=httpx.MockTransport(handle),
        )
        assert len(results) == len(expected_paths)
        assert all(result["validation"] == "válida" for result in results)

    asyncio.run(verify())
    assert tuple(request.url.path for request in requests) == expected_paths
    for request in requests:
        if request.url.path in authenticated_paths:
            assert request.headers["Authorization"] == "Bearer token-de-teste"
        else:
            assert "Authorization" not in request.headers


def test_diagnostic_validates_200_records_and_never_reports_values(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    sensitive_email = "pessoa.secreta@example.test"
    sensitive_token = "token-de-resposta-privado"

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/minhas/emprestimos":
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "email": sensitive_email,
                            "authToken": sensitive_token,
                        }
                    ]
                },
            )
        if request.url.path == "/catalogo/categorias":
            return httpx.Response(
                200,
                json=[{"id": 7, "nome": "Literatura"}],
            )
        return httpx.Response(200, json=[])

    async def verify():
        results = await diagnose_xano(
            "estudante",
            "token-de-sessao",
            transport=httpx.MockTransport(handle),
        )
        invalid = next(
            result
            for result in results
            if result["name"] == "Meus empréstimos"
        )
        valid = next(
            result
            for result in results
            if result["name"] == "Categorias públicas"
        )
        report = format_xano_diagnostic_report(results)

        assert valid["validation"] == "válida"
        assert valid["top_type"] == "lista"
        assert valid["record_count"] == 1
        assert "id: inteiro" in valid["fields"]
        assert "nome: texto" in valid["fields"]
        assert invalid["status"] == "HTTP 200"
        assert invalid["validation"] == "inválida"
        assert invalid["top_type"] == "objeto"
        assert invalid["record_count"] == 1
        assert "id" in invalid["problematic_fields"]
        assert "email: texto" in invalid["fields"]
        assert len(invalid["reference"]) == 5
        assert set(invalid["reference"]) <= set("0123456789ABCDEF")
        assert sensitive_email not in report
        assert sensitive_token not in report
        assert "Literatura" not in report
        assert "api.example.test" not in report
        assert "token-de-sessao" not in report
        assert "/minhas/emprestimos" not in report

    asyncio.run(verify())
    error_log = capsys.readouterr().err
    assert "content-type: application/json" in error_log
    assert "topo JSON: objeto | chaves: items" in error_log
    assert sensitive_email not in error_log
    assert sensitive_token not in error_log


@pytest.mark.parametrize("status_code", [403, 404, 429])
def test_diagnostic_reports_http_error_without_response_body(
    monkeypatch,
    status_code,
):
    from biblioteca_mais_nova import xano_client

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")

    async def no_wait(_seconds: float) -> None:
        return None

    monkeypatch.setattr(xano_client, "_sleep", no_wait)

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/minhas/emprestimos":
            return httpx.Response(
                status_code,
                json={"message": "detalhe-interno-nao-publico"},
            )
        return httpx.Response(200, json=[])

    async def verify():
        results = await diagnose_xano(
            "estudante",
            "token-de-sessao",
            transport=httpx.MockTransport(handle),
        )
        result = next(
            item
            for item in results
            if item["name"] == "Meus empréstimos"
        )
        report = format_xano_diagnostic_report(results)

        assert result["status"] == f"HTTP {status_code}"
        assert result["validation"] == "inválida"
        assert result["top_type"] == "indisponível"
        assert "detalhe-interno-nao-publico" not in report

    asyncio.run(verify())


def test_diagnostic_reports_non_json_200_without_body(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    private_body = "conteudo-interno-nao-publico"

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/minhas/emprestimos":
            return httpx.Response(
                200,
                text=private_body,
                headers={"content-type": "text/html"},
            )
        return httpx.Response(200, json=[])

    async def verify():
        results = await diagnose_xano(
            "estudante",
            "token-de-sessao",
            transport=httpx.MockTransport(handle),
        )
        result = next(
            item
            for item in results
            if item["name"] == "Meus empréstimos"
        )
        report = format_xano_diagnostic_report(results)

        assert result["status"] == "HTTP 200"
        assert result["validation"] == "inválida"
        assert result["reason"] == "resposta JSON ilegível"
        assert private_body not in report

    asyncio.run(verify())

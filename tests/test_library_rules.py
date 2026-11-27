import asyncio
import json

import httpx
import pytest

import biblioteca_mais_nova.xano_client as xano_client
from biblioteca_mais_nova.library_rules import (
    LibraryRulesValidationError,
    get_library_rules,
    update_library_rules,
)
from biblioteca_mais_nova.xano_client import (
    XanoInvalidResponseError,
    XanoResponseError,
)


@pytest.fixture(autouse=True)
def _isolar_cache_e_limitador():
    xano_client.limpar_cache_autenticado()
    xano_client._limpar_limitador_xano()
    yield
    xano_client.limpar_cache_autenticado()
    xano_client._limpar_limitador_xano()


def _payload(**overrides: object) -> dict[str, object]:
    return {
        "limite_emprestimos_ativos": 3,
        "limite_pedidos_em_aberto": 3,
        "permitir_pedido_com_reserva_ativa": True,
        "bloquear_com_atraso": True,
        "exigir_autorizacao_bibliotecaria": True,
        "prazo_emprestimo_dias": 14,
        "prazo_retirada_horas": 48,
        **overrides,
    }


def test_get_library_rules_uses_authenticated_endpoint_and_parses_metadata(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests = []
    transport = httpx.MockTransport(
        lambda request: (
            requests.append(request)
            or httpx.Response(
                200,
                json={
                    **_payload(limite_pedidos_em_aberto=5),
                    "atualizado_em": "2026-11-26T14:00:00Z",
                    "atualizado_por": "Admin",
                },
            )
        )
    )

    rules = asyncio.run(
        get_library_rules(
            "token-de-teste",
            transport=transport,
        )
    )

    assert rules["limite_pedidos_em_aberto"] == 5
    assert rules["atualizado_por"] == "Admin"
    assert requests[0].method == "GET"
    assert str(requests[0].url) == (
        "https://api.example.test/grupo/configuracoes"
    )


def test_get_library_rules_parses_exact_xano_configuration_payload(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    payload = {
        "id": 1,
        "limite_emprestimos_ativos": 3,
        "limite_pedidos_em_aberto": 3,
        "permitir_pedido_com_reserva_ativa": True,
        "bloquear_com_atraso": True,
        "exigir_autorizacao_bibliotecaria": True,
        "prazo_emprestimo_dias": 14,
        "prazo_retirada_horas": 48,
        "atualizado_em": 1795758190288,
        "atualizado_por": 70,
    }
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload)
    )

    rules = asyncio.run(
        get_library_rules("token-rules", transport=transport)
    )

    assert rules["limite_emprestimos_ativos"] == 3
    assert rules["limite_pedidos_em_aberto"] == 3
    assert rules["atualizado_em"] == "2026-11-27T05:43:10.288000+00:00"
    assert rules["atualizado_por"] == "70"
    assert "id" not in rules


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("atualizado_em", 0, None),
        ("atualizado_em", None, None),
        ("atualizado_em", 1795758190, "2026-11-27T05:43:10+00:00"),
        ("atualizado_em", "2026-11-27T00:23:10Z", "2026-11-27T00:23:10+00:00"),
        ("atualizado_por", None, None),
        ("atualizado_por", 70, "70"),
        ("atualizado_por", "Admin", "Admin"),
    ],
)
def test_library_rules_accepts_optional_metadata_formats(
    monkeypatch,
    field,
    value,
    expected,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    payload = {**_payload(), field: value, "extra": "ignorar"}
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload)
    )

    rules = asyncio.run(
        get_library_rules("token-metadata", transport=transport)
    )

    assert rules[field] == expected


def test_library_rules_invalid_field_is_reported_in_diagnostic(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("BIBLIOTECA_LOG_ERROS", "1")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={**_payload(), "atualizado_em": "data inválida"},
        )
    )

    with pytest.raises(XanoInvalidResponseError) as error:
        asyncio.run(get_library_rules("token-invalid", transport=transport))

    assert error.value.field == "atualizado_em"
    assert "campo atualizado_em" in capsys.readouterr().err


def test_update_library_rules_sends_only_contract_fields(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []

    def handle_request(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                **_payload(prazo_emprestimo_dias=21),
                "atualizado_em": "2026-11-26T14:00:00Z",
                "atualizado_por": "Admin",
            },
        )

    transport = httpx.MockTransport(handle_request)
    rules = asyncio.run(
        update_library_rules(
            {**_payload(prazo_emprestimo_dias=21), "atualizado_por": "Ignorar"},
            "token-de-teste",
            transport=transport,
        )
    )

    assert rules["prazo_emprestimo_dias"] == 21
    assert requests[0].method == "PUT"
    assert requests[0].url.path == "/admin/configuracoes"
    assert json.loads(requests[0].content) == _payload(prazo_emprestimo_dias=21)
    assert "atualizado_por" not in json.loads(requests[0].content)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("limite_emprestimos_ativos", 0),
        ("limite_pedidos_em_aberto", 21),
        ("prazo_emprestimo_dias", 1.5),
        ("prazo_retirada_horas", 169),
        ("bloquear_com_atraso", 1),
    ],
)
def test_update_library_rules_validates_values_before_network(
    monkeypatch,
    field,
    value,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []
    transport = httpx.MockTransport(
        lambda request: requests.append(request) or httpx.Response(200, json={})
    )

    with pytest.raises(LibraryRulesValidationError) as error:
        asyncio.run(
            update_library_rules(
                _payload(**{field: value}),
                "token-de-teste",
                transport=transport,
            )
        )

    assert error.value.field == field
    assert requests == []


@pytest.mark.parametrize("status_code", [403, 404])
def test_get_library_rules_preserves_unpublished_endpoint_errors(
    monkeypatch,
    status_code,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status_code, json={"message": "indisponível"})
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(
            get_library_rules(
                "token-de-teste",
                transport=transport,
            )
        )

    assert error.value.status_code == status_code


def test_update_library_rules_preserves_forbidden_response(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(403, json={"message": "sem permissão"})
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(
            update_library_rules(
                _payload(),
                "token-de-teste",
                transport=transport,
            )
        )

    assert error.value.status_code == 403


def test_library_rules_cache_lives_sixty_seconds_and_put_invalidates(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    now = [100.0]
    monkeypatch.setattr(xano_client, "_cache_clock", lambda: now[0])
    requests = []
    current_rules = _payload()

    def handle_request(request):
        nonlocal current_rules
        requests.append(request)
        if request.method == "PUT":
            current_rules = json.loads(request.content)
        return httpx.Response(200, json=current_rules)

    transport = httpx.MockTransport(handle_request)

    async def read():
        return await get_library_rules("token-cache", transport=transport)

    assert asyncio.run(read())["limite_pedidos_em_aberto"] == 3
    now[0] += 59
    assert asyncio.run(read())["limite_pedidos_em_aberto"] == 3
    assert [request.method for request in requests] == ["GET"]
    assert "token-cache" not in repr(tuple(xano_client._AUTHENTICATED_GET_CACHE))

    now[0] += 1.1
    assert asyncio.run(read())["limite_pedidos_em_aberto"] == 3
    assert [request.method for request in requests] == ["GET", "GET"]

    updated = _payload(limite_pedidos_em_aberto=6)
    asyncio.run(
        update_library_rules(
            updated,
            "token-cache",
            transport=transport,
        )
    )
    assert asyncio.run(read())["limite_pedidos_em_aberto"] == 6
    assert [request.method for request in requests] == [
        "GET",
        "GET",
        "PUT",
        "GET",
    ]

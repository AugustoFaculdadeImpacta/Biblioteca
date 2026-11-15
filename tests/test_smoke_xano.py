import asyncio
import json

import httpx

from scripts.smoke_xano import PROFILE_CHECKS, run_smoke
from biblioteca_mais_nova.xano_client import XanoClient


def test_smoke_checks_each_configured_profile_without_exposing_credentials(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []
    output: list[str] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/auth/login"):
            return httpx.Response(
                200,
                json={
                    "authToken": "token-de-teste",
                    "usuario": {"perfil": request.url.params.get("perfil", "")},
                },
            )
        if request.url.path.endswith("/auth/me"):
            return httpx.Response(200, json={"id": 10, "perfil": "teste"})
        return httpx.Response(200, json=[{"id": 1}, {"id": 2}])

    environment = {
        "XANO_SMOKE_ESTUDANTE_EMAIL": "aluno@exemplo.invalid",
        "XANO_SMOKE_ESTUDANTE_SENHA": "senha-falsa-estudante",
        "XANO_SMOKE_BIBLIOTECARIO_EMAIL": "bib@exemplo.invalid",
        "XANO_SMOKE_BIBLIOTECARIO_SENHA": "senha-falsa-bibliotecario",
        "XANO_SMOKE_ADMIN_EMAIL": "admin@exemplo.invalid",
        "XANO_SMOKE_ADMIN_SENHA": "senha-falsa-admin",
    }
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    results = asyncio.run(run_smoke(client, environment, emit=output.append))

    expected_gets = {
        (profile, path)
        for profile, (_, _, paths) in PROFILE_CHECKS.items()
        for path in paths
    }
    actual_gets = {
        (profile, request.url.path.removeprefix("/grupo"))
        for profile, request in zip(
            [
                profile
                for profile, (_, _, paths) in PROFILE_CHECKS.items()
                for _ in range(1 + len(paths))
            ],
            requests,
        )
        if request.method == "GET"
    }
    assert actual_gets == expected_gets
    assert len(results) == 3 + len(expected_gets)
    assert all(
        request.headers.get("Authorization") == "Bearer token-de-teste"
        for request in requests
        if request.method == "GET"
    )
    assert all(result.status == "200" for result in results)
    assert all(result.count in {None, 1, 2} for result in results)
    rendered = "\n".join(output)
    for secret in (
        "aluno@exemplo.invalid",
        "bib@exemplo.invalid",
        "admin@exemplo.invalid",
        "senha-falsa-estudante",
        "senha-falsa-bibliotecario",
        "senha-falsa-admin",
        "token-de-teste",
        "api.example.test",
    ):
        assert secret not in rendered


def test_smoke_ignores_incomplete_profiles_and_stops_after_failed_login(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests: list[httpx.Request] = []
    output: list[str] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(403, json={"message": "Credenciais inválidas."})

    environment = {
        "XANO_SMOKE_ESTUDANTE_EMAIL": "aluno@exemplo.invalid",
        "XANO_SMOKE_ADMIN_EMAIL": "admin@exemplo.invalid",
        "XANO_SMOKE_ADMIN_SENHA": "senha-falsa",
    }
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    results = asyncio.run(run_smoke(client, environment, emit=output.append))

    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert len(results) == 1
    assert results[0].profile == "admin"
    assert results[0].path == "/auth/login"
    assert results[0].status == "403"
    rendered = "\n".join(output)
    assert "perfil=estudante status=ignorado" in rendered
    assert "admin@exemplo.invalid" not in rendered
    assert "senha-falsa" not in rendered
    assert "Credenciais inválidas." not in rendered


def test_smoke_help_describes_power_shell_environment_setup():
    from scripts.smoke_xano import _build_parser

    help_text = _build_parser().format_help()

    assert "$env:XANO_SMOKE_ESTUDANTE_EMAIL" in help_text
    assert "$env:XANO_SMOKE_ADMIN_SENHA" in help_text
    assert "sem salvá-los em arquivo" in help_text

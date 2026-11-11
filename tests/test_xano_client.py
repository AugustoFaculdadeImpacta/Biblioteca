import asyncio

import httpx
import pytest

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoTimeoutError,
    XanoRequestError,
    XanoResponseError,
)


def test_client_reads_base_url_from_environment_file(tmp_path, monkeypatch):
    monkeypatch.delenv("XANO_API_BASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "XANO_API_BASE_URL=https://api.example.test/grupo",
        encoding="utf-8",
    )

    client = XanoClient.from_environment()

    assert str(client._base_url) == "https://api.example.test/grupo/"
    assert "api.example.test" not in repr(client)


@pytest.mark.parametrize(
    "base_url",
    [
        "",
        "ftp://api.example.test",
        "http://api.example.test",
        "https://usuario:senha@api.example.test",
        "https://api.example.test?token=nao-pode",
    ],
)
def test_client_rejects_missing_or_invalid_base_url(base_url, monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", base_url)

    with pytest.raises(XanoConfigurationError) as error:
        XanoClient.from_environment()

    if base_url:
        assert base_url not in str(error.value)


def test_request_uses_mock_transport_and_backend_authorization(monkeypatch):
    token = "token-de-teste-nao-real"
    requests: list[httpx.Request] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    client = XanoClient.from_environment(transport=httpx.MockTransport(handle_request))

    response = asyncio.run(
        client.request("GET", "/catalogo/titulos", token=token)
    )

    assert response.json() == {"ok": True}
    assert len(requests) == 1
    assert str(requests[0].url) == (
        "https://api.example.test/grupo/catalogo/titulos"
    )
    assert requests[0].headers["Authorization"] == f"Bearer {token}"


def test_request_failures_do_not_expose_response_body_or_token(
    monkeypatch, caplog
):
    token = "segredo-falso-token"

    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text=f"Authorization Bearer {token}")

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    client = XanoClient.from_environment(transport=httpx.MockTransport(handle_request))

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(client.request("GET", "/health", token=token))

    assert error.value.status_code == 503
    assert token not in str(error.value)
    assert "Authorization" not in str(error.value)
    assert token not in caplog.text


def test_transport_errors_are_sanitized_and_not_logged(monkeypatch, caplog):
    token = "segredo-falso-token"

    def fail_request(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            f"falha para {request.url} com Authorization Bearer {token}",
            request=request,
        )

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    client = XanoClient.from_environment(transport=httpx.MockTransport(fail_request))

    with pytest.raises(XanoRequestError) as error:
        asyncio.run(client.request("GET", "/health", token=token))

    assert token not in str(error.value)
    assert "api.example.test" not in str(error.value)
    assert error.value.__suppress_context__
    assert token not in caplog.text
    assert "api.example.test" not in caplog.text


def test_timeout_errors_are_classified_and_sanitized(monkeypatch):
    token = "token-de-teste"

    def timeout_request(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout(
            f"timeout em {request.url} com Bearer {token}",
            request=request,
        )

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(timeout_request)
    )

    with pytest.raises(XanoTimeoutError) as error:
        asyncio.run(client.request("GET", "/minhas/emprestimos", token=token))

    assert token not in str(error.value)
    assert "api.example.test" not in str(error.value)

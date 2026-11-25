import asyncio

import httpx
import pytest

import biblioteca_mais_nova.xano_client as xano_client
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoNonJsonResponseError,
    XanoTimeoutError,
    XanoRequestError,
    XanoResponseError,
    XanoWriteSucceededWithUnreadableResponse,
    diagnosticar_pagina_xano,
    parse_xano_response_json,
    xano_public_error_message,
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
    monkeypatch.delenv("BIBLIOTECA_DIAGNOSTICO", raising=False)
    caplog.set_level("INFO", logger="biblioteca.xano")
    delays = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

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
    assert delays == [0.5, 1.5, 3.0]


def test_transport_errors_are_sanitized_and_not_logged(monkeypatch, caplog):
    token = "segredo-falso-token"
    monkeypatch.delenv("BIBLIOTECA_DIAGNOSTICO", raising=False)
    caplog.set_level("INFO", logger="biblioteca.xano")
    delays = []
    requests = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

    def fail_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
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
    assert len(requests) == 4
    assert delays == [0.5, 1.5, 3.0]


def test_timeout_errors_are_classified_and_sanitized(monkeypatch):
    token = "token-de-teste"
    delays = []
    requests = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

    def timeout_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
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
    assert len(requests) == 4
    assert delays == [0.5, 1.5, 3.0]


def test_get_retries_transient_statuses_with_increasing_delays(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    responses = iter((503, 502, 504, 200))
    requests = []
    delays = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(next(responses), json={"ok": True})

    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    response = asyncio.run(client.request("GET", "/catalogo/titulos"))

    assert response.json() == {"ok": True}
    assert len(requests) == 4
    assert delays == [0.5, 1.5, 3.0]


def test_get_uses_retry_after_and_caps_wait_at_ten_seconds(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    delays = []
    requests = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "30"},
                json={"message": "limite"},
            )
        return httpx.Response(200, json={"ok": True})

    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    response = asyncio.run(client.request("GET", "/catalogo/categorias"))

    assert response.status_code == 200
    assert len(requests) == 2
    assert delays == [10.0]


def test_get_does_not_retry_other_http_errors(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []
    delays = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(500, json={"message": "erro"})

    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(client.request("GET", "/catalogo/titulos"))

    assert error.value.status_code == 500
    assert len(requests) == 1
    assert delays == []


@pytest.mark.parametrize("method", ["POST", "PATCH", "DELETE"])
def test_writes_are_never_retried(monkeypatch, method):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []
    delays = []

    async def skip_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(503, json={"message": "indisponivel"})

    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    with pytest.raises(XanoResponseError):
        asyncio.run(client.request(method, "/admin/acervo"))

    assert len(requests) == 1
    assert delays == []


def test_diagnostics_are_opt_in_and_hide_private_values(monkeypatch, caplog):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    monkeypatch.setenv("BIBLIOTECA_DIAGNOSTICO", "1")
    caplog.set_level("INFO", logger="biblioteca.xano")
    token = "token-privado-de-teste"
    private_email = "pessoa-privada@example.test"
    private_password = "senha-privada-de-teste"

    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"senha": private_password},
            headers={"content-type": "application/json; charset=utf-8"},
        )

    client = XanoClient.from_environment(
        transport=httpx.MockTransport(handle_request)
    )

    @diagnosticar_pagina_xano("catalogo")
    async def load_page():
        return await client.request(
            "GET",
            f"/catalogo/titulos?email={private_email}",
            token=token,
        )

    asyncio.run(load_page())

    assert "metodo=GET" in caplog.text
    assert "caminho=/catalogo/titulos" in caplog.text
    assert "status=200" in caplog.text
    assert "content_type=application/json" in caplog.text
    assert "duracao_ms=" in caplog.text
    assert "tamanho_resposta=" in caplog.text
    assert "tentativa=1" in caplog.text
    assert "xano_pagina rota=catalogo chamadas=1 falhas=0" in caplog.text
    assert token not in caplog.text
    assert private_email not in caplog.text
    assert private_password not in caplog.text
    assert "api.example.test" not in caplog.text
    assert "?email=" not in caplog.text


def test_diagnostic_page_counts_failed_attempts(monkeypatch, caplog):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("BIBLIOTECA_DIAGNOSTICO", "1")
    caplog.set_level("INFO", logger="biblioteca.xano")
    statuses = iter((503, 200))

    async def skip_sleep(delay):
        return None

    monkeypatch.setattr(xano_client, "_sleep", skip_sleep)
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(next(statuses), json={"ok": True})
        )
    )

    @diagnosticar_pagina_xano("home")
    async def load_page():
        return await client.request("GET", "/catalogo/titulos")

    asyncio.run(load_page())

    assert "xano_pagina rota=home chamadas=2 falhas=1" in caplog.text


def test_unexpected_response_format_is_reported_without_body(monkeypatch, caplog):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("BIBLIOTECA_DIAGNOSTICO", "1")
    caplog.set_level("INFO", logger="biblioteca.xano")
    response_body = "conteudo-privado-de-pagina"
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(502, text=response_body)
        )
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(client.request("GET", "/catalogo/titulos"))

    assert xano_public_error_message(error.value) == (
        f"O Xano devolveu uma página de erro (código 502). "
        f"(ref. {error.value.reference})"
    )
    assert response_body not in caplog.text
    assert response_body not in str(error.value)


def test_json_parser_distinguishes_non_json_and_incompatible_json():
    with pytest.raises(XanoNonJsonResponseError) as non_json:
        parse_xano_response_json(
            httpx.Response(502, text="<html>erro</html>")
        )
    assert xano_public_error_message(non_json.value) == (
        f"O Xano devolveu uma página de erro (código 502). "
        f"(ref. {non_json.value.reference})"
    )

    with pytest.raises(XanoInvalidResponseError) as invalid_json:
        parse_xano_response_json(
            httpx.Response(
                200,
                text="<html>erro</html>",
                headers={"content-type": "application/json"},
            )
        )
    assert xano_public_error_message(invalid_json.value) == (
        f"O Xano respondeu em formato inesperado. "
        f"(ref. {invalid_json.value.reference})"
    )


def test_invalid_response_counts_as_page_failure(monkeypatch, caplog):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("BIBLIOTECA_DIAGNOSTICO", "1")
    caplog.set_level("INFO", logger="biblioteca.xano")
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text="resposta inesperada")
        )
    )

    @diagnosticar_pagina_xano("catalogo")
    async def load_page():
        response = await client.request("GET", "/catalogo/titulos")
        return parse_xano_response_json(response)

    with pytest.raises(XanoNonJsonResponseError):
        asyncio.run(load_page())

    assert "xano_pagina rota=catalogo chamadas=1 falhas=1" in caplog.text


def test_xano_limits_simultaneous_requests_to_three(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")

    class ConcurrentTransport(httpx.AsyncBaseTransport):
        def __init__(self):
            self.active = 0
            self.maximum = 0

        async def handle_async_request(self, request):
            self.active += 1
            self.maximum = max(self.maximum, self.active)
            await asyncio.sleep(0.01)
            self.active -= 1
            return httpx.Response(200, json={"ok": True})

        async def aclose(self):
            return None

    transport = ConcurrentTransport()
    client = XanoClient.from_environment(transport=transport)

    async def load_many():
        await asyncio.gather(
            *(
                client.request("GET", f"/catalogo/titulos/{title_id}")
                for title_id in range(8)
            )
        )

    asyncio.run(load_many())

    assert transport.maximum == 3


def test_failure_block_is_always_written_and_redacts_private_values(
    monkeypatch, capsys
):
    token = "token-super-secreto"
    email = "pessoa.privada@example.test"
    password = "senha-super-secreta"
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    monkeypatch.delenv("BIBLIOTECA_LOG_ERROS", raising=False)
    monkeypatch.delenv("BIBLIOTECA_DIAGNOSTICO", raising=False)
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                429,
                json={
                    "code": "limite",
                    "message": "Limite de pedidos atingido.",
                    "access_token": token,
                    "senha": password,
                    "email": email,
                },
            )
        )
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(
            client.request(
                "POST",
                "/solicitacoes-emprestimo",
                token=token,
                json={"titulo_id": 41, "email": email, "senha": password},
            )
        )

    output = capsys.readouterr().err
    assert error.value.reference is not None
    assert f"ref={error.value.reference}" in output
    assert "ação: reservar_livro | perfil: estudante" in output
    assert "chamada: POST /solicitacoes-emprestimo -> 429" in output
    assert "email" in output
    assert "senha" in output
    assert "titulo_id" in output
    assert "Limite de pedidos atingido." in output
    assert token not in output
    assert email not in output
    assert password not in output
    assert "api.example.test" not in output


@pytest.mark.parametrize(
    ("failure", "expected_result"),
    [
        ("timeout", "tempo esgotado"),
        ("connection", "falha de conexão"),
    ],
)
def test_transport_failure_blocks_include_reference_and_no_host(
    monkeypatch, capsys, failure, expected_result
):
    token = "token-de-transporte"
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.delenv("BIBLIOTECA_LOG_ERROS", raising=False)

    def fail(request):
        error = (
            httpx.ReadTimeout(
                f"timeout com Bearer {token} em https://api.example.test",
                request=request,
            )
            if failure == "timeout"
            else httpx.ConnectError(
                f"falha com Authorization Bearer {token} "
                "https://api.example.test",
                request=request,
            )
        )
        raise error

    client = XanoClient.from_environment(
        transport=httpx.MockTransport(fail)
    )
    expected_error = XanoTimeoutError if failure == "timeout" else XanoRequestError

    with pytest.raises(expected_error) as error:
        asyncio.run(
            client.request(
                "POST",
                "/solicitacoes-emprestimo",
                token=token,
                json={"titulo_id": 41},
            )
        )

    output = capsys.readouterr().err
    assert error.value.reference is not None
    assert f"ref={error.value.reference}" in output
    assert expected_result in output
    assert token not in output
    assert "api.example.test" not in output


@pytest.mark.parametrize("body", ["", '{"resposta":'])
def test_unreadable_success_response_is_logged_with_reference(
    monkeypatch, capsys, body
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.delenv("BIBLIOTECA_LOG_ERROS", raising=False)
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                content=body.encode(),
                headers={"content-type": "application/json"},
            )
        )
    )
    async def parse_response():
        response = await client.request(
            "POST",
            "/solicitacoes-emprestimo",
            json={"titulo_id": 41},
        )
        return parse_xano_response_json(response)

    with pytest.raises(XanoInvalidResponseError) as error:
        asyncio.run(parse_response())

    output = capsys.readouterr().err
    assert error.value.reference is not None
    assert f"ref={error.value.reference}" in output
    assert "resposta 2xx ilegível" in output


def test_incompatible_success_shape_is_logged_with_reference(monkeypatch, capsys):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.delenv("BIBLIOTECA_LOG_ERROS", raising=False)
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"wrong": "shape"})
        )
    )
    def reject_shape(_value):
        raise XanoInvalidResponseError()

    async def parse_response():
        response = await client.request("GET", "/minhas/reservas")
        return xano_client.parse_xano_write_response(response, reject_shape)

    with pytest.raises(XanoWriteSucceededWithUnreadableResponse) as error:
        asyncio.run(parse_response())

    output = capsys.readouterr().err
    assert error.value.reference is not None
    assert f"ref={error.value.reference}" in output
    assert "registro 0, campo estrutura: formato incompatível" in output


def test_failure_logging_can_be_disabled(monkeypatch, capsys):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("BIBLIOTECA_LOG_ERROS", "0")
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(503, json={"message": "indisponível"})
        )
    )

    with pytest.raises(XanoResponseError):
        asyncio.run(client.request("POST", "/solicitacoes-emprestimo"))

    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    ("server_message", "shown"),
    [
        ("Limite de pedidos atingido.", "Limite de pedidos atingido."),
        ("Conta 123456789 não encontrada.", None),
        ("Erro para pessoa@example.test.", None),
    ],
)
def test_short_safe_server_message_is_available_but_personal_details_are_not(
    monkeypatch, capsys, server_message, shown
):
    from biblioteca_mais_nova.catalog import catalog_error_message

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    client = XanoClient.from_environment(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                400,
                json={"code": "regra", "message": server_message},
            )
        )
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(client.request("GET", "/catalogo/titulos"))

    message = catalog_error_message(error.value)
    assert error.value.reference is not None
    assert message.endswith(f"(ref. {error.value.reference})")
    if shown is not None:
        assert shown in message
    else:
        assert server_message not in message
    assert capsys.readouterr().err.find(error.value.reference) >= 0

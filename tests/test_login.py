import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.login import (
    LoginValidationError,
    build_login_payload,
    login_error_message,
    submit_login,
)
from biblioteca_mais_nova.xano_client import XanoRequestError, XanoResponseError


def _components(component: rx.Component):
    yield component
    for child in component.children:
        if isinstance(child, rx.Component):
            yield from _components(child)


def test_login_page_has_only_labeled_email_and_password_fields():
    page = frontend.login_page()
    components = list(_components(page))
    form = next(component for component in components if component.id == "form-login")
    fields = [
        component
        for component in form.children
        if component.alias == "RadixThemesTextField.Root"
    ]

    assert "login" in frontend.app._unevaluated_pages
    assert [field.name._var_value for field in fields] == ["email", "senha"]
    assert [field.type._var_value for field in fields] == ["email", "password"]
    assert all(field.required._var_value for field in fields)
    labels = [
        component
        for component in form.children
        if type(component).__name__ == "Label"
    ]
    assert [label.html_for._var_value for label in labels] == [
        "login-email",
        "login-senha",
    ]
    assert not any(field.name._var_value == "perfil" for field in fields)
    assert frontend.app.style[":focus-visible"] == {
        "outline": "3px solid #005fcc",
        "outline_offset": "3px",
    }


def test_login_payload_normalizes_email_and_preserves_password():
    assert build_login_payload(
        {"email": "  ANA.Exemplo@Escola.edu.br  ", "senha": " senha "}
    ) == {
        "email": "ana.exemplo@escola.edu.br",
        "senha": " senha ",
    }


@pytest.mark.parametrize(
    ("form_data", "message"),
    [
        ({"email": "  ", "senha": "senha"}, "Informe seu e-mail."),
        (
            {"email": "ana silva@escola.edu.br", "senha": "senha"},
            "O e-mail não pode conter espaços internos.",
        ),
        (
            {"email": "ana-escola", "senha": "senha"},
            "Informe um endereço de e-mail válido.",
        ),
        ({"email": "ana@escola.edu.br", "senha": ""}, "Informe sua senha."),
    ],
)
def test_invalid_login_data_is_rejected_before_http(form_data, message):
    with pytest.raises(LoginValidationError, match=message):
        build_login_payload(form_data)


@pytest.mark.parametrize("profile", ["estudante", "bibliotecario"])
def test_login_posts_only_contract_fields_through_mock_transport(
    monkeypatch, profile
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []
    session_token = "token-falso-de-sessao"

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "authToken": session_token,
                "usuario": {
                    "id": 41,
                    "nome": "Ana",
                    "email": "ana@escola.edu.br",
                    "perfil": profile,
                },
            },
        )

    payload = build_login_payload(
        {"email": " ANA@ESCOLA.EDU.BR ", "senha": "senha secreta"}
    )
    result = asyncio.run(
        submit_login(payload, transport=httpx.MockTransport(handle_request))
    )

    assert result["authToken"] == session_token
    assert result["usuario"]["perfil"] == profile
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.example.test/grupo/auth/login"
    assert "Authorization" not in request.headers
    assert json.loads(request.content) == {
        "email": "ana@escola.edu.br",
        "senha": "senha secreta",
    }


@pytest.mark.parametrize("status_code", [400, 401])
def test_login_rejections_have_safe_message_and_hide_response(
    monkeypatch, caplog, status_code
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    detail = "detalhe interno e credencial"
    payload = build_login_payload(
        {"email": "ana@escola.edu.br", "senha": "senha privada"}
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(
            submit_login(
                payload,
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(status_code, text=detail)
                ),
            )
        )

    assert login_error_message(error.value) == (
        "Não foi possível autenticar. Confira os dados e tente novamente."
    )
    assert detail not in str(error.value)
    assert "api.example.test" not in str(error.value)
    assert detail not in caplog.text


def test_login_rejects_malformed_or_unexpected_session(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    payload = build_login_payload(
        {"email": "ana@escola.edu.br", "senha": "senha"}
    )
    responses = [
        httpx.Response(200, text="não é JSON"),
        httpx.Response(
            200,
            json={
                "authToken": "token-falso",
                "usuario": {
                    "id": 41,
                    "nome": "Ana",
                    "email": "ana@escola.edu.br",
                    "perfil": "perfil-desconhecido",
                },
            },
        ),
    ]

    for response in responses:
        with pytest.raises(XanoRequestError):
            asyncio.run(
                submit_login(
                    payload,
                    transport=httpx.MockTransport(lambda request: response),
                )
            )


def test_login_event_keeps_token_profile_and_password_private(monkeypatch, caplog):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    session_token = "token-falso-privado"
    password = "senha falsa de teste"
    profile = "bibliotecario"
    payload = {"email": "ana@escola.edu.br", "senha": password}
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "authToken": session_token,
                "usuario": {
                    "id": 41,
                    "nome": "Ana",
                    "email": "ana@escola.edu.br",
                    "perfil": profile,
                },
            },
        )
    )

    async def mocked_authenticate(login_payload):
        return await submit_login(login_payload, transport=transport)

    monkeypatch.setattr(frontend, "authenticate", mocked_authenticate)
    session_id = f"login-privacy-{uuid4()}"

    async def verify_session():
        async with frontend.app.modify_state(
            BaseStateToken(ident=session_id, cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            await state.submit_login(payload)
            delta = await root._get_resolved_delta()
            public_state = state.dict()
            assert state._read_session_token() == session_token
            assert state._session_profile == profile
            assert state.is_authenticated is True
            assert state.login_has_error is False
            for value in (session_token, password, profile):
                assert value not in json.dumps(delta, default=str)
                assert value not in json.dumps(public_state, default=str)
            assert "api.example.test" not in json.dumps(delta, default=str)
            assert "Authorization" not in json.dumps(delta, default=str)
            assert "_session_token" not in frontend.State.base_vars
            assert "_session_profile" not in frontend.State.base_vars

    asyncio.run(verify_session())
    assert session_token not in caplog.text
    assert password not in caplog.text
    assert profile not in caplog.text
    assert "api.example.test" not in caplog.text


def test_login_sessions_are_isolated(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")

    async def mocked_authenticate(login_payload):
        return {
            "authToken": "token-sessao-1",
            "usuario": {
                "id": 41,
                "nome": "Ana",
                "email": "ana@escola.edu.br",
                "perfil": "bibliotecario",
            },
        }

    monkeypatch.setattr(frontend, "authenticate", mocked_authenticate)

    async def verify_sessions():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"login-first-{uuid4()}", cls=rx.State)
        ) as first_root:
            first = await first_root.get_state(frontend.State)
            await first.submit_login(
                {"email": "ana@escola.edu.br", "senha": "senha"}
            )
            assert first._read_session_token() == "token-sessao-1"
            assert first._session_profile == "bibliotecario"

        async with frontend.app.modify_state(
            BaseStateToken(ident=f"login-second-{uuid4()}", cls=rx.State)
        ) as second_root:
            second = await second_root.get_state(frontend.State)
            assert second._read_session_token() is None
            assert second._session_profile == ""
            assert second.is_authenticated is False

    asyncio.run(verify_sessions())

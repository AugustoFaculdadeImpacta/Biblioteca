import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.signup import (
    SignupValidationError,
    build_signup_payload,
    signup_error_message,
    submit_student_signup,
)
from biblioteca_mais_nova.xano_client import (
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
)


def _components(component: rx.Component):
    yield component
    for child in component.children:
        if isinstance(child, rx.Component):
            yield from _components(child)


def test_signup_route_has_labeled_fields_in_keyboard_order_and_visible_focus():
    page = frontend.student_signup()
    components = list(_components(page))
    form = next(component for component in components if component.id == "form-cadastro-estudante")
    fields = [
        component
        for component in form.children
        if component.alias == "RadixThemesTextField.Root"
    ]

    assert "cadastro" in frontend.app._unevaluated_pages
    assert [field.name._var_value for field in fields] == [
        "nome",
        "email",
        "senha",
    ]
    assert [field.type._var_value for field in fields] == [
        "text",
        "email",
        "password",
    ]
    assert all(field.required._var_value for field in fields)
    labels = [
        component
        for component in form.children
        if type(component).__name__ == "Label"
    ]
    assert [label.html_for._var_value for label in labels] == [
        "signup-nome",
        "signup-email",
        "signup-senha",
    ]
    assert not any(field.name._var_value == "perfil" for field in fields)
    assert frontend.app.style[":focus-visible"] == {
        "outline": "3px solid #005fcc",
        "outline_offset": "3px",
    }


@pytest.mark.parametrize(
    ("form_data", "expected"),
    [
        (
            {"nome": " Ana ", "email": "  ANA.Exemplo@Escola.edu.br  ", "senha": " senha "},
            {"nome": " Ana ", "email": "ana.exemplo@escola.edu.br", "senha": " senha "},
        ),
    ],
)
def test_signup_payload_normalizes_only_email(form_data, expected):
    assert build_signup_payload(form_data) == expected


@pytest.mark.parametrize(
    ("form_data", "message"),
    [
        ({"nome": " ", "email": "ana@escola.edu.br", "senha": "senha"}, "Informe seu nome."),
        ({"nome": "Ana", "email": " ", "senha": "senha"}, "Informe seu e-mail."),
        (
            {"nome": "Ana", "email": "ana silva@escola.edu.br", "senha": "senha"},
            "O e-mail não pode conter espaços internos.",
        ),
        (
            {"nome": "Ana", "email": "ana-escola", "senha": "senha"},
            "Informe um endereço de e-mail válido.",
        ),
        ({"nome": "Ana", "email": "ana@escola.edu.br", "senha": ""}, "Informe sua senha."),
    ],
)
def test_invalid_signup_data_is_rejected_before_http(form_data, message):
    with pytest.raises(SignupValidationError, match=message):
        build_signup_payload(form_data)


def test_signup_posts_only_contract_fields_through_mock_transport(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "authToken": "token-falso",
                "usuario": {
                    "id": 41,
                    "nome": "Ana",
                    "email": "ana@escola.edu.br",
                    "perfil": "estudante",
                },
            },
        )

    payload = build_signup_payload(
        {"nome": "Ana", "email": " ANA@ESCOLA.EDU.BR ", "senha": "senha secreta"}
    )
    result = asyncio.run(
        submit_student_signup(
            payload,
            transport=httpx.MockTransport(handle_request),
        )
    )

    assert result["authToken"] == "token-falso"
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.example.test/grupo/auth/signup"
    assert "Authorization" not in request.headers
    assert json.loads(request.content) == {
        "nome": "Ana",
        "email": "ana@escola.edu.br",
        "senha": "senha secreta",
    }


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (409, "Este e-mail já está cadastrado. Tente entrar com sua conta."),
        (400, "Confira os dados informados e tente novamente."),
        (503, "Não foi possível concluir o cadastro. Tente novamente mais tarde."),
    ],
)
def test_signup_api_errors_have_safe_portuguese_messages(
    monkeypatch, caplog, status_code, message
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    secret_body = "segredo-no-corpo"
    secret_url = "api.example.test"
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status_code, text=secret_body)
    )
    payload = build_signup_payload(
        {"nome": "Ana", "email": "ana@escola.edu.br", "senha": "senha falsa"}
    )

    with pytest.raises(XanoRequestError) as error:
        asyncio.run(submit_student_signup(payload, transport=transport))

    assert signup_error_message(error.value) == message
    assert secret_body not in str(error.value)
    assert secret_url not in str(error.value)
    assert secret_body not in caplog.text
    assert secret_url not in caplog.text


def test_signup_response_must_return_a_student_session(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "authToken": "token-falso",
                "usuario": {
                    "id": 41,
                    "nome": "Ana",
                    "email": "ana@escola.edu.br",
                    "perfil": "bibliotecario",
                },
            },
        )
    )
    payload = build_signup_payload(
        {"nome": "Ana", "email": "ana@escola.edu.br", "senha": "senha"}
    )

    with pytest.raises(XanoRequestError):
        asyncio.run(submit_student_signup(payload, transport=transport))


def test_signup_event_keeps_token_and_password_out_of_client_state_and_logs(
    monkeypatch, caplog
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    session_token = "token-falso-privado"
    password = "senha falsa de teste"
    requests: list[httpx.Request] = []
    payload = {
        "nome": "Ana",
        "email": "ana@escola.edu.br",
        "senha": password,
    }

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
                    "perfil": "estudante",
                },
            },
        )

    transport = httpx.MockTransport(handle_request)

    async def mocked_signup(signup_payload):
        return await submit_student_signup(signup_payload, transport=transport)

    monkeypatch.setattr(frontend, "submit_student_signup", mocked_signup)
    session_id = f"signup-privacy-{uuid4()}"

    async def verify_session():
        async with frontend.app.modify_state(
            BaseStateToken(ident=session_id, cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            await state.submit_signup(payload)
            delta = await root._get_resolved_delta()
            public_state = state.dict()
            assert state._read_session_token() == session_token
            assert state.is_authenticated is True
            assert state.signup_has_error is False
            assert password not in json.dumps(delta, default=str)
            assert session_token not in json.dumps(delta, default=str)
            assert "api.example.test" not in json.dumps(delta, default=str)
            assert "Authorization" not in json.dumps(delta, default=str)
            assert password not in json.dumps(public_state, default=str)
            assert session_token not in json.dumps(public_state, default=str)
            assert "api.example.test" not in json.dumps(public_state, default=str)
            assert "_session_token" not in frontend.State.base_vars

    asyncio.run(verify_session())
    assert len(requests) == 1
    assert "Authorization" not in requests[0].headers
    assert password not in caplog.text
    assert session_token not in caplog.text
    assert "api.example.test" not in caplog.text


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (409, "Este e-mail já está cadastrado. Tente entrar com sua conta."),
        (400, "Confira os dados informados e tente novamente."),
    ],
)
def test_signup_api_failure_does_not_authenticate_session(
    monkeypatch, status_code, message
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status_code, text="resposta interna")
    )

    async def mocked_signup(signup_payload):
        return await submit_student_signup(signup_payload, transport=transport)

    monkeypatch.setattr(frontend, "submit_student_signup", mocked_signup)

    async def verify_session():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"signup-failure-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            await state.submit_signup(
                {"nome": "Ana", "email": "ana@escola.edu.br", "senha": "senha"}
            )
            assert state.signup_has_error is True
            assert state.signup_message == message
            assert state.is_authenticated is False
            assert state._read_session_token() is None

    asyncio.run(verify_session())


def test_signup_event_does_not_call_api_for_invalid_email(monkeypatch):
    calls = 0

    async def fail_if_called(payload):
        nonlocal calls
        calls += 1
        raise AssertionError("A API não deveria ser chamada.")

    monkeypatch.setattr(frontend, "submit_student_signup", fail_if_called)
    session_id = f"signup-invalid-{uuid4()}"

    async def verify_session():
        async with frontend.app.modify_state(
            BaseStateToken(ident=session_id, cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            await state.submit_signup(
                {"nome": "Ana", "email": "ana invalido@escola.edu.br", "senha": "senha"}
            )
            assert state.signup_has_error is True
            assert state.signup_message == (
                "O e-mail não pode conter espaços internos."
            )

    asyncio.run(verify_session())
    assert calls == 0


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (
            XanoConfigurationError("detalhe interno"),
            "O cadastro está temporariamente indisponível. Tente novamente mais tarde.",
        ),
        (
            XanoRequestError("detalhe interno"),
            "Não foi possível concluir o cadastro. Tente novamente mais tarde.",
        ),
        (
            SignupValidationError("Informe seu nome."),
            "Informe seu nome.",
        ),
    ],
)
def test_signup_error_mapping_does_not_expose_exception_details(error, message):
    assert signup_error_message(error) == message
    assert "detalhe interno" not in signup_error_message(error)

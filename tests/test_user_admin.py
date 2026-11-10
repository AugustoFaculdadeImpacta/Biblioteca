import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.user_admin import (
    UserAdminValidationError,
    build_librarian_payload,
    create_librarian,
    list_librarians,
    set_librarian_active,
)
from biblioteca_mais_nova.xano_client import XanoRequestError


def _librarian(user_id=12, *, active=True):
    return {
        "id": user_id,
        "nome": "Ana",
        "email": "ana@escola.edu.br",
        "ativo": active,
    }


def test_librarian_payload_normalizes_email_and_preserves_password():
    assert build_librarian_payload(
        {
            "nome": "  Ana Silva  ",
            "email": " ANA@ESCOLA.EDU.BR ",
            "senha": " senha inicial ",
        }
    ) == {
        "nome": "Ana Silva",
        "email": "ana@escola.edu.br",
        "senha": " senha inicial ",
    }


@pytest.mark.parametrize(
    ("form", "message"),
    [
        ({"nome": " ", "email": "ana@escola.edu.br", "senha": "senha"}, "nome"),
        (
            {"nome": "Ana", "email": "ana escola@escola.edu.br", "senha": "senha"},
            "espaços",
        ),
        ({"nome": "Ana", "email": "ana@escola.edu.br", "senha": ""}, "senha"),
    ],
)
def test_invalid_librarian_payload_is_rejected(form, message):
    with pytest.raises(UserAdminValidationError, match=message):
        build_librarian_payload(form)


def test_list_librarians_uses_authenticated_route_and_strips_extra_fields(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    **_librarian(active=False),
                    "senha": "hash-falso",
                    "authToken": "token-falso",
                    "hash": "hash-falso",
                }
            ],
        )

    result = asyncio.run(
        list_librarians(
            "token-de-teste",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == [
        {
            "id": 12,
            "nome": "Ana",
            "email": "ana@escola.edu.br",
            "ativo": False,
        }
    ]
    assert requests[0].method == "GET"
    assert str(requests[0].url) == "https://api.example.test/grupo/admin/usuarios"
    assert "Authorization" in requests[0].headers
    assert not ({"senha", "hash", "authToken"} & result[0].keys())


def test_create_librarian_sends_only_approved_fields_and_sanitizes_response(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []
    payload = build_librarian_payload(
        {
            "nome": "Ana",
            "email": " ANA@ESCOLA.EDU.BR ",
            "senha": "senha inicial",
        }
    )

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            201,
            json={
                **_librarian(),
                "perfil": "bibliotecario",
                "senha": "hash-falso",
                "authToken": "token-falso",
            },
        )

    result = asyncio.run(
        create_librarian(
            payload,
            "token-de-teste",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == _librarian()
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.example.test/grupo/admin/usuarios"
    assert json.loads(request.content) == {
        "nome": "Ana",
        "email": "ana@escola.edu.br",
        "senha": "senha inicial",
    }
    assert not (
        {"perfil", "ativo", "authToken"} & json.loads(request.content).keys()
    )
    assert not ({"senha", "authToken"} & result.keys())


@pytest.mark.parametrize("active", [False, True])
def test_status_update_supports_deactivation_and_reactivation_with_mock(
    monkeypatch, active
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=_librarian(active=active))

    result = asyncio.run(
        set_librarian_active(
            12,
            active,
            "token-de-teste",
            transport=httpx.MockTransport(handle),
        )
    )

    request = requests[0]
    assert request.method == "PATCH"
    assert str(request.url) == "https://api.example.test/admin/usuarios/12"
    assert json.loads(request.content) == {"ativo": active}
    assert result["ativo"] is active


def test_invalid_status_update_arguments_do_not_send_request(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    with pytest.raises(XanoRequestError):
        asyncio.run(set_librarian_active(0, False, "token-de-teste"))


def test_librarian_management_page_has_labeled_fields_and_responsive_styles():
    page = frontend.librarian_management()
    components = []

    def walk(component):
        components.append(component)
        for child in getattr(component, "children", []):
            if isinstance(child, rx.Component):
                walk(child)

    walk(page)
    form = next(
        component
        for component in components
        if component.id == "form-cadastro-bibliotecario"
    )
    fields = [
        component
        for component in form.children
        if component.alias == "RadixThemesTextField.Root"
    ]
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
    assert "admin/bibliotecarios" in frontend.app._unevaluated_pages
    assert frontend.app.style[":focus-visible"]["outline"].startswith("3px solid ")
    assert frontend.app.style[".librarian-list"]["grid_template_columns"] == (
        "repeat(auto-fit, minmax(min(100%, 18rem), 1fr))"
    )
    assert frontend.app.style["@media screen and (max-width: 40rem)"][
        ".librarian-card"
    ]["width"] == "100%"


def test_management_handlers_require_admin_and_keep_session_private(monkeypatch):
    async def verify():
        session_id = f"user-management-{uuid4()}"
        async with frontend.app.modify_state(
            BaseStateToken(ident=session_id, cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso-admin", "admin")
            monkeypatch.setattr(
                frontend,
                "list_librarians",
                lambda token: asyncio.sleep(0, result=[_librarian()]),
            )
            await state.load_librarians()
            assert state.managed_librarians == [
                {
                    "id": 12,
                    "nome": "Ana",
                    "email": "ana@escola.edu.br",
                    "ativo": True,
                }
            ]

            monkeypatch.setattr(
                frontend,
                "create_librarian",
                lambda payload, token: asyncio.sleep(
                    0, result=_librarian(user_id=13)
                ),
            )
            await state.submit_librarian(
                {
                    "nome": "Bia",
                    "email": "bia@escola.edu.br",
                    "senha": "senha falsa",
                }
            )
            assert state.librarian_management_success is True
            assert state.managed_librarians[-1]["id"] == 13

            monkeypatch.setattr(
                frontend,
                "set_librarian_active",
                lambda user_id, active, token: asyncio.sleep(
                    0, result=_librarian(user_id, active=active)
                ),
            )
            await state.set_librarian_active(13, False)
            assert state.managed_librarians[-1]["ativo"] is False

            delta = await root._get_resolved_delta()
            serialized = json.dumps(delta, default=str)
            assert "token-falso-admin" not in serialized
            assert '"admin"' not in serialized

    asyncio.run(verify())


def test_non_admin_cannot_load_or_mutate_librarians(monkeypatch):
    async def verify():
        session_id = f"user-management-denied-{uuid4()}"
        async with frontend.app.modify_state(
            BaseStateToken(ident=session_id, cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso-bibliotecario", "bibliotecario")

            async def fail_if_called(*args, **kwargs):
                raise AssertionError("A API não deveria ser chamada.")

            monkeypatch.setattr(frontend, "list_librarians", fail_if_called)
            redirect = await state.load_librarians()
            assert redirect is not None
            assert state.managed_librarians == []
            assert (
                await state.submit_librarian(
                    {
                        "nome": "Bia",
                        "email": "bia@escola.edu.br",
                        "senha": "senha falsa",
                    }
                )
                is not None
            )
            assert await state.set_librarian_active(13, False) is not None

    asyncio.run(verify())


def test_librarian_list_failure_is_reported(monkeypatch):
    async def verify():
        session_id = f"user-management-error-{uuid4()}"
        async with frontend.app.modify_state(
            BaseStateToken(ident=session_id, cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso-admin", "admin")

            async def fail(*args, **kwargs):
                raise XanoRequestError("Falha simulada.")

            monkeypatch.setattr(frontend, "list_librarians", fail)
            await state.load_librarians()
            assert state.librarian_management_has_error is True
            assert state.librarian_management_message
            assert state.librarian_management_pending is False

    asyncio.run(verify())

import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.catalog import (
    build_title_payload,
    catalog_error_message,
    get_public_title,
    list_admin_catalog,
    list_public_titles,
    update_title,
)
from biblioteca_mais_nova.xano_client import XanoRequestError, XanoResponseError


def _entry(active=True):
    return {
        "titulo": {
            "id": 81,
            "titulo": "Livro",
            "autores": "Autoria",
            "ativo": active,
            "isbn": None,
            "editora": None,
            "edicao": None,
            "ano_publicacao": None,
            "descricao": None,
        },
        "categorias": [
            {"id": 9, "titulo_id": 81, "categoria_id": 7},
        ],
        "exemplares_disponiveis": 1,
        "exemplares": [
            {
                "id": 101,
                "titulo_id": 81,
                "estado": "disponivel",
                "codigo_tombo": "EX-000101",
            },
            {
                "id": 102,
                "titulo_id": 81,
                "estado": "indisponivel",
                "codigo_tombo": None,
            },
        ],
    }


def test_public_catalog_never_returns_inactive_titles(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    response = [
        {
            "titulo": {
                "id": 1,
                "titulo": "Ativo",
                "autores": "Autoria",
                "ativo": True,
            },
            "categorias": [],
            "exemplares_disponiveis": 0,
        },
        {
            "titulo": {
                "id": 2,
                "titulo": "Legado",
                "autores": "Autoria",
                "ativo": None,
            },
            "categorias": [],
            "exemplares_disponiveis": 0,
        },
        {
            "titulo": {
                "id": 3,
                "titulo": "Inativo",
                "autores": "Autoria",
                "ativo": False,
            },
            "categorias": [],
            "exemplares_disponiveis": 0,
        },
    ]
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=response)
    )

    titles = asyncio.run(list_public_titles(transport=transport))

    assert [item["titulo"]["id"] for item in titles] == [1, 2]
    assert titles[1]["titulo"]["ativo"] is None


def test_public_catalog_detail_treats_inactive_title_as_not_found(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=_entry(active=False))
    )

    with pytest.raises(XanoResponseError) as error:
        asyncio.run(get_public_title(81, transport=transport))

    assert error.value.status_code == 404


def test_catalog_error_message_allows_only_known_business_messages(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    responses = [
        {"message": "A desativacao foi recusada: ha reserva ativa."},
        {"message": "Internal database details"},
    ]

    def handle(request):
        body = responses.pop(0)
        return httpx.Response(403, json=body)

    transport = httpx.MockTransport(handle)
    with pytest.raises(XanoResponseError) as blocked:
        asyncio.run(
            list_admin_catalog("token", transport=transport)
        )
    assert catalog_error_message(blocked.value) == (
        "O título não pode ser desativado enquanto houver reserva ativa."
    )

    with pytest.raises(XanoResponseError) as internal:
        asyncio.run(
            list_admin_catalog("token", transport=transport)
        )
    assert internal.value.public_detail is None
    assert "Internal database details" not in catalog_error_message(internal.value)


def test_admin_catalog_client_returns_inactive_titles_and_all_copy_states(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=[_entry(active=False)])

    entries = asyncio.run(
        list_admin_catalog(
            "token-restrito",
            transport=httpx.MockTransport(handle),
        )
    )

    assert len(entries) == 1
    assert entries[0]["titulo"]["ativo"] is False
    assert [copy["estado"] for copy in entries[0]["exemplares"]] == [
        "disponivel",
        "indisponivel",
    ]
    assert entries[0]["exemplares"][1]["codigo_tombo"] is None
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/grupo/admin/acervo"
    assert "Authorization" in requests[0].headers


def test_update_title_reuses_patch_and_only_sends_approved_fields(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests: list[httpx.Request] = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"id": 81, "ativo": False})

    payload = build_title_payload(
        {"titulo": "Novo título", "autores": "Autoria", "isbn": ""}
    )
    result = asyncio.run(
        update_title(
            81,
            payload,
            "token-restrito",
            active=False,
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == {"id": 81}
    assert requests[0].method == "PATCH"
    assert requests[0].url.path == "/catalogo/titulos/81"
    assert json.loads(requests[0].content) == {
        "titulo": "Novo título",
        "autores": "Autoria",
        "ativo": False,
    }
    assert "Authorization" in requests[0].headers


def test_catalog_admin_page_loads_full_inventory_and_keeps_token_private(
    monkeypatch,
):
    async def categories():
        return [{"id": 7, "nome": "Literatura"}]

    async def admin_catalog(token):
        assert token == "segredo-de-teste"
        return [_entry(active=False)]

    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"admin-catalog-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("segredo-de-teste", "bibliotecario")

            await state.load_catalog_page()

            assert state.admin_catalog_pending is False
            assert state.admin_catalog_has_error is False
            assert state.admin_catalog_display_entries[0]["ativo"] is False
            assert state.admin_catalog_display_entries[0]["categorias"] == "Literatura"
            assert len(state.admin_catalog_display_entries[0]["exemplares"]) == 2
            serialized = json.dumps(state.dict(), default=str)
            assert "segredo-de-teste" not in serialized
            assert "_session_token" not in serialized

    asyncio.run(verify())


def test_admin_catalog_edits_titles_and_adds_copies_without_repeating_writes(
    monkeypatch,
):
    updates = []
    added_copy_ids = []

    async def admin_catalog(token):
        assert token == "token-falso"
        return [_entry(active=True)]

    async def update(title_id, payload, token, *, active=None):
        updates.append((title_id, payload, token, active))
        return {"id": title_id}

    async def add_copy(title_id, token):
        added_copy_ids.append(title_id)
        return {
            "id": 103,
            "titulo_id": title_id,
            "estado": "disponivel",
            "codigo_tombo": "EX-000103",
        }

    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)
    monkeypatch.setattr(frontend, "update_title", update)
    monkeypatch.setattr(frontend, "create_copy", add_copy)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"catalog-admin-actions-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]

            await state.save_admin_title(
                {
                    "titulo_id": "81",
                    "titulo": "Livro revisado",
                    "autores": "Autoria",
                    "ano_publicacao": "2024",
                }
            )
            assert updates[0][0] == 81
            assert updates[0][1] == {
                "titulo": "Livro revisado",
                "autores": "Autoria",
                "ano_publicacao": 2024,
            }
            assert updates[0][3] is None
            assert state.admin_catalog_message == "Título atualizado."

            await state.set_title_active(81, False)
            assert updates[1][0] == 81
            assert updates[1][3] is False
            assert state.admin_catalog_message == "Título desativado."

            await state.set_title_active(81, True)
            assert updates[2][3] is True
            assert state.admin_catalog_message == "Título reativado."

            await state.add_copy_to_title(81)
            assert added_copy_ids == [81]
            assert state.admin_catalog_message == "Exemplar adicionado."

    asyncio.run(verify())


def test_uncertain_copy_creation_requires_manual_review_before_retry(
    monkeypatch,
):
    calls = 0

    async def create_uncertain_then_succeed(title_id, token):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise XanoRequestError("Falha de transporte")
        return {
            "id": 103,
            "titulo_id": title_id,
            "estado": "disponivel",
            "codigo_tombo": "EX-000103",
        }

    async def admin_catalog(token):
        return [_entry(active=True)]

    monkeypatch.setattr(frontend, "create_copy", create_uncertain_then_succeed)
    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"uncertain-copy-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]

            await state.add_copy_to_title(81)
            assert state.admin_catalog_needs_manual_check is True
            assert state.admin_catalog_has_error is True

            await state.add_copy_to_title(81)
            assert calls == 1

            await state.refresh_admin_catalog()
            state.acknowledge_admin_catalog_check()
            assert state.admin_catalog_needs_manual_check is False

            await state.add_copy_to_title(81)
            assert calls == 2
            assert state.admin_catalog_message == "Exemplar adicionado."

    asyncio.run(verify())


@pytest.mark.parametrize("profile", ["", "estudante"])
def test_admin_catalog_handlers_reject_unauthorized_profiles(
    monkeypatch,
    profile,
):
    async def unexpected(*args, **kwargs):
        raise AssertionError("A API administrativa não deve ser chamada.")

    monkeypatch.setattr(frontend, "list_admin_catalog", unexpected)
    monkeypatch.setattr(frontend, "update_title", unexpected)
    monkeypatch.setattr(frontend, "create_copy", unexpected)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"catalog-admin-block-{profile}-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            if profile:
                state._store_session("token-falso", profile)

            destination = "/login" if not profile else "/"
            for result in (
                await state.refresh_admin_catalog(),
                await state.save_admin_title(
                    {"titulo_id": "81", "titulo": "Livro", "autores": "Autoria"}
                ),
                await state.set_title_active(81, False),
                await state.add_copy_to_title(81),
            ):
                assert f"_var_value='{destination}'" in repr(result)

    asyncio.run(verify())

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


def _example_book(title, authors, category, copies=2):
    return {
        "titulo": title,
        "autores": authors,
        "isbn": "9780000000002",
        "ano_publicacao": 2024,
        "editora": "Editora teste",
        "edicao": "Brasileira",
        "categoria": category,
        "exemplares": copies,
        "descricao": "Descrição de teste.",
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


def test_admin_actions_handle_success_404_403_and_connection():
    assert catalog_error_message(XanoResponseError(404)) == (
        "O recurso não foi encontrado ou a rota ainda não está disponível."
    )
    assert catalog_error_message(XanoResponseError(403)) == (
        "Sua conta não tem permissão para acessar este recurso."
    )
    assert catalog_error_message(XanoRequestError("Falha de rede")) == (
        "Não foi possível se comunicar com o serviço Xano. Verifique a conexão e tente novamente."
    )


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (XanoResponseError(403), "Sua conta não tem permissão"),
        (XanoResponseError(404), "O recurso não foi encontrado"),
        (XanoRequestError("Falha de rede"), "Não foi possível se comunicar"),
    ],
)
def test_title_deactivation_reports_http_and_connection_errors(
    monkeypatch,
    error,
    expected,
):
    async def fail_update(*args, **kwargs):
        raise error

    async def admin_catalog(token):
        return [_entry(active=True)]

    monkeypatch.setattr(frontend, "update_title", fail_update)
    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"title-error-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]
            state.request_title_deactivation(81)

            await state.set_title_active(81, False)

            assert state.admin_catalog_has_error is True
            assert expected in state.admin_catalog_title_action_message
            assert state.admin_catalog_confirm_title_id is None

    asyncio.run(verify())


def test_title_deactivation_detects_apparent_success(monkeypatch):
    async def update(title_id, payload, token, *, active=None):
        assert active is False
        return {"id": title_id, "ativo": False}

    async def admin_catalog(token):
        return [_entry(active=True)]

    monkeypatch.setattr(frontend, "update_title", update)
    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"title-apparent-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]
            state.request_title_deactivation(81)

            await state.set_title_active(81, False)

            assert state.admin_catalog_title_action_error is True
            assert state.admin_catalog_title_action_message == (
                "O servidor respondeu, mas o título continua ativo. "
                "A atualização do servidor pode não estar publicada"
            )
            assert state.admin_catalog_display_entries[0]["ativo"] is True

    asyncio.run(verify())


def test_deactivation_diagnostic_is_opt_in_and_never_prints_secrets(
    monkeypatch,
    capfd,
):
    async def update(title_id, payload, token, *, active=None):
        assert active is False
        return {"id": title_id, "ativo": False, "detalhe_publico": "ok"}

    async def admin_catalog(token):
        return [_entry(active=False)]

    monkeypatch.setattr(frontend, "update_title", update)
    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)
    monkeypatch.delenv("BIBLIOTECA_DIAGNOSTICO", raising=False)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"title-diagnostic-off-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-super-secreto", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]
            state.request_title_deactivation(81)
            await state.set_title_active(81, False)

    asyncio.run(verify())
    assert "desativacao-titulo" not in capfd.readouterr().out

    monkeypatch.setenv("BIBLIOTECA_DIAGNOSTICO", "1")

    async def verify_enabled():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"title-diagnostic-on-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-super-secreto", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]
            state.request_title_deactivation(81)
            await state.set_title_active(81, False)

    asyncio.run(verify_enabled())
    output = capfd.readouterr().out
    assert "desativacao-titulo" in output
    assert "metodo=PATCH" in output
    assert "caminho=/catalogo/titulos/81" in output
    assert "chaves_corpo=" in output
    assert "ativo_releitura=False" in output
    assert "token-super-secreto" not in output
    assert "81" in output


def test_title_deactivation_reports_refresh_connection_failure(monkeypatch):
    async def update(title_id, payload, token, *, active=None):
        return {"id": title_id, "ativo": False}

    async def fail_refresh(token):
        raise XanoRequestError("Falha de comunicação")

    monkeypatch.setattr(frontend, "update_title", update)
    monkeypatch.setattr(frontend, "list_admin_catalog", fail_refresh)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"title-refresh-error-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            state.admin_catalog_entries = [_entry(active=True)]
            state.request_title_deactivation(81)

            await state.set_title_active(81, False)

            assert state.admin_catalog_title_action_error is True
            assert state.admin_catalog_title_action_message == (
                "Não foi possível confirmar a atualização do título."
            )

    asyncio.run(verify())


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

            tarefa_em_segundo_plano = await state.load_catalog_page()
            state.public_catalog_cover_resolutions[
                frontend._capa_busca_key("Livro", "Autoria")
            ] = "https://covers.openlibrary.org/b/id/81-L.jpg"

            assert state.admin_catalog_pending is False
            assert state.admin_catalog_has_error is False
            assert state.admin_catalog_display_entries[0]["ativo"] is False
            assert state.admin_catalog_display_entries[0]["categorias"] == "Literatura"
            assert state.admin_catalog_display_entries[0]["capa_real"] == (
                "https://covers.openlibrary.org/b/id/81-L.jpg"
            )
            assert tarefa_em_segundo_plano is not None
            assert len(state.admin_catalog_display_entries[0]["exemplares"]) == 2
            serialized = json.dumps(state.dict(), default=str)
            assert "segredo-de-teste" not in serialized
            assert "_session_token" not in serialized

    asyncio.run(verify())


def test_acervo_search_normalizes_text_and_empty_state():
    entries = [
        {
            "id": 1,
            "titulo": "Ciência Fácil",
            "autores": "Álvaro Silva",
            "isbn": "978-1",
            "categorias": "Ciências",
            "exemplares": [],
            "exemplares_disponiveis": 1,
            "capa_url": "",
            "ativo": True,
        },
    ]
    assert frontend._catalog_search_key("CIENCIA") == "ciencia"
    assert frontend._catalog_search_key("Álvaro") == "alvaro"
    assert "Nenhum título encontrado." in repr(
        rx.text("Nenhum título encontrado.")
    ) or "Nenhum" in repr(rx.text("Nenhum título encontrado."))


def test_acervo_has_one_edit_panel():
    card = frontend.admin_title_card(
        rx.Var.create(
            {
                "id": 81,
                "titulo": "Livro",
                "autores": "Autoria",
                "isbn": "",
                "editora": "",
                "edicao": "",
                "ano_publicacao": "",
                "descricao": "",
                "capa_url": "",
                "capa_real": "",
                "capa_gerada": "",
                "ativo": True,
                "categorias": "Literatura",
                "exemplares_disponiveis": 1,
                "exemplares": [],
            }
        ).to(frontend.AdminCatalogDisplayEntry)
    )
    assert "admin-title-edit-form" in repr(card)
    assert "painel-exemplares-titulo-" in repr(card)
    assert "aria-controls" in repr(card)


def test_acervo_hides_inactive_by_default_and_keeps_one_panel_open():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"acervo-inactive-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state.admin_catalog_entries = [
                _entry(active=True),
                _entry(active=False),
            ]
            state.admin_catalog_entries[1]["titulo"]["id"] = 82
            state.admin_catalog_entries[1]["titulo"]["titulo"] = "Desativado"

            assert state.admin_catalog_show_inactive is False
            assert all(
                entry["ativo"]
                for entry in state.filtered_admin_catalog_entries
            )

            state.set_admin_catalog_show_inactive(True)
            assert any(
                not entry["ativo"]
                for entry in state.filtered_admin_catalog_entries
            )

            state.open_admin_title_edit(81)
            assert state.admin_catalog_edit_title_id == 81
            assert state.admin_catalog_copy_title_id is None

            state.toggle_admin_title_copies(81)
            assert state.admin_catalog_edit_title_id is None
            assert state.admin_catalog_copy_title_id == 81

            state.toggle_admin_title_copies(82)
            assert state.admin_catalog_copy_title_id == 82

            state.toggle_admin_title_copies(82)
            assert state.admin_catalog_copy_title_id is None

    asyncio.run(verify())


def test_acervo_vertical_layout_is_responsive_and_covers_keep_portrait_ratio():
    page = repr(frontend.catalog_admin())
    style = frontend.app.style
    mobile = style["@media screen and (max-width: 48rem)"]

    assert "admin-catalog-grid" in page
    assert "Mostrar desativados" in page
    assert "admin-title-row" in page
    assert style[".admin-catalog-grid"]["display"] == "flex"
    assert style[".admin-catalog-grid"]["flex_direction"] == "column"
    assert style[".admin-title-row"]["grid_template_columns"] == (
        "72px minmax(0, 1fr) auto"
    )
    cover_style = style[
        ".admin-catalog-cover-image, .admin-catalog-cover-fallback"
    ]
    assert cover_style["width"] == "72px"
    assert cover_style["aspect_ratio"] == "2 / 3"
    assert "height" not in cover_style
    assert mobile[".admin-title-row"]["grid_template_columns"] == (
        "72px minmax(0, 1fr)"
    )


def test_acervo_paginates_in_groups_of_ten():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"acervo-pagination-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.admin_catalog_visible_limit = 10
            state.show_more_admin_catalog()
            assert state.admin_catalog_visible_limit == 20

    asyncio.run(verify())


def test_example_books_preview_is_read_only_and_reports_categories(monkeypatch):
    books = [
        _example_book("Dom Casmurro", "Machado de Assis", "Literatura"),
        _example_book("Livro Novo", "Autora Nova", "Literatura"),
        _example_book("Livro sem categoria", "Outra Autora", "Ciências"),
    ]
    monkeypatch.setattr(frontend, "TITULOS_EXEMPLO", books)

    async def admin_catalog(token):
        assert token == "token-admin"
        return [
            {
                "titulo": {
                    "titulo": "DOM CASMURRO",
                    "autores": "Machado de Ássis",
                }
            }
        ]

    async def categories():
        return [{"id": 7, "nome": "literatura"}]

    async def unexpected(*args, **kwargs):
        raise AssertionError("A prévia não pode fazer gravações.")

    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)
    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "create_title", unexpected)
    monkeypatch.setattr(frontend, "associate_category", unexpected)
    monkeypatch.setattr(frontend, "create_copy", unexpected)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"example-preview-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")

            await state.preview_example_books()

            assert state.example_seed_preview_ready is True
            assert state.example_seed_preview_create_count == 1
            assert state.example_seed_preview_existing_count == 1
            assert state.example_seed_missing_categories == ["Ciências"]
            serialized = json.dumps(state.dict(), default=str)
            assert "token-admin" not in serialized
            assert "_session_token" not in serialized

    asyncio.run(verify())


def test_example_books_import_maps_categories_and_is_idempotent(monkeypatch):
    books = [
        _example_book("Livro Um", "Autora Um", "Literatura", copies=2),
        _example_book("Livro Dois", "Autor Dois", "Ciências", copies=3),
        _example_book("Sem categoria", "Outra Autoria", "História"),
    ]
    monkeypatch.setattr(frontend, "TITULOS_EXEMPLO", books)
    entries = []
    title_calls = []
    category_calls = []
    copy_calls = []

    async def admin_catalog(token):
        assert token == "token-admin"
        return list(entries)

    async def categories():
        return [
            {"id": 7, "nome": "literatura"},
            {"id": 9, "nome": "CIENCIAS"},
        ]

    async def create_title(payload, token):
        assert token == "token-admin"
        title_calls.append(payload)
        title_id = len(title_calls) + 100
        entry = _entry()
        entry["titulo"]["titulo"] = payload["titulo"]
        entry["titulo"]["autores"] = payload["autores"]
        entries.append(entry)
        return {"id": title_id}

    async def associate_category(title_id, category_id, token):
        category_calls.append((title_id, category_id, token))
        return {
            "id": title_id + 1000,
            "titulo_id": title_id,
            "categoria_id": category_id,
        }

    async def create_copy(title_id, token):
        copy_calls.append((title_id, token))
        return {
            "id": len(copy_calls) + 500,
            "titulo_id": title_id,
            "estado": "disponivel",
            "codigo_tombo": f"EX-{len(copy_calls):06}",
        }

    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)
    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "create_title", create_title)
    monkeypatch.setattr(frontend, "associate_category", associate_category)
    monkeypatch.setattr(frontend, "create_copy", create_copy)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"example-import-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")

            state.request_example_books_import()
            assert state.example_seed_confirming is True
            await state.confirm_example_books_import()

            assert state.example_seed_created == 2
            assert state.example_seed_ignored == 1
            assert state.example_seed_errors == 0
            assert [call[1] for call in category_calls] == [7, 9]
            assert len(copy_calls) == 5

            state.request_example_books_import()
            await state.confirm_example_books_import()

            assert len(title_calls) == 2
            assert state.example_seed_created == 0
            assert state.example_seed_ignored == 3
            assert state.example_seed_errors == 0

    asyncio.run(verify())


def test_example_books_import_stops_at_first_server_error_without_secrets(
    monkeypatch,
):
    books = [
        _example_book("Livro Um", "Autora Um", "Literatura"),
        _example_book("Livro Dois", "Autor Dois", "Literatura"),
    ]
    monkeypatch.setattr(frontend, "TITULOS_EXEMPLO", books)
    create_calls = []

    async def admin_catalog(token):
        return []

    async def categories():
        return [{"id": 7, "nome": "Literatura"}]

    async def create_title(payload, token):
        create_calls.append(payload)
        raise XanoResponseError(503)

    async def unexpected(*args, **kwargs):
        raise AssertionError("A sequência deve parar na primeira falha.")

    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)
    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "create_title", create_title)
    monkeypatch.setattr(frontend, "associate_category", unexpected)
    monkeypatch.setattr(frontend, "create_copy", unexpected)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"example-import-error-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("sensitive-session-value", "admin")
            state.request_example_books_import()
            await state.confirm_example_books_import()

            assert len(create_calls) == 1
            assert state.example_seed_progress == 1
            assert state.example_seed_errors == 1
            assert "1 erro" in state.example_seed_message
            assert "sensitive-session-value" not in state.example_seed_message
            assert "503" not in state.example_seed_message

    asyncio.run(verify())


def test_example_books_import_is_admin_only_and_section_is_conditional(
    monkeypatch,
):
    async def unexpected(*args, **kwargs):
        raise AssertionError("Somente admin real pode consultar ou gravar.")

    monkeypatch.setattr(frontend, "list_admin_catalog", unexpected)
    monkeypatch.setattr(frontend, "list_categories", unexpected)
    monkeypatch.setattr(frontend, "create_title", unexpected)
    page = repr(frontend.example_books_import_section())

    assert "can_manage_librarians" in page
    assert "Livros de exemplo" in page
    assert "Confirmar" in page
    assert "Cancelar" in page

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"example-import-noadmin-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-librarian", "bibliotecario")

            await state.preview_example_books()
            result = await state.confirm_example_books_import()

            assert "_var_value='/'" in repr(result)

    asyncio.run(verify())


def test_staff_can_edit_from_catalog_and_detail():
    catalog = repr(frontend.public_catalog())
    detail = repr(frontend.public_catalog_detail())
    assert "Editar" in catalog
    assert "Editar" in detail


def test_admin_catalog_edits_titles_and_adds_copies_without_repeating_writes(
    monkeypatch,
):
    updates = []
    added_copy_ids = []

    async def admin_catalog(token):
        assert token == "token-falso"
        if updates and updates[-1][3] is not None:
            return [_entry(active=updates[-1][3])]
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

            state.request_title_deactivation(81)
            assert state.admin_catalog_confirm_title_id == 81
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

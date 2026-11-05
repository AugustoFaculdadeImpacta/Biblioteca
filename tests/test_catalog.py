import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.catalog import (
    CatalogValidationError,
    associate_category,
    build_title_payload,
    category_contains_title,
    create_copy,
    create_title,
    list_categories,
)
from biblioteca_mais_nova.xano_client import XanoRequestError, XanoResponseError


def _components(component: rx.Component):
    yield component
    for child in component.children:
        if isinstance(child, rx.Component):
            yield from _components(child)


def test_catalog_form_has_only_defined_fields_and_category_selection():
    page = frontend.catalog_admin()
    components = list(_components(page))
    form = next(
        component
        for component in components
        if component.id == "form-cadastro-titulo"
    )
    fields = [
        component
        for component in form.children
        if component.alias == "RadixThemesTextField.Root"
    ]

    assert "admin/acervo" in frontend.app._unevaluated_pages
    assert [field.name._var_value for field in fields] == [
        "titulo",
        "autores",
        "isbn",
        "editora",
        "edicao",
        "ano_publicacao",
    ]
    assert all(fields[index].required._var_value for index in (0, 1))
    labels = [
        component
        for component in form.children
        if type(component).__name__ == "Label"
    ]
    assert [label.html_for._var_value for label in labels] == [
        "catalog-titulo",
        "catalog-autores",
        "catalog-isbn",
        "catalog-editora",
        "catalog-edicao",
        "catalog-ano-publicacao",
        "catalog-descricao",
    ]
    assert any(
        component.alias == "RadixThemesCheckbox"
        for component in _components(form)
    )
    description = next(
        component
        for component in form.children
        if component.alias == "RadixThemesTextArea"
    )
    assert description.name._var_value == "descricao"
    assert frontend.app.style[":focus-visible"] == {
        "outline": "3px solid #005fcc",
        "outline_offset": "3px",
    }


def test_title_payload_uses_only_defined_fields_and_omits_blank_optionals():
    assert build_title_payload(
        {
            "titulo": "  Livro  ",
            "autores": "  Autoria  ",
            "isbn": " ISBN ",
            "editora": "",
            "edicao": " 2ª ",
            "ano_publicacao": "2024",
            "descricao": "  Descrição ",
            "campo_extra": "não permitido",
        }
    ) == {
        "titulo": "Livro",
        "autores": "Autoria",
        "isbn": "ISBN",
        "edicao": "2ª",
        "ano_publicacao": 2024,
        "descricao": "Descrição",
    }


@pytest.mark.parametrize(
    ("form_data", "message"),
    [
        ({"titulo": " ", "autores": "Autoria"}, "Informe o título."),
        ({"titulo": "Livro", "autores": " "}, "Informe os autores."),
        (
            {"titulo": "Livro", "autores": "Autoria", "ano_publicacao": "20x"},
            "O ano de publicação deve ser um número inteiro.",
        ),
    ],
)
def test_invalid_title_is_rejected(form_data, message):
    with pytest.raises(CatalogValidationError, match=message):
        build_title_payload(form_data)


def test_catalog_services_follow_local_xano_fields_and_routes(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/grupo")
    requests: list[httpx.Request] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        path = request.url.path
        if request.method == "GET" and path.endswith("/catalogo/categorias"):
            return httpx.Response(
                200,
                json=[{"id": 7, "nome": "Literatura"}],
            )
        if request.method == "POST" and path.endswith("/catalogo/titulos"):
            return httpx.Response(
                200,
                json={"id": 81, "titulo": "Livro", "autores": "Autoria"},
            )
        if request.method == "POST" and path.endswith("/admin/titulos/81/categorias"):
            return httpx.Response(
                200,
                json={"id": 9, "titulo_id": 81, "categoria_id": 7},
            )
        if request.method == "GET" and path.endswith(
            "/catalogo/categorias/7/titulos"
        ):
            return httpx.Response(200, json=[{"id": 81, "titulo": "Livro"}])
        if request.method == "POST" and path.endswith("/admin/exemplares"):
            return httpx.Response(
                200,
                json={
                    "id": 101,
                    "titulo_id": 81,
                    "estado": "disponivel",
                    "codigo_tombo": "EX-000101",
                },
            )
        raise AssertionError(f"Chamada não esperada: {request.method} {path}")

    transport = httpx.MockTransport(handle_request)
    token = "token-de-teste"
    categories = asyncio.run(list_categories(transport=transport))
    title = asyncio.run(
        create_title(
            build_title_payload({"titulo": "Livro", "autores": "Autoria"}),
            token,
            transport=transport,
        )
    )
    association = asyncio.run(
        associate_category(title["id"], categories[0]["id"], token, transport=transport)
    )
    has_association = asyncio.run(
        category_contains_title(
            categories[0]["id"],
            title["id"],
            transport=transport,
        )
    )
    copy = asyncio.run(create_copy(title["id"], token, transport=transport))

    assert categories == [{"id": 7, "nome": "Literatura"}]
    assert title == {"id": 81}
    assert association == {"id": 9, "titulo_id": 81, "categoria_id": 7}
    assert has_association is True
    assert copy == {
        "id": 101,
        "titulo_id": 81,
        "estado": "disponivel",
        "codigo_tombo": "EX-000101",
    }
    assert [request.method for request in requests] == [
        "GET",
        "POST",
        "POST",
        "GET",
        "POST",
    ]
    assert [request.url.path for request in requests] == [
        "/grupo/catalogo/categorias",
        "/grupo/catalogo/titulos",
        "/grupo/admin/titulos/81/categorias",
        "/grupo/catalogo/categorias/7/titulos",
        "/grupo/admin/exemplares",
    ]
    assert json.loads(requests[1].content) == {
        "titulo": "Livro",
        "autores": "Autoria",
    }
    assert json.loads(requests[2].content) == {"categoria_id": 7}
    assert json.loads(requests[4].content) == {"titulo_id": 81}
    for request in (requests[1], requests[2], requests[4]):
        assert request.headers["Authorization"] == f"Bearer {token}"


def test_catalog_services_reject_missing_ids_and_codes(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    payload = build_title_payload({"titulo": "Livro", "autores": "Autoria"})
    cases = [
        (create_title, (payload, "token"), {"id": "81"}),
        (
            associate_category,
            (81, 7, "token"),
            {"id": 9, "titulo_id": 999, "categoria_id": 7},
        ),
        (
            create_copy,
            (81, "token"),
            {"id": 101, "titulo_id": 81, "estado": "disponivel"},
        ),
    ]
    for operation, args, response_body in cases:
        with pytest.raises(XanoRequestError):
            asyncio.run(
                operation(
                    *args,
                    transport=httpx.MockTransport(
                        lambda request, body=response_body: httpx.Response(
                            200,
                            json=body,
                        )
                    ),
                )
            )


def test_admin_events_block_visitors_and_students_before_writes(monkeypatch):
    calls = 0

    async def fail_if_called(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("A operação administrativa não deveria ser chamada.")

    monkeypatch.setattr(frontend, "create_title", fail_if_called)
    monkeypatch.setattr(frontend, "list_categories", fail_if_called)

    async def verify_profile(profile):
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"catalog-block-{profile}-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            if profile:
                state._store_session("token-falso", profile)
            await state.load_catalog_categories()
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )
            await state.create_catalog_copy()
            assert state._catalog_title_id is None

    asyncio.run(verify_profile(""))
    asyncio.run(verify_profile("estudante"))
    assert calls == 0


def test_admin_rejected_write_is_not_reported_as_success(monkeypatch):
    async def rejected_title(payload, token):
        raise XanoResponseError(403)

    monkeypatch.setattr(frontend, "create_title", rejected_title)

    async def verify_rejection():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"catalog-403-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )
            assert state.catalog_title_created is False
            assert state._catalog_title_id is None
            assert state.catalog_has_error is True
            assert state.catalog_message != "Título e categorias cadastrados."
            assert "detalhe" not in state.catalog_message

    asyncio.run(verify_rejection())


def test_catalog_flow_uses_returned_ids_and_can_resume_rejected_category(
    monkeypatch,
):
    create_title_calls = 0
    association_calls: list[tuple[int, int]] = []
    association_fail_once = True

    async def mocked_list_categories():
        return [{"id": 7, "nome": "Literatura"}]

    async def mocked_create_title(payload, token):
        nonlocal create_title_calls
        create_title_calls += 1
        assert payload["titulo"] == "Livro"
        assert token == "token-falso"
        return {"id": 81}

    async def mocked_associate(title_id, category_id, token):
        nonlocal association_fail_once
        association_calls.append((title_id, category_id))
        if association_fail_once:
            association_fail_once = False
            raise XanoRequestError("Falha de rede sem detalhes")
        return {
            "id": 9,
            "titulo_id": title_id,
            "categoria_id": category_id,
        }

    async def mocked_category_contains_title(category_id, title_id):
        return False

    async def mocked_create_copy(title_id, token):
        return {
            "id": 101,
            "titulo_id": title_id,
            "estado": "disponivel",
            "codigo_tombo": "EX-000101",
        }

    monkeypatch.setattr(frontend, "list_categories", mocked_list_categories)
    monkeypatch.setattr(frontend, "create_title", mocked_create_title)
    monkeypatch.setattr(frontend, "associate_category", mocked_associate)
    monkeypatch.setattr(
        frontend,
        "category_contains_title",
        mocked_category_contains_title,
    )
    monkeypatch.setattr(frontend, "create_copy", mocked_create_copy)

    async def verify_flow():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"catalog-flow-retry-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            await state.load_catalog_categories()
            state.toggle_catalog_category(7, True)
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )

            assert state.catalog_title_created is True
            assert state._catalog_title_id == 81
            assert state.catalog_categories_pending is True
            assert state.catalog_needs_manual_check is False
            assert state.catalog_has_error is True
            assert state._catalog_title_id not in state.dict().values()

            await state.retry_catalog_categories()
            assert state.catalog_categories_pending is False
            assert state.catalog_has_error is False
            await state.create_catalog_copy()
            assert state.catalog_created_codes == ["EX-000101"]
            assert state._catalog_title_id not in state.dict().values()

    asyncio.run(verify_flow())
    assert create_title_calls == 1
    assert association_calls == [(81, 7), (81, 7)]


def test_uncertain_category_is_reconciled_without_repeating_the_write(monkeypatch):
    association_calls = 0
    title_id = 987654321

    async def mocked_list_categories():
        return [{"id": 7, "nome": "Literatura"}]

    async def mocked_create_title(payload, token):
        return {"id": title_id}

    async def uncertain_association(*args):
        nonlocal association_calls
        association_calls += 1
        raise XanoRequestError("Falha de transporte")

    async def association_exists(category_id, requested_title_id):
        assert category_id == 7
        assert requested_title_id == title_id
        return True

    monkeypatch.setattr(frontend, "list_categories", mocked_list_categories)
    monkeypatch.setattr(frontend, "create_title", mocked_create_title)
    monkeypatch.setattr(frontend, "associate_category", uncertain_association)
    monkeypatch.setattr(frontend, "category_contains_title", association_exists)

    async def verify_reconciliation():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"catalog-reconcile-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            await state.load_catalog_categories()
            state.toggle_catalog_category(7, True)
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )

            assert state.catalog_title_created is True
            assert state.catalog_categories_pending is False
            assert state.catalog_message == "Título e categorias cadastrados."
            public_state = json.dumps(state.dict(), default=str)
            delta = json.dumps(await root._get_resolved_delta(), default=str)
            assert str(title_id) not in public_state
            assert str(title_id) not in delta

    asyncio.run(verify_reconciliation())
    assert association_calls == 1


def test_uncertain_title_and_copy_results_are_never_retried_automatically(
    monkeypatch,
):
    title_calls = 0
    copy_calls = 0

    async def mocked_list_categories():
        return []

    async def uncertain_title(payload, token):
        nonlocal title_calls
        title_calls += 1
        raise XanoRequestError("Falha de transporte")

    async def successful_title(payload, token):
        return {"id": 81}

    async def uncertain_copy(title_id, token):
        nonlocal copy_calls
        copy_calls += 1
        raise XanoRequestError("Falha de transporte")

    monkeypatch.setattr(frontend, "list_categories", mocked_list_categories)
    monkeypatch.setattr(frontend, "create_title", uncertain_title)
    monkeypatch.setattr(frontend, "create_copy", uncertain_copy)

    async def verify_flow():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"catalog-title-uncertain-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )
            assert state.catalog_needs_manual_check is True
            assert state._catalog_title_uncertain is True

        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"catalog-copy-uncertain-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            monkeypatch.setattr(frontend, "create_title", successful_title)
            state._store_session("token-falso", "bibliotecario")
            await state.load_catalog_categories()
            await state.submit_catalog_title(
                {"titulo": "Livro", "autores": "Autoria"}
            )
            await state.create_catalog_copy()
            await state.create_catalog_copy()
            assert state._catalog_copy_uncertain is True
            assert state.catalog_needs_manual_check is True

    asyncio.run(verify_flow())
    assert title_calls == 1
    assert copy_calls == 1

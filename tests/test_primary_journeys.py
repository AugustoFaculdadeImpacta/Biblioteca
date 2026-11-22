import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.data import PageData
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.catalog import (
    associate_category,
    create_copy,
    create_title,
    get_public_title,
    list_admin_catalog,
    list_categories,
    list_public_titles,
)
from biblioteca_mais_nova.circulation import (
    list_admin_loans,
    list_admin_requests,
    list_admin_reservations,
    list_my_loans,
    list_my_requests,
    list_my_reservations,
    register_request_pickup,
    request_title_loan,
)
from biblioteca_mais_nova.login import submit_login
from biblioteca_mais_nova.xano_client import XanoResponseError


def _title_entry(title_id: int, *, copies: list[dict] | None = None) -> dict:
    categories = (
        [{"id": 91, "titulo_id": title_id, "categoria_id": 3}]
        if title_id == 81 and copies is not None
        else []
    )
    return {
        "titulo": {
            "id": title_id,
            "titulo": "A Ilha",
            "autores": "Autoria de teste",
            "ativo": True,
            "isbn": None,
            "editora": None,
            "edicao": None,
            "ano_publicacao": 2024,
            "descricao": "Descrição de teste",
        },
        "categorias": categories,
        "exemplares_disponiveis": sum(
            copy["estado"] == "disponivel" for copy in (copies or [])
        ),
        **({"exemplares": copies or []} if copies is not None else {}),
    }


def test_student_login_catalog_request_and_library_use_one_mock_transport(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    token = "token-estudante-sintetico"
    password = "senha-sintetica"
    title = _title_entry(81)
    calls: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        path = request.url.path
        if path == "/auth/login":
            return httpx.Response(
                200,
                json={
                    "authToken": token,
                    "usuario": {
                        "id": 41,
                        "nome": "Estudante de teste",
                        "email": "estudante@example.test",
                        "perfil": "estudante",
                    },
                },
            )
        if request.method == "GET" and path in {
            "/catalogo/titulos",
            "/catalogo/titulos/81",
        }:
            return httpx.Response(
                200,
                json=[title] if path == "/catalogo/titulos" else title,
            )
        if request.method == "GET" and path == "/catalogo/categorias":
            return httpx.Response(200, json=[{"id": 3, "nome": "Literatura"}])
        if request.method == "POST" and path == "/solicitacoes-emprestimo":
            return httpx.Response(
                201,
                json={
                    "id": 51,
                    "usuario_id": 41,
                    "titulo_id": 81,
                    "estado": "pendente",
                },
            )
        if request.method == "GET" and path == "/minhas/emprestimos":
            return httpx.Response(200, json=[])
        if request.method == "GET" and path == "/minhas/solicitacoes":
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 51,
                        "usuario_id": 41,
                        "titulo_id": 81,
                        "estado": "pendente",
                    }
                ],
            )
        if request.method == "GET" and path == "/minhas/reservas":
            return httpx.Response(200, json=[])
        raise AssertionError(f"Chamada inesperada: {request.method} {path}")

    transport = httpx.MockTransport(handle)

    async def authenticate(payload):
        return await submit_login(payload, transport=transport)

    async def public_titles():
        return await list_public_titles(transport=transport)

    async def categories():
        return await list_categories(transport=transport)

    async def public_title(title_id):
        return await get_public_title(title_id, transport=transport)

    async def request_loan(title_id, session_token):
        return await request_title_loan(
            title_id,
            session_token,
            transport=transport,
        )

    async def personal_loans(session_token):
        return await list_my_loans(session_token, transport=transport)

    async def personal_requests(session_token):
        return await list_my_requests(session_token, transport=transport)

    async def personal_reservations(session_token):
        return await list_my_reservations(session_token, transport=transport)

    monkeypatch.setattr(frontend, "authenticate", authenticate)
    monkeypatch.setattr(frontend, "list_public_titles", public_titles)
    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "get_public_title", public_title)
    monkeypatch.setattr(frontend, "request_title_loan", request_loan)
    monkeypatch.setattr(frontend, "list_my_loans", personal_loans)
    monkeypatch.setattr(frontend, "list_my_requests", personal_requests)
    monkeypatch.setattr(frontend, "list_my_reservations", personal_reservations)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"journey-student-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            await state.submit_login(
                {"email": "STUDENT@example.test", "senha": password}
            )
            assert state.is_student is True
            assert state._read_session_token() == token

            await state.load_public_catalog()
            assert state.public_catalog_entries[0]["titulo"]["id"] == 81

            state.rx_router_page = PageData(params={"titulo_id": "81"})
            await state.load_public_catalog_detail()
            assert state.public_catalog_detail["titulo"] == "A Ilha"

            await state.request_catalog_title(81)
            assert state.student_request_has_error is False
            assert state.student_request_message.startswith(
                "Sua solicitação foi registrada."
            )

            await state.load_student_library()
            assert state.student_library_requests[0]["id"] == 51
            assert state.student_library_requests[0]["titulo"] == "A Ilha"
            serialized = json.dumps(
                await root._get_resolved_delta(),
                default=str,
            )
            public_state = json.dumps(state.dict(), default=str)
            for secret in (token, password):
                assert secret not in serialized
                assert secret not in public_state

    asyncio.run(verify())
    assert [request.url.path for request in calls] == [
        "/auth/login",
        "/catalogo/titulos",
        "/catalogo/categorias",
        "/catalogo/titulos/81",
        "/catalogo/categorias",
        "/solicitacoes-emprestimo",
        "/minhas/emprestimos",
        "/minhas/solicitacoes",
        "/minhas/reservas",
        "/catalogo/titulos",
    ]
    assert json.loads(calls[0].content) == {
        "email": "student@example.test",
        "senha": password,
    }
    assert "Authorization" not in calls[0].headers
    assert all(
        request.headers.get("Authorization") == f"Bearer {token}"
        for request in calls
        if request.url.path == "/solicitacoes-emprestimo"
        or request.url.path.startswith("/minhas/")
    )


def test_home_sections_use_catalog_data_and_explicit_empty_error_states(
    monkeypatch,
):
    homepage = repr(frontend.index())
    assert "Livros em destaque" in homepage
    assert "Sobre a biblioteca" in homepage
    assert "Mostrar mais" in homepage
    assert homepage.count("section-more-link") == 1
    assert "Carregando o acervo" in homepage
    assert "Nenhum" in homepage
    assert "Livros que mais saem" not in homepage
    assert "Exemplares ativos" not in homepage
    assert "24 t" not in homepage
    assert "8 categorias" not in homepage

    calls = {"titles": 0}
    entries = [_title_entry(81)]

    async def public_titles():
        calls["titles"] += 1
        return entries

    async def categories():
        return [{"id": 3, "nome": "Literatura"}]

    async def failed_public_titles():
        raise XanoResponseError(503)

    monkeypatch.setattr(frontend, "list_public_titles", public_titles)
    monkeypatch.setattr(frontend, "list_categories", categories)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"journey-home-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            await state.load_home()
            assert state.public_catalog_pending is False
            assert state.public_catalog_has_error is False
            assert state.home_featured_titles[0]["titulo"] == "A Ilha"

            state.set_public_catalog_search("sem resultado")
            assert state.filtered_public_catalog == []
            assert state.home_featured_titles[0]["titulo"] == "A Ilha"
            state.set_public_catalog_search("")

            entries.clear()
            await state.load_home()
            assert state.home_featured_titles == []
            assert state.public_catalog_message == ""
            assert state.public_catalog_has_error is False

            monkeypatch.setattr(
                frontend,
                "list_public_titles",
                failed_public_titles,
            )
            await state.load_home()
            assert state.public_catalog_has_error is True
            assert state.public_catalog_message

            state._store_session("token-falso-home", "estudante")
            redirect = await state.load_home()
            assert redirect is None
            assert state.public_catalog_has_error is True
            assert calls["titles"] == 2

    asyncio.run(verify())


def test_librarian_creates_catalog_and_registers_pickup_through_mock_transport(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    token = "token-bibliotecario-sintetico"
    password = "senha-sintetica"
    created: dict[str, object] = {"title": None, "copies": [], "loan": None}
    request_pending = True
    calls: list[httpx.Request] = []
    pending_request = {
        "id": 71,
        "usuario_id": 41,
        "titulo_id": 81,
        "estado": "pendente",
    }

    def handle(request: httpx.Request) -> httpx.Response:
        nonlocal request_pending
        calls.append(request)
        path = request.url.path
        if path == "/auth/login":
            return httpx.Response(
                200,
                json={
                    "authToken": token,
                    "usuario": {
                        "id": 9,
                        "nome": "Bibliotecária de teste",
                        "email": "bibliotecaria@example.test",
                        "perfil": "bibliotecario",
                    },
                },
            )
        if request.method == "GET" and path == "/catalogo/categorias":
            return httpx.Response(200, json=[{"id": 3, "nome": "Literatura"}])
        if request.method == "GET" and path == "/admin/acervo":
            title = created["title"]
            return httpx.Response(
                200,
                json=(
                    [
                        _title_entry(
                            title["id"],
                            copies=created["copies"],
                        )
                    ]
                    if title is not None
                    else []
                ),
            )
        if request.method == "POST" and path == "/catalogo/titulos":
            title_payload = json.loads(request.content)
            created["title"] = {
                "id": 81,
                "titulo": title_payload["titulo"],
                "autores": title_payload["autores"],
            }
            return httpx.Response(201, json={"id": 81})
        if request.method == "POST" and path == "/admin/titulos/81/categorias":
            return httpx.Response(
                201,
                json={
                    "id": 91,
                    "titulo_id": 81,
                    "categoria_id": json.loads(request.content)["categoria_id"],
                },
            )
        if request.method == "POST" and path == "/admin/exemplares":
            copy = {
                "id": 101,
                "titulo_id": json.loads(request.content)["titulo_id"],
                "estado": "disponivel",
                "codigo_tombo": "EX-000101",
            }
            created["copies"].append(copy)
            return httpx.Response(201, json=copy)
        if request.method == "GET" and path == "/admin/solicitacoes":
            return httpx.Response(
                200,
                json=[pending_request] if request_pending else [],
            )
        if request.method == "GET" and path == "/admin/reservas":
            return httpx.Response(200, json=[])
        if request.method == "GET" and path == "/admin/emprestimos":
            loan = created["loan"]
            return httpx.Response(
                200,
                json=(
                    [
                        {
                            "id": loan["id"],
                            "usuario_id": loan["usuario_id"],
                            "usuario_nome": "Estudante de teste",
                            "titulo_id": 81,
                            "titulo": "A Ilha",
                            "autores": "Autoria de teste",
                            "exemplar_id": loan["exemplar_id"],
                            "retirado_em": loan["retirado_em"],
                            "vence_em": loan["vence_em"],
                        }
                    ]
                    if loan is not None
                    else []
                ),
            )
        if request.method == "POST" and path == "/admin/solicitacoes/71/retirada":
            request_pending = False
            loan = {
                "id": 91,
                "usuario_id": 41,
                "exemplar_id": 101,
                "solicitacao_id": 71,
                "retirado_em": "2026-11-15T10:00:00Z",
                "vence_em": "2026-11-29T10:00:00Z",
                "devolvido_em": None,
            }
            created["loan"] = loan
            return httpx.Response(201, json=loan)
        raise AssertionError(f"Chamada inesperada: {request.method} {path}")

    transport = httpx.MockTransport(handle)

    async def authenticate(payload):
        return await submit_login(payload, transport=transport)

    async def categories():
        return await list_categories(transport=transport)

    async def admin_catalog(session_token):
        return await list_admin_catalog(session_token, transport=transport)

    async def create(payload, session_token):
        return await create_title(
            payload,
            session_token,
            transport=transport,
        )

    async def associate(title_id, category_id, session_token):
        return await associate_category(
            title_id,
            category_id,
            session_token,
            transport=transport,
        )

    async def copy(title_id, session_token):
        return await create_copy(
            title_id,
            session_token,
            transport=transport,
        )

    async def admin_requests(session_token):
        return await list_admin_requests(session_token, transport=transport)

    async def admin_reservations(session_token):
        return await list_admin_reservations(
            session_token,
            transport=transport,
        )

    async def admin_loans(session_token):
        return await list_admin_loans(session_token, transport=transport)

    async def pickup(request_id, session_token):
        return await register_request_pickup(
            request_id,
            session_token,
            transport=transport,
        )

    monkeypatch.setattr(frontend, "authenticate", authenticate)
    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "list_admin_catalog", admin_catalog)
    monkeypatch.setattr(frontend, "create_title", create)
    monkeypatch.setattr(frontend, "associate_category", associate)
    monkeypatch.setattr(frontend, "create_copy", copy)
    monkeypatch.setattr(frontend, "list_admin_requests", admin_requests)
    monkeypatch.setattr(frontend, "list_admin_reservations", admin_reservations)
    monkeypatch.setattr(frontend, "list_admin_loans", admin_loans)
    monkeypatch.setattr(frontend, "register_request_pickup", pickup)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"journey-librarian-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            redirect = await state.submit_login(
                {"email": "bibliotecaria@example.test", "senha": password}
            )
            assert "admin/acervo" in repr(redirect)
            assert state.is_librarian is True

            await state.load_catalog_page()
            state.toggle_catalog_category(3, True)
            await state.submit_catalog_title(
                {
                    "titulo": "A Ilha",
                    "autores": "Autoria de teste",
                    "ano_publicacao": "2024",
                }
            )
            assert state.catalog_title_created is True
            assert state.catalog_categories_pending is False
            assert state.catalog_message == "Título e categorias cadastrados."

            await state.add_copy_to_title(81)
            assert state.admin_catalog_message == "Exemplar adicionado."
            assert state.admin_catalog_entries[0]["exemplares_disponiveis"] == 1

            await state.load_circulation_page()
            assert state.circulation_requests[0]["id"] == 71
            await state.circulation_pickup_request(71)
            assert state.circulation_message == (
                "Retirada registrada; empréstimo com prazo de 14 dias."
            )
            assert state.circulation_requests == []
            assert state.circulation_loans[0]["id"] == 91

            state_json = json.dumps(state.dict(), default=str)
            assert token not in state_json
            assert password not in state_json

    asyncio.run(verify())
    assert created["title"]["id"] == 81
    assert created["copies"][0]["codigo_tombo"] == "EX-000101"
    assert sum(request.url.path == "/catalogo/titulos" for request in calls) == 1
    assert sum(
        request.url.path == "/admin/titulos/81/categorias" for request in calls
    ) == 1
    assert sum(request.url.path == "/admin/exemplares" for request in calls) == 1
    assert sum(
        request.url.path == "/admin/solicitacoes/71/retirada"
        for request in calls
    ) == 1
    assert all(
        request.headers.get("Authorization") == f"Bearer {token}"
        for request in calls
        if request.url.path.startswith("/admin/")
        or request.url.path == "/catalogo/titulos"
    )


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (
            401,
            "[RES-401] Sua sessão expirou, entre de novo",
        ),
        (
            403,
            "[RES-403] Seu perfil não pode reservar",
        ),
        (
            404,
            "[RES-404] Este recurso ainda não está disponível no servidor",
        ),
        (
            409,
            "[RES-409] Há limite ou duplicidade nesta reserva",
        ),
        (
            422,
            "[RES-422] Não foi possível confirmar a reserva",
        ),
        (
            429,
            "[RES-429] Não foi possível confirmar a reserva",
        ),
        (
            500,
            "[RES-5XX] O servidor teve um problema (código 5xx)",
        ),
    ],
)
def test_student_request_http_error_matrix_is_safe_and_not_retried(
    monkeypatch,
    status_code,
    message,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    token = "token-falso-nao-exposto"
    private_detail = "detalhe-interno-senha-privada"
    requests: list[httpx.Request] = []
    transport = httpx.MockTransport(
        lambda request: requests.append(request)
        or httpx.Response(status_code, json={"message": private_detail})
    )

    async def request_loan(title_id, session_token):
        return await request_title_loan(
            title_id,
            session_token,
            transport=transport,
        )

    monkeypatch.setattr(frontend, "request_title_loan", request_loan)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"journey-student-error-{status_code}-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session(token, "estudante")
            state.public_catalog_detail = {
                "id": 81,
                "exemplares_disponiveis": 1,
            }
            await state.request_catalog_title(81)

            assert state.student_request_has_error is True
            assert state.student_request_message == message
            assert state.student_request_pending is False
            assert "registrada" not in state.student_request_message
            assert private_detail not in state.student_request_message

    asyncio.run(verify())
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].headers["Authorization"] == f"Bearer {token}"


@pytest.mark.parametrize("failure", ["transport", "incompatible_success"])
def test_student_request_uncertain_result_is_not_reported_or_retried(
    monkeypatch, failure
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    token = "token-falso-nao-exposto"
    private_detail = "detalhe-interno-nao-exposto"
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if failure == "transport":
            raise httpx.ConnectError(private_detail, request=request)
        return httpx.Response(
            201,
            json={
                "id": 51,
                "titulo_id": 82,
                "estado": "pendente",
                "detalhe": private_detail,
            },
        )

    transport = httpx.MockTransport(handle)

    async def request_loan(title_id, session_token):
        return await request_title_loan(
            title_id,
            session_token,
            transport=transport,
        )

    monkeypatch.setattr(frontend, "request_title_loan", request_loan)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"journey-student-uncertain-{failure}-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session(token, "estudante")
            state.public_catalog_detail = {
                "id": 81,
                "exemplares_disponiveis": 1,
            }
            await state.request_catalog_title(81)

            assert state.student_request_has_error is True
            assert state.student_request_pending is False
            assert (
                "Minhas reservas" in state.student_request_message
                or "[RES-INVALID]" in state.student_request_message
            )
            assert "registrada" not in state.student_request_message
            serialized = json.dumps(state.dict(), default=str)
            assert token not in serialized
            assert private_detail not in serialized

    asyncio.run(verify())
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].headers["Authorization"] == f"Bearer {token}"

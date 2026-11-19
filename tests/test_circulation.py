import asyncio
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.circulation import (
    list_admin_loans,
    list_admin_requests,
    list_admin_reservations,
    offer_next_reservation,
    refuse_loan_request,
    refuse_reservation,
    register_loan_return,
    register_request_pickup,
    register_reservation_pickup,
)
from biblioteca_mais_nova.xano_client import XanoRequestError


def _loan(*, returned: str | None = None) -> dict[str, object]:
    return {
        "id": 5,
        "usuario_id": 101,
        "exemplar_id": 9,
        "solicitacao_id": 7,
        "retirado_em": "2026-01-01T10:00:00Z",
        "vence_em": "2026-01-15T10:00:00Z",
        "devolvido_em": returned,
    }


def _readable_component(component):
    tree = json.loads(repr(component))
    values = []

    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "contents" and isinstance(child, str):
                    try:
                        values.append(json.loads(child))
                    except json.JSONDecodeError:
                        values.append(child)
                elif key == "props" and isinstance(child, list):
                    values.extend(prop for prop in child if isinstance(prop, str))
                else:
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(tree)
    return " ".join(values)


def test_admin_lists_use_typed_contracts_and_bearer_auth(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []

    def handle(request):
        requests.append(request)
        if request.url.path == "/admin/solicitacoes":
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 7,
                        "usuario_id": 101,
                        "titulo_id": 12,
                        "estado": "pendente",
                    }
                ],
            )
        if request.url.path == "/admin/reservas":
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 15,
                        "usuario_id": 101,
                        "usuario_nome": "Estudante",
                        "titulo_id": 12,
                        "titulo": "Livro",
                        "criada_em": "2026-01-01T10:00:00Z",
                        "estado": "aguardando",
                        "exemplar_id": None,
                        "ofertada_em": None,
                        "expira_em": None,
                        "expira_em_sao_paulo": None,
                    }
                ],
            )
        return httpx.Response(
            200,
            json=[
                {
                    "id": 5,
                    "usuario_id": 101,
                    "usuario_nome": "Estudante",
                    "titulo_id": 12,
                    "titulo": "Livro",
                    "autores": "Autoria",
                    "exemplar_id": 9,
                    "retirado_em": "2026-01-01T10:00:00Z",
                    "vence_em": "2026-01-15T10:00:00Z",
                }
            ],
        )

    transport = httpx.MockTransport(handle)

    requests_result = asyncio.run(
        list_admin_requests("token-falso", transport=transport)
    )
    reservations_result = asyncio.run(
        list_admin_reservations("token-falso", transport=transport)
    )
    loans_result = asyncio.run(list_admin_loans("token-falso", transport=transport))

    assert requests_result[0]["estado"] == "pendente"
    assert reservations_result[0]["usuario_nome"] == "Estudante"
    assert loans_result[0]["titulo"] == "Livro"
    assert [request.url.path for request in requests] == [
        "/admin/solicitacoes",
        "/admin/reservas",
        "/admin/emprestimos",
    ]
    assert all(
        request.headers["Authorization"] == "Bearer token-falso"
        for request in requests
    )


def test_admin_actions_use_expected_paths_bodies_and_validate_results(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []

    def handle(request):
        requests.append(request)
        path = request.url.path
        if path.endswith("/solicitacoes/7/retirada"):
            return httpx.Response(201, json=_loan())
        if path.endswith("/solicitacoes/7/recusar"):
            return httpx.Response(
                200,
                json={
                    "id": 7,
                    "usuario_id": 101,
                    "titulo_id": 12,
                    "estado": "recusada",
                },
            )
        if path.endswith("/reservas/ofertar-proxima"):
            return httpx.Response(
                200,
                json={
                    "reserva": {"id": 15, "titulo_id": 12, "estado": "ofertada"},
                    "expira_em_utc": "2026-01-03T10:00:00Z",
                    "expira_em_sao_paulo": "2026-01-03 07:00:00",
                },
            )
        if path.endswith("/reservas/15/retirada"):
            return httpx.Response(201, json=_loan())
        if path.endswith("/reservas/15/recusar"):
            return httpx.Response(
                200,
                json={"id": 15, "estado": "recusada"},
            )
        if path.endswith("/emprestimos/5/devolucao"):
            return httpx.Response(
                200,
                json={"emprestimo": _loan(returned="2026-01-10T10:00:00Z")},
            )
        raise AssertionError(f"Chamada inesperada: {request.method} {path}")

    transport = httpx.MockTransport(handle)
    token = "token-falso"
    asyncio.run(register_request_pickup(7, token, transport=transport))
    asyncio.run(refuse_loan_request(7, token, transport=transport))
    asyncio.run(offer_next_reservation(12, 9, token, transport=transport))
    asyncio.run(register_reservation_pickup(15, token, transport=transport))
    asyncio.run(refuse_reservation(15, token, transport=transport))
    asyncio.run(register_loan_return(5, token, transport=transport))

    assert [request.url.path for request in requests] == [
        "/admin/solicitacoes/7/retirada",
        "/admin/solicitacoes/7/recusar",
        "/admin/reservas/ofertar-proxima",
        "/admin/reservas/15/retirada",
        "/admin/reservas/15/recusar",
        "/admin/emprestimos/5/devolucao",
    ]
    assert json.loads(requests[2].content) == {
        "titulo_id": 12,
        "exemplar_id": 9,
    }
    assert all(request.headers["Authorization"] == f"Bearer {token}" for request in requests)


def test_circulation_client_rejects_invalid_action_response(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            json={
                "reserva": {"id": 15, "titulo_id": 99, "estado": "ofertada"},
                "expira_em_utc": "2026-01-03T10:00:00Z",
                "expira_em_sao_paulo": "2026-01-03 07:00:00",
            },
        )
    )

    with pytest.raises(XanoRequestError):
        asyncio.run(
            offer_next_reservation(
                12,
                9,
                "token-falso",
                transport=transport,
            )
        )


def test_circulation_page_loads_lists_and_marks_overdue_loans(monkeypatch):
    async def list_requests(token):
        assert token == "token-falso"
        return [
            {
                "id": 7,
                "usuario_id": 101,
                "titulo_id": 12,
                "estado": "pendente",
            }
        ]

    async def list_reservations(token):
        assert token == "token-falso"
        return []

    async def list_loans(token):
        assert token == "token-falso"
        return [
            {
                **_loan(),
                "usuario_nome": "Estudante",
                "titulo_id": 12,
                "titulo": "Livro",
                "autores": "Autoria",
            }
        ]

    async def list_catalog(token):
        assert token == "token-falso"
        return []

    monkeypatch.setattr(frontend, "list_admin_requests", list_requests)
    monkeypatch.setattr(frontend, "list_admin_reservations", list_reservations)
    monkeypatch.setattr(frontend, "list_admin_loans", list_loans)
    monkeypatch.setattr(frontend, "list_admin_catalog", list_catalog)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"circulation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")

            await state.load_circulation_page()

            assert state.circulation_requests[0]["id"] == 7
            assert state.circulation_overdue_loan_count == 1
            assert state.circulation_pending is False
            serialized = json.dumps(state.dict(), default=str)
            assert "token-falso" not in serialized
            assert "_session_token" not in serialized

    asyncio.run(verify())


def test_circulation_page_has_accessible_actions_and_focus_style():
    page = repr(frontend.circulation_page())
    header = repr(frontend.site_header())

    assert "Reservas e circula" in page
    assert "Registrar retirada" in page
    assert r"Oferecer ao pr\\u00f3ximo da fila" in page
    assert r"Registrar devolu\\u00e7\\u00e3o" in page
    assert "Atrasados" in page
    assert "/admin/circulacao" not in header
    assert frontend.app.style[":focus-visible"]["outline"].startswith("3px solid ")


def test_staff_reservations_tabs_reuse_current_operations():
    page = _readable_component(frontend.circulation_page())

    assert 'role:"tablist"' in page
    assert 'role:"tab"' in page
    assert "aria-controls" in page
    assert "Pedidos" in page
    assert "Empréstimos e devoluções" in page
    assert "Solicitações pendentes" in page
    assert "Devoluções previstas hoje" in page
    assert "Registrar retirada" in page
    assert "Oferecer ao próximo da fila" in page
    assert "Reservar para estudante" in page
    assert "Registrar devolução" in page
    assert frontend.app.style[".circulation-tab"]["min_height"] == "44px"
    assert frontend.app.style["@media screen and (max-width: 40rem)"][
        ".circulation-tab"
    ]["width"] == "100%"


def test_staff_operational_counts_use_loaded_records(monkeypatch):
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"operational-counts-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            state.circulation_requests = [
                {"estado": "pendente"},
                {"estado": "atendida"},
            ]
            today = datetime.now(timezone.utc).date()
            state.circulation_loans = [
                {
                    "atrasado": True,
                    "vence_em": datetime.combine(
                        today - timedelta(days=1),
                        datetime.min.time(),
                        tzinfo=timezone.utc,
                    ).isoformat(),
                },
                {
                    "atrasado": False,
                    "vence_em": datetime.combine(
                        today,
                        datetime.min.time(),
                        tzinfo=timezone.utc,
                    ).isoformat(),
                },
                {
                    "atrasado": False,
                    "vence_em": datetime.combine(
                        today + timedelta(days=1),
                        datetime.min.time(),
                        tzinfo=timezone.utc,
                    ).isoformat(),
                },
            ]

            assert state.circulation_pending_request_count == 1
            assert state.circulation_overdue_loan_count == 1
            assert state.circulation_active_loan_count == 3
            assert state.circulation_due_today_count == 1

    asyncio.run(verify())


@pytest.mark.parametrize("profile", ["", "estudante"])
def test_circulation_load_rejects_non_staff_profiles(monkeypatch, profile):
    async def unexpected(*_args, **_kwargs):
        raise AssertionError("A API administrativa não deve ser chamada.")

    monkeypatch.setattr(frontend, "list_admin_requests", unexpected)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"circulation-denied-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            if profile:
                state._store_session("token-falso", profile)

            result = await state.load_circulation_page()

            destination = "/login" if not profile else "/"
            assert f"_var_value='{destination}'" in repr(result)

    asyncio.run(verify())


def test_uncertain_circulation_action_requires_refresh_before_retry(monkeypatch):
    calls = 0

    async def fail_pickup(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        raise XanoRequestError("Falha de comunicação")

    async def no_requests(_token):
        return []

    async def no_reservations(_token):
        return []

    async def no_loans(_token):
        return []

    async def no_catalog(_token):
        return []

    monkeypatch.setattr(frontend, "register_request_pickup", fail_pickup)
    monkeypatch.setattr(frontend, "list_admin_requests", no_requests)
    monkeypatch.setattr(frontend, "list_admin_reservations", no_reservations)
    monkeypatch.setattr(frontend, "list_admin_loans", no_loans)
    monkeypatch.setattr(frontend, "list_admin_catalog", no_catalog)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"circulation-uncertain-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")

            await state.circulation_pickup_request(7)
            assert state.circulation_needs_manual_check is True
            await state.circulation_pickup_request(7)
            assert calls == 1

            await state.load_circulation_page()
            assert state.circulation_needs_manual_check is False

    asyncio.run(verify())

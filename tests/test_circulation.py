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
from biblioteca_mais_nova.xano_client import (
    XanoRequestError,
    XanoResponseError,
    XanoWriteSucceededWithUnreadableResponse,
)


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


def test_admin_lists_accept_envelopes_numeric_ids_and_timestamp_units(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")

    def handle(request):
        if request.url.path == "/admin/solicitacoes":
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": "7",
                            "usuario_id": "101",
                            "titulo_id": "12",
                            "estado": "pendente",
                        }
                    ]
                },
            )
        if request.url.path == "/admin/reservas":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "15",
                            "usuario_id": "101",
                            "usuario_nome": "Estudante",
                            "titulo_id": "12",
                            "titulo": "Livro",
                            "criada_em": 1794312000000,
                            "estado": "aguardando",
                            "exemplar_id": None,
                            "ofertada_em": 0,
                            "expira_em": None,
                        }
                    ]
                },
            )
        return httpx.Response(
            200,
            json={
                "records": [
                    {
                        "id": "5",
                        "usuario_id": "101",
                        "usuario_nome": "Estudante",
                        "titulo_id": "12",
                        "titulo": "Livro",
                        "autores": "Autoria",
                        "exemplar_id": "9",
                        "retirado_em": 1794312000,
                        "vence_em": 0,
                    }
                ]
            },
        )

    requests = asyncio.run(
        list_admin_requests("token", transport=httpx.MockTransport(handle))
    )
    reservations = asyncio.run(
        list_admin_reservations("token", transport=httpx.MockTransport(handle))
    )
    loans = asyncio.run(
        list_admin_loans("token", transport=httpx.MockTransport(handle))
    )

    assert requests[0]["id"] == 7
    assert reservations[0]["criada_em"] == "2026-11-10T12:00:00+00:00"
    assert reservations[0]["expira_em"] is None
    assert reservations[0]["expira_em_sao_paulo"] is None
    assert loans[0]["id"] == 5
    assert loans[0]["retirado_em"] == "2026-11-10T12:00:00+00:00"
    assert loans[0]["vence_em"] is None


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

    with pytest.raises(XanoWriteSucceededWithUnreadableResponse):
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


def test_circulation_unreadable_success_refreshes_lists_without_retry(monkeypatch):
    writes = []
    refreshes = []

    async def unreadable_pickup(request_id, token):
        writes.append((request_id, token))
        raise XanoWriteSucceededWithUnreadableResponse()

    async def empty_records(token):
        refreshes.append(token)
        return []

    monkeypatch.setattr(frontend, "register_request_pickup", unreadable_pickup)
    monkeypatch.setattr(frontend, "list_admin_requests", empty_records)
    monkeypatch.setattr(frontend, "list_admin_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_admin_loans", empty_records)
    monkeypatch.setattr(frontend, "list_admin_catalog", empty_records)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"circulation-write-warning-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-bibliotecario", "bibliotecario")

            await state.circulation_pickup_request(7)

            assert writes == [(7, "token-bibliotecario")]
            assert refreshes == ["token-bibliotecario"] * 4
            assert state.circulation_pending is False
            assert state.circulation_has_error is False
            assert "Não foi possível ler a resposta" in state.circulation_message

    asyncio.run(verify())


def test_admin_librarian_view_uses_own_session_for_circulation_action(monkeypatch):
    writes = []
    refreshes = []

    async def pickup(request_id, token):
        writes.append((request_id, token))
        return _loan()

    async def empty_records(token):
        refreshes.append(token)
        return []

    monkeypatch.setattr(frontend, "register_request_pickup", pickup)
    monkeypatch.setattr(frontend, "list_admin_requests", empty_records)
    monkeypatch.setattr(frontend, "list_admin_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_admin_loans", empty_records)
    monkeypatch.setattr(frontend, "list_admin_catalog", empty_records)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"admin-circulation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            state.set_admin_view_mode("bibliotecaria")

            await state.circulation_pickup_request(7)

            assert writes == [(7, "token-admin")]
            assert refreshes == ["token-admin"] * 4
            assert state._session_profile == "admin"
            assert state.circulation_has_error is False
            assert state.circulation_message.startswith("Retirada registrada")

    asyncio.run(verify())


def test_stale_circulation_403_refreshes_lists_once_without_retrying_write(
    monkeypatch,
):
    writes = []
    refreshes = []

    async def stale_refusal(request_id, token):
        writes.append((request_id, token))
        raise XanoResponseError(
            403,
            "Somente solicitacao pendente pode ser recusada",
            reference="REF44",
        )

    async def empty_records(token):
        refreshes.append(token)
        return []

    monkeypatch.setattr(frontend, "refuse_loan_request", stale_refusal)
    monkeypatch.setattr(frontend, "list_admin_requests", empty_records)
    monkeypatch.setattr(frontend, "list_admin_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_admin_loans", empty_records)
    monkeypatch.setattr(frontend, "list_admin_catalog", empty_records)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"stale-circulation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            state.set_admin_view_mode("bibliotecaria")

            await state.circulation_refuse_request(7)

            assert writes == [(7, "token-admin")]
            assert refreshes == ["token-admin"] * 4
            assert state.circulation_message == (
                "Só dá para recusar pedidos que ainda estão pendentes. "
                "A lista foi atualizada. (ref. REF44)"
            )
            assert state.circulation_has_error is True

    asyncio.run(verify())


def test_admin_librarian_profile_403_shows_publication_guidance(monkeypatch):
    writes = []
    refreshes = []

    async def denied_pickup(request_id, token):
        writes.append((request_id, token))
        raise XanoResponseError(
            403,
            "Perfil não autorizado.",
            reference="REF42",
        )

    async def unexpected_read(_token):
        refreshes.append(True)
        raise AssertionError("Falha de perfil não deve reler a circulação.")

    monkeypatch.setattr(frontend, "register_request_pickup", denied_pickup)
    monkeypatch.setattr(frontend, "list_admin_requests", unexpected_read)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"admin-circulation-403-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            state.set_admin_view_mode("bibliotecaria")

            await state.circulation_pickup_request(7)

            assert writes == [(7, "token-admin")]
            assert refreshes == []
            assert state.circulation_message == (
                "O Xano ainda não permite que o admin faça esta ação como "
                "Bibliotecário. Veja docs/publicacao-xano-regras.md. "
                "(ref. REF42)"
            )

    asyncio.run(verify())


def test_circulation_page_has_accessible_actions_and_focus_style():
    page = repr(frontend.circulation_page())
    header = repr(frontend.site_header())

    assert "Reservas e circula" in page
    assert "Registrar retirada" in page
    assert "Oferecer reserva" in page
    assert "Devolver" in page
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
    assert "Oferecer reserva" in page
    assert "Reservar para estudante" in page
    assert "Devolver" in page
    assert frontend.app.style[".circulation-tab"]["min_height"] == "44px"
    assert frontend.app.style["@media screen and (max-width: 48rem)"][
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

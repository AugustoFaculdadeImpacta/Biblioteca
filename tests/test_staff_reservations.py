import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.staff_reservations import (
    StaffReservationValidationError,
    create_staff_reservation,
    find_student_by_email,
    staff_reservation_error_message,
)
from biblioteca_mais_nova.xano_client import XanoRequestError, XanoResponseError


def _entry(title_id: int, title: str, *, active: bool = True):
    return {
        "titulo": {
            "id": title_id,
            "titulo": title,
            "autores": "Autoria",
            "ativo": active,
        },
        "categorias": [],
        "exemplares_disponiveis": 1,
        "exemplares": [],
    }


def test_student_search_normalizes_exact_email_and_returns_minimal_identity(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "id": 8,
                    "nome": "Ana",
                    "email": "ana+teste@example.org",
                    "perfil": "estudante",
                    "senha": "nao deve retornar",
                    "hash": "nao deve retornar",
                }
            ],
        )

    result = asyncio.run(
        find_student_by_email(
            "  ANA+Teste@Example.org ",
            "token-nao-exposto",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == {"id": 8, "nome": "Ana"}
    assert requests[0].url.path == "/admin/estudantes"
    assert requests[0].url.params["email"] == "ana+teste@example.org"
    assert "Authorization" in requests[0].headers
    assert "token-nao-exposto" not in json.dumps(result)


def test_student_search_returns_none_and_rejects_malformed_input(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []
    transport = httpx.MockTransport(
        lambda request: requests.append(request) or httpx.Response(200, json=[])
    )

    assert (
        asyncio.run(
            find_student_by_email(
                "ausente@example.org",
                "token",
                transport=transport,
            )
        )
        is None
    )
    with pytest.raises(StaffReservationValidationError):
        asyncio.run(
            find_student_by_email(
                "nao e um email",
                "token",
                transport=transport,
            )
        )
    assert len(requests) == 1


def test_create_staff_reservation_sends_only_student_and_title_ids(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            201,
            json={
                "id": 92,
                "usuario_id": 8,
                "titulo_id": 81,
                "estado": "aguardando",
                "senha": "nao deve retornar",
                "hash": "nao deve retornar",
                "authToken": "nao deve retornar",
            },
        )

    result = asyncio.run(
        create_staff_reservation(
            8,
            81,
            "token-nao-exposto",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == {
        "id": 92,
        "usuario_id": 8,
        "titulo_id": 81,
        "estado": "aguardando",
    }
    assert requests[0].url.path == "/admin/reservas"
    assert requests[0].read() == b'{"usuario_id":8,"titulo_id":81}'
    assert "Authorization" in requests[0].headers
    assert "token-nao-exposto" not in json.dumps(result)


@pytest.mark.parametrize(
    ("detail", "expected"),
    [
        (
            "Estudante nao encontrado ou inativo.",
            "Estudante não encontrado ou com conta desativada.",
        ),
        (
            "Estudante possui emprestimo atrasado.",
            "A reserva foi recusada porque o estudante possui empréstimo atrasado.",
        ),
        (
            "Estudante ja possui o titulo emprestado.",
            "A reserva foi recusada porque o estudante já está com esse título.",
        ),
        (
            "Estudante ja possui reserva ativa para este titulo.",
            "O estudante já possui uma reserva ativa para esse título.",
        ),
        (
            "Titulo inativo nao aceita novas reservas.",
            "Não é possível reservar um título desativado.",
        ),
    ],
)
def test_reservation_business_errors_are_explained_in_portuguese(detail, expected):
    assert staff_reservation_error_message(XanoResponseError(409, expected)) == expected


def test_staff_page_loads_only_active_titles_and_creates_for_confirmed_student(
    monkeypatch,
):
    calls = []

    async def list_catalog(token):
        assert token == "token-falso"
        return [
            _entry(81, "Título ativo"),
            _entry(82, "Título inativo", active=False),
        ]

    async def find_student(email, token):
        calls.append(("buscar", email, token))
        return {"id": 8, "nome": "Ana"}

    async def create_reservation(student_id, title_id, token):
        calls.append(("reservar", student_id, title_id, token))
        return {
            "id": 92,
            "usuario_id": student_id,
            "titulo_id": title_id,
            "estado": "aguardando",
        }

    monkeypatch.setattr(frontend, "list_admin_catalog", list_catalog)
    monkeypatch.setattr(frontend, "find_student_by_email", find_student)
    monkeypatch.setattr(
        frontend,
        "create_staff_reservation",
        create_reservation,
    )

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"staff-reservation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")

            await state.load_staff_reservation_page()
            assert state.staff_reservation_title_options == [
                {"id": "81", "label": "Título ativo"}
            ]

            state.update_staff_reservation_email("ana@example.org")
            await state.search_staff_reservation_student()
            assert state.staff_reservation_student == {"id": 8, "nome": "Ana"}
            state.staff_reservation_title_id = "81"
            await state.submit_staff_reservation()

            assert calls == [
                ("buscar", "ana@example.org", "token-falso"),
                ("reservar", 8, 81, "token-falso"),
            ]
            assert state.staff_reservation_student == {}
            assert state.staff_reservation_title_id == ""
            assert "fila normal" in state.staff_reservation_message
            serialized = json.dumps(state.dict(), default=str)
            assert "token-falso" not in serialized
            assert "_session_token" not in serialized

    asyncio.run(verify())


def test_missing_student_does_not_allow_reservation_creation(monkeypatch):
    async def list_catalog(token):
        return [_entry(81, "Título ativo")]

    async def missing_student(email, token):
        return None

    async def unexpected(*args, **kwargs):
        raise AssertionError("A reserva não pode ser criada sem estudante.")

    monkeypatch.setattr(frontend, "list_admin_catalog", list_catalog)
    monkeypatch.setattr(frontend, "find_student_by_email", missing_student)
    monkeypatch.setattr(frontend, "create_staff_reservation", unexpected)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"staff-reservation-missing-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "bibliotecario")
            await state.load_staff_reservation_page()
            state.update_staff_reservation_email("ausente@example.org")
            await state.search_staff_reservation_student()
            state.staff_reservation_title_id = "81"
            await state.submit_staff_reservation()

            assert state.staff_reservation_student == {}
            assert "Busque e confirme" in state.staff_reservation_message
            assert state.staff_reservation_has_error is True

    asyncio.run(verify())


def test_uncertain_staff_reservation_requires_manual_review_before_retry(
    monkeypatch,
):
    calls = 0

    async def list_catalog(token):
        return [_entry(81, "Título ativo")]

    async def find_student(email, token):
        return {"id": 8, "nome": "Ana"}

    async def create_reservation(student_id, title_id, token):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise XanoRequestError("Falha de transporte")
        return {
            "id": 92,
            "usuario_id": student_id,
            "titulo_id": title_id,
            "estado": "aguardando",
        }

    monkeypatch.setattr(frontend, "list_admin_catalog", list_catalog)
    monkeypatch.setattr(frontend, "find_student_by_email", find_student)
    monkeypatch.setattr(frontend, "create_staff_reservation", create_reservation)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"staff-reservation-uncertain-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso", "admin")
            await state.load_staff_reservation_page()
            state.update_staff_reservation_email("ana@example.org")
            await state.search_staff_reservation_student()
            state.staff_reservation_title_id = "81"

            await state.submit_staff_reservation()
            assert state.staff_reservation_needs_manual_check is True
            await state.submit_staff_reservation()
            assert calls == 1

            state.acknowledge_staff_reservation_check()
            await state.search_staff_reservation_student()
            state.staff_reservation_title_id = "81"
            await state.submit_staff_reservation()
            assert calls == 2
            assert state.staff_reservation_needs_manual_check is False

    asyncio.run(verify())


@pytest.mark.parametrize("profile", ["", "estudante"])
def test_reservation_handlers_reject_profiles_without_staff_access(
    monkeypatch,
    profile,
):
    async def unexpected(*args, **kwargs):
        raise AssertionError("A API administrativa não deve ser chamada.")

    monkeypatch.setattr(frontend, "list_admin_catalog", unexpected)
    monkeypatch.setattr(frontend, "find_student_by_email", unexpected)
    monkeypatch.setattr(frontend, "create_staff_reservation", unexpected)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"staff-reservation-denied-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            if profile:
                state._store_session("token-falso", profile)

            destination = "/login" if not profile else "/"
            results = (
                await state.load_staff_reservation_page(),
                await state.search_staff_reservation_student(),
                await state.submit_staff_reservation(),
                state.update_staff_reservation_email("ana@example.org"),
                state.acknowledge_staff_reservation_check(),
            )
            for result in results:
                assert f"_var_value='{destination}'" in repr(result)

    asyncio.run(verify())


def test_reservation_page_exposes_accessible_controls_and_visible_focus():
    page = repr(frontend.staff_reservation_page())
    header = repr(frontend.site_header())

    assert "/admin/reservas" in header
    assert "Reservas para estudantes" in header
    assert "E-mail completo do estudante" in page
    assert r"T\\u00edtulo ativo" in page
    assert "Registrar reserva na fila" in page
    assert frontend.app.style[":focus-visible"]["outline"].startswith("3px solid ")

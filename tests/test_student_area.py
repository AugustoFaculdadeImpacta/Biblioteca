import asyncio
import json
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.circulation import (
    list_my_loans,
    list_my_requests,
    list_my_reservations,
    request_title_loan,
)
from biblioteca_mais_nova.xano_client import (
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    XanoTimeoutError,
)


def _request_records():
    return [
        {
            "id": 31,
            "usuario_id": 9,
            "titulo_id": 14,
            "solicitada_em": "2026-11-10T12:00:00Z",
            "estado": "em_reserva",
            "reserva_id": 41,
            "atendida_em": None,
        },
        {
            "id": 32,
            "usuario_id": 9,
            "titulo_id": 14,
            "solicitada_em": "2026-11-10T12:10:00Z",
            "estado": "pendente",
            "reserva_id": None,
            "atendida_em": None,
        },
    ]


def _reservation_records():
    return [
        {
            "id": 41,
            "usuario_id": 9,
            "titulo_id": 14,
            "criada_em": "2026-11-10T12:00:00Z",
            "estado": "ofertada",
            "exemplar_id": 25,
            "ofertada_em": "2026-11-10T12:00:00Z",
            "expira_em": "2026-11-12T12:00:00Z",
            "expira_em_sao_paulo": "2026-11-12 09:00:00",
        }
    ]


def _loan_records(devolvido_em=None):
    return [
        {
            "id": 17,
            "usuario_id": 9,
            "exemplar_id": 25,
            "solicitacao_id": 32,
            "retirado_em": "2026-11-01T12:00:00Z",
            "vence_em": "2026-11-15T12:00:00Z",
            "devolvido_em": devolvido_em,
        }
    ]


def test_personal_services_use_openapi_routes_and_authenticated_headers(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/Biblioteca")
    requests: list[httpx.Request] = []
    token = "token-de-teste"

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/minhas/emprestimos"):
            return httpx.Response(200, json=_loan_records())
        if request.url.path.endswith("/minhas/solicitacoes"):
            return httpx.Response(200, json=_request_records())
        if request.url.path.endswith("/minhas/reservas"):
            return httpx.Response(200, json=_reservation_records())
        raise AssertionError(f"Chamada inesperada: {request.method} {request.url.path}")

    transport = httpx.MockTransport(handle)
    loans = asyncio.run(list_my_loans(token, transport=transport))
    requests_list = asyncio.run(list_my_requests(token, transport=transport))
    reservations = asyncio.run(list_my_reservations(token, transport=transport))

    assert loans == _loan_records()
    assert requests_list == _request_records()
    assert reservations == _reservation_records()
    assert [request.url.path for request in requests] == [
        "/Biblioteca/minhas/emprestimos",
        "/Biblioteca/minhas/solicitacoes",
        "/Biblioteca/minhas/reservas",
    ]
    assert all(
        request.headers["Authorization"] == f"Bearer {token}"
        for request in requests
    )
    assert all(request.method == "GET" for request in requests)


@pytest.mark.parametrize("devolvido_em", [None, 0, "2026-11-14T12:00:00Z"])
def test_loan_parser_accepts_null_zero_and_timestamp_returned_values(
    monkeypatch, devolvido_em
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=_loan_records(devolvido_em))
    )
    records = asyncio.run(list_my_loans("token", transport=transport))
    assert records[0]["devolvido_em"] == devolvido_em


def test_personal_services_reject_malformed_responses(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    malformed_cases = [
        (list_my_loans, [{"id": 1, "devolvido_em": 0}]),
        (list_my_requests, [{"id": 1, "estado": "inexistente"}]),
        (
            list_my_requests,
            [{**_request_records()[0], "estado": []}],
        ),
        (
            list_my_reservations,
            [{**_reservation_records()[0], "expira_em_sao_paulo": 42}],
        ),
        (
            list_my_reservations,
            [{**_reservation_records()[0], "expira_em_sao_paulo": "sem data"}],
        ),
    ]
    for service, body in malformed_cases:
        transport = httpx.MockTransport(
            lambda request, response_body=body: httpx.Response(
                200, json=response_body
            )
        )
        with pytest.raises(XanoInvalidResponseError):
            asyncio.run(service("token", transport=transport))


def test_request_service_sends_only_title_id_to_openapi_post(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test/Biblioteca")
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            201,
            json={
                "id": 33,
                "usuario_id": 9,
                "titulo_id": 14,
                "estado": "em_reserva",
                "reserva_id": 42,
            },
        )

    result = asyncio.run(
        request_title_loan(
            14,
            "token-de-teste",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == {
        "id": 33,
        "titulo_id": 14,
        "estado": "em_reserva",
        "reserva_id": 42,
    }
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/Biblioteca/solicitacoes-emprestimo"
    assert json.loads(requests[0].content) == {"titulo_id": 14}
    assert requests[0].headers["Authorization"] == "Bearer token-de-teste"


def test_request_service_rejects_mismatched_title_and_invalid_json(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    mismatched = httpx.MockTransport(
        lambda request: httpx.Response(
            201,
            json={"id": 33, "usuario_id": 9, "titulo_id": 15, "estado": "pendente"},
        )
    )
    with pytest.raises(XanoRequestError):
        asyncio.run(request_title_loan(14, "token", transport=mismatched))

    invalid_json = httpx.MockTransport(
        lambda request: httpx.Response(201, content=b"not-json")
    )
    with pytest.raises(XanoInvalidResponseError):
        asyncio.run(request_title_loan(14, "token", transport=invalid_json))


def test_student_library_formats_timezone_and_detects_only_active_overdue_loans():
    assert frontend._format_timestamp("2026-11-10T15:00:00Z") == (
        "10/11/2026 15:00 UTC"
    )
    assert frontend._format_sao_paulo_deadline("2026-11-12 09:00:00") == (
        "12/11/2026 09:00"
    )
    assert frontend._is_overdue("2000-01-01T00:00:00Z", None) is True
    assert frontend._is_overdue("2000-01-01T00:00:00Z", 0) is True
    assert frontend._is_overdue(
        "2000-01-01T00:00:00Z", "2000-01-02T00:00:00Z"
    ) is False
    assert frontend._is_overdue("2999-01-01T00:00:00Z", None) is False


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (
            XanoResponseError(401),
            "Sua sessão expirou ou não é mais válida. Entre novamente para continuar.",
        ),
        (
            XanoResponseError(403),
            "Sua conta não tem permissão para acessar este recurso.",
        ),
        (
            XanoResponseError(404),
            "O recurso não foi encontrado ou a rota ainda não está disponível.",
        ),
        (
            XanoResponseError(503),
            "O serviço Xano está temporariamente indisponível. Tente novamente mais tarde.",
        ),
        (
            XanoTimeoutError("detalhe interno não deve aparecer"),
            "O serviço Xano demorou para responder. Verifique a conexão e tente novamente.",
        ),
        (
            XanoInvalidResponseError("payload interno não deve aparecer"),
            "O serviço Xano retornou uma resposta inválida. Tente novamente mais tarde.",
        ),
        (
            XanoRequestError("detalhe de transporte não deve aparecer"),
            "Não foi possível se comunicar com o serviço Xano. Verifique a conexão e tente novamente.",
        ),
    ],
)
def test_student_library_maps_integration_errors_without_internal_details(
    error, message
):
    assert frontend.catalog_error_message(error) == message


def test_student_library_preserves_allowlisted_business_error():
    error = XanoResponseError(
        403,
        "A reserva foi recusada porque o estudante possui empréstimo atrasado.",
    )

    assert frontend.catalog_error_message(error) == (
        "A reserva foi recusada porque o estudante possui empréstimo atrasado."
    )


def test_student_library_route_guards_before_any_personal_get(monkeypatch):
    calls = []

    async def unexpected_call(*args, **kwargs):
        calls.append(True)
        raise AssertionError("GET pessoal não deveria ser chamado")

    monkeypatch.setattr(frontend, "list_my_loans", unexpected_call)
    monkeypatch.setattr(frontend, "list_my_requests", unexpected_call)
    monkeypatch.setattr(frontend, "list_my_reservations", unexpected_call)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-guard-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            visitor_redirect = await state.load_student_library()
            assert visitor_redirect is not None
            assert state.is_authenticated is False

            state._store_session("token-bibliotecario", "bibliotecario")
            librarian_redirect = await state.load_student_library()
            assert librarian_redirect is not None
            assert calls == []

    asyncio.run(verify())


def test_student_library_loads_only_session_data_and_deduplicates_linked_reserve(
    monkeypatch,
):
    async def loans(token):
        assert token == "token-estudante"
        return [
            {
                **_loan_records()[0],
                "vence_em": "2000-01-01T00:00:00Z",
                "devolvido_em": 0,
            }
        ]

    async def requests(token):
        assert token == "token-estudante"
        return _request_records()

    async def reservations(token):
        assert token == "token-estudante"
        return _reservation_records()

    async def titles():
        return [
            {
                "titulo": {"id": 14, "titulo": "Livro público", "autores": "Autoria"},
                "categorias": [],
                "exemplares_disponiveis": 0,
            }
        ]

    monkeypatch.setattr(frontend, "list_my_loans", loans)
    monkeypatch.setattr(frontend, "list_my_requests", requests)
    monkeypatch.setattr(frontend, "list_my_reservations", reservations)
    monkeypatch.setattr(frontend, "list_public_titles", titles)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-library-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            await state.load_student_library()
            assert state.student_library_loans[0]["em_atraso"] is True
            assert len(state.student_library_requests) == 1
            assert state.student_library_requests[0]["id"] == 32
            assert state.student_library_reservations[0]["titulo"] == "Livro público"
            assert state.student_library_reservations[0]["prazo"] == (
                "12/11/2026 09:00"
            )
            delta = await root._get_resolved_delta()
            assert "token-estudante" not in json.dumps(delta, default=str)

    asyncio.run(verify())


def test_student_request_does_not_retry_uncertain_result(monkeypatch):
    calls = []

    async def uncertain_request(title_id, token):
        calls.append((title_id, token))
        raise XanoRequestError("Falha de comunicação sanitizada.")

    monkeypatch.setattr(frontend, "request_title_loan", uncertain_request)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-request-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}
            await state.request_catalog_title(14)
            assert len(calls) == 1
            assert state.student_request_has_error is True
            assert "Minha biblioteca" in state.student_request_message

    asyncio.run(verify())


@pytest.mark.parametrize(
    ("available", "status", "message"),
    [
        (1, "pendente", "Sua solicitação foi registrada."),
        (0, "em_reserva", "fila de reservas"),
    ],
)
def test_student_request_uses_backend_result_for_available_or_unavailable_title(
    monkeypatch, available, status, message
):
    calls = []

    async def submit(title_id, token):
        calls.append(title_id)
        return {
            "id": 33,
            "titulo_id": title_id,
            "estado": status,
            **({"reserva_id": 42} if status == "em_reserva" else {}),
        }

    monkeypatch.setattr(frontend, "request_title_loan", submit)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-result-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {
                "id": 14,
                "exemplares_disponiveis": available,
            }
            assert state.public_catalog_has_available_copies is bool(available)
            await state.request_catalog_title(14)
            assert calls == [14]
            assert message in state.student_request_message
            assert state.student_request_has_error is False

    asyncio.run(verify())


def test_student_request_explains_backend_eligibility_refusal_without_retry(
    monkeypatch,
):
    calls = []

    async def denied(title_id, token):
        calls.append(title_id)
        raise XanoResponseError(409)

    monkeypatch.setattr(frontend, "request_title_loan", denied)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-denied-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14, "exemplares_disponiveis": 0}
            await state.request_catalog_title(14)
            assert calls == [14]
            assert state.student_request_has_error is True
            assert "atraso" in state.student_request_message

    asyncio.run(verify())


def test_student_library_page_and_navigation_are_profile_gated():
    page = json.dumps(json.loads(repr(frontend.student_library())), ensure_ascii=False)
    header = repr(frontend.site_header())
    assert "Minha biblioteca" in page
    assert "empr" in page
    assert "solicita" in page
    assert "reservas" in page
    assert "minha-biblioteca" in header
    assert "minha-biblioteca" in frontend.app._unevaluated_pages

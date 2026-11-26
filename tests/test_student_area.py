import asyncio
import json
import re
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import pytest
import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
import biblioteca_mais_nova.xano_client as xano_client
from biblioteca_mais_nova.circulation import (
    list_my_loans,
    list_my_requests,
    list_my_reservations,
    request_title_loan,
    reservation_request_error_message,
)


@pytest.fixture(autouse=True)
def _isolar_cache_autenticado():
    xano_client.limpar_cache_autenticado()
    yield
    xano_client.limpar_cache_autenticado()
from biblioteca_mais_nova.xano_client import (
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    XanoTimeoutError,
    XanoWriteSucceededWithUnreadableResponse,
)


def _readable_text(component):
    serialized = json.loads(repr(component))
    values = []

    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "name" and isinstance(child, str):
                    values.append(child)
                elif key == "contents" and isinstance(child, str):
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

    collect(serialized)
    return re.sub(
        r"\\u([0-9a-fA-F]{4})",
        lambda match: chr(int(match.group(1), 16)),
        " ".join(values),
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


def test_personal_list_accepts_envelope_and_skips_one_unreadable_record(
    monkeypatch,
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    response_body = {
        "items": [
            {
                "id": "31",
                "usuario_id": "9",
                "titulo_id": "14",
                "solicitada_em": 1794312000000,
                "estado": "em_reserva",
                "reserva_id": "41",
                "atendida_em": 0,
                "campo_desconhecido": "ignorado",
            },
            {
                "id": 32,
                "usuario_id": 9,
                "titulo_id": 14,
                "estado": [],
            },
            {
                "id": 33,
                "usuario_id": 9,
                "titulo_id": 14,
                "estado": "pendente",
            },
        ]
    }

    records = asyncio.run(
        list_my_requests(
            "token",
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(200, json=response_body)
            ),
        )
    )

    assert [record["id"] for record in records] == [31, 33]
    assert records[0]["usuario_id"] == 9
    assert records[0]["reserva_id"] == 41
    assert records[0]["atendida_em"] is None
    assert records[1]["solicitada_em"] is None
    assert records[1]["reserva_id"] is None
    assert records[1]["atendida_em"] is None
    assert records.skipped_count == 1


def test_incompatible_successful_list_response_is_not_retried(monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=[{"id": 0}])

    records = asyncio.run(
        list_my_requests(
            "token-incompatible-list",
            transport=httpx.MockTransport(handle),
        )
    )

    assert records == []
    assert records.skipped_count == 1
    assert len(requests) == 1
    assert requests[0].method == "GET"


def test_request_service_confirms_minimal_post_response_by_ids(monkeypatch):
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            json={"id": 44, "titulo_id": 50},
        )
    )
    monkeypatch.setenv("BIBLIOTECA_XANO_API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("BIBLIOTECA_XANO_API_GROUP", "Biblioteca")

    result = asyncio.run(
        request_title_loan(50, "token-test", transport=transport)
    )

    assert result == {"id": 44, "titulo_id": 50}


@pytest.mark.parametrize(
    "devolvido_em",
    [None, 0, "2026-11-14T12:00:00Z", 1794312000, 1794312000000],
)
def test_loan_parser_accepts_null_zero_and_timestamp_returned_values(
    monkeypatch, devolvido_em
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=_loan_records(devolvido_em))
    )
    records = asyncio.run(list_my_loans("token", transport=transport))
    expected = devolvido_em
    if type(devolvido_em) is int and devolvido_em != 0:
        timestamp = (
            devolvido_em / 1000
            if devolvido_em > 100_000_000_000
            else devolvido_em
        )
        expected = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    elif devolvido_em in (None, 0):
        expected = None
    assert records[0]["devolvido_em"] == expected


def test_optional_circulation_ids_and_timestamps_treat_zero_as_absent(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    loan = _loan_records(0)[0]
    loan["solicitacao_id"] = 0
    loan["retirado_em"] = 0
    loan["vence_em"] = 0
    reservation = _reservation_records()[0]
    reservation["exemplar_id"] = 0
    reservation["ofertada_em"] = 0
    reservation["expira_em"] = 0

    def service_with(payload, service):
        return asyncio.run(
            service(
                "token",
                transport=httpx.MockTransport(
                    lambda _request: httpx.Response(200, json=[payload])
                ),
            )
        )[0]

    parsed_loan = service_with(loan, list_my_loans)
    parsed_reservation = service_with(reservation, list_my_reservations)

    assert parsed_loan["solicitacao_id"] is None
    assert parsed_loan["retirado_em"] is None
    assert parsed_loan["vence_em"] is None
    assert parsed_loan["devolvido_em"] is None
    assert parsed_reservation["exemplar_id"] is None
    assert parsed_reservation["ofertada_em"] is None
    assert parsed_reservation["expira_em"] is None


def test_personal_services_skip_individually_unreadable_records(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    malformed_cases = [
        (list_my_loans, [{"id": 1, "devolvido_em": 0}]),
        (
            list_my_requests,
            [
                {
                    "id": 1,
                    "usuario_id": 9,
                    "titulo_id": 14,
                    "estado": "pendente",
                    "reserva_id": -1,
                }
            ],
        ),
        (
            list_my_requests,
            [{**_request_records()[0], "estado": []}],
        ),
        (
            list_my_reservations,
            [{**_reservation_records()[0], "expira_em": "sem data"}],
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
        records = asyncio.run(service("token", transport=transport))
        assert records == []
        assert records.skipped_count == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"items": []},
        {"result": []},
        {"data": []},
        {"results": []},
        {"records": []},
    ],
)
def test_personal_lists_accept_all_supported_envelopes(monkeypatch, payload):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    records = asyncio.run(
        list_my_requests(
            "token",
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(200, json=payload)
            ),
        )
    )
    assert records == []
    assert records.skipped_count == 0


@pytest.mark.parametrize("payload", [{"items": "invalid"}, {"id": 1}])
def test_personal_lists_reject_invalid_top_level_shapes(monkeypatch, payload):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    with pytest.raises(XanoInvalidResponseError):
        asyncio.run(
            list_my_requests(
                "token",
                transport=httpx.MockTransport(
                    lambda _request: httpx.Response(200, json=payload)
                ),
            )
        )


def test_personal_lists_reject_records_without_identifier(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    with pytest.raises(XanoInvalidResponseError):
        asyncio.run(
            list_my_requests(
                "token",
                transport=httpx.MockTransport(
                    lambda _request: httpx.Response(
                        200,
                        json=[{"usuario_id": 9, "titulo_id": 14}],
                    )
                ),
            )
        )


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


def test_xano_request_examples_parse_zero_as_absent_for_post_and_list(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    post_payload = {
        "id": 44,
        "usuario_id": 84,
        "titulo_id": 50,
        "solicitada_em": 1795621677771,
        "estado": "pendente",
        "reserva_id": 0,
        "atendida_em": 0,
    }
    list_payload = [
        {
            "id": 32,
            "usuario_id": 84,
            "titulo_id": 38,
            "solicitada_em": 1795366927556,
            "estado": "pendente",
            "reserva_id": 0,
            "atendida_em": 0,
        },
        {
            "id": 33,
            "usuario_id": 84,
            "titulo_id": 56,
            "solicitada_em": 1795539975848,
            "estado": "pendente",
            "reserva_id": 0,
            "atendida_em": 0,
        },
    ]

    def handle(request):
        if request.method == "POST":
            return httpx.Response(200, json=post_payload)
        return httpx.Response(200, json=list_payload)

    transport = httpx.MockTransport(handle)
    created = asyncio.run(request_title_loan(50, "token-test", transport=transport))
    records = asyncio.run(list_my_requests("token-test", transport=transport))

    assert created == {
        "id": 44,
        "titulo_id": 50,
        "estado": "pendente",
        "reserva_id": None,
        "solicitada_em": "2026-11-25T15:47:57.771000+00:00",
    }
    assert [record["id"] for record in records] == [32, 33]
    assert [record["estado"] for record in records] == ["pendente", "pendente"]
    assert [record["reserva_id"] for record in records] == [None, None]
    assert [record["atendida_em"] for record in records] == [None, None]
    assert records.skipped_count == 0


@pytest.mark.parametrize("unknown_state", ["aguardando análise", "estado_novo"])
def test_request_parser_preserves_unknown_state_text(monkeypatch, unknown_state):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    payload = {
        "id": 44,
        "usuario_id": 84,
        "titulo_id": 50,
        "estado": unknown_state,
        "reserva_id": 0,
        "atendida_em": None,
    }
    records = asyncio.run(
        list_my_requests(
            "token",
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(200, json=[payload])
            ),
        )
    )
    assert records[0]["estado"] == unknown_state


def test_invalid_records_log_one_field_specific_block_with_real_duration(
    monkeypatch,
    capsys,
):
    import biblioteca_mais_nova.xano_client as xano_client

    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    invalid_requests = [
        {
            "id": 44,
            "usuario_id": 84,
            "titulo_id": 50,
            "estado": "pendente",
            "reserva_id": -1,
            "atendida_em": 0,
        },
        {
            "id": 45,
            "usuario_id": 84,
            "titulo_id": 51,
            "estado": "pendente",
            "reserva_id": -2,
            "atendida_em": 0,
        },
    ]

    def handle(_request):
        time.sleep(0.02)
        return httpx.Response(200, json=invalid_requests)

    records = asyncio.run(
        list_my_requests(
            "token",
            transport=httpx.MockTransport(handle),
        )
    )
    log = capsys.readouterr().err

    assert records == []
    assert records.skipped_count == 2
    assert log.count("[ERRO xano]") == 1
    assert "registro 0, campo reserva_id: valor não é um id válido" in log
    assert "chamada: GET /minhas/solicitacoes -> 200 em " in log
    elapsed = re.search(r"-> 200 em (\d+) ms", log)
    assert elapsed is not None
    assert int(elapsed.group(1)) >= 10
    assert "perfil real: estudante | visão: estudante" in log

    response = httpx.Response(
        200,
        json=[],
        request=httpx.Request("GET", "https://api.example.test/diag"),
    )
    response.extensions["xano_duration_ms"] = 184
    xano_client._log_response_failure(response, "teste local de duração")
    assert "-> 200 em 184 ms" in capsys.readouterr().err

    invalid_post = {
        "id": 44,
        "usuario_id": 84,
        "titulo_id": 51,
        "estado": "pendente",
        "reserva_id": -1,
        "atendida_em": 0,
    }

    def invalid_post_response(_request):
        time.sleep(0.02)
        return httpx.Response(200, json=invalid_post)

    async def send_invalid_post():
        with xano_client.contexto_evento_xano(
            "reservar_livro",
            "estudante",
        ):
            with pytest.raises(XanoWriteSucceededWithUnreadableResponse):
                await request_title_loan(
                    50,
                    "token",
                    transport=httpx.MockTransport(invalid_post_response),
                )

    asyncio.run(send_invalid_post())
    post_log = capsys.readouterr().err
    assert post_log.count("[ERRO xano]") == 1
    assert (
        "ação: reservar_livro | perfil real: estudante | visão: estudante"
        in post_log
    )
    assert (
        "registro 0, campo titulo_id: não corresponde ao título solicitado"
        in post_log
    )
    elapsed = re.search(r"-> 200 em (\d+) ms", post_log)
    assert elapsed is not None
    assert int(elapsed.group(1)) >= 10


def test_request_service_reports_unreadable_success_without_retry(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []

    def mismatched_handler(request):
        requests.append(request)
        return httpx.Response(
            201,
            json={
                "id": 33,
                "usuario_id": 9,
                "titulo_id": 15,
                "estado": "pendente",
            },
        )

    mismatched = httpx.MockTransport(mismatched_handler)
    with pytest.raises(XanoWriteSucceededWithUnreadableResponse):
        asyncio.run(request_title_loan(14, "token", transport=mismatched))

    requests.clear()

    def invalid_json_handler(request):
        requests.append(request)
        return httpx.Response(201, content=b"not-json")

    invalid_json = httpx.MockTransport(invalid_json_handler)
    with pytest.raises(XanoWriteSucceededWithUnreadableResponse):
        asyncio.run(request_title_loan(14, "token", transport=invalid_json))
    assert len(requests) == 1
    assert requests[0].method == "POST"


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
            "O Xano demorou para responder. Tente novamente.",
        ),
        (
            XanoInvalidResponseError("payload interno não deve aparecer"),
            "O Xano respondeu em formato inesperado.",
        ),
        (
            XanoRequestError("detalhe de transporte não deve aparecer"),
            "Não foi possível conectar ao Xano. Verifique a conexão e tente novamente.",
        ),
        (
            XanoResponseError(502, non_json_response=True),
            "O Xano devolveu uma página de erro (código 502).",
        ),
        (
            XanoResponseError(429),
            "O Xano permite só 10 chamadas a cada 20 segundos no plano atual. "
            "Aguarde cerca de 20 s e tente de novo.",
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


def test_admin_student_preview_uses_own_token_and_does_not_invent_records(
    monkeypatch,
):
    calls = []

    async def forbidden_for_admin(token):
        calls.append(token)
        raise XanoResponseError(403)

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("A consulta deve parar na primeira recusa")

    monkeypatch.setattr(frontend, "list_my_loans", forbidden_for_admin)
    monkeypatch.setattr(frontend, "list_my_requests", unexpected_call)
    monkeypatch.setattr(frontend, "list_my_reservations", unexpected_call)
    monkeypatch.setattr(frontend, "list_public_titles", unexpected_call)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"admin-student-preview-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-proprio-admin", "admin", "Ana")
            state.set_admin_view_mode("estudante")

            await state.load_student_library()

            assert calls == ["token-proprio-admin"]
            assert state._session_token == "token-proprio-admin"
            assert state._session_profile == "admin"
            assert state.is_student is True
            assert state.student_library_has_error is True
            assert state.student_library_loans == []
            assert state.student_library_requests == []
            assert state.student_library_reservations == []

    asyncio.run(verify())


def test_admin_student_view_can_submit_request_with_real_admin_session(
    monkeypatch,
):
    calls = []

    async def create_request(title_id, token):
        calls.append((title_id, token))
        return {
            "id": 91,
            "titulo_id": title_id,
            "estado": "pendente",
            "solicitada_em": None,
        }

    monkeypatch.setattr(frontend, "request_title_loan", create_request)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"admin-student-request-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-real-admin", "admin", "Ana")
            state.set_admin_view_mode("estudante")
            state.public_catalog_detail = {
                "id": 44,
                "titulo": "Livro de teste",
            }

            await state.request_catalog_title(44)

            assert calls == [(44, "token-real-admin")]
            assert state._session_profile == "admin"
            assert state._session_token == "token-real-admin"
            assert state.is_student is True
            assert state.student_request_message.startswith("Pedido enviado.")

    asyncio.run(verify())


def test_student_library_401_clears_session_and_offers_login(monkeypatch):
    async def expired_session(token):
        assert token == "token-expirado"
        raise XanoResponseError(401)

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("A carga deve parar no primeiro 401")

    monkeypatch.setattr(frontend, "list_my_loans", expired_session)
    monkeypatch.setattr(frontend, "list_my_requests", unexpected_call)
    monkeypatch.setattr(frontend, "list_my_reservations", unexpected_call)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-expired-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-expirado", "estudante")

            await state.load_student_library()

            assert state._session_token == ""
            assert state.is_authenticated is False
            assert state.student_library_requires_login is True
            assert state.student_library_has_error is True
            assert state.student_library_pending is False
            assert "Entre novamente" in state.student_library_message
            assert state.student_library_loans == []
            assert state.student_library_requests == []
            assert state.student_library_reservations == []

    asyncio.run(verify())

    page = json.dumps(
        json.loads(repr(frontend.student_library())),
        ensure_ascii=False,
    )
    assert "Entrar" in page
    assert "/login" in page
    assert "role" in page and "alert" in page


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
            assert state.student_library_requests[0]["href"] == "/catalogo/14"
            assert state.student_library_reservations[0]["titulo"] == "Livro público"
            assert state.student_library_reservations[0]["href"] == "/catalogo/14"
            assert state.student_library_reservations[0]["prazo"] == (
                "12/11/2026 09:00"
            )
            delta = await root._get_resolved_delta()
            assert "token-estudante" not in json.dumps(delta, default=str)

    asyncio.run(verify())


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (XanoResponseError(401), "[RES-401] Sua sessão expirou, entre de novo"),
        (XanoResponseError(403), "[RES-403] Seu perfil não pode reservar"),
        (
            XanoResponseError(404),
            "[RES-404] Este recurso ainda não está disponível no servidor",
        ),
        (
            XanoResponseError(409),
            "[RES-409] Há limite ou duplicidade nesta reserva",
        ),
        (
            XanoResponseError(503),
            "[RES-5XX] O servidor teve um problema (código 5xx)",
        ),
        (
            XanoTimeoutError("tempo esgotado"),
            "O Xano demorou para responder. Tente novamente.",
        ),
        (
            XanoResponseError(429),
            "O Xano permite só 10 chamadas a cada 20 segundos no plano atual. "
            "Aguarde cerca de 20 s e tente de novo.",
        ),
    ],
)
def test_reservation_request_error_codes(error, expected):
    assert reservation_request_error_message(error) == expected


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
            assert state.student_request_message == (
                "Não foi possível conectar ao Xano. "
                "Verifique a conexão e tente novamente."
            )

    asyncio.run(verify())


@pytest.mark.parametrize(
    "error",
    [
        XanoResponseError(429, reference="E4290"),
        XanoResponseError(503, reference="E5030"),
        XanoTimeoutError("tempo esgotado", reference="ETIME"),
    ],
)
def test_student_request_http_and_timeout_failures_keep_reference_without_retry(
    monkeypatch, error
):
    writes = []

    async def failed_request(title_id, token):
        writes.append((title_id, token))
        raise error

    async def unexpected_read(*_args, **_kwargs):
        raise AssertionError("Falha na escrita não deve iniciar releitura")

    monkeypatch.setattr(frontend, "request_title_loan", failed_request)
    monkeypatch.setattr(frontend, "list_my_loans", unexpected_read)
    monkeypatch.setattr(frontend, "list_my_requests", unexpected_read)
    monkeypatch.setattr(frontend, "list_my_reservations", unexpected_read)
    monkeypatch.setattr(frontend, "list_public_titles", unexpected_read)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-request-error-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}

            await state.request_catalog_title(14)

            assert writes == [(14, "token-estudante")]
            assert state.student_request_has_error is True
            assert f"(ref. {error.reference})" in state.student_request_message
            assert state.student_request_pending is False

    asyncio.run(verify())


def test_student_request_treats_unreadable_success_as_success_and_refreshes(
    monkeypatch,
):
    writes = []
    request_reads = 0
    retry_delays = []

    async def unreadable_write(title_id, token):
        writes.append((title_id, token))
        raise XanoWriteSucceededWithUnreadableResponse()

    async def empty_records(_token):
        return []

    async def delayed_request(_token):
        nonlocal request_reads
        request_reads += 1
        if request_reads == 1:
            return []
        return [
            {
                "id": 9,
                "usuario_id": 7,
                "titulo_id": 14,
                "estado": "pendente",
            }
        ]

    async def public_titles():
        return []

    async def sleep(delay):
        retry_delays.append(delay)

    monkeypatch.setattr(frontend, "request_title_loan", unreadable_write)
    monkeypatch.setattr(frontend, "list_my_loans", empty_records)
    monkeypatch.setattr(frontend, "list_my_requests", delayed_request)
    monkeypatch.setattr(frontend, "list_my_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_public_titles", public_titles)
    monkeypatch.setattr(frontend.asyncio, "sleep", sleep)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-write-warning-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}

            await state.request_catalog_title(14)

            assert writes == [(14, "token-estudante")]
            assert request_reads == 2
            assert state.student_request_message == (
                "Pedido enviado. Sua solicitação foi registrada. "
                "A equipe da biblioteca "
                "confirmará a retirada."
            )
            assert retry_delays == [1.5]
            assert state.student_request_has_error is False
            assert state.student_library_pending is False
            assert state.student_request_pending is False

    asyncio.run(verify())


def test_student_request_stays_locked_until_refresh_confirms_unreadable_write(
    monkeypatch, capsys
):
    writes = []
    request_reads = 0
    retry_delays = []

    async def unreadable_write(title_id, token):
        writes.append((title_id, token))
        raise XanoWriteSucceededWithUnreadableResponse(reference="E7F3A")

    async def empty_records(_token):
        return []

    async def requests(_token):
        nonlocal request_reads
        request_reads += 1
        if request_reads <= 3:
            return []
        return [
            {
                "id": 9,
                "usuario_id": 7,
                "titulo_id": 14,
                "estado": "pendente",
            }
        ]

    async def public_titles():
        return []

    async def sleep(delay):
        retry_delays.append(delay)

    monkeypatch.setattr(frontend, "request_title_loan", unreadable_write)
    monkeypatch.setattr(frontend, "list_my_loans", empty_records)
    monkeypatch.setattr(frontend, "list_my_requests", requests)
    monkeypatch.setattr(frontend, "list_my_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_public_titles", public_titles)
    monkeypatch.setattr(frontend.asyncio, "sleep", sleep)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-request-confirm-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}

            await state.request_catalog_title(14)

            assert writes == [(14, "token-estudante")]
            assert state.student_request_pending is True
            assert state.student_request_has_error is True
            assert state.student_request_message == (
                "Não foi possível confirmar a solicitação. "
                "Confira Reservas antes de tentar novamente. (ref. E7F3A)"
            )
            assert request_reads == 3
            assert retry_delays == [1.5, 2.5]

            await state.request_catalog_title(14)
            assert writes == [(14, "token-estudante")]
            assert request_reads == 3

            await state.retry_student_library()
            assert request_reads == 4
            assert state.student_request_pending is False
            assert state.student_request_has_error is False
            assert state.student_request_message == (
                "Pedido enviado. Sua solicitação foi registrada. "
                "A equipe da biblioteca "
                "confirmará a retirada."
            )

    asyncio.run(verify())
    output = capsys.readouterr().err
    assert "[ERRO xano] ref=E7F3A" in output
    assert "releitura 3x não achou o pedido" in output


def test_student_request_cannot_be_submitted_again_while_pending(monkeypatch):
    writes = []
    request_reads = 0

    async def unreadable_write(title_id, token):
        writes.append((title_id, token))
        raise XanoWriteSucceededWithUnreadableResponse(reference="E7F3A")

    async def empty_records(_token):
        return []

    async def delayed_request(_token):
        nonlocal request_reads
        request_reads += 1
        if request_reads == 1:
            return []
        return [
            {
                "id": 9,
                "usuario_id": 7,
                "titulo_id": 14,
                "estado": "pendente",
            }
        ]

    async def public_titles():
        return []

    monkeypatch.setattr(frontend, "request_title_loan", unreadable_write)
    monkeypatch.setattr(frontend, "list_my_loans", empty_records)
    monkeypatch.setattr(frontend, "list_my_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_public_titles", public_titles)

    async def verify():
        reread_started = asyncio.Event()
        continue_read = asyncio.Event()

        async def delayed_request(_token):
            nonlocal request_reads
            request_reads += 1
            if request_reads == 1:
                return []
            reread_started.set()
            await continue_read.wait()
            return [
                {
                    "id": 9,
                    "usuario_id": 7,
                    "titulo_id": 14,
                    "estado": "pendente",
                }
            ]

        monkeypatch.setattr(frontend, "list_my_requests", delayed_request)

        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-request-pending-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}
            first_submission = asyncio.create_task(
                state.request_catalog_title(14)
            )
            try:
                await asyncio.wait_for(reread_started.wait(), timeout=5)
                assert state.student_request_pending is True
                assert request_reads == 2

                await state.request_catalog_title(14)

                assert writes == [(14, "token-estudante")]
                assert state.student_request_pending is True
                assert request_reads == 2
            finally:
                continue_read.set()
            await asyncio.wait_for(first_submission, timeout=2)

            assert writes == [(14, "token-estudante")]
            assert request_reads == 2
            assert state.student_request_pending is False
            assert state.student_request_has_error is False
            assert state.student_request_message.startswith("Pedido enviado.")

    asyncio.run(verify())


def test_reopening_reservations_does_not_repeat_uncertain_write_retries(
    monkeypatch,
):
    calls = {"loans": 0, "requests": 0, "reservations": 0, "titles": 0}

    async def records(name):
        calls[name] += 1
        return []

    async def loans(_token):
        return await records("loans")

    async def requests(_token):
        return await records("requests")

    async def reservations(_token):
        return await records("reservations")

    async def titles():
        return await records("titles")

    retry_delays = []
    original_sleep = asyncio.sleep

    async def unexpected_sleep(delay):
        if delay > 0:
            retry_delays.append(delay)
            return
        await original_sleep(0)

    monkeypatch.setattr(frontend, "list_my_loans", loans)
    monkeypatch.setattr(frontend, "list_my_requests", requests)
    monkeypatch.setattr(frontend, "list_my_reservations", reservations)
    monkeypatch.setattr(frontend, "list_public_titles", titles)
    monkeypatch.setattr(frontend.asyncio, "sleep", unexpected_sleep)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"reservations-reopen-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.student_request_uncertain_title_id = 14
            state.student_request_pending = True
            state.student_request_has_error = True

            await state.load_student_library()

            assert calls == {
                "loans": 1,
                "requests": 1,
                "reservations": 1,
                "titles": 1,
            }
            assert state.student_request_pending is True
            assert state.student_request_has_error is True
            assert retry_delays == []

    asyncio.run(verify())


def test_student_request_confirms_direct_response_without_reloading_lists(
    monkeypatch,
):
    writes = []

    async def direct_request(title_id, token):
        writes.append((title_id, token))
        return {
            "id": 44,
            "titulo_id": title_id,
            "estado": "pendente",
            "solicitada_em": "2026-11-24T19:31:02Z",
        }

    async def unexpected_read(_token):
        raise AssertionError("Resposta confirmada não deve reler as listas")

    monkeypatch.setattr(frontend, "request_title_loan", direct_request)
    monkeypatch.setattr(frontend, "list_my_loans", unexpected_read)
    monkeypatch.setattr(frontend, "list_my_requests", unexpected_read)
    monkeypatch.setattr(frontend, "list_my_reservations", unexpected_read)
    monkeypatch.setattr(frontend, "list_public_titles", unexpected_read)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-request-direct-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {
                "id": 14,
                "titulo": "Livro solicitado",
            }

            await state.request_catalog_title(14)

            assert writes == [(14, "token-estudante")]
            assert state.student_request_pending is False
            assert state.student_request_has_error is False
            assert state.student_request_message.startswith("Pedido enviado.")
            assert state.student_library_requests == [
                {
                    "id": 44,
                    "titulo": "Livro solicitado",
                    "href": "/catalogo/14",
                    "estado": "Aguardando confirmação da retirada",
                    "solicitada_em": "24/11/2026 19:31 UTC",
                }
            ]

    asyncio.run(verify())


def test_student_request_blocks_duplicate_from_loaded_lists(monkeypatch):
    writes = []

    async def unexpected_request(title_id, token):
        writes.append((title_id, token))
        raise AssertionError("Pedido duplicado não deve enviar POST")

    monkeypatch.setattr(frontend, "request_title_loan", unexpected_request)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-request-duplicate-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}
            state._student_pending_title_ids = [14]

            await state.request_catalog_title(14)

            assert writes == []
            assert state.student_request_pending is False
            assert state.student_request_has_error is False
            assert state.student_request_message == (
                "Você já tem um pedido para este livro. "
                "Veja em Reservas."
            )
            assert "(ref." not in state.student_request_message

    asyncio.run(verify())


def test_student_request_remains_locked_until_failed_refresh_recovers(monkeypatch):
    calls = []

    async def unreadable_write(title_id, token):
        raise XanoWriteSucceededWithUnreadableResponse()

    async def loans(_token):
        calls.append("loans")
        if len(calls) == 1:
            raise XanoRequestError("Falha de comunicação")
        return []

    async def empty_records(_token):
        return []

    async def matching_request(_token):
        return [
            {
                "id": 9,
                "usuario_id": 7,
                "titulo_id": 14,
                "estado": "pendente",
            }
        ]

    async def public_titles():
        return []

    monkeypatch.setattr(frontend, "request_title_loan", unreadable_write)
    monkeypatch.setattr(frontend, "list_my_loans", loans)
    monkeypatch.setattr(frontend, "list_my_requests", matching_request)
    monkeypatch.setattr(frontend, "list_my_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_public_titles", public_titles)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-write-lock-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}

            await state.request_catalog_title(14)
            assert state.student_library_has_error is True
            assert state.student_request_pending is True

            await state.retry_student_library()
            assert state.student_library_has_error is False
            assert state.student_request_pending is False

    asyncio.run(verify())


@pytest.mark.parametrize(
    ("server_message", "status_code", "expected_message"),
    [
        (
            "Solicitacao duplicada. Consulte Minha biblioteca.",
            403,
            "[RES-403] Seu perfil não pode reservar",
        ),
        (
            "Já existe solicitação ativa para este título.",
            409,
            "[RES-409] Você já tem uma solicitação ativa para este título. "
            "Consulte Minha biblioteca.",
        ),
        (
            "Já existe reserva ativa para este título.",
            409,
            "[RES-409] Você já tem uma reserva ativa para este título. "
            "Consulte Minha biblioteca.",
        ),
        (
            "Titulo nao encontrado.",
            404,
            "[RES-404] Este recurso ainda não está disponível no servidor",
        ),
    ],
)
def test_student_request_shows_allowlisted_business_error(
    monkeypatch, capsys, server_message, status_code, expected_message
):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://api.example.test")
    requests = []
    messages = []

    def handle(request):
        requests.append(request)
        return httpx.Response(status_code, json={"message": server_message})

    transport = httpx.MockTransport(handle)

    async def submit(title_id, token):
        return await request_title_loan(title_id, token, transport=transport)

    monkeypatch.setattr(frontend, "request_title_loan", submit)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"student-business-error-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state.public_catalog_detail = {"id": 14}
            await state.request_catalog_title(14)

            assert state.student_request_has_error is True
            assert state.student_request_message.startswith(expected_message)
            messages.append(state.student_request_message)
            assert len(requests) == 1
            assert requests[0].url.path == "/solicitacoes-emprestimo"

    asyncio.run(verify())
    output = capsys.readouterr().err
    reference = output.split("[ERRO xano] ref=", 1)[1][:5]
    assert messages[0].endswith(f"(ref. {reference})")
    if status_code == 409:
        assert server_message not in messages[0]
        assert expected_message in messages[0]


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

    async def empty_records(_token):
        return []

    async def public_titles():
        return []

    monkeypatch.setattr(frontend, "request_title_loan", submit)
    monkeypatch.setattr(frontend, "list_my_loans", empty_records)
    monkeypatch.setattr(frontend, "list_my_requests", empty_records)
    monkeypatch.setattr(frontend, "list_my_reservations", empty_records)
    monkeypatch.setattr(frontend, "list_public_titles", public_titles)

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
            assert state.student_request_message == (
                "[RES-409] Há limite ou duplicidade nesta reserva"
            )

    asyncio.run(verify())


def test_student_library_page_and_navigation_are_profile_gated():
    page = _readable_text(frontend.student_library())
    header = repr(frontend.site_header())
    assert "Reservas e empréstimos" in page
    assert "empr" in page
    assert "solicita" in page
    assert "reservas" in page
    assert "/reservas" in header
    assert "minha-biblioteca" in frontend.app._unevaluated_pages


def test_student_reservations_has_four_sections_and_empty_states():
    page = _readable_text(frontend.student_reservations())
    tab_labels = (
        "Aguardando",
        "Aprovadas",
        "Emprestados",
        "Atrasos",
    )

    assert all(label in page for label in tab_labels)
    assert "reservation-tabs" in repr(frontend.student_reservations())
    assert "Você não tem pedidos aguardando aprovação." in page
    assert "Você não tem reservas aprovadas aguardando retirada." in page
    assert "Você não tem livros emprestados no momento." in page
    assert "Você não tem empréstimos em atraso." in page
    assert "student-reservations-count" in page
    assert "student-overdue-alert" in page


def test_my_library_redirects_to_reservations_without_personal_gets(monkeypatch):
    calls = []

    async def unexpected_get(*_args, **_kwargs):
        calls.append(True)
        raise AssertionError("A rota legada não deve consultar dados pessoais")

    monkeypatch.setattr(frontend, "list_my_loans", unexpected_get)
    monkeypatch.setattr(frontend, "list_my_requests", unexpected_get)
    monkeypatch.setattr(frontend, "list_my_reservations", unexpected_get)

    async def verify_redirect():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"my-library-redirect-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            redirect = state.redirect_student_library()
            assert "/reservas" in repr(redirect)
            assert "reservas" in frontend.app._unevaluated_pages
            assert "minha-biblioteca" in frontend.app._unevaluated_pages
            assert calls == []

    asyncio.run(verify_redirect())


def test_student_reservation_groups_order_overdue_and_show_neutral_missing_data(
    monkeypatch,
):
    now = datetime.now(timezone.utc)

    def timestamp(day_offset):
        return (now + timedelta(days=day_offset)).isoformat()

    async def loans(_token):
        return [
            {
                **_loan_records()[0],
                "id": 21,
                "retirado_em": timestamp(-10),
                "vence_em": timestamp(-5),
                "devolvido_em": None,
            },
            {
                **_loan_records()[0],
                "id": 22,
                "retirado_em": timestamp(-8),
                "vence_em": timestamp(-2),
                "devolvido_em": None,
            },
            {
                **_loan_records()[0],
                "id": 23,
                "retirado_em": timestamp(-5),
                "vence_em": timestamp(3),
                "devolvido_em": None,
            },
            {
                **_loan_records()[0],
                "id": 24,
                "retirado_em": timestamp(-3),
                "vence_em": timestamp(1),
                "devolvido_em": None,
            },
        ]

    async def requests(_token):
        return [
            {
                "id": 51,
                "usuario_id": 9,
                "titulo_id": 900,
                "estado": "pendente",
            }
        ]

    async def reservations(_token):
        return [
            {
                **_reservation_records()[0],
                "id": 61,
                "titulo_id": 901,
                "expira_em_sao_paulo": None,
            }
        ]

    async def titles():
        return []

    monkeypatch.setattr(frontend, "list_my_loans", loans)
    monkeypatch.setattr(frontend, "list_my_requests", requests)
    monkeypatch.setattr(frontend, "list_my_reservations", reservations)
    monkeypatch.setattr(frontend, "list_public_titles", titles)

    async def verify_groups():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"reservation-groups-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante-reservas", "estudante")
            await state.load_student_library()

            assert [
                loan["dias_atraso"] for loan in state.student_overdue_loans
            ] == [5, 2]
            assert [
                loan["dias_restantes"] for loan in state.student_current_loans
            ] == [1, 3]
            assert len(state.student_awaiting_approval_requests) == 1
            assert state.student_awaiting_approval_requests[0]["titulo"] == (
                "Título indisponível"
            )
            assert state.student_awaiting_approval_requests[0]["solicitada_em"] == (
                "Data indisponível"
            )
            assert len(state.student_approved_reservations) == 1
            assert state.student_approved_reservations[0]["titulo"] == (
                "Título indisponível"
            )
            assert state.student_approved_reservations[0]["prazo"] == (
                "Data indisponível"
            )

    asyncio.run(verify_groups())

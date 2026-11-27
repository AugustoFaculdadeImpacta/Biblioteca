import threading
from datetime import datetime
from http.server import ThreadingHTTPServer

import httpx
import pytest

import scripts.demo_api as demo_api


@pytest.fixture
def demo_server(monkeypatch):
    data = demo_api.DemoData()
    monkeypatch.setattr(demo_api, "DATA", data)
    server = ThreadingHTTPServer(("127.0.0.1", 0), demo_api.DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = httpx.Client(base_url=f"http://127.0.0.1:{server.server_port}")
    try:
        yield client, data
    finally:
        client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_demo_api_applies_configured_latency(monkeypatch, demo_server):
    delays = []
    monkeypatch.setenv("BIBLIOTECA_DEMO_LATENCIA_MS", "37")
    monkeypatch.setattr(demo_api, "_sleep", delays.append)
    client, _ = demo_server

    response = client.get("/catalogo/categorias")

    assert response.status_code == 200
    assert delays == [0.037]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _rules(**overrides: object) -> dict[str, object]:
    return {**demo_api.DEFAULT_LIBRARY_RULES, **overrides}


def _save_rules(client: httpx.Client, **overrides: object) -> dict[str, object]:
    response = client.put(
        "/admin/configuracoes",
        headers=_headers("demo-token-admin"),
        json=_rules(**overrides),
    )
    assert response.status_code == 200
    return response.json()


def _release_seed_loan(data: demo_api.DemoData) -> None:
    data.loans.clear()
    for copy in data.copies:
        if copy["estado"] == "emprestado":
            copy["estado"] = "disponivel"


def _available_title_id(data: demo_api.DemoData) -> int:
    return next(
        int(title["id"])
        for title in data.titles
        if data.available_count(int(title["id"])) > 0
    )


def test_demo_api_reads_default_rules_and_allows_admin_to_save_them(demo_server):
    client, _ = demo_server
    read = client.get(
        "/configuracoes",
        headers=_headers("demo-token-estudante"),
    )

    assert read.status_code == 200
    assert {key: read.json()[key] for key in demo_api.DEFAULT_LIBRARY_RULES} == (
        demo_api.DEFAULT_LIBRARY_RULES
    )
    assert read.json()["atualizado_em"] is None
    assert read.json()["atualizado_por"] is None

    saved = _save_rules(
        client,
        limite_emprestimos_ativos=5,
        prazo_emprestimo_dias=21,
    )
    assert saved["limite_emprestimos_ativos"] == 5
    assert saved["prazo_emprestimo_dias"] == 21
    assert saved["atualizado_em"]
    assert saved["atualizado_por"] == "Administrador Demonstração"
    assert set(saved) == set(demo_api.DEFAULT_LIBRARY_RULES) | {
        "atualizado_em",
        "atualizado_por",
    }


@pytest.mark.parametrize(
    ("token", "expected_status"),
    [
        ("demo-token-estudante", 403),
        ("demo-token-bibliotecario", 403),
    ],
)
def test_demo_api_only_admin_can_write_library_rules(
    demo_server,
    token,
    expected_status,
):
    client, _ = demo_server
    response = client.put(
        "/admin/configuracoes",
        headers=_headers(token),
        json=_rules(),
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("overrides", "extra", "missing", "expected_field"),
    [
        ({"limite_emprestimos_ativos": 0}, {}, None, "limite_emprestimos_ativos"),
        ({"prazo_retirada_horas": 169}, {}, None, "prazo_retirada_horas"),
        ({"limite_pedidos_em_aberto": True}, {}, None, "limite_pedidos_em_aberto"),
        ({"bloquear_com_atraso": 1}, {}, None, "bloquear_com_atraso"),
        ({}, {"desconhecido": 1}, None, "sete campos"),
        ({}, {}, "prazo_emprestimo_dias", "sete campos"),
    ],
)
def test_demo_api_rejects_invalid_or_incomplete_library_rules(
    demo_server,
    overrides,
    extra,
    missing,
    expected_field,
):
    client, _ = demo_server
    body = {**_rules(**overrides), **extra}
    if missing is not None:
        body.pop(missing)
    response = client.put(
        "/admin/configuracoes",
        headers=_headers("demo-token-admin"),
        json=body,
    )

    assert response.status_code == 400
    assert expected_field in response.json()["message"]


def test_demo_api_applies_request_limit_and_allows_admin_personal_requests(
    demo_server,
):
    client, data = demo_server
    _release_seed_loan(data)
    _save_rules(client, limite_pedidos_em_aberto=1)
    first_title = _available_title_id(data)
    second_title = next(
        int(title["id"])
        for title in data.titles
        if int(title["id"]) != first_title
        and data.available_count(int(title["id"])) > 0
    )

    first = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": first_title},
    )
    over_limit = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": second_title},
    )
    admin_request = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-admin"),
        json={"titulo_id": first_title},
    )

    assert first.status_code == 201
    assert over_limit.status_code == 403
    assert over_limit.json()["message"] == "Limite de pedidos em aberto atingido."
    assert admin_request.status_code == 201
    assert admin_request.json()["usuario_id"] == 102
    personal = client.get(
        "/minhas/solicitacoes",
        headers=_headers("demo-token-admin"),
    )
    assert [item["id"] for item in personal.json()] == [admin_request.json()["id"]]
    staff_headers = _headers("demo-token-bibliotecario")
    student_pickup = client.post(
        f"/admin/solicitacoes/{first.json()['id']}/retirada",
        headers=staff_headers,
    )
    admin_pickup = client.post(
        f"/admin/solicitacoes/{admin_request.json()['id']}/retirada",
        headers=staff_headers,
    )
    admin_loans = client.get("/admin/emprestimos", headers=staff_headers)
    assert student_pickup.status_code == admin_pickup.status_code == 201
    assert any(
        item["usuario_id"] == 102
        and item["usuario_nome"] == "Administrador Demonstração"
        for item in admin_loans.json()
    )


def test_demo_api_applies_configurable_active_loan_limit(demo_server):
    client, data = demo_server
    active_loan = next(item for item in data.loans if item["usuario_id"] == 101)
    title_id = next(
        int(title["id"])
        for title in data.titles
        if int(title["id"]) != active_loan["titulo_id"]
        and data.available_count(int(title["id"])) > 0
    )
    _save_rules(client, limite_emprestimos_ativos=1)

    response = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": title_id},
    )

    assert response.status_code == 403
    assert response.json()["message"] == (
        "Limite de 1 empréstimo ativo atingido."
    )


def test_demo_api_applies_configurable_loan_deadline_and_authorization(
    demo_server,
):
    client, data = demo_server
    _release_seed_loan(data)
    _save_rules(
        client,
        exigir_autorizacao_bibliotecaria=False,
        prazo_emprestimo_dias=1,
    )
    title_id = _available_title_id(data)

    request = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": title_id},
    )
    assert request.status_code == 201
    assert request.json()["estado"] == "aprovada"
    staff_queue = client.get(
        "/admin/solicitacoes",
        headers=_headers("demo-token-bibliotecario"),
    )
    assert [item["id"] for item in staff_queue.json()] == [request.json()["id"]]

    pickup = client.post(
        f"/admin/solicitacoes/{request.json()['id']}/retirada",
        headers=_headers("demo-token-bibliotecario"),
    )
    assert pickup.status_code == 201
    withdrawn = datetime.fromisoformat(pickup.json()["retirado_em"].replace("Z", "+00:00"))
    due = datetime.fromisoformat(pickup.json()["vence_em"].replace("Z", "+00:00"))
    assert (due - withdrawn).total_seconds() == 24 * 60 * 60


def test_demo_api_can_disable_overdue_block_and_reuse_active_reservation(
    demo_server,
):
    client, data = demo_server
    loan = next(item for item in data.loans if item["usuario_id"] == 101)
    loan["vence_em"] = "2020-01-01T00:00:00Z"
    _save_rules(
        client,
        bloquear_com_atraso=False,
        permitir_pedido_com_reserva_ativa=True,
    )
    title_id = next(
        int(title["id"])
        for title in data.titles
        if int(title["id"]) != loan["titulo_id"]
        and data.available_count(int(title["id"])) > 0
    )
    reservation = {
        "id": data.next_reservation_id,
        "usuario_id": 101,
        "titulo_id": title_id,
        "criada_em": "2026-01-01T10:00:00Z",
        "estado": "aguardando",
        "exemplar_id": None,
        "ofertada_em": None,
        "expira_em": None,
    }
    data.next_reservation_id += 1
    data.reservations.append(reservation)

    response = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": title_id},
    )

    assert response.status_code == 201
    assert response.json()["estado"] == "em_reserva"
    assert response.json()["reserva_id"] == reservation["id"]
    assert len(
        [
            item
            for item in data.reservations
            if item["usuario_id"] == 101 and item["titulo_id"] == title_id
        ]
    ) == 1


def test_demo_api_rejects_request_with_active_reservation_when_rule_is_disabled(
    demo_server,
):
    client, data = demo_server
    title_id = _available_title_id(data)
    _save_rules(client, permitir_pedido_com_reserva_ativa=False)
    reservation = {
        "id": data.next_reservation_id,
        "usuario_id": 101,
        "titulo_id": title_id,
        "criada_em": "2026-01-01T10:00:00Z",
        "estado": "aguardando",
        "exemplar_id": None,
        "ofertada_em": None,
        "expira_em": None,
    }
    data.reservations.append(reservation)
    data.next_reservation_id += 1

    response = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": title_id},
    )

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Já existe reserva ativa para este título."
    )


def test_demo_api_uses_configured_reservation_offer_window(demo_server):
    client, data = demo_server
    _release_seed_loan(data)
    _save_rules(client, prazo_retirada_horas=1)
    title_id = _available_title_id(data)
    copy = next(
        item
        for item in data.copies
        if item["titulo_id"] == title_id and item["estado"] == "disponivel"
    )
    data.reservations.append(
        {
            "id": data.next_reservation_id,
            "usuario_id": 101,
            "titulo_id": title_id,
            "criada_em": "2026-01-01T10:00:00Z",
            "estado": "aguardando",
            "exemplar_id": None,
            "ofertada_em": None,
            "expira_em": None,
        }
    )
    data.next_reservation_id += 1

    response = client.post(
        "/admin/reservas/ofertar-proxima",
        headers=_headers("demo-token-bibliotecario"),
        json={"titulo_id": title_id, "exemplar_id": copy["id"]},
    )

    assert response.status_code == 200
    offered = datetime.fromisoformat(response.json()["reserva"]["ofertada_em"].replace("Z", "+00:00"))
    expires = datetime.fromisoformat(response.json()["expira_em_utc"].replace("Z", "+00:00"))
    assert (expires - offered).total_seconds() == 60 * 60

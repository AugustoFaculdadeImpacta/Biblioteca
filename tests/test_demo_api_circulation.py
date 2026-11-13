import threading
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


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _add_second_student(data: demo_api.DemoData) -> None:
    student = {
        "id": 103,
        "nome": "Segunda Estudante",
        "email": "segunda.estudante@example.invalid",
        "perfil": "estudante",
        "token": "token-demo-estudante-2",
        "ativo": True,
    }
    data.users[student["email"]] = student
    data.students.append(
        {key: student[key] for key in ("id", "nome", "email", "perfil", "ativo")}
    )


def _release_seed_loan(data: demo_api.DemoData) -> None:
    data.loans.clear()
    for copy in data.copies:
        if copy["estado"] == "emprestado":
            copy["estado"] = "disponivel"


def test_demo_api_enforces_fifo_and_sets_fourteen_day_loan(demo_server):
    client, data = demo_server
    _add_second_student(data)
    _release_seed_loan(data)

    first = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": 1},
    )
    second = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("token-demo-estudante-2"),
        json={"titulo_id": 1},
    )
    assert first.status_code == second.status_code == 201
    assert first.json()["estado"] == second.json()["estado"] == "pendente"

    librarian = _headers("demo-token-bibliotecario")
    pending = client.get("/admin/solicitacoes", headers=librarian).json()
    assert [item["id"] for item in pending] == [
        first.json()["id"],
        second.json()["id"],
    ]

    out_of_order = client.post(
        f"/admin/solicitacoes/{second.json()['id']}/retirada",
        headers=librarian,
    )
    assert out_of_order.status_code == 409

    picked_up = client.post(
        f"/admin/solicitacoes/{first.json()['id']}/retirada",
        headers=librarian,
    )
    assert picked_up.status_code == 201
    loan = picked_up.json()
    assert loan["solicitacao_id"] == first.json()["id"]
    assert loan["devolvido_em"] is None
    from datetime import datetime

    withdrawn = datetime.fromisoformat(loan["retirado_em"].replace("Z", "+00:00"))
    due = datetime.fromisoformat(loan["vence_em"].replace("Z", "+00:00"))
    assert (due - withdrawn).total_seconds() == 14 * 24 * 60 * 60

    returned_first = client.post(
        f"/admin/emprestimos/{loan['id']}/devolucao",
        headers=librarian,
    )
    assert returned_first.status_code == 200
    assert returned_first.json()["emprestimo"]["devolvido_em"] is not None
    second_pickup = client.post(
        f"/admin/solicitacoes/{second.json()['id']}/retirada",
        headers=librarian,
    )
    assert second_pickup.status_code == 201


def test_demo_api_reservation_offer_refusal_pickup_and_return_respect_fifo(
    demo_server,
):
    client, data = demo_server
    _add_second_student(data)
    _release_seed_loan(data)
    reservation_entries = []
    for reservation_id, user_id, student in (
        (1, 101, data.students[0]),
        (2, 103, data.students[-1]),
    ):
        reservation = {
            "id": reservation_id,
            "usuario_id": user_id,
            "titulo_id": 1,
            "criada_em": f"2026-01-0{reservation_id}T10:00:00Z",
            "estado": "aguardando",
            "exemplar_id": None,
            "ofertada_em": None,
            "expira_em": None,
        }
        data.reservations.append(reservation)
        request = {
            "id": reservation_id,
            "usuario_id": user_id,
            "titulo_id": 1,
            "solicitada_em": reservation["criada_em"],
            "estado": "em_reserva",
            "reserva_id": reservation_id,
            "atendida_em": None,
        }
        data.loan_requests.append(request)
        reservation_entries.append((reservation, request, student))

    librarian = _headers("demo-token-bibliotecario")
    available_copy = next(
        copy
        for copy in data.copies
        if copy["titulo_id"] == 1 and copy["estado"] == "disponivel"
    )
    offered = client.post(
        "/admin/reservas/ofertar-proxima",
        headers=librarian,
        json={"titulo_id": 1, "exemplar_id": available_copy["id"]},
    )
    assert offered.status_code == 200
    assert offered.json()["reserva"]["id"] == 1
    assert offered.json()["reserva"]["estado"] == "ofertada"
    assert offered.json()["expira_em_sao_paulo"]

    refused_offer = client.post(
        "/admin/reservas/1/recusar",
        headers=librarian,
    )
    assert refused_offer.status_code == 409

    picked_up = client.post("/admin/reservas/1/retirada", headers=librarian)
    assert picked_up.status_code == 201
    assert reservation_entries[0][1]["estado"] == "atendida"

    returned = client.post(
        f"/admin/emprestimos/{picked_up.json()['id']}/devolucao",
        headers=librarian,
    )
    assert returned.status_code == 200
    assert returned.json()["reserva_ofertada"]["id"] == 2
    assert reservation_entries[1][0]["estado"] == "ofertada"

    second_pickup = client.post("/admin/reservas/2/retirada", headers=librarian)
    assert second_pickup.status_code == 201


def test_demo_api_offers_other_title_to_student_with_active_loan(demo_server):
    client, data = demo_server
    reservation = {
        "id": 1,
        "usuario_id": 101,
        "titulo_id": 1,
        "criada_em": "2026-01-01T10:00:00Z",
        "estado": "aguardando",
        "exemplar_id": None,
        "ofertada_em": None,
        "expira_em": None,
    }
    data.reservations.append(reservation)
    loan = next(item for item in data.loans if item["usuario_id"] == 101)
    assert loan["titulo_id"] != reservation["titulo_id"]

    copy = next(
        item
        for item in data.copies
        if item["titulo_id"] == reservation["titulo_id"]
        and item["estado"] == "disponivel"
    )
    offered = client.post(
        "/admin/reservas/ofertar-proxima",
        headers=_headers("demo-token-bibliotecario"),
        json={"titulo_id": reservation["titulo_id"], "exemplar_id": copy["id"]},
    )

    assert offered.status_code == 200
    assert offered.json()["reserva"]["id"] == reservation["id"]
    assert offered.json()["reserva"]["estado"] == "ofertada"


def test_demo_api_allows_two_other_title_loans_but_enforces_three_and_same_title(
    demo_server,
):
    client, data = demo_server
    loan = next(item for item in data.loans if item["usuario_id"] == 101)
    loan["vence_em"] = "2099-12-31T23:59:59Z"

    same_title = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": loan["titulo_id"]},
    )
    assert same_title.status_code == 403
    assert (
        same_title.json()["message"]
        == "Estudante já possui empréstimo ativo deste título."
    )

    allowed = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": 1},
    )
    assert allowed.status_code == 201

    data.loans.append(
        {
            **loan,
            "id": data.next_loan_id,
            "titulo_id": 3,
            "exemplar_id": next(
                item["id"] for item in data.copies if item["titulo_id"] == 3
            ),
        }
    )
    data.next_loan_id += 1
    data.loans.append(
        {
            **loan,
            "id": data.next_loan_id,
            "titulo_id": 4,
            "exemplar_id": next(
                item["id"] for item in data.copies if item["titulo_id"] == 4
            ),
        }
    )
    data.next_loan_id += 1

    at_limit = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": 6},
    )
    assert at_limit.status_code == 403
    assert at_limit.json()["message"] == "Limite de três empréstimos ativos atingido."


def test_demo_api_rejects_student_admin_access_and_refusal_updates_request(
    demo_server,
):
    client, data = demo_server
    _add_second_student(data)
    _release_seed_loan(data)
    unauthenticated = client.get("/admin/reservas")
    forbidden = client.get(
        "/admin/reservas",
        headers=_headers("demo-token-estudante"),
    )
    assert unauthenticated.status_code == 401
    assert forbidden.status_code == 403

    request = {
        "id": 80,
        "usuario_id": 101,
        "titulo_id": 4,
        "solicitada_em": "2026-01-01T10:00:00Z",
        "estado": "em_reserva",
        "reserva_id": 80,
        "atendida_em": None,
    }
    other_request = {
        "id": 81,
        "usuario_id": 103,
        "titulo_id": 3,
        "solicitada_em": "2026-01-01T10:00:00Z",
        "estado": "pendente",
        "reserva_id": None,
        "atendida_em": None,
    }
    reservation = {
        "id": 80,
        "usuario_id": 101,
        "titulo_id": 4,
        "criada_em": "2026-01-01T10:00:00Z",
        "estado": "aguardando",
        "exemplar_id": None,
        "ofertada_em": None,
        "expira_em": None,
    }
    data.loan_requests.append(request)
    data.loan_requests.append(other_request)
    data.reservations.append(reservation)

    refused = client.post(
        "/admin/reservas/80/recusar",
        headers=_headers("demo-token-admin"),
    )
    assert refused.status_code == 200
    assert refused.json()["estado"] == "recusada"
    assert request["estado"] == "recusada"

    personal = client.get(
        "/minhas/solicitacoes",
        headers=_headers("demo-token-estudante"),
    )
    assert personal.status_code == 200
    assert [item["id"] for item in personal.json()] == [80]
    assert personal.json()[0]["estado"] == "recusada"


def test_demo_api_requires_available_copy_and_student_eligibility(demo_server):
    client, data = demo_server
    _release_seed_loan(data)
    title_id = 1
    for copy in data.copies:
        if copy["titulo_id"] == title_id:
            copy["estado"] = "emprestado"

    unavailable = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": title_id},
    )
    assert unavailable.status_code == 201
    assert unavailable.json()["estado"] == "em_reserva"
    assert unavailable.json()["reserva_id"] is not None

    data.loans.append(
        {
            "id": data.next_loan_id,
            "usuario_id": 101,
            "titulo_id": 1,
            "exemplar_id": data.copies[0]["id"],
            "solicitacao_id": None,
            "retirado_em": "2026-01-01T10:00:00Z",
            "vence_em": "2020-01-01T10:00:00Z",
            "devolvido_em": None,
        }
    )
    blocked = client.post(
        "/solicitacoes-emprestimo",
        headers=_headers("demo-token-estudante"),
        json={"titulo_id": 2},
    )
    assert blocked.status_code == 403
    assert blocked.json()["message"] == "Estudante possui empréstimo atrasado."

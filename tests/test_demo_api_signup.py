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


def test_signup_returns_student_session_and_accepts_login(demo_server):
    client, data = demo_server
    response = client.post(
        "/auth/signup",
        json={
            "nome": "Estudante novo",
            "email": " NOVO.ESTUDANTE@example.invalid ",
            "senha": "senha-local-de-teste",
        },
    )

    assert response.status_code == 201
    session = response.json()
    assert session["usuario"] == {
        "id": 103,
        "nome": "Estudante novo",
        "email": "novo.estudante@example.invalid",
        "perfil": "estudante",
    }
    assert "senha" not in session
    assert len(data.students) == 2

    login = client.post(
        "/auth/login",
        json={
            "email": "novo.estudante@example.invalid",
            "senha": "senha-local-de-teste",
        },
    )

    assert login.status_code == 200
    assert login.json() == session


def test_signup_rejects_duplicate_email_case_insensitively(demo_server):
    client, data = demo_server
    first = client.post(
        "/auth/signup",
        json={
            "nome": "Estudante novo",
            "email": "novo.estudante@example.invalid",
            "senha": "senha-local-de-teste",
        },
    )
    duplicate = client.post(
        "/auth/signup",
        json={
            "nome": "Outra pessoa",
            "email": "NOVO.ESTUDANTE@EXAMPLE.INVALID",
            "senha": "outra-senha-local",
        },
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["message"] == (
        "Este e-mail já está cadastrado. Tente entrar com sua conta."
    )
    assert len(data.students) == 2

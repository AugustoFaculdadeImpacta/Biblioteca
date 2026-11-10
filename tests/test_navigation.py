import asyncio
import json
from uuid import uuid4

import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend


def test_homepage_has_public_and_profile_specific_actions_and_confirmation():
    homepage = repr(frontend.index())
    assert "Bem-vindo" in homepage
    assert "/login" in homepage
    assert "/cadastro" in homepage
    assert "/admin/acervo" in homepage
    assert "signup_success_message_rx_state_" in homepage
    assert "dismiss_signup_confirmation" in homepage


def test_navigation_changes_by_profile_and_logout_clears_session():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"navigation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            header = repr(frontend.site_header())
            assert state.is_authenticated is False
            assert state.is_librarian is False
            assert state.is_student is False
            assert "/minha-biblioteca" in header

            state._store_session("token-falso-navegacao", "estudante")
            assert state.is_authenticated is True
            assert state.is_librarian is False
            assert state.is_student is True
            assert "/minha-biblioteca" in header

            state._store_session("token-falso-bibliotecario", "bibliotecario")
            assert state.is_librarian is True
            assert state.is_student is False
            delta = await root._get_resolved_delta()
            serialized_delta = json.dumps(delta, default=str)
            assert "token-falso-bibliotecario" not in serialized_delta
            assert "bibliotecario" not in serialized_delta

            redirect = state.logout()
            assert redirect is not None
            assert "redirect" in repr(redirect).lower()
            assert state.is_authenticated is False
            assert state.is_librarian is False
            assert state.is_student is False
            assert state._read_session_token() is None

    asyncio.run(verify())


def test_student_navigation_has_accessible_labels_focus_and_mobile_layout():
    header = repr(frontend.site_header())
    style = frontend.app.style

    assert r"Navega\\u00e7\\u00e3o principal" in header
    assert "/catalogo" in header
    assert r"In\\u00edcio" in header
    assert r"Cat\\u00e1logo" in header
    assert "Minha biblioteca" in header
    assert "Sair" in header

    assert style[":focus-visible"]["outline"].startswith("3px solid ")
    assert style[".site-nav a"]["color"] == "var(--blue-11)"
    mobile = style["@media screen and (max-width: 40rem)"]
    assert mobile[".site-header"]["flex_direction"] == "column"
    assert mobile[".app-shell"]["padding"] == "0.5rem"


def test_signup_confirmation_is_consumed_from_home_state():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"signup-confirmation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.signup_success_message = (
                "Cadastro realizado. Seu acesso de estudante está ativo."
            )
            state.dismiss_signup_confirmation()
            assert state.signup_success_message == ""

    asyncio.run(verify())

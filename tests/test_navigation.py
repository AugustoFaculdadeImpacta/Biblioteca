import asyncio
import json
from uuid import uuid4

import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend


def test_homepage_is_login_and_authenticated_sessions_go_to_catalog():
    homepage = repr(frontend.index())
    assert "Entrar" in homepage
    assert "login-email" in homepage
    assert "login-senha" in homepage
    assert "/cadastro" in homepage

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"home-redirect-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            assert state.redirect_authenticated_home() is None

            state._store_session(
                "token-falso-estudante", "estudante", "Ana Silva"
            )
            redirect = state.redirect_authenticated_home()
            assert "/catalogo" in repr(redirect)
            assert state.greeting_name == "Ana Silva"

    asyncio.run(verify())


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
            assert "/admin/reservas" in header
            assert "Reservas para estudantes" in header

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

            state._store_session("token-falso-admin", "admin")
            assert state.is_librarian is True
            assert state.is_student is False
            admin_delta = await root._get_resolved_delta()
            admin_serialized_delta = json.dumps(admin_delta, default=str)
            assert "token-falso-admin" not in admin_serialized_delta
            assert '"admin"' not in admin_serialized_delta

            redirect = state.logout()
            assert redirect is not None
            assert "redirect" in repr(redirect).lower()
            assert state.is_authenticated is False
            assert state.is_librarian is False
            assert state.is_student is False
            assert state._read_session_token() is None
            assert state.greeting_name == ""

    asyncio.run(verify())


def test_student_navigation_has_accessible_labels_focus_and_mobile_layout():
    header = repr(frontend.site_header())
    style = frontend.app.style

    assert r"Navega\\u00e7\\u00e3o principal" in header
    assert "/catalogo" in header
    assert "In\\u00edcio" not in header
    assert r"Cat\\u00e1logo" in header
    assert "greeting_name_rx_state_" in header
    assert "Minha biblioteca" in header
    assert "Sair" in header

    assert style[":focus-visible"]["outline"].startswith("3px solid ")
    assert style[".site-nav a"]["color"] == "var(--blue-11)"
    assert "Início" not in repr(header)
    assert "greeting_name_rx_state_" in repr(header)
    assert r"Ol\\u00e1, " in header
    mobile = style["@media screen and (max-width: 40rem)"]
    assert mobile[".site-header"]["flex_direction"] == "column"
    assert mobile[".site-nav"]["width"] == "100%"
    assert mobile[".a11y-menu"]["width"] == "100%"
    assert mobile[".app-shell"]["padding"] == "0.5rem"


def test_accessibility_font_limits_restoration_and_invalid_storage():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"accessibility-font-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.accessibility_font_scale_raw = "150"
            state.increase_accessibility_font()
            assert state.accessibility_font_scale == 150
            assert state.accessibility_font_scale_raw == "150"

            state.accessibility_font_scale_raw = "100"
            state.decrease_accessibility_font()
            assert state.accessibility_font_scale == 100
            assert state.accessibility_font_scale_raw == "100"

            state.accessibility_font_scale_raw = "bogus"
            assert state.accessibility_font_scale == 100
            state.increase_accessibility_font()
            assert state.accessibility_font_scale_raw == "110"

            state.reset_accessibility_font()
            assert state.accessibility_font_scale == 100

    asyncio.run(verify())


def test_accessibility_toggle_state_is_validated_and_reflected_globally():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"accessibility-modes-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.accessibility_high_contrast_raw = "invalid"
            state.accessibility_reduce_motion_raw = "invalid"
            assert state.accessibility_high_contrast is False
            assert state.accessibility_reduce_motion is False

            state.toggle_accessibility_high_contrast()
            state.toggle_accessibility_reduce_motion()
            assert state.accessibility_high_contrast is True
            assert state.accessibility_reduce_motion is True
            assert state.accessibility_classes == (
                "a11y-shell a11y-high-contrast a11y-reduce-motion"
            )

            state.toggle_accessibility_high_contrast()
            state.toggle_accessibility_reduce_motion()
            assert state.accessibility_high_contrast is False
            assert state.accessibility_reduce_motion is False
            assert state.accessibility_classes == "a11y-shell"

    asyncio.run(verify())


def test_session_name_is_private_and_never_uses_email_or_token_as_greeting():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"session-name-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            assert state.greeting_name == ""
            state._store_session(
                "token-privado-de-teste",
                "bibliotecario",
                "Ana Silva",
            )
            assert state.greeting_name == "Ana Silva"

            serialized = json.dumps(
                await root._get_resolved_delta(),
                default=str,
            )
            assert "token-privado-de-teste" not in serialized
            assert "ana@escola" not in serialized
            assert "_session_name" not in serialized

    asyncio.run(verify())


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

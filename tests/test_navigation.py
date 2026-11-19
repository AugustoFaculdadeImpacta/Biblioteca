import asyncio
import json
import re
from pathlib import Path
from uuid import uuid4

import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend


def _components(component: rx.Component):
    yield component
    for child in component.children:
        if isinstance(child, rx.Component):
            yield from _components(child)


def _serialized_class_count(component: rx.Component, class_name: str) -> int:
    tree = json.loads(repr(component))

    def count(value):
        if isinstance(value, dict):
            props = value.get("props", [])
            own_count = sum(
                prop == f'className:"{class_name}"'
                for prop in props
            )
            return own_count + sum(count(child) for child in value.values())
        if isinstance(value, list):
            return sum(count(child) for child in value)
        return 0

    return count(tree)


def _readable(component: rx.Component) -> str:
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
                    for prop in child:
                        values.append(prop)
                        if isinstance(prop, str) and prop.startswith('"'):
                            try:
                                values.append(json.loads("{" + prop + "}"))
                            except json.JSONDecodeError:
                                pass
                else:
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(serialized)
    return re.sub(
        r"\\u([0-9a-fA-F]{4})",
        lambda match: chr(int(match.group(1), 16)),
        " ".join(map(str, values)),
    )


def test_homepage_is_storefront_and_authenticated_sessions_go_to_catalog():
    homepage = repr(frontend.index())
    assert "Entrar" in homepage
    assert "Cadastrar-se" in homepage
    assert "home-catalog-search" in homepage
    assert "login-email" not in homepage
    assert "login-senha" not in homepage
    assert "form-login-home" not in homepage
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
            assert "'/'" in repr(redirect)
            assert state.greeting_name == "Ana Silva"

    asyncio.run(verify())


def test_authenticated_users_redirect_from_auth_pages_to_profile_home():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"auth-page-redirect-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            assert state.redirect_authenticated_auth_page() is None

            state._store_session("token-estudante-redirect", "estudante")
            redirect = state.redirect_authenticated_auth_page()
            assert "'/'" in repr(redirect)

            state._store_session("token-bibliotecario-redirect", "bibliotecario")
            redirect = state.redirect_authenticated_auth_page()
            assert "/admin/acervo" in repr(redirect)

            state._store_session("token-admin-redirect", "admin")
            redirect = state.redirect_authenticated_auth_page()
            assert "/admin/acervo" in repr(redirect)

            state.set_admin_view_mode("bibliotecaria")
            redirect = state.redirect_authenticated_auth_page()
            assert "/admin/acervo" in repr(redirect)

            state.set_admin_view_mode("estudante")
            redirect = state.redirect_authenticated_auth_page()
            assert "'/'" in repr(redirect)

    asyncio.run(verify())


def test_home_has_no_login_or_signup_form_and_keeps_profile_shortcuts():
    homepage = _readable(frontend.index())
    assert "form-busca-home" in homepage
    assert "Buscar no catálogo" in homepage
    assert "home-catalog-search" in homepage
    assert "type:\"password\"" not in homepage
    assert "login-email" not in homepage
    assert "login-senha" not in homepage
    assert "Entrar" in homepage
    assert "Cadastrar-se" in homepage
    assert "Reservas" in homepage
    assert "Acervo" in homepage
    assert "Contas" in homepage

    async def verify_search():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"home-search-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            redirect = state.search_home_catalog({"busca": "  A Ilha  "})
            assert state.public_catalog_search == "A Ilha"
            assert "/catalogo" in repr(redirect)

    asyncio.run(verify_search())


def test_home_statistics_are_derived_from_public_catalog():
    async def verify_statistics():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"home-statistics-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.public_catalog_entries = [
                {
                    "titulo": {
                        "id": 1,
                        "titulo": "Livro ativo",
                        "autores": "Ana",
                        "ativo": True,
                    },
                    "categorias": [],
                    "exemplares_disponiveis": 2,
                },
                {
                    "titulo": {
                        "id": 2,
                        "titulo": "Ativo sem campo ativo",
                        "autores": "Bia",
                    },
                    "categorias": [],
                    "exemplares_disponiveis": 3,
                },
                {
                    "titulo": {
                        "id": 3,
                        "titulo": "Livro inativo",
                        "autores": "Caio",
                        "ativo": False,
                    },
                    "categorias": [],
                    "exemplares_disponiveis": 50,
                },
            ]
            state.public_catalog_categories = [
                {"id": 1, "nome": "Literatura"},
                {"id": 2, "nome": "História"},
                {"id": 3, "nome": "Categoria sem títulos"},
            ]

            assert state.home_total_titles == 2
            assert state.home_available_copies == 5
            assert state.home_category_count == 3

    asyncio.run(verify_statistics())


def test_home_shows_profile_shortcuts_and_about_section():
    homepage = _readable(frontend.index())

    assert "Sobre a biblioteca" in homepage
    assert "Livros em destaque" in homepage
    assert "Ver mais" in homepage
    assert "hero-stat-grid" in homepage
    assert all(
        route in homepage
        for route in (
            "/reservas",
            "/admin/acervo",
            "/admin/reservas",
            "/admin/bibliotecarios",
        )
    )


def test_home_omits_popularity_without_loan_counts():
    homepage = _readable(frontend.index())

    assert "Livros que mais saem" not in homepage
    assert "empréstimos por título" not in homepage


def test_login_page_contains_only_login_form():
    page = _readable(frontend.login_page())
    components = list(_components(frontend.login_page()))
    input_ids = {
        component.id
        for component in components
        if component.alias == "RadixThemesTextField.Root"
    }

    assert "form-login" in page
    assert "login-email" in input_ids
    assert "login-senha" in input_ids
    assert "form-cadastro-estudante" not in page
    assert "signup-nome" not in input_ids
    assert "signup-email" not in input_ids
    assert "Ver catálogo sem entrar" in page


def test_signup_page_contains_only_signup_form():
    page = _readable(frontend.student_signup())
    components = list(_components(frontend.student_signup()))
    input_ids = {
        component.id
        for component in components
        if component.alias == "RadixThemesTextField.Root"
    }

    assert "form-cadastro-estudante" in page
    assert {"signup-nome", "signup-email", "signup-senha"} <= input_ids
    assert "form-login" not in page
    assert "login-email" not in input_ids
    assert "login-senha" not in input_ids
    assert "Já tem conta? Entrar" in page


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
            assert "/reservas" in header
            assert "/admin/reservas" in header

            state._store_session("token-falso-navegacao", "estudante")
            assert state.is_authenticated is True
            assert state.is_librarian is False
            assert state.is_student is True
            assert "/reservas" in header

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
            assert "token-falso-admin" not in admin_serialized_delta

            redirect = state.logout()
            assert redirect is not None
            assert "redirect" in repr(redirect).lower()
            assert state.is_authenticated is False
            assert state.is_librarian is False
            assert state.is_student is False
            assert state._read_session_token() is None
            assert state.greeting_name == ""

    asyncio.run(verify())


def test_admin_view_mode_changes_navigation_without_changing_session():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"admin-view-mode-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-falso-admin-view", "admin", "Ana")
            assert state.admin_view_mode == ""

            state.set_admin_view_mode("estudante")

            assert state.admin_view_mode == "estudante"
            assert state._session_profile == "admin"
            assert state.is_librarian is True
            assert state.is_student is False
            assert state.can_manage_librarians is True
            serialized = json.dumps(
                await root._get_resolved_delta(),
                default=str,
            )
            assert "token-falso-admin-view" not in serialized
            assert '"admin"' not in serialized

            state.set_admin_view_mode("bibliotecaria")
            assert state.admin_view_mode == "bibliotecaria"
            state._store_session("token-falso-bibliotecario", "bibliotecario")
            state.set_admin_view_mode("estudante")
            assert state.admin_view_mode == ""

    asyncio.run(verify())


def test_admin_view_mode_controls_are_visible_and_accessible():
    header = _readable(frontend.site_header())
    menu = _readable(frontend.profile_menu())
    style = frontend.app.style

    assert "Modo de visualização" in header
    assert "Modo de visualização" in menu
    assert "Admin" in header
    assert "Bibliotecária" in header
    assert "Estudante" in header
    assert 'role:"radio"' in header
    assert "aria-checked" in header
    assert "Modo escuro" in menu
    assert "Voltar à visão de admin" not in menu
    assert "Voltar à visão de admin" in header
    assert style[":focus-visible"]["outline"].startswith("3px solid ")


def test_admin_view_mode_can_reset_and_is_hidden_for_non_admin():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"admin-view-reset-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin-reset", "admin", "Ana")
            assert state.admin_view_mode == ""
            assert state.can_manage_librarians is True

            state.set_admin_view_mode("estudante")
            assert state.admin_view_mode == "estudante"
            assert state.is_librarian is True
            assert state.is_student is False

            state.reset_admin_view_mode()
            assert state.admin_view_mode == ""

            state._store_session("token-estudante-reset", "estudante", "Bia")
            assert state.can_manage_librarians is False
            assert state.admin_view_mode == ""
            assert state.is_librarian is False
            assert state.is_student is True

    asyncio.run(verify())


def test_student_navigation_has_accessible_labels_focus_and_mobile_layout():
    header = _readable(frontend.site_header())
    style = frontend.app.style

    assert "Navegação principal" in header
    assert "/catalogo" in header
    assert "Início" not in header
    assert "Catálogo" in header
    assert "greeting_name_rx_state_" in header
    assert "Reservas" in header
    assert "/reservas" in header
    assert "Sair" in header

    assert style[":focus-visible"]["outline"].startswith("3px solid ")
    assert style[".site-primary-nav a"]["color"] == "var(--brand-700)"
    assert "Início" not in header
    assert "Perfil" in header
    assert style[".brand-link"]["white_space"] == "nowrap"
    assert style[".profile-menu"]["position"] == "relative"
    assert style[".profile-menu-content"]["position"] == "absolute"
    mobile = style["@media screen and (max-width: 40rem)"]
    assert mobile[".site-header"]["display"] == "grid"
    assert mobile[".site-menu-toggle"]["display"] == "inline-flex"
    assert mobile[".site-header-desktop"]["display"] == "none"
    assert mobile[".app-shell"]["padding"] == "0.5rem"


def test_site_header_brand_and_footer_links_preserve_profile_access():
    header = _readable(frontend.site_header())
    footer = _readable(frontend.site_footer())
    homepage = repr(frontend.index())
    style = frontend.app.style

    assert "Biblioteca escolar" in header
    assert "Leitura, encontro e conhecimento" not in header
    assert homepage.index("brand-link") < homepage.index("Descubra")
    assert "Perfil" in header
    assert "/admin/acervo" in header
    assert "/admin/reservas" in header
    assert "/admin/bibliotecarios" in header
    assert "Voltar à visão de admin" in header
    assert "/admin/circulacao" not in header
    assert "Sobre a biblioteca" in footer
    assert "Links úteis" in footer
    assert "/catalogo" in footer
    assert "/acessibilidade" not in footer
    assert "/#controles-acessibilidade" not in footer
    assert "contato" not in footer.lower()
    assert "privacidade" not in footer.lower()
    assert style[".profile-menu-trigger"]["min_height"] == "2.75rem"
    assert style[".site-menu-toggle"]["min_height"] == "2.75rem"


def _route_components():
    return {
        "/": frontend.index,
        "/login": frontend.login_page,
        "/cadastro": frontend.student_signup,
        "/perfil": frontend.profile_page,
        "/acessibilidade": frontend.accessibility_page,
        "/catalogo": frontend.public_catalog,
        "/catalogo/[titulo_id]": frontend.public_catalog_detail,
        "/reservas": frontend.student_reservations,
        "/minha-biblioteca": frontend.student_library_redirect,
        "/admin/acervo": frontend.catalog_admin,
        "/admin/reservas": frontend.staff_reservation_page,
        "/admin/circulacao": frontend.circulation_page,
        "/admin/bibliotecarios": frontend.librarian_management,
    }


def test_header_has_catalog_and_profile_on_every_route():
    for route, page_factory in _route_components().items():
        page = page_factory()
        text = _readable(page)
        components = list(_components(page))

        assert "Catálogo" in text, route
        assert "Perfil" in text, route
        assert _serialized_class_count(page, "site-header") == 1, route


def test_all_routes_use_one_shared_header_and_footer():
    for route, page_factory in _route_components().items():
        page = page_factory()
        assert _serialized_class_count(page, "site-header") == 1, route
        assert _serialized_class_count(page, "site-footer") == 1, route

    footer = _readable(frontend.site_footer())
    assert "Sobre a biblioteca" in footer
    assert "Catálogo" in footer
    assert "Acessibilidade" not in footer
    assert "/acessibilidade" not in footer
    assert "/#controles-acessibilidade" not in footer


def test_page_bodies_do_not_duplicate_global_navigation():
    detail = _readable(frontend.public_catalog_detail())
    student_library = _readable(frontend.student_library())
    home = _readable(frontend.index())
    login = _readable(frontend.login_page())
    signup = _readable(frontend.student_signup())

    assert "Voltar ao catálogo" not in detail
    assert "Acompanhar em Minha biblioteca" not in detail
    assert "Voltar ao catálogo" not in student_library
    assert "Ver catálogo" in home
    assert "Ver catálogo sem entrar" in login
    assert "Não tem conta? Cadastre-se" in login
    assert "Já tem conta? Entrar" in signup


def test_profile_menu_for_visitor_has_login_and_signup():
    component = frontend.profile_menu()
    menu = _readable(component)
    details = next(
        item for item in _components(component) if type(item).__name__ == "Details"
    )
    summary = next(
        item for item in _components(component) if type(item).__name__ == "Summary"
    )

    assert details.class_name == "profile-menu"
    assert summary.class_name == "profile-menu-trigger"
    assert "Perfil" in menu
    assert "Entrar" in menu
    assert "Cadastrar-se" in menu


def test_profile_disclosure_uses_details_without_rx_menu():
    component = frontend.profile_menu()
    components = list(_components(component))

    assert any(type(item).__name__ == "Details" for item in components)
    assert any(type(item).__name__ == "Summary" for item in components)
    assert not any("RadixThemesDropdownMenu" in repr(item) for item in components)


def test_profile_disclosure_escape_and_outside_click_script():
    script = _readable(frontend.profile_menu())

    assert "__bibliotecaProfileDisclosureInstalled" in script
    assert 'event.key !== "Escape"' in script
    assert 'disclosure.querySelector("summary")?.focus()' in script
    assert 'document.querySelectorAll("details.profile-menu[open]")' in script
    assert "item.contains(event.target)" in script
    assert "event.preventDefault()" in script


def test_application_contains_no_rx_menu():
    app_directory = Path(__file__).parents[1] / "biblioteca_mais_nova"

    assert all(
        "rx.menu" not in path.read_text(encoding="utf-8")
        for path in app_directory.rglob("*.py")
    )


def test_profile_disclosure_for_visitor_and_authenticated_users():
    menu = _readable(frontend.profile_menu())

    assert "Entrar" in menu
    assert "Cadastrar-se" in menu
    assert "Modo escuro" in menu
    assert "greeting_name_rx_state_" in menu
    assert "session_email_rx_state_" in menu
    assert "session_role_label_rx_state_" in menu
    assert "Diminuir fonte" in menu
    assert "Aumentar fonte" in menu
    assert "Ativar alto contraste" in menu
    assert "Reduzir movimento" in menu
    assert "Sair" in menu
    assert "Meu perfil" not in menu
    assert "href:\"/acessibilidade\"" not in menu

    async def verify_session_role_labels():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"profile-role-labels-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            assert state.is_authenticated is False
            state._store_session(
                "token-profile-student", "estudante", "Leitora", "leitura@example.test"
            )
            assert state.greeting_name == "Leitora"
            assert state.session_email == "leitura@example.test"
            assert state.session_role_label == "Estudante"

            state._store_session(
                "token-profile-librarian",
                "bibliotecario",
                "Bibliotecário",
                "acervo@example.test",
            )
            assert state.session_role_label == "Bibliotecário"

            state._store_session(
                "token-profile-admin", "admin", "Admin", "gestao@example.test"
            )
            assert state.session_role_label == "Administrador"

    asyncio.run(verify_session_role_labels())


def test_profile_page_shows_session_identity_read_only():
    page = frontend.profile_page()
    text = _readable(page)
    components = list(_components(page))

    assert "Meu perfil" in text
    assert "Nome" in text
    assert "E-mail" in text
    assert "Papel" in text
    assert "greeting_name_rx_state_" in text
    assert "session_email_rx_state_" in text
    assert "session_role_label_rx_state_" in text
    assert not any(
        component.alias == "RadixThemesTextField.Root"
        for component in components
    )
    assert "type:\"password\"" not in text

    async def verify_session_identity():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"profile-readonly-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            assert "'/login'" in repr(state.require_authenticated_user())
            state._store_session(
                "token-profile-readonly",
                "estudante",
                "Pessoa de teste",
                "perfil@example.test",
            )
            assert state.require_authenticated_user() is None
            assert state.greeting_name == "Pessoa de teste"
            assert state.session_email == "perfil@example.test"
            assert state.session_role_label == "Estudante"

    asyncio.run(verify_session_identity())


def test_accessibility_page_reuses_existing_controls():
    page = _readable(frontend.accessibility_page())
    style = frontend.app.style

    assert "Acessibilidade" in page
    assert "Controles de acessibilidade" in page
    assert "Diminuir fonte" in page
    assert "Tamanho padrão" in page
    assert "Aumentar fonte" in page
    assert "Ativar alto contraste" in page
    assert "Reduzir movimento" in page
    assert "increase_accessibility_font" in page
    assert "toggle_accessibility_high_contrast" in page
    assert "toggle_accessibility_reduce_motion" in page
    assert "aria-pressed" in page
    assert style[".a11y-controls button"]["min_height"] == "2.75rem"


def test_header_navigation_by_profile_and_view():
    nav = _readable(frontend.site_primary_nav())
    menu = _readable(frontend.profile_menu())
    header = frontend.site_header()
    header_text = _readable(header)

    assert all(
        route in nav
        for route in (
            "/catalogo",
            "/reservas",
            "/admin/acervo",
            "/admin/reservas",
            "/admin/bibliotecarios",
        )
    )
    assert all(
        label in nav
        for label in (
            "Catálogo",
            "Reservas",
            "Acervo",
            "Contas",
        )
    )
    assert "Minha biblioteca" not in nav
    assert "Circulação" not in nav
    assert _serialized_class_count(header, "site-primary-nav") == 2
    assert all(label in menu for label in ("Admin", "Bibliotecária", "Estudante"))
    assert "aria-checked" in menu
    assert "Modo de visualização" in header_text

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"active-nav-role-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante-nav", "estudante")
            assert state.active_navigation_role == "Estudante"

            state._store_session("token-bibliotecario-nav", "bibliotecario")
            assert state.active_navigation_role == "Bibliotecária"

            state._store_session("token-admin-nav", "admin")
            assert state.active_navigation_role == "Admin"
            state.set_admin_view_mode("bibliotecaria")
            assert state.active_navigation_role == "Bibliotecária"
            state.set_admin_view_mode("estudante")
            assert state.active_navigation_role == "Estudante"

    asyncio.run(verify())


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


def test_dark_mode_toggles_scoped_theme_tokens():
    menu = _readable(frontend.profile_menu())
    style = frontend.app.style
    script = menu

    assert "Modo escuro" in menu
    assert "data-dark-mode-toggle" in menu
    assert "a11y-dark" in script
    assert "a11y-light" in script
    assert ".a11y-shell.a11y-dark" in style
    assert "--bg-page" in style[".a11y-shell.a11y-dark"]
    assert "background_color" not in style.get(":root", {})


def test_dark_mode_follows_system_without_persistence():
    menu = _readable(frontend.profile_menu())
    script = menu

    assert "prefers-color-scheme: dark" in script
    assert "window.matchMedia" in script
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "document.cookie" not in script


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

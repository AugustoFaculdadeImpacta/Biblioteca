import reflex as rx

from biblioteca_mais_nova.biblioteca_mais_nova import (
    app,
    index,
    login_page,
    site_header,
)
from rxconfig import config


def _components(component: rx.Component):
    yield component
    for child in component.children:
        if isinstance(child, rx.Component):
            yield from _components(child)


def _contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return sum(
            weight * channel
            for weight, channel in zip(linear, (0.2126, 0.7152, 0.0722))
        )

    light, dark = sorted(
        (luminance(foreground), luminance(background)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def test_index_renders_navigable_application_shell():
    page = index()
    components = list(_components(page))
    nav = next(component for component in components if type(component).__name__ == "Nav")
    nav_content = repr(nav)
    button = next(
        component
        for component in components
        if component.alias == "RadixThemesButton"
    )

    assert nav.custom_attrs["aria-label"] == "Navegação principal"
    assert "/catalogo" in nav_content
    assert "active_navigation_role_rx_state_" in nav_content
    assert "/cadastro" in repr(page)
    assert "/login" in repr(page)
    assert "/admin/acervo" in nav_content
    assert "Início" not in repr(page)
    assert "Modo escuro" in repr(page)
    assert "#conteudo-home" in repr(page.children[0].children)
    assert "site-header-search" in repr(page)
    assert "home-catalog-search" not in repr(page)
    assert "form-busca-home" not in repr(page)
    assert "hero-stat-grid" in repr(page)
    assert getattr(button, "disabled", None) is None
    assert not any(component.id == "conteudo-login" for component in components)
    assert not any(
        component.id in {"login-email", "login-senha"}
        for component in components
    )


def test_focusable_field_and_button_have_visible_keyboard_focus_style():
    components = list(_components(login_page()))
    aliases = {component.alias for component in components}

    assert any(type(component).__name__ == "Input" for component in components)
    assert "RadixThemesTextField.Root" not in aliases
    assert "RadixThemesButton" in aliases
    assert app.style[":focus-visible"] == {
        "outline": "3px solid var(--brand-700)",
        "outline_offset": "3px",
    }


def test_visual_tokens_keep_accessible_contrast_and_reduced_motion():
    tokens = app.style[".a11y-shell"]
    assert tokens["--bg-page"] == "#f5efe4"
    assert tokens["--brand-900"] == "#183a4a"
    assert tokens["--success-700"] == "#245c45"
    assert tokens["--warning-700"] == "#8b5e17"
    assert _contrast_ratio(tokens["--slate-500"], tokens["--bg-page"]) >= 4.5
    assert _contrast_ratio(tokens["--brand-700"], tokens["--bg-panel"]) >= 4.5
    assert _contrast_ratio(tokens["--success-700"], tokens["--success-100"]) >= 4.5
    assert _contrast_ratio(tokens["--warning-700"], tokens["--warning-100"]) >= 4.5
    assert app.style["font_family"] == "system-ui, 'Segoe UI', sans-serif"
    assert app.style["h1, h2, h3, h4, h5, h6"]["font_family"] == (
        "Georgia, 'Times New Roman', serif"
    )
    assert app.style[":focus-visible"]["outline"].startswith("3px solid")
    assert app.style["@media (prefers-reduced-motion: reduce)"][
        "*, *::before, *::after"
    ]["transition_duration"] == "0.01ms !important"


def test_shared_header_and_footer_follow_the_restored_visual_hierarchy():
    header = app.style[".site-header"]

    assert header["position"] == "sticky"
    assert header["grid_template_columns"] == (
        "auto minmax(0, 1fr) minmax(10rem, 17rem) auto"
    )
    assert header["border_radius"] == "1rem"
    assert header["border"] == "1px solid var(--line)"
    assert "height" not in header
    assert "max_height" not in header
    assert app.style[".brand-link"]["font_family"] == (
        "Georgia, 'Times New Roman', serif"
    )
    assert app.style[".profile-menu-trigger"]["background_color"] == "transparent"
    assert app.style[".accessibility-menu-trigger"]["background_color"] == (
        "transparent"
    )
    assert app.style[".accessibility-menu-trigger"]["color"] == (
        "var(--button-subtle-text)"
    )
    assert app.style[".profile-menu-trigger"]["color"] == "var(--brand-text)"
    assert app.style[".site-footer"]["flex_wrap"] == "wrap"


def test_backend_exception_hook_logs_a_sanitized_traceback(monkeypatch, capsys):
    token = "token-nao-pode-aparecer"
    email = "pessoa.privada@example.test"
    password = "senha-nao-pode-aparecer"
    monkeypatch.delenv("BIBLIOTECA_LOG_ERROS", raising=False)

    try:
        raise RuntimeError(
            f"falha Authorization: Bearer {token}; email={email}; "
            f"password={password}"
        )
    except RuntimeError as error:
        result = app.backend_exception_handler(error)

    output = capsys.readouterr().err
    assert result is not None
    assert "[ERRO xano] ref=" in output
    assert "ref." in repr(result)
    assert "Traceback" in output
    assert token not in output
    assert email not in output
    assert password not in output


def test_dark_and_high_contrast_tokens_meet_wcag_aa():
    dark = app.style[".a11y-shell.a11y-dark"]
    assert _contrast_ratio(dark["--slate-900"], dark["--bg-page"]) >= 4.5
    assert _contrast_ratio(dark["--slate-900"], dark["--bg-panel"]) >= 4.5
    assert _contrast_ratio(dark["--slate-700"], dark["--bg-panel"]) >= 4.5
    assert _contrast_ratio(dark["--slate-500"], dark["--bg-page"]) >= 4.5
    assert _contrast_ratio(dark["--brand-text"], dark["--bg-panel"]) >= 4.5
    assert _contrast_ratio(dark["--brand-text"], dark["--bg-soft"]) >= 4.5
    assert _contrast_ratio(dark["--brand-text"], dark["--brand-100"]) >= 4.5
    assert _contrast_ratio(dark["--brand-700"], dark["--bg-panel"]) >= 4.5
    assert _contrast_ratio(dark["--line"], dark["--bg-page"]) >= 3
    assert _contrast_ratio(dark["--line"], dark["--bg-panel"]) >= 3
    assert _contrast_ratio(dark["--brand-700"], dark["--bg-page"]) >= 3
    assert _contrast_ratio("#ffffff", dark["--brand-900"]) >= 4.5
    assert _contrast_ratio(dark["--success-700"], dark["--success-100"]) >= 4.5
    assert _contrast_ratio(dark["--warning-700"], dark["--warning-100"]) >= 4.5
    assert _contrast_ratio(dark["--danger-700"], dark["--danger-100"]) >= 4.5
    assert _contrast_ratio("#000000", "#ffffff") >= 7
    assert _contrast_ratio("#00008b", "#ffffff") >= 7


def test_catalog_cover_grid_has_bounded_card_size():
    assert app.style[".catalog-grid"]["grid_template_columns"] == (
        "repeat(auto-fill, minmax(190px, 220px))"
    )
    assert app.style[".catalog-grid"]["justify_content"] == "start"
    assert app.style[".admin-catalog-grid"]["display"] == "flex"
    assert app.style[".admin-catalog-grid"]["flex_direction"] == "column"
    assert app.style[".catalog-card-cover"]["aspect_ratio"] == "2 / 3"


def test_motion_rules_have_reduced_motion_override():
    reduced = app.style["@media (prefers-reduced-motion: reduce)"]["*, *::before, *::after"]
    assert reduced["animation_duration"] == "0.01ms !important"
    assert reduced["animation_name"] == "none !important"
    assert reduced["transition_duration"] == "0.01ms !important"
    assert app.style[".app-shell"]["animation"] == "biblioteca-page-enter 300ms ease-out both"
    assert "@keyframes biblioteca-page-enter" in app.style
    assert "@keyframes biblioteca-profile-enter" in app.style
    assert "@keyframes biblioteca-availability-pulse" in app.style
    assert app.style[
        ".profile-menu[open] .profile-menu-content, "
        ".accessibility-menu[open] .profile-menu-content"
    ]["animation"].startswith("biblioteca-profile-enter")
    assert app.style[".status-pill-success"]["animation"].startswith(
        "biblioteca-availability-pulse"
    )


def test_button_variants_meet_wcag_aa_in_both_themes():
    variants = {
        "primary": (".focus-demo-button", ".focus-demo-button:hover"),
        "secondary": (".nav-logout", ".nav-logout:hover"),
        "danger": (".destructive-action", ".destructive-action:hover"),
        "warning": (".warning-action", ".warning-action:hover"),
        "subtle": (".subtle-action", ".subtle-action:hover"),
    }

    for theme_selector in (".a11y-shell", ".a11y-shell.a11y-dark"):
        theme = app.style[theme_selector]
        for variant, (base_selector, hover_selector) in variants.items():
            foreground = theme[f"--button-{variant}-text"]
            backgrounds = (
                theme[f"--button-{variant}-bg"],
                theme[f"--button-{variant}-hover-bg"],
            )
            assert all(
                _contrast_ratio(foreground, background) >= 4.5
                for background in backgrounds
            ), f"{variant} não atinge WCAG AA em {theme_selector}"
            assert app.style[base_selector]["color"] == (
                f"var(--button-{variant}-text)"
            )
            assert app.style[base_selector]["background_color"] == (
                f"var(--button-{variant}-bg)"
            )
            assert app.style[hover_selector]["background_color"] == (
                f"var(--button-{variant}-hover-bg)"
            )

    assert app.style[":focus-visible"]["outline"].startswith("3px solid")
    disabled = app.style[
        ".focus-demo-button:disabled, .nav-logout:disabled, "
        ".destructive-action:disabled, .warning-action:disabled, "
        ".subtle-action:disabled"
    ]
    assert disabled["border_style"] == "dashed"
    assert "opacity" not in disabled


def test_dark_theme_tokens_cover_operational_components():
    token_backgrounds = {
        ".student-library-section": "var(--bg-panel)",
        ".catalog-controls": "var(--bg-panel)",
        ".admin-catalog-section": "var(--bg-panel)",
        ".admin-title-card": "var(--bg-panel)",
        ".admin-title-edit-form": "var(--bg-soft)",
        ".librarian-management-section": "var(--bg-panel)",
        ".librarian-form": "var(--bg-soft)",
        ".librarian-card": "var(--bg-panel)",
        ".circulation-tab": "var(--bg-soft)",
        ".circulation-tab[aria-selected='true']": "var(--brand-100)",
        ".signup-feedback-error": "var(--danger-100)",
        ".signup-feedback-success": "var(--success-100)",
    }

    for selector, background in token_backgrounds.items():
        assert app.style[selector]["background_color"] == background

    for selector in (
        ".student-library-section",
        ".catalog-controls",
        ".admin-catalog-section",
        ".admin-title-card",
        ".admin-title-edit-form",
        ".librarian-management-section",
        ".librarian-form",
        ".librarian-card",
        ".circulation-tab",
    ):
        assert app.style[selector]["border"].endswith("var(--line)")


def test_dark_cover_fallbacks_use_saturated_palette():
    cover_backgrounds = [
        app.style[f".a11y-shell.a11y-dark .catalog-cover-{index}"][
            "background_color"
        ]
        for index in range(5)
    ]

    assert cover_backgrounds == [
        "#163b5c",
        "#14532d",
        "#7c2d12",
        "#7f1d1d",
        "#312e81",
    ]
    assert all(
        _contrast_ratio("#ffffff", background) >= 4.5
        for background in cover_backgrounds
    )


def test_text_fields_align_and_autofill_safely():
    field = app.style[".campo"]
    area = app.style[".campo-area"]
    select = app.style[".campo-select"]
    autofill = app.style["input.campo:-webkit-autofill, input.campo:autofill"]

    assert field["min_height"] == "2.75rem"
    assert field["height"] == "2.75rem"
    assert field["line_height"] == "normal"
    assert area["min_height"] == "5.5rem"
    assert select["min_height"] == "2.75rem"
    assert autofill["-webkit_text_fill_color"] == "var(--slate-900)"
    assert autofill["caret_color"] == "var(--slate-900)"
    assert "var(--bg-panel)" in autofill["box_shadow"]
    assert "9999s" in autofill["transition"]


def test_form_routes_use_native_fields_and_hidden_ids_are_invisible():
    from biblioteca_mais_nova import biblioteca_mais_nova as frontend

    routes = (
        frontend.login_page(),
        frontend.student_signup(),
        frontend.catalog_admin(),
        frontend.librarian_management(),
    )
    components = [
        item
        for route in routes
        for item in _components(route)
    ]
    assert not any(
        item.alias is not None
        and (
            item.alias.startswith("RadixThemesTextField")
            or item.alias in {"RadixThemesTextArea", "RadixThemesCheckbox"}
        )
        for item in components
    )
    title = rx.Var.create(
        {
            "id": 81,
            "titulo": "Livro",
            "autores": "Autoria",
            "isbn": "",
            "editora": "",
            "edicao": "",
            "ano_publicacao": "",
            "descricao": "",
            "capa_url": "",
            "capa_gerada": "",
            "ativo": True,
            "categorias": "Literatura",
            "exemplares_disponiveis": 1,
            "exemplares": [],
        }
    ).to(frontend.AdminCatalogDisplayEntry)
    card = frontend.admin_title_card(title)
    hidden = next(
        item
        for item in _components(card)
        if type(item).__name__ == "Input" and item.type._var_value == "hidden"
    )

    assert hidden.name._var_value == "titulo_id"
    assert app.style[".campo"]["border"] == "1px solid var(--line)"
    assert ".campo input" not in app.style


def test_category_checkboxes_share_44px_row():
    from biblioteca_mais_nova.biblioteca_mais_nova import catalog_category_option

    category = rx.Var.create({"id": 3, "nome": "Ciências"})
    row = catalog_category_option(category)
    assert row.class_name == "category-checkbox-row"
    assert type(row.children[0]).__name__ == "CheckboxInput"
    assert row.children[0].type._var_value == "checkbox"
    assert app.style[".category-checkbox-row"]["display"] == "inline-flex"
    assert app.style[".category-checkbox-row"]["align_items"] == "center"
    assert app.style[".category-checkbox-row"]["min_height"] == "2.75rem"


def test_text_controls_have_explicit_theme_aware_colors_and_focus():
    controls_style = app.style[".campo"]
    assert controls_style["color"] == "var(--slate-900)"
    assert controls_style["background_color"] == "var(--bg-panel)"
    assert app.style[".campo-area"]["color"] == "var(--slate-900)"
    assert app.style[".campo-select"]["background_color"] == "var(--bg-panel)"
    assert any(
        type(plugin).__name__ == "RadixThemesPlugin" and plugin.theme is not None
        for plugin in config.plugins
    )


def test_native_fields_have_single_border_and_visible_focus():
    field = app.style[".campo"]
    focused_fields = app.style[
        ".campo:focus-visible, .campo-area:focus-visible, .campo-select:focus-visible, .campo-check:focus-visible"
    ]

    assert field["border"] == "1px solid var(--line)"
    assert field["border_radius"] == "0.5rem"
    assert focused_fields["outline"] == "3px solid var(--brand-700)"
    assert focused_fields["outline_offset"] == "2px"


def test_form_controls_keep_keyboard_focus_visible():
    for selector in (".campo", ".campo-select"):
        assert app.style[selector]["min_height"] == "2.75rem"
        assert app.style[selector]["border"] == "1px solid var(--line)"
    assert app.style[".campo-area"]["min_height"] == "5.5rem"
    assert app.style[".campo-check-row"]["min_height"] == "2.75rem"
    assert app.style[":focus-visible"] == {
        "outline": "3px solid var(--brand-700)",
        "outline_offset": "3px",
    }


def test_authentication_forms_use_responsive_cards_and_distinct_feedback():
    assert app.style[".signup-section"]["width"] == "min(100%, 34rem)"
    assert app.style[".signup-section"]["background_color"] == "var(--bg-panel)"
    assert app.style[".signup-form"]["width"] == "100%"
    assert app.style[".signup-feedback-error"]["color"] == "var(--danger-700)"
    assert app.style[".signup-feedback-success"]["color"] == "var(--success-700)"


def test_forms_and_admin_panels_use_shared_visual_states():
    tokens = app.style[".a11y-shell"]
    for selector in (
        ".student-library-section",
        ".catalog-controls",
        ".admin-catalog-section",
        ".admin-title-card",
        ".librarian-management-section",
        ".librarian-card",
    ):
        panel = app.style[selector]
        assert panel["border"].startswith("1px solid var(--line)")
        assert panel["background_color"] == "var(--bg-panel)"
        assert panel["box_shadow"] == "var(--shadow-soft)"

    assert app.style[".admin-title-edit-form"]["background_color"] == "var(--bg-soft)"
    assert app.style[".librarian-form"]["background_color"] == "var(--bg-soft)"
    assert app.style[".signup-feedback-error"]["background_color"] == (
        "var(--danger-100)"
    )
    assert app.style[".signup-feedback-success"]["background_color"] == (
        "var(--success-100)"
    )
    assert app.style[
        ".content-section > [role='status'], .catalog-section > [role='status']"
    ]["background_color"] == "var(--brand-100)"
    assert app.style[
        ".content-section > [role='alert']:not(.signup-feedback)"
    ]["background_color"] == "var(--warning-100)"
    assert _contrast_ratio(tokens["--danger-700"], tokens["--danger-100"]) >= 4.5


def test_touch_targets_and_keyboard_accessibility_at_mobile_viewport():
    for selector in (
        "button, [role='button'], [role='checkbox'], [role='switch'], [role='radio']",
        ".campo",
        ".campo-select",
        ".campo-check-row",
        ".site-primary-nav a",
        ".site-menu-toggle",
        ".profile-menu-trigger, .accessibility-menu-trigger",
        ".profile-menu-item",
        ".admin-view-reset",
        ".a11y-controls button",
        ".catalog-card-link",
        ".footer-links a, .brand-link",
        ".skip-link",
    ):
        assert app.style[selector]["min_height"] == "2.75rem"

    mobile_styles = app.style["@media screen and (max-width: 48rem)"]
    assert mobile_styles["a"]["min_height"] == "2.75rem"
    assert mobile_styles["a"]["display"] == "inline-flex"
    assert mobile_styles[".site-header"]["grid_template_columns"] == (
        "minmax(0, 1fr)"
    )
    assert mobile_styles[".site-header"]["grid_template_areas"] == (
        '"logo" "nav" "busca" "acoes"'
    )
    assert mobile_styles[".site-menu-toggle"]["display"] == "none"
    assert app.style[":focus-visible"] == {
        "outline": "3px solid var(--brand-700)",
        "outline_offset": "3px",
    }


def test_shared_navigation_is_conditioned_on_private_session_profile():
    header = site_header()
    components = list(_components(header))
    navs = [
        component
        for component in components
        if type(component).__name__ == "Nav"
    ]

    assert len(navs) == 1
    assert all(
        nav.custom_attrs["aria-label"] == "Navegação principal"
        for nav in navs
    )
    nav_content = repr(navs[0])
    assert "active_navigation_role_rx_state_" in nav_content
    assert "Início" not in repr(header)
    assert "Meu perfil" not in repr(header)
    assert "Acessibilidade" in repr(header)
    assert "Aumentar fonte" in repr(header)
    assert "Modo escuro" in repr(header)


def test_accessibility_high_contrast_and_reduced_motion_styles():
    assert app.style[".a11y-high-contrast, .a11y-high-contrast *"]["color"] == (
        "#000000 !important"
    )
    assert app.style[".a11y-high-contrast a"]["color"] == "#00008b !important"
    assert app.style[
        ".a11y-high-contrast button, .a11y-high-contrast [role='button']"
    ]["color"] == "#ffffff !important"
    assert "0.01ms !important" in app.style[
        ".a11y-reduce-motion *, .a11y-reduce-motion *::before, .a11y-reduce-motion *::after"
    ]["transition_duration"]

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
    assert "home-catalog-search" not in repr(page)
    assert "form-busca-home" not in repr(page)
    assert getattr(button, "disabled", None) is None
    assert not any(component.id == "conteudo-login" for component in components)
    assert not any(
        component.id in {"login-email", "login-senha"}
        for component in components
    )


def test_focusable_field_and_button_have_visible_keyboard_focus_style():
    components = list(_components(login_page()))
    aliases = {component.alias for component in components}

    assert "RadixThemesTextField.Root" in aliases
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
    for selector in (".catalog-grid", ".admin-catalog-grid"):
        assert "11.25rem" in app.style[selector]["grid_template_columns"]
        assert "15rem" in app.style[selector]["grid_template_columns"]
    assert app.style[".catalog-card-cover"]["aspect_ratio"] == "0.72"


def test_motion_rules_have_reduced_motion_override():
    reduced = app.style["@media (prefers-reduced-motion: reduce)"]["*, *::before, *::after"]
    assert reduced["animation_duration"] == "0.01ms !important"
    assert reduced["animation_name"] == "none !important"
    assert reduced["transition_duration"] == "0.01ms !important"
    assert app.style[".app-shell"]["animation"] == "biblioteca-page-enter 300ms ease-out both"
    assert "@keyframes biblioteca-page-enter" in app.style
    assert "@keyframes biblioteca-profile-enter" in app.style
    assert "@keyframes biblioteca-hero-gradient" in app.style
    assert "@keyframes biblioteca-availability-pulse" in app.style
    assert app.style[".profile-menu[open] .profile-menu-content"]["animation"].startswith(
        "biblioteca-profile-enter"
    )
    assert app.style[".status-pill-success"]["animation"].startswith(
        "biblioteca-availability-pulse"
    )


def test_primary_actions_meet_wcag_contrast():
    dark = app.style[".a11y-shell.a11y-dark"]
    primary = app.style[".a11y-shell.a11y-dark .primary-cta"]
    button = app.style[".a11y-shell.a11y-dark .focus-demo-button"]

    assert primary["background_color"] == "var(--brand-700)"
    assert primary["color"] == "#183a4a"
    assert _contrast_ratio(primary["color"], dark["--brand-700"]) >= 4.5
    assert _contrast_ratio(dark["--brand-700"], dark["--bg-page"]) >= 3
    assert button["background_color"] == "var(--brand-700)"
    assert button["color"] == "#183a4a"
    assert _contrast_ratio(button["color"], dark["--brand-700"]) >= 4.5


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
    assert app.style[".a11y-shell.a11y-dark .focus-demo-button"][
        "color"
    ] == "#183a4a"


def test_text_fields_align_and_autofill_safely():
    inner = app.style[".signup-input input, .rt-TextFieldInput"]
    general = app.style[
        "input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput), textarea, select"
    ]
    autofill = app.style[
        ".signup-input input:-webkit-autofill, .signup-input input:autofill, input:-webkit-autofill, input:autofill"
    ]

    assert inner["height"] == "100%"
    assert inner["line_height"] == "normal"
    assert inner["padding"] == "0 0.75rem"
    assert general["height"] == "2.75rem"
    assert general["line_height"] == "normal"
    assert autofill["-webkit_text_fill_color"] == "var(--slate-900)"
    assert autofill["caret_color"] == "var(--slate-900)"
    assert "var(--bg-panel)" in autofill["box_shadow"]
    assert "9999s" in autofill["transition"]


def test_editing_controls_keep_external_border_only():
    editing = app.style[
        ".admin-title-edit-form input:not([type='hidden']):not([type='checkbox']), .admin-title-edit-form textarea, .admin-title-edit-form select"
    ]
    assert editing["border"] == "0"
    assert editing["background_color"] == "transparent"
    assert editing["box_shadow"] == "none"


def test_category_checkboxes_share_44px_row():
    from biblioteca_mais_nova.biblioteca_mais_nova import catalog_category_option

    category = rx.Var.create({"id": 3, "nome": "Ciências"})
    row = catalog_category_option(category)
    assert row.class_name == "category-checkbox-row"
    assert app.style[".category-checkbox-row"]["display"] == "inline-flex"
    assert app.style[".category-checkbox-row"]["align_items"] == "center"
    assert app.style[".category-checkbox-row"]["min_height"] == "2.75rem"


def test_text_controls_have_explicit_theme_aware_colors_and_focus():
    controls_style = app.style[
        "input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput), textarea, select"
    ]
    assert controls_style["color"] == "var(--slate-900)"
    assert controls_style["background_color"] == "var(--bg-panel)"
    assert app.style[".signup-input"]["color"] == "var(--slate-900)"
    assert app.style[".signup-input"]["background_color"] == "var(--bg-panel)"
    assert any(
        type(plugin).__name__ == "RadixThemesPlugin" and plugin.theme is not None
        for plugin in config.plugins
    )


def test_text_fields_have_single_container_border_and_visible_container_focus():
    container = app.style[".signup-input"]
    inner = app.style[".signup-input input, .rt-TextFieldInput"]
    focused_container = app.style[
        ".signup-input:focus-within, .rt-TextFieldRoot:focus-within, .rt-SelectTrigger:focus-visible, input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput):focus-visible, textarea:focus-visible, select:focus-visible"
    ]

    assert container["border"] == "1px solid var(--line)"
    assert container["border_radius"] == "0.5rem"
    assert container["min_height"] == "2.75rem"
    assert inner["border"] == "0 !important"
    assert inner["box_shadow"] == "none !important"
    assert inner["outline"] == "none !important"
    assert inner["background_color"] == "transparent !important"
    assert focused_container["outline"] == "3px solid var(--brand-700)"
    assert focused_container["outline_offset"] == "2px"


def test_form_controls_keep_keyboard_focus_visible():
    for selector in (
        "input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput), textarea, select",
        ".rt-SelectTrigger",
    ):
        assert app.style[selector]["min_height"] == "2.75rem"
        assert app.style[selector]["border"] == "1px solid var(--line)"
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
        "input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput), textarea, select",
        ".site-primary-nav a",
        ".site-menu-toggle",
        ".profile-menu-trigger",
        ".profile-menu-item",
        ".admin-view-reset",
        ".a11y-controls button",
        ".catalog-card-link",
        ".footer-links a, .brand-link",
        ".skip-link",
    ):
        assert app.style[selector]["min_height"] == "2.75rem"

    mobile_styles = app.style["@media screen and (max-width: 40rem)"]
    assert mobile_styles["a"]["min_height"] == "2.75rem"
    assert mobile_styles["a"]["display"] == "inline-flex"
    assert mobile_styles[".site-header"]["grid_template_columns"] == (
        "minmax(0, 1fr) auto"
    )
    assert mobile_styles[".site-menu-toggle"]["display"] == "inline-flex"
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

    assert len(navs) == 2
    assert all(
        nav.custom_attrs["aria-label"] == "Navegação principal"
        for nav in navs
    )
    nav_content = repr(navs[0])
    assert "active_navigation_role_rx_state_" in nav_content
    assert "Início" not in repr(header)
    assert "Meu perfil" not in repr(header)
    assert "Acessibilidade" not in repr(header)
    assert "Aumentar fonte" in repr(header)
    assert "Modo escuro" in repr(header)
    assert "aria-controls" in repr(header)


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

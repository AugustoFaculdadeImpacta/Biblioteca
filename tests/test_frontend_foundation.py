import reflex as rx

from biblioteca_mais_nova.biblioteca_mais_nova import app, index, site_header
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
    links = nav.children
    fields = [
        component
        for component in components
        if component.alias == "RadixThemesTextField.Root"
    ]
    button = next(
        component
        for component in components
        if component.alias == "RadixThemesButton"
    )

    assert nav.custom_attrs["aria-label"] == "Navegação principal"
    assert len(links) == 2
    nav_content = repr(links)
    assert "/catalogo" in nav_content
    assert "/cadastro" in nav_content
    assert "/login" in nav_content
    assert "/admin/acervo" in nav_content
    assert "Início" not in nav_content
    assert "Acessibilidade" in repr(page)
    assert r"Ver cat\\u00e1logo sem entrar" in repr(page)
    assert "#conteudo-home" in repr(page.children[0].children)
    assert "#conteudo-login" in repr(page)
    assert all(getattr(link, "tab_index", None) is None for link in links)
    assert {field.id for field in fields} >= {"login-email", "login-senha"}
    assert all(getattr(field, "disabled", None) is None for field in fields)
    assert getattr(button, "disabled", None) is None
    assert any(component.id == "conteudo-login" for component in components)


def test_focusable_field_and_button_have_visible_keyboard_focus_style():
    components = list(_components(index()))
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


def test_text_controls_have_explicit_theme_aware_colors_and_focus():
    controls_style = app.style[
        "input:not([type='checkbox']):not([type='radio']), textarea, select"
    ]
    assert controls_style["color"] == "var(--gray-12)"
    assert controls_style["background_color"] == "var(--gray-1)"
    assert app.style[".signup-input"]["color"] == "var(--gray-12)"
    assert app.style[".signup-input"]["background_color"] == "var(--gray-1)"
    assert any(
        type(plugin).__name__ == "RadixThemesPlugin" and plugin.theme is not None
        for plugin in config.plugins
    )


def test_authentication_forms_use_responsive_cards_and_distinct_feedback():
    assert app.style[".signup-section"]["width"] == "min(100%, 34rem)"
    assert app.style[".signup-section"]["background_color"] == "var(--gray-1)"
    assert app.style[".signup-form"]["width"] == "100%"
    assert app.style[".signup-feedback-error"]["color"] == "var(--red-12)"
    assert app.style[".signup-feedback-success"]["color"] == "var(--green-12)"


def test_shared_navigation_is_conditioned_on_private_session_profile():
    header = site_header()
    components = list(_components(header))
    nav = next(component for component in components if type(component).__name__ == "Nav")

    assert nav.custom_attrs["aria-label"] == "Navegação principal"
    nav_content = repr(nav)
    assert "is_authenticated_rx_state_" in nav_content
    assert "is_librarian_rx_state_" in nav_content
    assert "greeting_name_rx_state_" in nav_content
    assert "Início" not in nav_content
    assert "logout" in nav_content
    assert "Acessibilidade" in repr(header)
    assert "Aumentar fonte" in repr(header)
    assert "Alto contraste" in repr(header)
    assert "accessibility_reduce_motion_rx_state_" in repr(header)


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

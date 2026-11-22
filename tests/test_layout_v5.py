import re

import biblioteca_mais_nova.biblioteca_mais_nova as frontend


def _hex(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def _luminance(value: str) -> float:
    channels = []
    for channel in _hex(value):
        normalized = channel / 255
        channels.append(
            normalized / 12.92
            if normalized <= 0.04045
            else ((normalized + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter = max(_luminance(first), _luminance(second))
    darker = min(_luminance(first), _luminance(second))
    return (lighter + 0.05) / (darker + 0.05)


def test_header_contract_is_stable_without_action_classes():
    style = frontend.app.style
    header = style[".site-header"]
    brand = style[".brand-link"]
    nav = style[".site-primary-nav"]
    nav_link = style[".site-primary-nav a"]
    menu = style[".site-menu-toggle"]

    assert header["position"] == "sticky"
    assert header["top"] == "0"
    assert header["z_index"] == "50"
    assert header["display"] == "flex"
    assert header["flex_direction"] == "row"
    assert header["flex_wrap"] == "nowrap"
    assert header["align_items"] == "center"
    assert header["justify_content"] == "space-between"
    assert header["min_height"] == "4rem"
    assert header["padding"] == "0 1rem"
    assert header["background_color"] == "var(--bg-panel)"
    assert header["border_bottom"] == "1px solid var(--line)"

    assert brand["font_size"] == "1.25rem"
    assert brand["font_family"] == "Georgia, 'Times New Roman', serif"
    assert brand["white_space"] == "nowrap"
    assert brand["background"] == "transparent"
    assert brand["border"] == "none"
    assert brand["color"] == "var(--text)"

    assert nav["flex_wrap"] == "nowrap"
    assert nav_link["min_height"] == "2.75rem"
    assert nav_link["padding"] == "0.5rem 0.85rem"
    assert nav_link["border_radius"] == "999px"
    assert nav_link["background_color"] == "transparent"
    assert nav_link["color"] == "var(--text)"
    assert menu["display"] == "none"

    nav_page = repr(frontend.site_primary_nav())
    assert "site-nav-link" in nav_page
    assert "focus-demo-button" not in nav_page
    assert "nav-logout" not in nav_page
    assert "data-action-type" not in nav_page

    mobile = style["@media screen and (max-width: 48rem)"]
    assert mobile[".site-menu-toggle"]["display"] == "inline-flex"


def test_header_nav_and_footer_tokens_meet_text_contrast():
    style = frontend.app.style
    for theme_key in (
        ".a11y-shell",
        ".a11y-shell.a11y-dark",
    ):
        tokens = style[theme_key]
        text = tokens["--text"]
        panel = tokens["--bg-panel"]
        soft = tokens["--bg-soft"]
        brand = tokens["--brand-text"]
        brand_100 = tokens["--brand-100"]

        assert _contrast_ratio(text, panel) >= 4.5
        assert _contrast_ratio(text, soft) >= 4.5
        assert _contrast_ratio(brand, brand_100) >= 4.5

    footer = style[".footer-links a"]
    assert footer["background"] == "transparent"
    assert footer["border"] == "none"
    assert footer["color"] == "var(--text)"

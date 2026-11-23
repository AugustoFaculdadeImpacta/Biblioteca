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
    assert header["display"] == "grid"
    assert header["grid_template_columns"] == "auto minmax(18rem, 1fr) minmax(12rem, 22rem) auto"
    assert header["grid_template_areas"] == '"logo nav busca acoes"'
    assert header["align_items"] == "center"
    assert header["min_height"] == "4rem"
    assert header["padding"] == "0 1rem"
    assert header["background_color"] == "var(--bg-panel)"
    assert header["border_bottom"] == "1px solid var(--line)"

    assert brand["font_size"] == "1.25rem"
    assert "sans-serif" in brand["font_family"]
    assert brand["white_space"] == "nowrap"
    assert brand["background"] == "transparent"
    assert brand["border"] == "none"
    assert brand["color"] == "var(--text)"
    assert "brand-link-label" in repr(frontend.site_header())

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
    assert mobile[".site-menu-toggle"]["display"] == "none"
    assert mobile[".brand-link"]["min_width"] == "2.75rem"
    assert mobile[".brand-link-label"]["display"] == "none"
    assert mobile[".site-header"]["grid_template_areas"] == '"logo acoes" "nav nav" "busca busca"'
    assert style[
        ".site-header-actions > .profile-menu, .site-header-actions > .accessibility-menu"
    ]["flex"] == "0 0 auto"


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


def test_page_container_layout_is_stable():
    style = frontend.app.style

    assert style[".app-shell"]["padding"] == "0 1rem"
    assert style[".main-content"]["max_width"] == "75rem"
    assert style[".main-content"]["margin"] == "0 auto"
    assert style[".content-section"]["width"] == "100%"
    assert style[".content-section"]["max_width"] == "75rem"
    assert style[".catalog-grid"]["grid_template_columns"] == (
        "repeat(auto-fill, minmax(min(100%, 10rem), 12.5rem))"
    )
    assert style[".librarian-list"]["display"] == "flex"
    assert style[".librarian-list"]["flex_direction"] == "column"
    assert style[".signup-section"]["width"] == "min(100%, 34rem)"
    assert style[".signup-section"]["margin"] == "2rem auto"
    assert style[".admin-acervo-content"]["width"] == "100%"
    assert style[".admin-acervo-content"]["max_width"] == "75rem"


def test_delivery_layout_has_category_rails_and_product_detail():
    style = frontend.app.style
    home = repr(frontend.index())
    catalog = repr(frontend.public_catalog())
    detail = repr(frontend.public_catalog_detail())
    reservations = repr(frontend.student_reservations())

    assert "home-category-rail" in home
    assert "home-book-grid" in home
    assert "Sobre a biblioteca" not in home
    assert "Bem-vindo" in home
    assert "Estante de livros" in home
    assert "Novidades no acervo" in home
    assert "Categorias" in home
    assert "Como reservar" in home
    assert "Escolha" in home
    assert "Reserve" in home
    assert "Retire" in home
    assert "home-stat-band" in home
    assert "catalog-category-rail" in catalog
    assert "catalog-detail-card" in detail
    assert "Reservar" in detail
    assert "reservation-tabs" in reservations
    assert "Aguardando" in reservations
    assert "Aprovadas" in reservations
    assert "Emprestados" in reservations
    assert "Atrasos" in reservations

    assert style[".home-category-rail"]["overflow_x"] == "auto"
    assert style[".home-category-rail"]["flex_wrap"] == "nowrap"
    assert style[".home-category-rail"]["margin_top"] == "1rem"
    assert style[".home-stat-band"]["display"] == "flex"
    assert style[".home-stat-band"]["position"] == "static"
    assert style[".hero-layout"]["display"] == "grid"
    assert style[".hero-layout"]["align_items"] == "center"
    assert style[".hero-layout"]["grid_template_columns"] == "minmax(0, 1fr) auto"
    assert style[".hero-layout"]["gap"] == "1.5rem"
    assert style[".hero-layout"]["padding"] == "1.5rem"
    assert style["@media screen and (max-width: 48rem)"][".hero-layout"][
        "grid_template_columns"
    ] == "minmax(0, 1fr)"
    assert style[".content-section"]["margin"] == "0 auto 1.5rem"
    assert style["*"]["min_width"] == "0"
    assert style[".home-book-grid"]["grid_template_columns"] == (
        "repeat(auto-fill, minmax(min(100%, 10rem), 12.5rem))"
    )
    assert style[".catalog-detail-card"]["grid_template_columns"] == (
        "minmax(12rem, 18rem) minmax(0, 1fr)"
    )


def test_home_flow_containers_have_no_fixed_height_or_positioning():
    style = frontend.app.style
    seletores = (
        ".home-hero",
        ".hero-layout",
        ".hero-copy-wrap",
        ".hero-copy",
        ".home-stat-band",
        ".home-profile-summary",
        ".home-summary-metrics",
        ".home-book-section",
        ".home-book-grid",
        ".home-category-section",
        ".home-category-rail",
        ".home-category-chip",
        ".home-reservation-section",
        ".home-reservation-steps",
    )

    for seletor in seletores:
        regra = style[seletor]
        assert "height" not in regra, seletor
        assert "max_height" not in regra, seletor
        assert regra.get("overflow") != "hidden", seletor
        assert regra.get("position") not in {"absolute", "fixed"}, seletor
        assert "transform" not in regra, seletor
        for nome in ("margin", "margin_top", "margin_right", "margin_bottom", "margin_left"):
            valor = str(regra.get(nome, ""))
            assert not re.search(r"-\d", valor), (seletor, nome, valor)
    assert ".hero-stat-grid" not in style
    assert ".home-category-shelf" not in style


def test_primary_pages_keep_content_in_normal_flow():
    style = frontend.app.style
    content_selectors = (
        ".content-section",
        ".catalog-section",
        ".catalog-controls",
        ".catalog-grid",
        ".catalog-detail-visual",
        ".catalog-detail-card",
        ".student-library-section",
        ".student-reservations-heading",
        ".reservation-tabs",
        ".admin-catalog-section",
        ".admin-acervo-content",
        ".admin-catalog-grid",
        ".admin-title-card",
        ".admin-title-row",
        ".admin-title-data",
        ".librarian-management-section",
        ".operational-counts",
        ".librarian-list",
        ".librarian-card",
        ".signup-section",
        ".signup-form",
        ".signup-feedback",
        ".auth-tabs",
    )

    for seletor in content_selectors:
        regra = style[seletor]
        assert "height" not in regra, seletor
        assert "max_height" not in regra, seletor
        assert regra.get("overflow") != "hidden", seletor
        assert regra.get("position") not in {"absolute", "fixed"}, seletor
        assert "transform" not in regra, seletor
        for nome in ("margin", "margin_top", "margin_right", "margin_bottom", "margin_left"):
            valor = str(regra.get(nome, ""))
            assert not re.search(r"-\d", valor), (seletor, nome, valor)

    mobile = style["@media screen and (max-width: 48rem)"]
    assert style[".catalog-detail-card"]["display"] == "grid"
    assert mobile[".catalog-detail-card"]["grid_template_columns"] == (
        "minmax(0, 1fr)"
    )
    assert mobile[".catalog-detail-actions"]["width"] == "100%"
    assert "position" not in mobile[".catalog-detail-actions"]
    assert mobile[".site-header > .site-primary-nav"].get("overflow_y") != "hidden"
    assert "height" not in style[
        ".admin-catalog-cover-image, .admin-catalog-cover-fallback"
    ]
    assert "overflow" not in style[".admin-catalog-cover-fallback"]

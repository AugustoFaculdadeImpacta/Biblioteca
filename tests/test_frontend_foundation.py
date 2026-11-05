import reflex as rx

from biblioteca_mais_nova.biblioteca_mais_nova import app, index


def _components(component: rx.Component):
    yield component
    for child in component.children:
        if isinstance(child, rx.Component):
            yield from _components(child)


def test_index_renders_navigable_application_shell():
    page = index()
    components = list(_components(page))
    nav = next(component for component in components if type(component).__name__ == "Nav")
    links = nav.children
    field = next(
        component
        for component in components
        if component.alias == "RadixThemesTextField.Root"
    )
    button = next(
        component
        for component in components
        if component.alias == "RadixThemesButton"
    )

    assert nav.custom_attrs["aria-label"] == "Navegação principal"
    assert len(links) == 5
    assert "#inicio" in repr(links)
    assert "#acessibilidade" in repr(links)
    assert "/cadastro" in repr(links)
    assert "/login" in repr(links)
    assert "/admin/acervo" in repr(links)
    assert "#conteudo" in repr(page.children[0].children)
    assert all(getattr(link, "tab_index", None) is None for link in links)
    assert field.read_only._var_value is True
    assert getattr(field, "disabled", None) is None
    assert getattr(button, "disabled", None) is None
    assert any(component.id == "inicio" for component in components)
    assert any(component.id == "conteudo" for component in components)


def test_focusable_field_and_button_have_visible_keyboard_focus_style():
    components = list(_components(index()))
    aliases = {component.alias for component in components}

    assert "RadixThemesTextField.Root" in aliases
    assert "RadixThemesButton" in aliases
    assert app.style[":focus-visible"] == {
        "outline": "3px solid #005fcc",
        "outline_offset": "3px",
    }

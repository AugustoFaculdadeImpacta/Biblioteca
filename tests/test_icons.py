import ast
from pathlib import Path

from biblioteca_mais_nova.icons import (
    ACOES,
    SELOS,
    atributos_acao,
    conteudo_acao,
    conteudo_selo,
)


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "biblioteca_mais_nova" / "biblioteca_mais_nova.py"


def _action_calls(source: str) -> list[ast.Call]:
    tree = ast.parse(source)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"button", "link"}
        and ast.unparse(node.func.value) in {"rx", "rx.el"}
    ]


def test_action_emojis_are_unique_and_have_visual_categories():
    emojis = [action.emoji for action in ACOES.values()]

    assert len(emojis) == len(set(emojis))
    assert all(
        len(action.rotulo.split()) <= 3
        for key, action in ACOES.items()
        if key != "restaurar_visao"
    )
    assert {action.tipo for action in ACOES.values()} == {
        "confirmar",
        "perigo",
        "navegar",
        "atencao",
    }


def test_action_helpers_include_accessible_icon_and_button_metadata():
    component = conteudo_acao("desativar")
    icon = component.children[0]
    label = component.children[1]
    attrs = atributos_acao("desativar")

    assert icon.custom_attrs["aria-hidden"] == "true"
    assert icon.class_name == "emoji-acao"
    assert attrs["title"] == "Desativar"
    assert attrs["aria_label"] == "Desativar"
    assert attrs["data_action_type"] == "perigo"
    assert label.class_name == "rotulo-acao"


def test_route_notice_close_keeps_its_plain_label_and_shared_action_metadata():
    source = APP_PATH.read_text(encoding="utf-8")

    assert 'conteudo_acao("fechar_aviso")' in source
    assert 'atributos_acao("fechar_aviso")' in source
    assert ACOES["fechar_aviso"].rotulo == "Fechar aviso"
    assert ACOES["fechar_aviso"].emoji == ""


def test_theme_action_marks_its_dynamic_emoji_and_label():
    component = conteudo_acao("tema")
    icon = component.children[0]
    label = component.children[1]

    assert icon.custom_attrs["data-appearance-theme-emoji"] == "true"
    assert label.custom_attrs["data-appearance-theme-label"] == "true"


def test_status_seals_render_an_aria_hidden_emoji():
    for key in SELOS:
        icon = conteudo_selo(key).children[0]

        assert icon.custom_attrs["aria-hidden"] == "true"
        assert icon.class_name == "emoji-selo"


def test_every_button_and_link_uses_the_shared_action_helpers():
    source = APP_PATH.read_text(encoding="utf-8")
    calls = _action_calls(source)

    assert calls
    for call in calls:
        assert call.args, f"Controle sem rótulo na linha {call.lineno}"
        class_keyword = next(
            (
                keyword.value
                for keyword in call.keywords
                if keyword.arg == "class_name"
            ),
            None,
        )
        class_names = (
            ast.literal_eval(class_keyword)
            if isinstance(class_keyword, ast.Constant)
            else ""
        )
        if isinstance(class_names, str) and (
            class_names in {
            "brand-link",
            "site-nav-link",
            "footer-link",
            "home-category-chip",
            "home-view-more",
            "catalog-card-link",
            "appearance-font-button",
            "appearance-switch",
            "auth-tab",
            }
            or class_names.startswith("auth-tab ")
        ):
            continue
        content = call.args[0]
        assert (
            isinstance(content, ast.Call)
            and isinstance(content.func, ast.Name)
            and content.func.id == "conteudo_acao"
        ), f"Controle sem ícone compartilhado na linha {call.lineno}"

        action_key = content.args[0]
        attrs = next(
            (
                keyword.value
                for keyword in call.keywords
                if keyword.arg is None
                and isinstance(keyword.value, ast.Call)
                and isinstance(keyword.value.func, ast.Name)
                and keyword.value.func.id == "atributos_acao"
            ),
            None,
        )
        assert attrs is not None, f"Controle sem metadados na linha {call.lineno}"
        assert ast.dump(attrs.args[0]) == ast.dump(action_key), (
            f"Chaves divergentes na linha {call.lineno}"
        )


def test_title_deactivation_keeps_inline_confirmation_actions():
    source = APP_PATH.read_text(encoding="utf-8")
    action_keys = {
        node.args[0].value
        for call in _action_calls(source)
        if call.args
        and isinstance(call.args[0], ast.Call)
        and isinstance(call.args[0].func, ast.Name)
        and call.args[0].func.id == "conteudo_acao"
        for node in [call.args[0]]
        if node.args and isinstance(node.args[0], ast.Constant)
    }

    assert {"confirmar_desativacao", "nao_confirmar"} <= action_keys
    assert ACOES["confirmar_desativacao"].rotulo == "Sim, desativar"
    assert ACOES["nao_confirmar"].rotulo == "Não"


def test_librarian_deactivation_requires_inline_confirmation():
    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    card_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "librarian_card"
    )
    card_source = ast.get_source_segment(source, card_function)

    assert 'State.librarian_management_confirm_id == librarian["id"]' in card_source
    assert "State.request_librarian_deactivation" in card_source
    assert "State.cancel_librarian_deactivation" in card_source
    assert 'conteudo_acao("confirmar_desativacao")' in card_source
    assert 'conteudo_acao("nao_confirmar")' in card_source


def test_icon_guide_restricts_decorative_emojis_to_semantic_places():
    guide = (ROOT / "docs" / "guia-de-icones.md").read_text(encoding="utf-8")

    assert "Títulos de seção" in guide
    assert "ações principais" in guide
    assert "selos de estado" in guide

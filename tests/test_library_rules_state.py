import asyncio
import json
from uuid import uuid4

import reflex as rx
import pytest
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.library_rules import DEFAULT_LIBRARY_RULES
from biblioteca_mais_nova.xano_client import XanoResponseError


def _readable(component: rx.Component) -> str:
    serialized = json.loads(repr(component))
    values = []

    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "contents" and isinstance(child, str):
                    try:
                        values.append(json.loads(child))
                    except json.JSONDecodeError:
                        values.append(child)
                else:
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(serialized)
    return " ".join(map(str, values))


def _components_named(component: rx.Component, name: str) -> list[dict]:
    serialized = json.loads(repr(component))
    matches = []

    def collect(value):
        if isinstance(value, dict):
            if value.get("name", "").strip('"') == name:
                matches.append(value)
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(serialized)
    return matches


def test_rules_page_contains_contract_fields_and_native_controls():
    page = frontend.library_rules_page()
    readable = _readable(page)

    for label in (
        "Regras da biblioteca",
        "Limite de empréstimos ativos",
        "Limite de pedidos em aberto",
        "Permitir pedido com reserva ativa",
        "Bloquear com atraso",
        "Exigir autorização bibliotecária",
        "Prazo de empréstimo (dias)",
        "Prazo de retirada (horas)",
        "Salvar regras",
        "Descartar mudanças",
    ):
        assert label in readable
    input_props = [
        prop
        for component in _components_named(page, "input")
        for prop in component["props"]
    ]
    assert sum('type:"number"' in prop for prop in input_props) == 4
    assert sum('type:"checkbox"' in prop for prop in input_props) == 3
    assert frontend.app._unevaluated_pages["regras"].route == "regras"


def test_only_real_admin_can_load_rules_but_any_admin_view_is_allowed(
    monkeypatch,
):
    calls = []

    async def get_rules(token):
        calls.append(token)
        return {
            **DEFAULT_LIBRARY_RULES,
            "atualizado_em": "2026-11-26T14:00:00Z",
            "atualizado_por": "Admin",
        }

    monkeypatch.setattr(frontend, "get_library_rules", get_rules)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"library-rules-guard-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-student", "estudante")
            redirect = await state.load_library_rules()
            assert "'/'" in repr(redirect)
            assert calls == []

        async with frontend.app.modify_state(
            BaseStateToken(ident=f"library-rules-admin-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            state.set_admin_view_mode("estudante")
            await state.load_library_rules()
            assert calls == ["token-admin"]
            assert state._session_profile == "admin"
            assert state.admin_view_mode == "estudante"
            assert state.library_rules_loaded is True
            assert state.library_rules_updated_at == "2026-11-26T14:00:00Z"
            assert state.library_rules_updated_by == "Admin"

    asyncio.run(verify())


@pytest.mark.parametrize("status_code", [403, 404])
def test_unpublished_rules_show_defaults_read_only(monkeypatch, status_code):
    async def unavailable(_token):
        raise XanoResponseError(status_code)

    monkeypatch.setattr(frontend, "get_library_rules", unavailable)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"library-rules-missing-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            await state.load_library_rules()
            assert state.library_rules_loaded is True
            assert state.library_rules_read_only is True
            assert state.library_rules_active_loan_limit == 3.0
            assert state.library_rules_open_request_limit == 3.0
            assert state.library_rules_loan_period_days == 14.0
            assert state.library_rules_message == (
                "As regras ainda não foram publicadas no Xano. "
                "Veja docs/publicacao-xano-regras.md."
            )

    asyncio.run(verify())


def test_rules_form_validates_without_sending_and_discard_restores_values(
    monkeypatch,
):
    updates = []

    async def update_rules(rules, _token):
        updates.append(rules)
        return {**rules}

    monkeypatch.setattr(frontend, "update_library_rules", update_rules)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"library-rules-validation-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            state._apply_library_rules(DEFAULT_LIBRARY_RULES)
            state.library_rules_active_loan_limit = 21.0

            await state.save_library_rules()
            assert updates == []
            assert state.library_rules_has_error is True
            assert "limite_emprestimos_ativos" in state.library_rules_message
            assert state.library_rules_active_loan_limit == 21.0

            state.discard_library_rules_changes()
            assert state.library_rules_active_loan_limit == 3.0
            assert state.library_rules_has_error is False
            assert state.library_rules_message == ""

    asyncio.run(verify())


def test_rules_save_sends_clean_fields_and_preserves_values_on_server_error(
    monkeypatch,
):
    updates = []

    async def reject_update(rules, _token):
        updates.append(rules)
        raise XanoResponseError(500, "Regra rejeitada")

    monkeypatch.setattr(frontend, "update_library_rules", reject_update)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"library-rules-save-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-admin", "admin")
            state._apply_library_rules(DEFAULT_LIBRARY_RULES)
            state.library_rules_open_request_limit = 5.0

            await state.save_library_rules()

            assert updates == [
                {
                    **DEFAULT_LIBRARY_RULES,
                    "limite_pedidos_em_aberto": 5,
                }
            ]
            assert state.library_rules_open_request_limit == 5.0
            assert state.library_rules_has_error is True
            assert "HTTP 500" in state.library_rules_message

    asyncio.run(verify())

import asyncio
import json
from uuid import uuid4

from reflex import State as ReflexState
from reflex.istate.manager.token import BaseStateToken

from biblioteca_mais_nova.biblioteca_mais_nova import State, app


def test_session_token_stays_private_and_isolated_between_sessions(caplog):
    app()
    session_a = f"privacy-test-{uuid4()}"
    session_b = f"privacy-test-{uuid4()}"
    token_a = "token-falso-sessao-a"
    token_b = "token-falso-sessao-b"

    async def verify_sessions():
        async with app.modify_state(
            BaseStateToken(ident=session_a, cls=ReflexState)
        ) as root_a:
            state_a = await root_a.get_state(State)
            state_a._store_session_token(token_a)
            delta_a = await root_a._get_resolved_delta()

        async with app.modify_state(
            BaseStateToken(ident=session_b, cls=ReflexState)
        ) as root_b:
            state_b = await root_b.get_state(State)
            assert state_b._read_session_token() is None
            state_b._store_session_token(token_b)
            delta_b = await root_b._get_resolved_delta()

        async with app.modify_state(
            BaseStateToken(ident=session_a, cls=ReflexState)
        ) as root_a:
            state_a = await root_a.get_state(State)
            assert state_a._read_session_token() == token_a

        assert token_a not in json.dumps(delta_a, default=str)
        assert token_b not in json.dumps(delta_b, default=str)
        assert "is_authenticated" in json.dumps(delta_a, default=str)
        assert "is_authenticated" in json.dumps(delta_b, default=str)
        assert "_session_token" not in State.base_vars
        assert "_session_token" not in State.computed_vars

    asyncio.run(verify_sessions())
    assert token_a not in caplog.text
    assert token_b not in caplog.text

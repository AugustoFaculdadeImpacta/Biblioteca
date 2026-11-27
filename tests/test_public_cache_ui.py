import asyncio
import concurrent.futures
from uuid import uuid4

import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend
from biblioteca_mais_nova.xano_client import XanoResponseError


def _entry(title: str) -> dict:
    return {
        "titulo": {
            "id": 31,
            "titulo": title,
            "autores": "Autoria",
            "ativo": True,
        },
        "categorias": [],
        "exemplares_disponiveis": 1,
    }


def _finished_prefetch(results=None):
    future = concurrent.futures.Future()
    future.set_result(results or {})
    return future


def test_catalog_load_event_applies_saved_copy_before_background_refresh(
    monkeypatch,
):
    cached_titles = [_entry("Livro salvo")]
    monkeypatch.setattr(
        frontend,
        "load_saved_public_catalog",
        lambda: (cached_titles, [{"id": 3, "nome": "Literatura"}]),
    )
    monkeypatch.setattr(frontend, "_schedule_public_prefetch", _finished_prefetch)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"saved-catalog-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.load_public_catalog_cached()
            assert state.public_catalog_entries == cached_titles
            assert state.public_catalog_categories == [
                {"id": 3, "nome": "Literatura"}
            ]
            assert state.public_catalog_pending is False
            assert state.public_catalog_message == "Atualizando…"

    asyncio.run(verify())


def test_detail_load_event_applies_saved_copy_before_background_refresh(
    monkeypatch,
):
    entry = _entry("Livro salvo")
    categories = [{"id": 3, "nome": "Literatura"}]
    monkeypatch.setattr(
        frontend,
        "load_saved_public_catalog",
        lambda: ([entry], categories),
    )
    monkeypatch.setattr(
        frontend,
        "_schedule_public_prefetch",
        _finished_prefetch,
    )

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"saved-detail-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.router.page.params["titulo_id"] = "31"
            state.load_public_catalog_detail_cached()
            assert state.public_catalog_detail["titulo"] == "Livro salvo"
            assert state.public_catalog_detail_pending is False
            assert state.public_catalog_detail_message == "Atualizando…"
            assert state.public_catalog_using_saved_copy is True

    asyncio.run(verify())


def test_catalog_background_refresh_replaces_saved_copy(monkeypatch):
    monkeypatch.setattr(
        frontend,
        "_schedule_public_prefetch",
        lambda: _finished_prefetch(
            {
                "titulos": [_entry("Livro atualizado")],
                "categorias": [{"id": 4, "nome": "Ciência"}],
            }
        ),
    )

    async def unexpected_request():
        raise AssertionError("A atualização não deve duplicar a pré-carga.")

    monkeypatch.setattr(frontend, "list_public_titles", unexpected_request)
    monkeypatch.setattr(frontend, "list_categories", unexpected_request)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"refresh-catalog-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.public_catalog_entries = [_entry("Livro salvo")]
            state._public_titles_cached = True
            await state._refresh_public_catalog_data()
            assert state.public_catalog_entries[0]["titulo"]["titulo"] == (
                "Livro atualizado"
            )
            assert state.public_catalog_categories[0]["nome"] == "Ciência"
            assert state.public_catalog_message == ""
            assert state.public_catalog_using_saved_copy is False

    asyncio.run(verify())


def test_catalog_429_keeps_saved_copy_and_shows_stale_notice(monkeypatch):
    limited = XanoResponseError(429)
    monkeypatch.setattr(
        frontend,
        "_schedule_public_prefetch",
        lambda: _finished_prefetch(
            {"titulos": limited, "categorias": limited}
        ),
    )

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"limited-catalog-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.public_catalog_entries = [_entry("Livro salvo")]
            state._public_titles_cached = True
            state.public_catalog_categories = [{"id": 3, "nome": "Literatura"}]
            state._public_categories_cached = True
            await state._refresh_public_catalog_data()
            assert state.public_catalog_entries[0]["titulo"]["titulo"] == (
                "Livro salvo"
            )
            assert state.public_catalog_categories[0]["nome"] == "Literatura"
            assert state.public_catalog_has_error is False
            assert state.public_catalog_message == (
                "Mostrando a última lista salva"
            )

    asyncio.run(verify())


def test_detail_refresh_reuses_prefetched_categories(monkeypatch):
    detail_calls = []
    entry = _entry("Livro atualizado")
    categories = [{"id": 4, "nome": "Ciência"}]
    monkeypatch.setattr(
        frontend,
        "_schedule_public_prefetch",
        lambda: _finished_prefetch(
            {"titulos": [entry], "categorias": categories, "regras": {}}
        ),
    )

    async def detail(title_id):
        detail_calls.append(title_id)
        return entry

    async def unexpected_request():
        raise AssertionError("A tela não deve repetir a pré-carga.")

    monkeypatch.setattr(frontend, "get_public_title", detail)
    monkeypatch.setattr(frontend, "list_categories", unexpected_request)

    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(ident=f"detail-refresh-{uuid4()}", cls=rx.State)
        ) as root:
            state = await root.get_state(frontend.State)
            state.router.page.params["titulo_id"] = "31"
            await state._refresh_public_catalog_detail_data()
            assert state.public_catalog_detail["titulo"] == "Livro atualizado"
            assert state.public_catalog_categories == categories
            assert state.public_catalog_detail_pending is False
            assert detail_calls == [31]

    asyncio.run(verify())


def test_public_prefetch_runs_once_for_repeated_requests(monkeypatch):
    calls = []

    async def titles():
        calls.append("titulos")
        await asyncio.sleep(0)
        return []

    async def categories():
        calls.append("categorias")
        await asyncio.sleep(0)
        return []

    async def rules():
        calls.append("regras")
        await asyncio.sleep(0)
        return {}

    monkeypatch.setattr(frontend, "list_public_titles", titles)
    monkeypatch.setattr(frontend, "list_categories", categories)
    monkeypatch.setattr(frontend, "get_library_rules", rules)
    frontend._reset_public_prefetch_for_tests()

    async def verify():
        first = frontend._schedule_public_prefetch()
        second = frontend._schedule_public_prefetch()
        assert first is second
        await asyncio.wrap_future(first)
        assert sorted(calls) == ["categorias", "regras", "titulos"]

    try:
        asyncio.run(verify())
    finally:
        frontend._reset_public_prefetch_for_tests()

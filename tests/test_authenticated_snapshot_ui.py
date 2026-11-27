import asyncio
import time
from uuid import uuid4

import reflex as rx
from reflex.istate.manager.token import BaseStateToken

import biblioteca_mais_nova.biblioteca_mais_nova as frontend


def test_student_library_uses_recent_copy_before_background_refresh():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"student-list-cache-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-estudante", "estudante")
            state._student_library_loaded_at = time.monotonic()
            state.student_library_requests = [
                {
                    "id": 7,
                    "titulo": "Pedido salvo",
                    "estado": "Aguardando confirmação da retirada",
                }
            ]

            refresh = state.load_student_library_cached()

            assert state.student_library_requests == [
                {
                    "id": 7,
                    "titulo": "Pedido salvo",
                    "estado": "Aguardando confirmação da retirada",
                }
            ]
            assert state.student_library_pending is False
            assert "refresh_student_library" in repr(refresh)
            state._student_library_loaded_at = time.monotonic() - 21
            stale_refresh = state.load_student_library_cached()
            assert "load_student_library" in repr(stale_refresh)

    asyncio.run(verify())


def test_staff_lists_use_recent_copy_before_background_refresh():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"staff-list-cache-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-bibliotecario", "bibliotecario")
            state._circulation_loaded_at = time.monotonic()
            state.circulation_requests = [{"id": 8, "estado": "pendente"}]

            refresh = state.load_staff_reservations_dashboard_cached()

            assert state.circulation_requests == [
                {"id": 8, "estado": "pendente"}
            ]
            assert state.circulation_pending is False
            assert "refresh_circulation_lists" in repr(refresh)

    asyncio.run(verify())


def test_admin_catalog_uses_recent_copy_before_background_refresh():
    async def verify():
        async with frontend.app.modify_state(
            BaseStateToken(
                ident=f"admin-catalog-cache-{uuid4()}",
                cls=rx.State,
            )
        ) as root:
            state = await root.get_state(frontend.State)
            state._store_session("token-bibliotecario", "bibliotecario")
            state._admin_catalog_loaded_at = time.monotonic()
            state.admin_catalog_entries = [
                {
                    "titulo": {
                        "id": 12,
                        "titulo": "Livro salvo",
                        "autores": "Autoria",
                        "ativo": True,
                    },
                    "categorias": [],
                    "exemplares_disponiveis": 1,
                    "exemplares": [],
                }
            ]

            refresh = state.load_catalog_page_cached()

            assert state.admin_catalog_entries[0]["titulo"]["titulo"] == (
                "Livro salvo"
            )
            assert state.admin_catalog_pending is False
            assert "refresh_admin_catalog" in repr(refresh)

    asyncio.run(verify())

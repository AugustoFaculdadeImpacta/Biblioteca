"""Estrutura inicial da interface da Biblioteca."""

import asyncio
import unicodedata
import os
from urllib.parse import quote
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Awaitable, Callable

import reflex as rx

from biblioteca_mais_nova.covers import gerar_capa_svg
from biblioteca_mais_nova.capas_isbn import (
    normalizar_texto,
    resolver_capa_por_titulo,
    resolver_capa_url,
)
from biblioteca_mais_nova.icons import (
    atributos_acao,
    conteudo_acao,
    conteudo_selo,
)

from biblioteca_mais_nova.signup import (
    SignupValidationError,
    build_signup_payload,
    signup_error_message,
    submit_student_signup,
)
from biblioteca_mais_nova.login import (
    LoginValidationError,
    build_login_payload,
    login_error_message,
    submit_login as authenticate,
)
from biblioteca_mais_nova.catalog import (
    AdminCatalogDisplayEntry,
    AdminCatalogEntry,
    CatalogValidationError,
    associate_category,
    build_title_payload,
    catalog_error_message,
    category_contains_title,
    create_copy,
    create_title,
    get_public_title,
    invalidar_cache_categorias_publicas,
    list_admin_catalog,
    list_categories,
    list_public_titles,
    invalidar_cache_titulos_publicos,
    update_title,
    invalidar_cache_catalogo_publico,
)
from biblioteca_mais_nova.seed_data import TITULOS as TITULOS_EXEMPLO
from biblioteca_mais_nova.circulation import (
    AdminReservation,
    LoanRequest,
    list_admin_loans,
    list_admin_requests,
    list_admin_reservations,
    list_my_loans,
    list_my_requests,
    list_my_reservations,
    offer_next_reservation,
    refuse_loan_request,
    refuse_reservation,
    register_loan_return,
    register_request_pickup,
    register_reservation_pickup,
    request_title_loan,
    reservation_request_error_message,
)
from biblioteca_mais_nova.user_admin import (
    UserAdminValidationError,
    build_librarian_payload,
    create_librarian,
    list_librarians,
    set_librarian_active,
    user_admin_error_message,
)
from biblioteca_mais_nova.staff_reservations import (
    StaffReservationValidationError,
    create_staff_reservation,
    find_student_by_email,
    staff_reservation_error_message,
)
from biblioteca_mais_nova.xano_diagnostics import (
    XanoDiagnosticResult,
    diagnose_xano,
    format_xano_diagnostic_report,
)
from biblioteca_mais_nova.xano_client import (
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    XanoTimeoutError,
    XanoWriteSucceededWithUnreadableResponse,
    contexto_evento_xano,
    diagnosticar_pagina_xano,
    registrar_excecao_backend,
    registrar_resultado_xano,
)


def _timestamp_is_past(
    value: str | int | float | None,
    now: datetime,
) -> bool:
    if value is None or value == 0:
        return False
    if type(value) in {int, float}:
        deadline = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        deadline = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
    return deadline < now


def _diagnostico_desativacao(
    *,
    title_id: int,
    status_code: int,
    body_keys: list[str],
    response_keys: list[str],
    active_sent: bool,
    active_response: object,
    active_reloaded: object,
) -> None:
    if os.environ.get("BIBLIOTECA_DIAGNOSTICO") != "1":
        return
    print(
        "desativacao-titulo "
        f"metodo=PATCH caminho=/catalogo/titulos/{title_id} "
        f"chaves_corpo={','.join(body_keys)} "
        f"status={status_code} "
        f"chaves_resposta={','.join(response_keys)} "
        f"ativo_enviado={active_sent!r} "
        f"ativo_resposta={active_response!r} "
        f"ativo_releitura={active_reloaded!r}",
    )


class State(rx.State):
    is_authenticated: bool = False
    mobile_navigation_open: bool = False
    signup_message: str = ""
    signup_success_message: str = ""
    signup_has_error: bool = False
    login_message: str = ""
    login_has_error: bool = False
    catalog_message: str = ""
    catalog_has_error: bool = False
    catalog_categories: list[dict[str, Any]] = []
    catalog_categories_skipped: int = 0
    selected_category_ids: list[int] = []
    catalog_categories_pending: bool = False
    catalog_title_created: bool = False
    catalog_created_codes: list[str] = []
    catalog_needs_manual_check: bool = False
    admin_catalog_entries: list[AdminCatalogEntry] = []
    admin_catalog_skipped: int = 0
    admin_catalog_message: str = ""
    admin_catalog_has_error: bool = False
    admin_catalog_pending: bool = False
    admin_catalog_needs_manual_check: bool = False
    admin_catalog_confirm_title_id: int | None = None
    admin_catalog_title_action_title_id: int | None = None
    admin_catalog_title_action_message: str = ""
    admin_catalog_title_action_error: bool = False
    admin_catalog_search: str = ""
    admin_catalog_visible_limit: int = 10
    admin_catalog_show_inactive: bool = False
    admin_catalog_edit_title_id: int | None = None
    admin_catalog_copy_title_id: int | None = None
    admin_catalog_new_title_open: bool = False
    connection_test_pending: bool = False
    connection_test_message: str = ""
    connection_test_has_error: bool = False
    connection_diagnostic_results: list[XanoDiagnosticResult] = []
    connection_diagnostic_report: str = ""
    example_seed_pending: bool = False
    example_seed_confirming: bool = False
    example_seed_preview_ready: bool = False
    example_seed_preview_create_count: int = 0
    example_seed_preview_existing_count: int = 0
    example_seed_missing_categories: list[str] = []
    example_seed_progress: int = 0
    example_seed_created: int = 0
    example_seed_ignored: int = 0
    example_seed_errors: int = 0
    example_seed_message: str = ""
    example_seed_has_error: bool = False
    example_seed_resume_index: int = 1
    example_seed_can_resume: bool = False
    _session_token: str = ""
    _session_profile: str = ""
    _session_name: str = ""
    _session_email: str = ""
    _admin_view_mode: str = ""
    _catalog_title_id: int | None = None
    _pending_category_ids: list[int] = []
    _uncertain_category_ids: list[int] = []
    _catalog_title_uncertain: bool = False
    _catalog_copy_uncertain: bool = False
    public_catalog_entries: list[dict[str, Any]] = []
    public_catalog_categories: list[dict[str, Any]] = []
    public_catalog_categories_skipped: int = 0
    public_catalog_cover_resolutions: dict[str, str] = {}
    public_catalog_message: str = ""
    public_catalog_has_error: bool = False
    public_catalog_pending: bool = True
    home_titles_pending: bool = True
    home_categories_pending: bool = True
    home_titles_has_error: bool = False
    home_categories_has_error: bool = False
    home_titles_error_message: str = ""
    home_categories_error_message: str = ""
    public_catalog_search: str = ""
    public_catalog_category_id: str = ""
    public_catalog_only_available: bool = False
    public_catalog_sort: str = "asc"
    public_catalog_detail: dict[str, Any] = {}
    public_catalog_detail_message: str = ""
    public_catalog_detail_has_error: bool = False
    public_catalog_detail_not_found: bool = False
    public_catalog_detail_pending: bool = False
    student_library_pending: bool = True
    student_library_message: str = ""
    student_library_has_error: bool = False
    student_library_requires_login: bool = False
    student_library_loans: list[dict[str, Any]] = []
    student_library_requests: list[dict[str, Any]] = []
    student_library_reservations: list[dict[str, Any]] = []
    student_library_skipped: int = 0
    student_reservation_tab: str = "aguardando"
    student_request_pending: bool = False
    student_request_uncertain_title_id: int | None = None
    _student_request_uncertain_reference: str = ""
    _student_library_manual_retry: bool = False
    student_request_message: str = ""
    student_request_has_error: bool = False
    librarian_management_pending: bool = False
    librarian_management_message: str = ""
    librarian_management_has_error: bool = False
    librarian_management_success: bool = False
    librarian_management_search: str = ""
    librarian_management_confirm_id: int | None = None
    managed_librarians: list[dict[str, Any]] = []
    librarian_management_skipped: int = 0
    staff_reservation_pending: bool = False
    staff_reservation_message: str = ""
    staff_reservation_has_error: bool = False
    staff_reservation_email: str = ""
    staff_reservation_student: dict[str, Any] = {}
    staff_reservation_title_options: list[dict[str, str]] = []
    staff_reservation_skipped: int = 0
    staff_reservation_title_id: str = ""
    staff_reservation_needs_manual_check: bool = False
    circulation_pending: bool = False
    circulation_active_tab: str = "pedidos"
    circulation_message: str = ""
    circulation_has_error: bool = False
    circulation_needs_manual_check: bool = False
    circulation_requests: list[LoanRequest] = []
    circulation_reservations: list[AdminReservation] = []
    circulation_loans: list[dict[str, Any]] = []
    circulation_catalog_entries: list[AdminCatalogEntry] = []
    circulation_skipped: int = 0

    def _store_session_token(self, token: str) -> None:
        if not token:
            raise ValueError("O token de sessão não pode ser vazio.")
        self._session_token = token
        self.is_authenticated = True

    def _store_session(
        self,
        token: str,
        profile: str,
        name: str = "",
        email: str = "",
    ) -> None:
        if profile not in {"estudante", "bibliotecario", "admin"}:
            raise ValueError("O perfil de sessão retornado não é válido.")
        self._store_session_token(token)
        self._session_profile = profile
        self._session_name = name.strip()
        self._session_email = email.strip()
        self._admin_view_mode = ""

    @rx.var
    def greeting_name(self) -> str:
        return self._session_name if self._session_token else ""

    @rx.var
    def session_email(self) -> str:
        return self._session_email if self._session_token else ""

    @rx.var
    def session_role_label(self) -> str:
        return {
            "estudante": "Estudante",
            "bibliotecario": "Bibliotecário",
            "admin": "Administrador",
        }.get(self._session_profile, "")

    @rx.var
    def active_navigation_role(self) -> str:
        if not self._session_token:
            return ""
        if self._is_admin():
            if self.admin_view_mode == "estudante":
                return "Estudante"
            if self.admin_view_mode == "bibliotecaria":
                return "Bibliotecária"
            return "Admin"
        if self._session_profile == "bibliotecario":
            return "Bibliotecária"
        return "Estudante"

    @rx.event
    def toggle_mobile_navigation(self):
        self.mobile_navigation_open = not self.mobile_navigation_open

    @rx.event
    def close_mobile_navigation(self):
        self.mobile_navigation_open = False

    def _read_session_token(self) -> str | None:
        return self._session_token or None

    @rx.var
    def admin_view_mode(self) -> str:
        if not self._is_admin():
            return ""
        if self._admin_view_mode not in {"bibliotecaria", "estudante"}:
            return ""
        return self._admin_view_mode

    @rx.event
    def set_admin_view_mode(self, mode: str):
        if not self._is_admin() or mode not in {"bibliotecaria", "estudante"}:
            return
        self._admin_view_mode = mode

    @rx.event
    def reset_admin_view_mode(self):
        if not self._is_admin():
            return
        self._admin_view_mode = ""

    def _clear_session_token(self) -> None:
        self._session_token = ""
        self._session_profile = ""
        self._session_name = ""
        self._session_email = ""
        self._admin_view_mode = ""
        self.mobile_navigation_open = False
        self.student_request_pending = False
        self.student_request_uncertain_title_id = None
        self._student_request_uncertain_reference = ""
        self._student_library_manual_retry = False
        self.is_authenticated = False

    def _is_librarian(self) -> bool:
        return bool(self._session_token) and self._session_profile in {
            "bibliotecario",
            "admin",
        }

    def _is_admin(self) -> bool:
        return bool(self._session_token) and self._session_profile == "admin"

    @rx.var
    def is_librarian(self) -> bool:
        return self._is_librarian()

    @rx.var
    def can_manage_librarians(self) -> bool:
        return self._is_admin()

    @rx.var
    def is_student(self) -> bool:
        return bool(self._session_token) and self._session_profile == "estudante"

    @rx.var
    def filtered_public_catalog(self) -> list[dict[str, Any]]:
        category_names = {
            category["id"]: category["nome"]
            for category in self.public_catalog_categories
        }
        search_key = _catalog_search_key(self.public_catalog_search.strip())
        visible: list[dict[str, Any]] = []
        for entry in self.public_catalog_entries:
            title = entry["titulo"]
            if title.get("ativo") is False:
                continue
            category_ids = {
                association["categoria_id"]
                for association in entry["categorias"]
            }
            if (
                self.public_catalog_category_id
                and int(self.public_catalog_category_id) not in category_ids
            ):
                continue
            available = entry["exemplares_disponiveis"]
            if self.public_catalog_only_available and available <= 0:
                continue
            if search_key and search_key not in _catalog_search_key(
                f"{title['titulo']} {title['autores']}"
            ):
                continue
            category_text = ", ".join(
                category_names[category_id]
                for category_id in sorted(category_ids)
                if category_id in category_names
            ) or "Sem categoria"
            cover_initial, cover_variant = _catalog_cover_identity(
                category_text,
                title["titulo"],
            )
            cover_key = _capa_busca_key(
                title["titulo"],
                title["autores"],
            )
            capa_real = (
                resolver_capa_url(
                    capa_resolvida=self.public_catalog_cover_resolutions[
                        cover_key
                    ],
                    isbn=title.get("isbn"),
                )
                if cover_key in self.public_catalog_cover_resolutions
                else ""
            )
            visible.append(
                {
                    "id": title["id"],
                    "titulo": title["titulo"],
                    "autores": title["autores"],
                    "capa_url": title.get("capa_url") or "",
                    "capa_real": capa_real,
                    "capa_gerada": gerar_capa_svg(
                        title["titulo"], title["autores"], category_text
                    ),
                    "categorias": category_text,
                    "exemplares_disponiveis": available,
                    "href": f"/catalogo/{title['id']}",
                    "cover_initial": cover_initial,
                    "cover_variant": cover_variant,
                }
            )
        return sorted(
            visible,
            key=lambda item: _catalog_search_key(item["titulo"]),
            reverse=self.public_catalog_sort == "desc",
        )

    @rx.var
    def home_featured_titles(self) -> list[dict[str, Any]]:
        cards = _home_catalog_cards(
            self.public_catalog_entries,
            self.public_catalog_categories,
            self.public_catalog_cover_resolutions,
        )
        return sorted(
            cards,
            key=lambda item: _catalog_search_key(item["titulo"]),
        )[:10]

    @rx.var
    def home_new_arrivals(self) -> list[dict[str, Any]]:
        cards = _home_catalog_cards(
            self.public_catalog_entries,
            self.public_catalog_categories,
            self.public_catalog_cover_resolutions,
        )
        return sorted(
            cards,
            key=lambda item: (
                _as_utc_datetime(item.get("created_at")) is not None,
                _as_utc_datetime(item.get("created_at"))
                or datetime.min.replace(tzinfo=timezone.utc),
                item["id"],
            ),
            reverse=True,
        )[:10]

    @rx.var
    def home_category_shelves(self) -> list[dict[str, Any]]:
        category_names = {
            category["id"]: category["nome"]
            for category in self.public_catalog_categories
        }
        shelves: list[dict[str, Any]] = []
        for category_id, category_name in sorted(
            category_names.items(),
            key=lambda item: _catalog_search_key(item[1]),
        ):
            titles: list[dict[str, Any]] = []
            for entry in self.public_catalog_entries:
                title = entry["titulo"]
                if title.get("ativo") is False:
                    continue
                if not any(
                    association["categoria_id"] == category_id
                    for association in entry["categorias"]
                ):
                    continue
                titles.append(
                    {
                        "id": title["id"],
                        "titulo": title["titulo"],
                        "autores": title["autores"],
                        "capa_url": title.get("capa_url") or "",
                        "capa_gerada": gerar_capa_svg(
                            title["titulo"], title["autores"], category_name
                        ),
                        "href": f"/catalogo/{title['id']}",
                        "exemplares_disponiveis": entry[
                            "exemplares_disponiveis"
                        ],
                    }
                )
            shelves.append(
                {
                    "id": category_id,
                    "nome": category_name,
                    "quantidade": len(titles),
                    "titulos": titles[:6],
                }
            )
        return shelves

    @rx.var
    def home_total_titles(self) -> int:
        return sum(
            entry["titulo"].get("ativo") is not False
            for entry in self.public_catalog_entries
        )

    @rx.var
    def home_available_copies(self) -> int:
        return sum(
            entry["exemplares_disponiveis"]
            for entry in self.public_catalog_entries
            if entry["titulo"].get("ativo") is not False
        )

    @rx.var
    def home_category_count(self) -> int:
        return len(self.public_catalog_categories)

    @rx.var
    def public_catalog_detail_categories(self) -> str:
        category_names = {
            category["id"]: category["nome"]
            for category in self.public_catalog_categories
        }
        return ", ".join(
            category_names[category_id]
            for category_id in self.public_catalog_detail.get(
                "categoria_ids", []
            )
            if category_id in category_names
        ) or "Sem categoria"

    @rx.var
    def has_public_catalog_detail(self) -> bool:
        return bool(self.public_catalog_detail)

    @rx.var
    def public_catalog_has_available_copies(self) -> bool:
        return self.public_catalog_detail.get("exemplares_disponiveis", 0) > 0

    @rx.var
    def admin_catalog_display_entries(self) -> list[AdminCatalogDisplayEntry]:
        category_names = {
            category["id"]: category["nome"]
            for category in self.catalog_categories
        }
        display_entries: list[AdminCatalogDisplayEntry] = []
        for entry in self.admin_catalog_entries:
            title = entry["titulo"]
            category_ids = sorted(
                association["categoria_id"]
                for association in entry["categorias"]
            )
            cover_key = _capa_busca_key(
                title["titulo"],
                title["autores"],
            )
            display_entry: AdminCatalogDisplayEntry = {
                "id": title["id"],
                "titulo": title["titulo"],
                "autores": title["autores"],
                "isbn": title.get("isbn") or "",
                "editora": title.get("editora") or "",
                "edicao": title.get("edicao") or "",
                "ano_publicacao": str(title.get("ano_publicacao") or ""),
                "descricao": title.get("descricao") or "",
                "capa_url": title.get("capa_url") or "",
                "capa_real": (
                    resolver_capa_url(
                        capa_resolvida=self.public_catalog_cover_resolutions[
                            cover_key
                        ],
                        isbn=title.get("isbn"),
                    )
                    if cover_key in self.public_catalog_cover_resolutions
                    else ""
                ),
                "capa_gerada": gerar_capa_svg(
                    title["titulo"],
                    title["autores"],
                    ", ".join(
                        category_names[category_id]
                        for category_id in category_ids
                        if category_id in category_names
                    ) or "Sem categoria",
                ),
                "ativo": title.get("ativo") is not False,
                "categorias": ", ".join(
                    category_names[category_id]
                    for category_id in category_ids
                    if category_id in category_names
                )
                or "Sem categoria",
                "exemplares_disponiveis": entry[
                    "exemplares_disponiveis"
                ],
                "exemplares": [
                    {
                        "codigo_tombo": copy.get("codigo_tombo")
                        or "Código de tombo não informado",
                        "estado": copy["estado"],
                    }
                    for copy in entry["exemplares"]
                ],
            }
            display_entries.append(display_entry)
        return display_entries

    @rx.var
    def filtered_admin_catalog_entries(self) -> list[AdminCatalogDisplayEntry]:
        query = _catalog_search_key(self.admin_catalog_search)
        visible: list[AdminCatalogDisplayEntry] = []
        for entry in self.admin_catalog_display_entries:
            if not self.admin_catalog_show_inactive and not entry["ativo"]:
                continue
            haystack = _catalog_search_key(
                f"{entry['titulo']} {entry['autores']} {entry['isbn']}"
            )
            if not query or query in haystack:
                visible.append(entry)
        return visible[: self.admin_catalog_visible_limit]

    @rx.var
    def admin_catalog_has_more(self) -> bool:
        query = _catalog_search_key(self.admin_catalog_search)
        total = sum(
            1
            for entry in self.admin_catalog_display_entries
            if (self.admin_catalog_show_inactive or entry["ativo"])
            and (
                not query
                or query
                in _catalog_search_key(
                    f"{entry['titulo']} {entry['autores']} {entry['isbn']}"
                )
            )
        )
        return total > len(self.filtered_admin_catalog_entries)

    @rx.var
    def has_student_library_loans(self) -> bool:
        return bool(self.student_library_loans)

    @rx.var
    def has_student_library_requests(self) -> bool:
        return bool(self.student_library_requests)

    @rx.var
    def has_student_library_reservations(self) -> bool:
        return bool(self.student_library_reservations)

    @rx.var
    def student_awaiting_approval_requests(self) -> list[dict[str, Any]]:
        return [
            request
            for request in self.student_library_requests
            if request["estado"] == "Aguardando confirmação da retirada"
        ]

    @rx.var
    def student_active_loan_count(self) -> int:
        return sum(not loan["devolvido"] for loan in self.student_library_loans)

    @rx.var
    def student_awaiting_count(self) -> int:
        return len(self.student_awaiting_approval_requests) + sum(
            reservation["estado"] == "Aguardando na fila"
            for reservation in self.student_library_reservations
        )

    @rx.var
    def student_approved_reservations(self) -> list[dict[str, Any]]:
        return [
            reservation
            for reservation in self.student_library_reservations
            if reservation["estado"] == "Disponível para retirada"
        ]

    @rx.var
    def student_current_loans(self) -> list[dict[str, Any]]:
        return sorted(
            (
                loan
                for loan in self.student_library_loans
                if not loan["devolvido"] and not loan["em_atraso"]
            ),
            key=lambda loan: loan["dias_restantes"],
        )

    @rx.var
    def student_overdue_loans(self) -> list[dict[str, Any]]:
        return sorted(
            (
                loan
                for loan in self.student_library_loans
                if not loan["devolvido"] and loan["em_atraso"]
            ),
            key=lambda loan: loan["dias_atraso"],
            reverse=True,
        )

    @rx.var
    def has_staff_reservation_student(self) -> bool:
        return bool(self.staff_reservation_student)

    @rx.var
    def has_circulation_requests(self) -> bool:
        return bool(self.circulation_requests)

    @rx.var
    def has_circulation_reservations(self) -> bool:
        return bool(self.circulation_reservations)

    @rx.var
    def has_circulation_loans(self) -> bool:
        return bool(self.circulation_loans)

    @rx.var
    def circulation_active_loan_count(self) -> int:
        return len(self.circulation_loans)

    @rx.var
    def circulation_overdue_loan_count(self) -> int:
        return sum(bool(loan["atrasado"]) for loan in self.circulation_loans)

    @rx.var
    def circulation_due_today_count(self) -> int:
        today = datetime.now(timezone.utc).date()
        return sum(
            (due := _as_utc_datetime(loan["vence_em"])) is not None
            and due.date() == today
            for loan in self.circulation_loans
        )

    @rx.var
    def circulation_pending_request_count(self) -> int:
        return sum(
            request["estado"] == "pendente"
            for request in self.circulation_requests
        )

    @rx.var
    def filtered_managed_librarians(self) -> list[dict[str, Any]]:
        query = _catalog_search_key(self.librarian_management_search.strip())
        if not query:
            return self.managed_librarians
        return [
            librarian
            for librarian in self.managed_librarians
            if query
            in _catalog_search_key(
                f'{librarian["nome"]} {librarian["email"]}'
            )
        ]

    def _redirect_non_librarian(self):
        if not self._session_token:
            return rx.redirect("/login")
        return rx.redirect("/")

    def _redirect_non_admin(self):
        if not self._session_token:
            return rx.redirect("/login")
        return rx.redirect("/")

    def _profile_home_path(self) -> str:
        if self._is_admin() and self.admin_view_mode == "estudante":
            return "/"
        if self._is_librarian():
            return "/admin/acervo"
        return "/"

    @rx.event
    def redirect_authenticated_auth_page(self):
        if self._session_token:
            return rx.redirect(self._profile_home_path())

    @rx.event
    def require_authenticated_user(self):
        if not self._session_token:
            return rx.redirect("/login")

    @rx.event
    def redirect_authenticated_home(self):
        if self._session_token:
            return rx.redirect(self._profile_home_path())

    @rx.event
    def logout(self):
        self._clear_session_token()
        self.signup_message = ""
        self.signup_success_message = ""
        self.signup_has_error = False
        self.login_message = ""
        self.login_has_error = False
        self.catalog_message = ""
        self.catalog_has_error = False
        self.student_library_message = ""
        self.student_library_has_error = False
        self.student_library_loans = []
        self.student_library_requests = []
        self.student_library_reservations = []
        self.student_library_skipped = 0
        self.student_request_message = ""
        self.student_request_has_error = False
        self.librarian_management_pending = False
        self.librarian_management_message = ""
        self.librarian_management_has_error = False
        self.librarian_management_success = False
        self.librarian_management_confirm_id = None
        self.managed_librarians = []
        self.librarian_management_skipped = 0
        self.staff_reservation_pending = False
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False
        self.staff_reservation_email = ""
        self.staff_reservation_student = {}
        self.staff_reservation_title_options = []
        self.staff_reservation_skipped = 0
        self.staff_reservation_title_id = ""
        self.staff_reservation_needs_manual_check = False
        self.catalog_categories = []
        self.catalog_categories_skipped = 0
        self.public_catalog_categories_skipped = 0
        self.admin_catalog_skipped = 0
        self.circulation_skipped = 0
        self.selected_category_ids = []
        self.catalog_categories_pending = False
        self.catalog_title_created = False
        self.catalog_created_codes = []
        self.catalog_needs_manual_check = False
        self.admin_catalog_show_inactive = False
        self.admin_catalog_edit_title_id = None
        self.admin_catalog_copy_title_id = None
        self._catalog_title_id = None
        self._pending_category_ids = []
        self._uncertain_category_ids = []
        self._catalog_title_uncertain = False
        self._catalog_copy_uncertain = False
        return rx.redirect("/")

    @rx.event
    def dismiss_signup_confirmation(self):
        self.signup_success_message = ""

    @rx.event
    def set_public_catalog_search(self, value: str):
        self.public_catalog_search = value

    @rx.event
    async def submit_global_search(self, form_data: dict[str, Any]):
        termo = str(form_data.get("q") or "").strip()
        self.public_catalog_search = termo
        if termo:
            return rx.redirect(f"/catalogo?q={quote(termo)}")
        return rx.redirect("/catalogo")

    @rx.event
    def set_public_catalog_category(self, value: str):
        if not value:
            self.public_catalog_category_id = ""
        elif value.isdecimal() and any(
            str(category["id"]) == value
            for category in self.public_catalog_categories
        ):
            self.public_catalog_category_id = value

    @rx.event
    def set_public_catalog_only_available(self, value: bool):
        self.public_catalog_only_available = value

    @rx.event
    def set_public_catalog_sort(self, value: str):
        if value in {"asc", "desc"}:
            self.public_catalog_sort = value

    @rx.event
    def set_student_reservation_tab(self, value: str):
        if value in {"aguardando", "aprovadas", "emprestados", "atrasos"}:
            self.student_reservation_tab = value

    @rx.event
    @diagnosticar_pagina_xano("home")
    async def load_home(self):
        await self.load_public_catalog()
        if self._session_profile == "estudante":
            await self.load_student_library()
        elif self._is_librarian():
            await self._refresh_circulation_data()
        if self.public_catalog_has_error:
            return None
        return State.resolve_public_catalog_covers

    @rx.event
    @diagnosticar_pagina_xano("catalogo")
    async def load_public_catalog(self):
        self.public_catalog_pending = True
        self.home_titles_pending = True
        self.home_categories_pending = True
        self.public_catalog_message = ""
        self.public_catalog_has_error = False
        self.home_titles_has_error = False
        self.home_categories_has_error = False
        self.home_titles_error_message = ""
        self.home_categories_error_message = ""
        self.public_catalog_categories_skipped = 0
        titles: list[dict[str, Any]] | None = None
        categories: list[dict[str, Any]] | None = None

        async def fetch_titles() -> list[dict[str, Any]] | Exception:
            try:
                return await list_public_titles()
            except (
                XanoConfigurationError,
                XanoRequestError,
                XanoResponseError,
            ) as error:
                return error

        async def fetch_categories() -> list[dict[str, Any]] | Exception:
            try:
                return await list_categories()
            except (
                XanoConfigurationError,
                XanoRequestError,
                XanoResponseError,
            ) as error:
                return error

        try:
            title_result, category_result = await asyncio.gather(
                fetch_titles(),
                fetch_categories(),
            )
            if isinstance(title_result, Exception):
                self.home_titles_has_error = True
                self.home_titles_error_message = catalog_error_message(
                    title_result
                )
            else:
                titles = title_result
                self.home_titles_has_error = False

            if isinstance(category_result, Exception):
                self.home_categories_has_error = True
                self.home_categories_error_message = catalog_error_message(
                    category_result
                )
            else:
                categories = category_result
                self.home_categories_has_error = False

            self.home_titles_pending = False
        finally:
            self.home_titles_pending = False
            self.home_categories_pending = False
            self.public_catalog_pending = False

        if titles is not None:
            self.public_catalog_entries = titles
        if categories is not None:
            self.public_catalog_categories = categories
            self.public_catalog_categories_skipped = getattr(
                categories,
                "skipped_count",
                0,
            )
        self._sync_public_catalog_errors()
        if titles is not None:
            return State.resolve_public_catalog_covers

    @rx.event
    @diagnosticar_pagina_xano("home_titulos")
    async def retry_home_titles(self):
        if self.home_titles_pending:
            return
        self.home_titles_pending = True
        titles: list[dict[str, Any]] | None = None
        self.home_titles_error_message = ""
        try:
            invalidar_cache_titulos_publicos()
            titles = await list_public_titles()
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.home_titles_has_error = True
            self.home_titles_error_message = catalog_error_message(error)
        finally:
            self.home_titles_pending = False

        if titles is not None:
            self.public_catalog_entries = titles
            self.home_titles_has_error = False
        self._sync_public_catalog_errors()
        if titles is not None:
            return State.resolve_public_catalog_covers

    @rx.event
    @diagnosticar_pagina_xano("home_categorias")
    async def retry_home_categories(self):
        if self.home_categories_pending:
            return
        self.home_categories_pending = True
        categories: list[dict[str, Any]] | None = None
        self.home_categories_error_message = ""
        try:
            invalidar_cache_categorias_publicas()
            categories = await list_categories()
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.home_categories_has_error = True
            self.home_categories_error_message = catalog_error_message(error)
        finally:
            self.home_categories_pending = False

        if categories is not None:
            self.public_catalog_categories = categories
            self.public_catalog_categories_skipped = getattr(
                categories,
                "skipped_count",
                0,
            )
            self.home_categories_has_error = False
        self._sync_public_catalog_errors()

    def _sync_public_catalog_errors(self) -> None:
        self.public_catalog_has_error = (
            self.home_titles_has_error or self.home_categories_has_error
        )
        self.public_catalog_message = (
            self.home_titles_error_message
            or self.home_categories_error_message
        )

    @rx.event
    async def retry_public_catalog(self):
        invalidar_cache_catalogo_publico()
        await self.load_public_catalog()

    @rx.event
    async def retry_public_catalog_detail(self):
        invalidar_cache_catalogo_publico()
        await self.load_public_catalog_detail()

    @rx.event
    async def retry_student_library(self):
        self._student_library_manual_retry = True
        try:
            await self.load_student_library()
        finally:
            self._student_library_manual_retry = False

    @rx.event(background=True)
    async def resolve_public_catalog_covers(self):
        async with self:
            requests: dict[str, tuple[str, str]] = {}

            def adicionar(
                titulo: object,
                autoria: object,
                capa_url: object,
            ) -> None:
                titulo_texto = str(titulo or "").strip()
                autoria_texto = str(autoria or "")
                if (
                    not titulo_texto
                    or str(capa_url or "").strip().startswith("https://")
                ):
                    return
                chave = _capa_busca_key(titulo_texto, autoria_texto)
                if (
                    not self.public_catalog_cover_resolutions.get(chave)
                    and chave not in requests
                ):
                    requests[chave] = (titulo_texto, autoria_texto)

            for entry in self.public_catalog_entries:
                title = entry["titulo"]
                adicionar(
                    title["titulo"],
                    title["autores"],
                    title.get("capa_url"),
                )

            for entry in self.admin_catalog_entries:
                title = entry["titulo"]
                adicionar(
                    title["titulo"],
                    title["autores"],
                    title.get("capa_url"),
                )

            detail = self.public_catalog_detail
            if detail:
                adicionar(
                    detail["titulo"],
                    detail["autores"],
                    detail.get("capa_url"),
                )

        itens = list(requests.items())
        for inicio in range(0, len(itens), 3):
            lote = itens[inicio : inicio + 3]
            resultados = await asyncio.gather(
                *(
                    resolver_capa_por_titulo(titulo, autoria)
                    for _, (titulo, autoria) in lote
                )
            )
            async with self:
                for (chave, _), capa_encontrada in zip(lote, resultados):
                    self.public_catalog_cover_resolutions[chave] = (
                        capa_encontrada
                    )
                    detail = self.public_catalog_detail
                    if (
                        detail
                        and not detail.get("capa_url")
                        and _capa_busca_key(
                            detail["titulo"],
                            detail["autores"],
                        )
                        == chave
                    ):
                        detail["capa_real"] = resolver_capa_url(
                            capa_resolvida=capa_encontrada,
                            isbn=detail.get("isbn"),
                        )

    @rx.event
    @diagnosticar_pagina_xano("detalhe")
    async def load_public_catalog_detail(self):
        self.public_catalog_detail = {}
        self.public_catalog_detail_message = ""
        self.public_catalog_detail_has_error = False
        self.public_catalog_detail_not_found = False
        self.public_catalog_detail_pending = True
        self.student_request_message = ""
        self.student_request_has_error = False

        raw_title_id = self.router.page.params.get("titulo_id", "")
        if not raw_title_id.isdecimal() or int(raw_title_id) < 1:
            self.public_catalog_detail_not_found = True
            self.public_catalog_detail_pending = False
            return

        try:
            entry = await get_public_title(int(raw_title_id))
            categories = await list_categories()
        except XanoResponseError as error:
            self.public_catalog_detail_pending = False
            if error.status_code == 404:
                self.public_catalog_detail_not_found = True
                return
            self.public_catalog_detail_message = catalog_error_message(error)
            self.public_catalog_detail_has_error = True
            return
        except (XanoConfigurationError, XanoRequestError) as error:
            self.public_catalog_detail_message = catalog_error_message(error)
            self.public_catalog_detail_has_error = True
            self.public_catalog_detail_pending = False
            return

        self.public_catalog_categories = categories
        self.public_catalog_categories_skipped = getattr(
            categories,
            "skipped_count",
            0,
        )
        category_names = {
            category["id"]: category["nome"]
            for category in categories
        }
        category_text = ", ".join(
            category_names[association["categoria_id"]]
            for association in entry["categorias"]
            if association["categoria_id"] in category_names
        ) or "Sem categoria"
        cover_initial, cover_variant = _catalog_cover_identity(
            category_text,
            entry["titulo"]["titulo"],
        )
        cover_key = _capa_busca_key(
            entry["titulo"]["titulo"],
            entry["titulo"]["autores"],
        )
        self.public_catalog_detail = {
            "id": entry["titulo"]["id"],
            "titulo": entry["titulo"]["titulo"],
            "autores": entry["titulo"]["autores"],
            "capa_url": entry["titulo"].get("capa_url") or "",
            "capa_real": (
                resolver_capa_url(
                    capa_resolvida=self.public_catalog_cover_resolutions[
                        cover_key
                    ],
                    isbn=entry["titulo"].get("isbn"),
                )
                if cover_key in self.public_catalog_cover_resolutions
                else ""
            ),
            "capa_gerada": gerar_capa_svg(
                entry["titulo"]["titulo"],
                entry["titulo"]["autores"],
                category_text,
            ),
            "cover_initial": cover_initial,
            "cover_variant": cover_variant,
            "isbn": entry["titulo"].get("isbn") or "",
            "editora": entry["titulo"].get("editora") or "",
            "edicao": entry["titulo"].get("edicao") or "",
            "ano_publicacao": (
                str(entry["titulo"]["ano_publicacao"])
                if entry["titulo"].get("ano_publicacao") is not None
                else ""
            ),
            "descricao": entry["titulo"].get("descricao")
            or "Sem descrição cadastrada",
            "categoria_ids": [
                association["categoria_id"]
                for association in entry["categorias"]
            ],
            "exemplares_disponiveis": entry["exemplares_disponiveis"],
        }
        self.public_catalog_detail_pending = False
        return State.resolve_public_catalog_covers

    @rx.event
    async def request_catalog_title(self, title_id: int):
        if not self._session_token:
            return rx.redirect("/login")
        if self._session_profile != "estudante" or type(title_id) is not int or title_id < 1:
            self.student_request_message = (
                "Somente estudantes podem solicitar um empréstimo ou reserva."
            )
            self.student_request_has_error = True
            return rx.redirect("/")
        if self.student_request_pending:
            return
        if self.public_catalog_detail.get("id") != title_id:
            return

        self.student_request_pending = True
        self.student_request_message = ""
        self.student_request_has_error = False
        write_succeeded = False
        refresh_after_write = False
        try:
            try:
                with contexto_evento_xano(
                    "reservar_livro",
                    self._session_profile,
                ):
                    result = await request_title_loan(
                        title_id,
                        self._session_token,
                    )
            except XanoWriteSucceededWithUnreadableResponse as error:
                write_succeeded = True
                refresh_after_write = True
                self.student_request_uncertain_title_id = title_id
                self._student_request_uncertain_reference = (
                    error.reference or ""
                )
                self.student_request_message = (
                    "Atualizando Reservas para confirmar a solicitação."
                )
            else:
                write_succeeded = True
                estado = result.get("estado")
                if estado == "em_reserva":
                    self.student_request_message = (
                        "Pedido enviado. Sua solicitação foi registrada "
                        "na fila de reservas."
                    )
                else:
                    self.student_request_message = (
                        "Pedido enviado. Sua solicitação foi registrada. "
                        "A equipe da biblioteca "
                        "confirmará a retirada."
                    )
                if estado in {"pendente", "em_reserva"}:
                    self.student_library_requests = [
                        request
                        for request in self.student_library_requests
                        if request["id"] != result["id"]
                    ]
                    self.student_library_requests.append(
                        {
                            "id": result["id"],
                            "titulo": self.public_catalog_detail.get(
                                "titulo",
                                "Título indisponível",
                            ),
                            "href": f"/catalogo/{title_id}",
                            "estado": _request_status_label(estado),
                            "solicitada_em": _format_known_timestamp(
                                result.get("solicitada_em")
                            ),
                        }
                    )
                else:
                    self.student_library_requests.append(
                        {
                            "id": result["id"],
                            "titulo": self.public_catalog_detail.get(
                                "titulo",
                                "Título indisponível",
                            ),
                            "href": f"/catalogo/{title_id}",
                            "estado": "Solicitação registrada",
                            "solicitada_em": _format_known_timestamp(
                                result.get("solicitada_em")
                            ),
                        }
                    )
                self.student_request_uncertain_title_id = None
                self._student_request_uncertain_reference = ""
                self.student_library_has_error = False
            if refresh_after_write:
                await self.load_student_library()
        except (
            XanoResponseError,
            XanoTimeoutError,
            XanoInvalidResponseError,
            XanoRequestError,
            XanoConfigurationError,
        ) as error:
            self.student_request_has_error = True
            self.student_request_message = (
                reservation_request_error_message(error)
                if not isinstance(error, XanoConfigurationError)
                else "[RES-SERVICE] O servidor de reservas está temporariamente indisponível"
            )
            if (
                isinstance(error, XanoResponseError)
                and error.status_code == 401
            ):
                self._clear_session_token()
                self.student_request_pending = False
        finally:
            if not write_succeeded or not self.student_library_has_error:
                self.student_request_pending = False

    @rx.event
    @diagnosticar_pagina_xano("reservas")
    async def load_student_library(self):
        if not self._session_token:
            return rx.redirect("/login")
        if not self.is_student and not (
            self._is_admin() and self.admin_view_mode == "estudante"
        ):
            return rx.redirect("/")

        self.student_library_pending = True
        self.student_library_message = ""
        self.student_library_has_error = False
        self.student_library_requires_login = False
        self.student_library_skipped = 0
        try:
            with contexto_evento_xano(
                "carregar_reservas",
                self._session_profile,
            ):
                loans = await list_my_loans(self._session_token)
                requests = await list_my_requests(self._session_token)
                reservations = await list_my_reservations(self._session_token)
                titles = await list_public_titles()
                uncertain_title_id = self.student_request_uncertain_title_id
                if (
                    uncertain_title_id is not None
                    and not self._student_library_manual_retry
                ):
                    for retry_delay in (1.5, 2.5):
                        request_confirmed = any(
                            request["titulo_id"] == uncertain_title_id
                            and request["estado"] in {"pendente", "em_reserva"}
                            for request in requests
                        )
                        reservation_confirmed = any(
                            reservation["titulo_id"] == uncertain_title_id
                            and reservation["estado"] in {"aguardando", "ofertada"}
                            for reservation in reservations
                        )
                        if request_confirmed or reservation_confirmed:
                            break
                        await asyncio.sleep(retry_delay)
                        requests = await list_my_requests(self._session_token)
                        reservations = await list_my_reservations(self._session_token)
        except (XanoConfigurationError, XanoRequestError, XanoResponseError) as error:
            self.student_library_message = catalog_error_message(error)
            self.student_library_has_error = True
            if self.student_request_uncertain_title_id is not None:
                self.student_request_message = (
                    reservation_request_error_message(error)
                    if not isinstance(error, XanoConfigurationError)
                    else "[RES-SERVICE] O servidor de reservas está temporariamente indisponível"
                )
                self.student_request_has_error = True
            if isinstance(error, XanoResponseError) and error.status_code == 401:
                self._clear_session_token()
                self.student_library_requires_login = True
            return
        finally:
            self.student_library_pending = False

        self.student_library_skipped = sum(
            getattr(records, "skipped_count", 0)
            for records in (loans, requests, reservations)
        )
        title_names = {
            entry["titulo"]["id"]: entry["titulo"]["titulo"] for entry in titles
        }
        reservation_ids = {
            reservation["id"] for reservation in reservations
        }
        self.student_library_loans = [
            {
                "id": loan["id"],
                "titulo": "Título indisponível",
                "exemplar_id": loan["exemplar_id"],
                "retirado_em": _format_timestamp(loan["retirado_em"]),
                "vence_em": _format_known_timestamp(loan["vence_em"]),
                "devolvido": loan["devolvido_em"] not in (None, 0),
                "em_atraso": _is_overdue(loan["vence_em"], loan["devolvido_em"]),
                "dias_restantes": max(
                    0,
                    _calendar_days_until(loan["vence_em"]) or 0,
                ),
                "dias_atraso": (
                    max(
                        1,
                        -(_calendar_days_until(loan["vence_em"]) or 0),
                    )
                    if _is_overdue(loan["vence_em"], loan["devolvido_em"])
                    else 0
                ),
            }
            for loan in loans
        ]
        self.student_library_requests = [
            {
                "id": request["id"],
                "titulo": title_names.get(
                    request["titulo_id"], "Título indisponível"
                ),
                "href": f"/catalogo/{request['titulo_id']}",
                "estado": _request_status_label(request["estado"]),
                "solicitada_em": _format_known_timestamp(
                    request.get("solicitada_em")
                ),
            }
            for request in requests
            if not (
                request["estado"] == "em_reserva"
                and request.get("reserva_id") in reservation_ids
            )
        ]
        self.student_library_reservations = [
            {
                "id": reservation["id"],
                "titulo": title_names.get(
                    reservation["titulo_id"], "Título indisponível"
                ),
                "href": f"/catalogo/{reservation['titulo_id']}",
                "estado": _reservation_status_label(reservation["estado"]),
                "prazo": (
                    _format_sao_paulo_deadline(
                        reservation["expira_em_sao_paulo"]
                    )
                    if reservation["expira_em_sao_paulo"]
                    else "Data indisponível"
                ),
            }
            for reservation in reservations
        ]
        uncertain_title_id = self.student_request_uncertain_title_id
        if uncertain_title_id is not None:
            confirmed_reservation = next(
                (
                    reservation
                    for reservation in reservations
                    if reservation["titulo_id"] == uncertain_title_id
                    and reservation["estado"] in {"aguardando", "ofertada"}
                ),
                None,
            )
            confirmed_request = next(
                (
                    request
                    for request in requests
                    if request["titulo_id"] == uncertain_title_id
                    and request["estado"] in {"pendente", "em_reserva"}
                ),
                None,
            )
            if confirmed_reservation is not None or confirmed_request is not None:
                self.student_request_uncertain_title_id = None
                self._student_request_uncertain_reference = ""
                self.student_request_pending = False
                self.student_request_has_error = False
                if confirmed_reservation is not None:
                    self.student_request_message = (
                        "Pedido enviado. Sua reserva foi registrada. "
                        "Confira em Reservas."
                    )
                elif (
                    confirmed_request is not None
                    and confirmed_request["estado"] == "em_reserva"
                ):
                    self.student_request_message = (
                        "Pedido enviado. Sua solicitação entrou na fila de reservas."
                    )
                else:
                    self.student_request_message = (
                        "Pedido enviado. Sua solicitação foi registrada. "
                        "A equipe da biblioteca confirmará a retirada."
                    )
            else:
                self.student_library_has_error = True
                reference = registrar_resultado_xano(
                    action="reservar_livro",
                    profile="estudante",
                    method="GET",
                    path="/minhas/solicitacoes e /minhas/reservas",
                    status="2xx",
                    result="releitura 3x não achou o pedido",
                    reference=self._student_request_uncertain_reference or None,
                    duration_ms=3000,
                )
                self._student_request_uncertain_reference = reference
                self.student_library_message = (
                    "Ainda não foi possível confirmar a solicitação. "
                    f"Atualize Reservas antes de tentar novamente. (ref. {reference})"
                )
                self.student_request_message = (
                    "Não foi possível confirmar a solicitação. "
                    f"Confira Reservas antes de tentar novamente. (ref. {reference})"
                )
                self.student_request_has_error = True
        else:
            self.student_request_pending = False

    @rx.event
    def redirect_student_library(self):
        return rx.redirect("/reservas")

    def _sync_catalog_progress(self) -> None:
        self.catalog_categories_pending = bool(
            self._pending_category_ids or self._uncertain_category_ids
        )

    @rx.event
    async def submit_signup(self, form_data: dict[str, Any]):
        self.signup_message = ""
        self.signup_success_message = ""
        self.signup_has_error = False
        try:
            payload = build_signup_payload(form_data)
            session = await submit_student_signup(payload)
        except XanoWriteSucceededWithUnreadableResponse:
            self.signup_success_message = (
                "Cadastro enviado. Não foi possível ler a resposta; "
                "tente entrar com a conta."
            )
            self.signup_has_error = False
            return
        except (
            SignupValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.signup_message = signup_error_message(error)
            self.signup_has_error = True
            return

        self._store_session(
            session["authToken"],
            "estudante",
            str(session["usuario"]["nome"]),
            str(session["usuario"]["email"]),
        )
        self.signup_success_message = (
            "Cadastro realizado. Seu acesso de estudante está ativo."
        )
        return rx.redirect("/")

    @rx.event
    async def submit_login(self, form_data: dict[str, Any]):
        self.login_message = ""
        self.signup_success_message = ""
        self.login_has_error = False
        try:
            payload = build_login_payload(form_data)
            session = await authenticate(payload)
        except (
            LoginValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.login_message = login_error_message(error)
            self.login_has_error = True
            return

        self._store_session(
            session["authToken"],
            session["usuario"]["perfil"],
            session["usuario"]["nome"],
            session["usuario"]["email"],
        )
        return rx.redirect(self._profile_home_path())

    @rx.event
    @diagnosticar_pagina_xano("contas")
    async def load_librarians(self):
        if not self._is_admin():
            return self._redirect_non_admin()

        self.librarian_management_pending = True
        self.librarian_management_message = ""
        self.librarian_management_has_error = False
        self.librarian_management_skipped = 0
        try:
            librarians = await list_librarians(self._session_token)
            self.managed_librarians = librarians
            self.librarian_management_skipped = getattr(
                librarians,
                "skipped_count",
                0,
            )
        except (
            UserAdminValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.librarian_management_message = user_admin_error_message(error)
            self.librarian_management_has_error = True
        finally:
            self.librarian_management_pending = False

    @rx.event
    def request_librarian_deactivation(self, librarian_id: int):
        if not self._is_admin():
            return self._redirect_non_admin()
        self.librarian_management_confirm_id = librarian_id

    @rx.event
    def cancel_librarian_deactivation(self):
        self.librarian_management_confirm_id = None

    @rx.event
    async def submit_librarian(self, form_data: dict[str, Any]):
        if not self._is_admin():
            return self._redirect_non_admin()

        self.librarian_management_pending = True
        self.librarian_management_message = ""
        self.librarian_management_has_error = False
        self.librarian_management_success = False
        try:
            payload = build_librarian_payload(
                {
                    "nome": str(form_data.get("nome", "")),
                    "email": str(form_data.get("email", "")),
                    "senha": str(form_data.get("senha", "")),
                }
            )
            librarian = await create_librarian(
                payload,
                self._session_token,
            )
        except XanoWriteSucceededWithUnreadableResponse:
            await self.load_librarians()
            self.librarian_management_message = (
                "Bibliotecário cadastrado. Não foi possível ler a resposta; "
                "confira as contas bibliotecárias."
            )
            self.librarian_management_success = (
                not self.librarian_management_has_error
            )
            return rx.call_script(
                "document.getElementById('form-cadastro-bibliotecario')?.reset()"
            )
        except (
            UserAdminValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.librarian_management_message = user_admin_error_message(error)
            self.librarian_management_has_error = True
            return
        finally:
            self.librarian_management_pending = False

        self.managed_librarians = [
            item
            for item in self.managed_librarians
            if item["id"] != librarian["id"]
        ]
        self.managed_librarians.append(librarian)
        self.librarian_management_message = "Bibliotecário cadastrado."
        self.librarian_management_success = True
        return rx.call_script(
            "document.getElementById('form-cadastro-bibliotecario')?.reset()"
        )

    @rx.event
    async def set_librarian_active(self, librarian_id: int, active: bool):
        if not self._is_admin():
            return self._redirect_non_admin()
        if type(librarian_id) is not int or librarian_id < 1:
            self.librarian_management_message = (
                "Não foi possível identificar o bibliotecário."
            )
            self.librarian_management_has_error = True
            return

        self.librarian_management_pending = True
        self.librarian_management_message = ""
        self.librarian_management_has_error = False
        self.librarian_management_success = False
        try:
            librarian = await set_librarian_active(
                librarian_id,
                active,
                self._session_token,
            )
        except XanoWriteSucceededWithUnreadableResponse:
            await self.load_librarians()
            self.librarian_management_confirm_id = None
            self.librarian_management_message = (
                "Operação concluída. Não foi possível ler a resposta; "
                "confira as contas bibliotecárias."
            )
            self.librarian_management_success = (
                not self.librarian_management_has_error
            )
            return
        except (
            UserAdminValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.librarian_management_message = user_admin_error_message(error)
            self.librarian_management_has_error = True
            return
        finally:
            self.librarian_management_pending = False

        self.managed_librarians = [
            librarian if item["id"] == librarian_id else item
            for item in self.managed_librarians
        ]
        self.librarian_management_confirm_id = None
        self.librarian_management_message = (
            "Bibliotecário reativado."
            if active
            else "Bibliotecário desativado."
        )
        self.librarian_management_success = True

    @rx.event
    def update_staff_reservation_email(self, value: str):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        self.staff_reservation_email = value
        self.staff_reservation_student = {}
        self.staff_reservation_title_id = ""
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False

    @rx.event
    def update_staff_reservation_title_id(self, value: str):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        self.staff_reservation_title_id = value

    @rx.event
    def update_librarian_management_search(self, value: str):
        if not self._is_admin():
            return self._redirect_non_admin()
        self.librarian_management_search = value

    @rx.event
    def select_circulation_tab(self, tab: str):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if tab not in {"pedidos", "emprestimos"}:
            self.circulation_message = "A aba selecionada não é válida."
            self.circulation_has_error = True
            return
        self.circulation_active_tab = tab

    @rx.event
    async def load_staff_reservation_page(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()

        self.staff_reservation_pending = True
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False
        self.staff_reservation_email = ""
        self.staff_reservation_student = {}
        self.staff_reservation_title_id = ""
        self.staff_reservation_needs_manual_check = False
        self.staff_reservation_skipped = 0
        try:
            entries = await list_admin_catalog(self._session_token)
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.staff_reservation_message = catalog_error_message(error)
            self.staff_reservation_has_error = True
            self.staff_reservation_title_options = []
        else:
            self.staff_reservation_skipped = getattr(
                entries,
                "skipped_count",
                0,
            )
            self.staff_reservation_title_options = [
                {
                    "id": str(entry["titulo"]["id"]),
                    "label": entry["titulo"]["titulo"],
                }
                for entry in entries
                if entry["titulo"].get("ativo") is not False
            ]
            if not self.staff_reservation_title_options:
                self.staff_reservation_message = (
                    "Não há títulos ativos disponíveis para reserva."
                )
        finally:
            self.staff_reservation_pending = False

    @rx.event
    async def search_staff_reservation_student(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.staff_reservation_pending:
            self.staff_reservation_message = "Aguarde a operação atual."
            self.staff_reservation_has_error = True
            return

        self.staff_reservation_pending = True
        self.staff_reservation_student = {}
        self.staff_reservation_title_id = ""
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False
        try:
            student = await find_student_by_email(
                self.staff_reservation_email,
                self._session_token,
            )
        except (
            StaffReservationValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.staff_reservation_message = staff_reservation_error_message(
                error
            )
            self.staff_reservation_has_error = True
        else:
            if student is None:
                self.staff_reservation_message = (
                    "Nenhum estudante ativo foi encontrado para esse e-mail."
                )
                self.staff_reservation_has_error = True
            else:
                self.staff_reservation_student = student
                self.staff_reservation_message = (
                    "Confirme o estudante antes de registrar a reserva."
                )
        finally:
            self.staff_reservation_pending = False

    @rx.event
    async def submit_staff_reservation(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.staff_reservation_pending:
            self.staff_reservation_message = "Aguarde a operação atual."
            self.staff_reservation_has_error = True
            return
        if self.staff_reservation_needs_manual_check:
            self.staff_reservation_message = (
                "Confira a fila de reservas antes de tentar novamente."
            )
            self.staff_reservation_has_error = True
            return
        student_id = self.staff_reservation_student.get("id")
        try:
            title_id = int(self.staff_reservation_title_id)
        except ValueError:
            title_id = 0
        if type(student_id) is not int or student_id < 1:
            self.staff_reservation_message = "Busque e confirme um estudante."
            self.staff_reservation_has_error = True
            return
        if title_id < 1 or not any(
            option["id"] == self.staff_reservation_title_id
            for option in self.staff_reservation_title_options
        ):
            self.staff_reservation_message = "Selecione um título ativo."
            self.staff_reservation_has_error = True
            return

        self.staff_reservation_pending = True
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False
        try:
            await create_staff_reservation(
                student_id,
                title_id,
                self._session_token,
            )
        except XanoWriteSucceededWithUnreadableResponse:
            await self._refresh_circulation_data()
            self.staff_reservation_message = (
                "Reserva enviada. Não foi possível ler a resposta; "
                "confira Reservas."
            )
            self.staff_reservation_has_error = False
            return
        except XanoResponseError as error:
            if error.status_code >= 500:
                self.staff_reservation_needs_manual_check = True
                self.staff_reservation_message = (
                    "Não foi possível confirmar o resultado. Confira a fila "
                    "antes de tentar novamente."
                )
            else:
                self.staff_reservation_message = (
                    staff_reservation_error_message(error)
                )
            self.staff_reservation_has_error = True
        except XanoRequestError:
            self.staff_reservation_needs_manual_check = True
            self.staff_reservation_message = (
                "Não foi possível confirmar o resultado. Confira a fila "
                "antes de tentar novamente."
            )
            self.staff_reservation_has_error = True
        except XanoConfigurationError as error:
            self.staff_reservation_message = staff_reservation_error_message(
                error
            )
            self.staff_reservation_has_error = True
        finally:
            self.staff_reservation_pending = False
        if self.staff_reservation_has_error:
            return

        self.staff_reservation_student = {}
        self.staff_reservation_title_id = ""
        self.staff_reservation_message = (
            "Reserva registrada na fila normal do título; a ordem é definida "
            "pelo servidor."
        )

    async def _refresh_circulation_data(self) -> bool:
        self.circulation_pending = True
        self.circulation_skipped = 0
        try:
            requests = await list_admin_requests(self._session_token)
            reservations = await list_admin_reservations(self._session_token)
            loans = await list_admin_loans(self._session_token)
            catalog_entries = await list_admin_catalog(self._session_token)
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.circulation_message = catalog_error_message(error)
            self.circulation_has_error = True
            return False
        finally:
            self.circulation_pending = False

        now = datetime.now(timezone.utc)
        self.circulation_requests = requests
        self.circulation_reservations = reservations
        self.circulation_loans = [
            {
                **loan,
                "atrasado": _timestamp_is_past(loan["vence_em"], now),
            }
            for loan in loans
        ]
        self.circulation_catalog_entries = catalog_entries
        self.circulation_has_error = False
        self.circulation_skipped = sum(
            getattr(records, "skipped_count", 0)
            for records in (
                requests,
                reservations,
                loans,
                catalog_entries,
            )
        )
        self.circulation_needs_manual_check = False
        return True

    @rx.event
    async def load_circulation_page(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        self.circulation_message = ""
        self.circulation_has_error = False
        await self._refresh_circulation_data()

    @rx.event
    @diagnosticar_pagina_xano("reservas_admin")
    async def load_staff_reservations_dashboard(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        self.circulation_active_tab = "pedidos"
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False
        self.staff_reservation_email = ""
        self.staff_reservation_student = {}
        self.staff_reservation_title_id = ""
        self.staff_reservation_needs_manual_check = False
        await self.load_circulation_page()
        self.staff_reservation_title_options = [
            {
                "id": str(entry["titulo"]["id"]),
                "label": entry["titulo"]["titulo"],
            }
            for entry in self.circulation_catalog_entries
            if entry["titulo"].get("ativo") is not False
        ]
        if not self.staff_reservation_title_options and not self.circulation_has_error:
            self.staff_reservation_message = (
                "Não há títulos ativos disponíveis para reserva."
            )

    @rx.event
    @diagnosticar_pagina_xano("emprestimos_admin")
    async def load_circulation_loans_tab(self):
        result = await self.load_staff_reservations_dashboard()
        self.circulation_active_tab = "emprestimos"
        return result

    async def _perform_circulation_action(
        self,
        action: Callable[[], Awaitable[object | None]],
        success_message: str,
    ) -> None:
        if not self._is_librarian():
            return
        if self.circulation_pending:
            self.circulation_message = "Aguarde a operação atual."
            self.circulation_has_error = True
            return
        if self.circulation_needs_manual_check:
            self.circulation_message = (
                "Atualize a fila e os empréstimos antes de tentar outra operação."
            )
            self.circulation_has_error = True
            return

        self.circulation_pending = True
        self.circulation_message = ""
        self.circulation_has_error = False
        write_warning = False
        try:
            await action()
        except XanoWriteSucceededWithUnreadableResponse:
            write_warning = True
            success_message = (
                "Operação concluída. Não foi possível ler a resposta; "
                "a lista foi atualizada."
            )
        except XanoResponseError as error:
            if error.status_code >= 500:
                self.circulation_needs_manual_check = True
                self.circulation_message = (
                    "Não foi possível confirmar o resultado. Atualize a "
                    "circulação antes de tentar novamente."
                )
            else:
                self.circulation_message = catalog_error_message(error)
            self.circulation_has_error = True
            return
        except XanoRequestError:
            self.circulation_needs_manual_check = True
            self.circulation_message = (
                "Não foi possível confirmar o resultado. Atualize a "
                "circulação antes de tentar novamente."
            )
            self.circulation_has_error = True
            return
        except XanoConfigurationError as error:
            self.circulation_message = catalog_error_message(error)
            self.circulation_has_error = True
            return
        finally:
            self.circulation_pending = False

        self.circulation_message = success_message
        if not await self._refresh_circulation_data():
            if write_warning:
                self.circulation_message = (
                    "Operação concluída, mas não foi possível ler a resposta "
                    "nem atualizar a lista. Tente recarregar."
                )
            return
        self.circulation_message = success_message

    @rx.event
    async def circulation_pickup_request(self, request_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._perform_circulation_action(
            lambda: register_request_pickup(request_id, self._session_token),
            "Retirada registrada; empréstimo com prazo de 14 dias.",
        )

    @rx.event
    async def circulation_refuse_request(self, request_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._perform_circulation_action(
            lambda: refuse_loan_request(request_id, self._session_token),
            "Solicitação recusada.",
        )

    @rx.event
    async def circulation_offer_reservation(self, title_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        title_entry = next(
            (
                entry
                for entry in self.circulation_catalog_entries
                if entry["titulo"]["id"] == title_id
            ),
            None,
        )
        copy_id = None
        if title_entry is not None:
            copy = next(
                (
                    item
                    for item in title_entry["exemplares"]
                    if item["estado"] == "disponivel"
                ),
                None,
            )
            if copy is not None:
                copy_id = copy["id"]
        if copy_id is None:
            self.circulation_message = (
                "Não há exemplar disponível para oferecer neste momento."
            )
            self.circulation_has_error = True
            return
        await self._perform_circulation_action(
            lambda: offer_next_reservation(
                title_id,
                copy_id,
                self._session_token,
            ),
            "Oferta registrada para a próxima reserva elegível da fila.",
        )

    @rx.event
    async def circulation_pickup_reservation(self, reservation_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._perform_circulation_action(
            lambda: register_reservation_pickup(
                reservation_id,
                self._session_token,
            ),
            "Retirada da reserva registrada; empréstimo com prazo de 14 dias.",
        )

    @rx.event
    async def circulation_refuse_reservation(self, reservation_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._perform_circulation_action(
            lambda: refuse_reservation(reservation_id, self._session_token),
            "Reserva aguardando recusada.",
        )

    @rx.event
    async def circulation_return_loan(self, loan_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._perform_circulation_action(
            lambda: register_loan_return(loan_id, self._session_token),
            "Devolução registrada.",
        )

    @rx.event
    def acknowledge_staff_reservation_check(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.staff_reservation_pending:
            self.staff_reservation_message = "Aguarde a operação atual."
            self.staff_reservation_has_error = True
            return
        self.staff_reservation_needs_manual_check = False
        self.staff_reservation_message = (
            "A verificação foi confirmada. Você pode iniciar uma nova busca."
        )
        self.staff_reservation_has_error = False

    async def _load_catalog_categories(self):
        self.catalog_categories_skipped = 0
        try:
            categories = await list_categories()
            self.catalog_categories = categories
            self.catalog_categories_skipped = getattr(
                categories,
                "skipped_count",
                0,
            )
        except (XanoConfigurationError, XanoRequestError, XanoResponseError) as error:
            self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return
        self.catalog_has_error = False

    @rx.event
    async def load_catalog_categories(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._load_catalog_categories()

    @rx.event
    @diagnosticar_pagina_xano("acervo")
    async def load_catalog_page(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._load_catalog_categories()
        if not self.catalog_has_error:
            await self._refresh_admin_catalog()
            return State.resolve_public_catalog_covers

    async def _refresh_admin_catalog(self):
        self.admin_catalog_pending = True
        self.admin_catalog_has_error = False
        self.admin_catalog_skipped = 0
        try:
            entries = await list_admin_catalog(self._session_token)
            self.admin_catalog_entries = entries
            self.admin_catalog_skipped = getattr(
                entries,
                "skipped_count",
                0,
            )
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            message = catalog_error_message(error)
            self.admin_catalog_message = message
            self.admin_catalog_has_error = True
        finally:
            self.admin_catalog_pending = False

    @rx.event
    def set_admin_catalog_search(self, value: str):
        self.admin_catalog_search = value
        self.admin_catalog_visible_limit = 10
        self.admin_catalog_edit_title_id = None
        self.admin_catalog_copy_title_id = None

    @rx.event
    def set_admin_catalog_show_inactive(self, value: bool):
        self.admin_catalog_show_inactive = value
        self.admin_catalog_visible_limit = 10
        self.admin_catalog_edit_title_id = None
        self.admin_catalog_copy_title_id = None

    @rx.event
    def show_more_admin_catalog(self):
        self.admin_catalog_visible_limit += 10

    @rx.event
    def open_admin_new_title(self):
        self.admin_catalog_new_title_open = True
        self.admin_catalog_edit_title_id = None
        self.admin_catalog_copy_title_id = None

    @rx.event
    def close_admin_new_title(self):
        self.admin_catalog_new_title_open = False

    @rx.event
    def open_admin_title_edit(self, title_id: int):
        self.admin_catalog_edit_title_id = (
            None if self.admin_catalog_edit_title_id == title_id else title_id
        )
        self.admin_catalog_copy_title_id = None
        self.admin_catalog_new_title_open = False

    @rx.event
    def close_admin_title_edit(self):
        self.admin_catalog_edit_title_id = None

    @rx.event
    def toggle_admin_title_copies(self, title_id: int):
        self.admin_catalog_copy_title_id = (
            None if self.admin_catalog_copy_title_id == title_id else title_id
        )
        self.admin_catalog_edit_title_id = None
        self.admin_catalog_new_title_open = False

    @rx.event
    async def refresh_admin_catalog(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        self.admin_catalog_message = ""
        await self._refresh_admin_catalog()

    @rx.event
    @diagnosticar_pagina_xano("perfil_diagnostico")
    async def test_xano_connection(self):
        if not self._session_token:
            return rx.redirect("/login")
        if self._session_profile not in {"estudante", "bibliotecario", "admin"}:
            return rx.redirect("/")
        if self.connection_test_pending:
            return

        self.connection_test_pending = True
        self.connection_test_has_error = False
        self.connection_test_message = "Testando..."
        self.connection_diagnostic_results = []
        self.connection_diagnostic_report = ""
        try:
            with contexto_evento_xano("testar_conexao", self._session_profile):
                results = await diagnose_xano(
                    self._session_profile,
                    self._session_token,
                )
            self.connection_diagnostic_results = results
            self.connection_diagnostic_report = format_xano_diagnostic_report(
                results
            )
        finally:
            self.connection_test_pending = False

        successful = sum(
            result["status"] == "HTTP 200"
            and result["validation"] == "válida"
            for result in results
        )
        slowest_ms = max(
            (result["duration_ms"] for result in results),
            default=0,
        )
        self.connection_test_has_error = successful != len(results)
        limit_hint = (
            " O Xano limitou as chamadas se algum resultado for HTTP 429."
            if any(result["status"] == "HTTP 429" for result in results)
            else ""
        )
        self.connection_test_message = (
            f"{successful} de {len(results)} leituras foram validadas. "
            f"A mais lenta levou {slowest_ms} ms.{limit_hint}"
        )

    @rx.event
    async def preview_example_books(self):
        if not self._is_admin():
            return self._redirect_non_admin()
        if self.example_seed_pending:
            self.example_seed_message = "Aguarde a operação atual do acervo."
            self.example_seed_has_error = True
            return

        self.example_seed_pending = True
        self.example_seed_preview_ready = False
        self.example_seed_message = ""
        self.example_seed_has_error = False
        try:
            entries = await list_admin_catalog(self._session_token)
            categories = await list_categories()
            plan = _example_book_plan(entries, categories, TITULOS_EXEMPLO)
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.example_seed_message = catalog_error_message(error)
            self.example_seed_has_error = True
        else:
            self.example_seed_preview_create_count = len(plan["criar"])
            self.example_seed_preview_existing_count = plan["existentes"]
            self.example_seed_missing_categories = plan["categorias_ausentes"]
            self.example_seed_preview_ready = True
        finally:
            self.example_seed_pending = False

    @rx.event
    def request_example_books_import(self):
        if not self._is_admin():
            return self._redirect_non_admin()
        if self.example_seed_pending:
            self.example_seed_message = "Aguarde a operação atual do acervo."
            self.example_seed_has_error = True
            return
        self.example_seed_confirming = True

    @rx.event
    def cancel_example_books_import(self):
        if not self._is_admin():
            return self._redirect_non_admin()
        self.example_seed_confirming = False

    @rx.event
    async def continue_example_books_import(self):
        if not self._is_admin():
            return self._redirect_non_admin()
        if not self.example_seed_can_resume or self.example_seed_pending:
            return
        await self.confirm_example_books_import()

    @rx.event
    async def confirm_example_books_import(self):
        if not self._is_admin():
            return self._redirect_non_admin()
        if self.example_seed_pending:
            self.example_seed_message = "Aguarde a operação atual do acervo."
            self.example_seed_has_error = True
            return

        self.example_seed_confirming = False
        self.example_seed_pending = True
        start_index = (
            self.example_seed_resume_index
            if self.example_seed_can_resume
            else 1
        )
        self.example_seed_progress = start_index - 1
        self.example_seed_created = 0
        self.example_seed_ignored = 0
        self.example_seed_errors = 0
        self.example_seed_can_resume = False
        self.example_seed_message = ""
        self.example_seed_has_error = False
        self.example_seed_preview_ready = False
        failure_message = ""
        write_warning = False
        plan_loaded = False

        try:
            try:
                entries = await list_admin_catalog(self._session_token)
                categories = await list_categories()
                plan = _example_book_plan(entries, categories, TITULOS_EXEMPLO)
                plan_loaded = True
            except (
                XanoConfigurationError,
                XanoRequestError,
                XanoResponseError,
            ) as error:
                self.example_seed_errors = 1
                failure_message = catalog_error_message(error)
            else:
                self.example_seed_preview_create_count = len(plan["criar"])
                self.example_seed_preview_existing_count = plan["existentes"]
                self.example_seed_missing_categories = plan["categorias_ausentes"]
                self.example_seed_preview_ready = True
                existing_pairs = plan["pares_existentes"]
                category_ids = plan["ids_categoria"]
                for index, book in enumerate(
                    TITULOS_EXEMPLO,
                    start=start_index,
                ):
                    pair = _example_book_key(book["titulo"], book["autores"])
                    if pair in existing_pairs:
                        self.example_seed_ignored += 1
                        self.example_seed_progress = index
                        continue

                    category_id = category_ids.get(
                        _catalog_search_key(" ".join(book["categoria"].split()))
                    )
                    if category_id is None:
                        self.example_seed_ignored += 1
                        self.example_seed_progress = index
                        continue

                    try:
                        payload = build_title_payload(
                            {
                                "titulo": book["titulo"],
                                "autores": book["autores"],
                                "isbn": book["isbn"],
                                "editora": book["editora"],
                                "edicao": book["edicao"],
                                "ano_publicacao": str(book["ano_publicacao"]),
                                "descricao": book["descricao"],
                            }
                        )
                        title = None
                        step_error: Exception | None = None
                        for attempt in range(3):
                            try:
                                entries = await list_admin_catalog(
                                    self._session_token
                                )
                                reconciled = _example_book_plan(
                                    entries,
                                    categories,
                                    [book],
                                )
                                if reconciled["existentes"] == 1:
                                    self.example_seed_ignored += 1
                                    existing_pairs.add(pair)
                                    title = {"id": 0}
                                    break
                                title = await create_title(
                                    payload,
                                    self._session_token,
                                )
                                break
                            except (
                                XanoTimeoutError,
                                XanoRequestError,
                                XanoResponseError,
                            ) as error:
                                step_error = error
                                if isinstance(error, XanoResponseError) and (
                                    error.status_code not in {429, 502, 503, 504}
                                ):
                                    break
                                if attempt < 2:
                                    await asyncio.sleep(1.5)
                        if title is None:
                            if step_error is not None:
                                raise step_error
                            raise XanoRequestError(
                                "Não foi possível confirmar a gravação."
                            )
                        if title["id"] == 0:
                            continue
                        self.example_seed_created += 1
                        existing_pairs.add(pair)
                        await asyncio.sleep(1.5)
                        await associate_category(
                            title["id"],
                            category_id,
                            self._session_token,
                        )
                        await asyncio.sleep(1.5)
                        for _ in range(book["exemplares"]):
                            await create_copy(title["id"], self._session_token)
                            await asyncio.sleep(1.5)
                    except XanoWriteSucceededWithUnreadableResponse:
                        write_warning = True
                        self.example_seed_progress = index
                        self.example_seed_resume_index = index
                        self.example_seed_can_resume = True
                        break
                    except (
                        CatalogValidationError,
                        XanoConfigurationError,
                        XanoRequestError,
                        XanoResponseError,
                        XanoTimeoutError,
                    ) as error:
                        self.example_seed_errors = 1
                        self.example_seed_progress = index
                        self.example_seed_resume_index = index
                        self.example_seed_can_resume = True
                        failure_message = catalog_error_message(error)
                        break
                    else:
                        self.example_seed_progress = index
        finally:
            self.example_seed_pending = False

        if plan_loaded:
            await self._refresh_admin_catalog()
        if write_warning:
            self.example_seed_message = (
                "Importação pausada. Uma gravação foi concluída, mas não foi "
                "possível ler a resposta. Confira o Acervo antes de continuar."
            )
            self.example_seed_has_error = False
            return
        error_label = "erro" if self.example_seed_errors == 1 else "erros"
        totals = (
            f"{self.example_seed_created} criados, "
            f"{self.example_seed_ignored} ignorados, "
            f"{self.example_seed_errors} {error_label}"
        )
        self.example_seed_message = f"Importação encerrada: {totals}."
        if failure_message:
            self.example_seed_message += f" {failure_message}"
        self.example_seed_has_error = self.example_seed_errors > 0

    @rx.event
    async def save_admin_title(self, form_data: dict[str, Any]):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.admin_catalog_pending:
            self.admin_catalog_message = "Aguarde a operação atual do acervo."
            self.admin_catalog_has_error = True
            return
        self.admin_catalog_message = ""

        raw_id = str(form_data.get("titulo_id", ""))
        if not raw_id.isdecimal() or int(raw_id) < 1:
            self.admin_catalog_message = "Não foi possível identificar o título."
            self.admin_catalog_has_error = True
            return

        try:
            payload = build_title_payload(
                {
                    key: str(form_data.get(key, ""))
                    for key in (
                        "titulo",
                        "autores",
                        "isbn",
                        "editora",
                        "edicao",
                        "ano_publicacao",
                        "descricao",
                        "capa_url",
                    )
                }
            )
            self.admin_catalog_pending = True
            await update_title(int(raw_id), payload, self._session_token)
        except XanoWriteSucceededWithUnreadableResponse:
            await self._refresh_admin_catalog()
            self.admin_catalog_message = (
                "Título atualizado. Não foi possível ler a resposta; "
                "confira o Acervo."
            )
            if self.admin_catalog_has_error:
                self.admin_catalog_message += (
                    " A lista também não pôde ser atualizada."
                )
            return
        except (
            CatalogValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.admin_catalog_message = catalog_error_message(error)
            self.admin_catalog_has_error = True
            return
        finally:
            self.admin_catalog_pending = False

        self.admin_catalog_message = "Título atualizado."
        self.admin_catalog_has_error = False
        await self._refresh_admin_catalog()

    @rx.event
    def request_title_deactivation(self, title_id: int):
        self.admin_catalog_confirm_title_id = title_id
        self.admin_catalog_title_action_title_id = title_id
        self.admin_catalog_title_action_message = "Confirme a desativação deste título."
        self.admin_catalog_title_action_error = False

    @rx.event
    def cancel_title_deactivation(self):
        self.admin_catalog_confirm_title_id = None
        self.admin_catalog_title_action_message = ""
        self.admin_catalog_title_action_error = False

    @rx.event
    async def set_title_active(self, title_id: int, active: bool):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.admin_catalog_pending:
            self.admin_catalog_message = "Aguarde a operação atual do acervo."
            self.admin_catalog_has_error = True
            return
        if type(title_id) is not int or title_id < 1 or type(active) is not bool:
            self.admin_catalog_message = "Não foi possível identificar o título."
            self.admin_catalog_has_error = True
            return
        if not active and self.admin_catalog_confirm_title_id != title_id:
            self.request_title_deactivation(title_id)
            return

        entry = next(
            (
                item
                for item in self.admin_catalog_entries
                if item["titulo"]["id"] == title_id
            ),
            None,
        )
        if entry is None:
            self.admin_catalog_message = "Título não encontrado no acervo."
            self.admin_catalog_has_error = True
            return

        title = entry["titulo"]
        form_data = {
            key: str(title.get(key) or "")
            for key in (
                "titulo",
                "autores",
                "isbn",
                "editora",
                "edicao",
                "descricao",
                "capa_url",
            )
        }
        year = title.get("ano_publicacao")
        form_data["ano_publicacao"] = str(year) if year is not None else ""
        payload: dict[str, Any] = {}
        update_result: object = None
        write_warning = False
        try:
            self.admin_catalog_pending = True
            self.admin_catalog_title_action_title_id = title_id
            self.admin_catalog_title_action_message = "Processando..."
            self.admin_catalog_title_action_error = False
            payload = build_title_payload(form_data)
            update_result = await update_title(
                title_id,
                payload,
                self._session_token,
                active=active,
            )
        except XanoWriteSucceededWithUnreadableResponse:
            write_warning = True
        except (
            CatalogValidationError,
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.admin_catalog_message = catalog_error_message(error)
            self.admin_catalog_has_error = True
            self.admin_catalog_title_action_title_id = title_id
            self.admin_catalog_title_action_message = catalog_error_message(error)
            self.admin_catalog_title_action_error = True
            self.admin_catalog_confirm_title_id = None
            _diagnostico_desativacao(
                title_id=title_id,
                status_code=(
                    error.status_code
                    if isinstance(error, XanoResponseError)
                    else 0
                ),
                body_keys=sorted(payload.keys()),
                response_keys=[],
                active_sent=active,
                active_response=None,
                active_reloaded=None,
            )
            return
        finally:
            self.admin_catalog_pending = False

        await self._refresh_admin_catalog()
        refreshed_entry = next(
            (
                item
                for item in self.admin_catalog_entries
                if item["titulo"]["id"] == title_id
            ),
            None,
        )

        if write_warning:
            active_reloaded = (
                refreshed_entry["titulo"].get("ativo")
                if refreshed_entry is not None
                else None
            )
            _diagnostico_desativacao(
                title_id=title_id,
                status_code=200,
                body_keys=sorted(payload.keys()),
                response_keys=[],
                active_sent=active,
                active_response=None,
                active_reloaded=active_reloaded,
            )
            self.admin_catalog_message = (
                "Título atualizado. Não foi possível ler a resposta; "
                "confira o Acervo."
            )
            if self.admin_catalog_has_error:
                self.admin_catalog_message += (
                    " A lista também não pôde ser atualizada."
                )
            self.admin_catalog_confirm_title_id = None
            self.admin_catalog_title_action_title_id = title_id
            self.admin_catalog_title_action_message = self.admin_catalog_message
            self.admin_catalog_title_action_error = self.admin_catalog_has_error
            return

        if self.admin_catalog_has_error:
            _diagnostico_desativacao(
                title_id=title_id,
                status_code=200,
                body_keys=sorted(payload.keys()),
                response_keys=(
                    sorted(update_result.keys())
                    if isinstance(update_result, dict)
                    else []
                ),
                active_sent=active,
                active_response=(
                    update_result.get("ativo")
                    if isinstance(update_result, dict)
                    else None
                ),
                active_reloaded=None,
            )
            self.admin_catalog_message = (
                "Não foi possível confirmar a atualização do título após a resposta "
                "do servidor."
            )
            self.admin_catalog_title_action_title_id = title_id
            self.admin_catalog_title_action_message = (
                "Não foi possível confirmar a atualização do título."
            )
            self.admin_catalog_title_action_error = True
            return

        if refreshed_entry is None:
            _diagnostico_desativacao(
                title_id=title_id,
                status_code=200,
                body_keys=sorted(payload.keys()),
                response_keys=(
                    sorted(update_result.keys())
                    if isinstance(update_result, dict)
                    else []
                ),
                active_sent=active,
                active_response=(
                    update_result.get("ativo")
                    if isinstance(update_result, dict)
                    else None
                ),
                active_reloaded=None,
            )
            self.admin_catalog_message = (
                "Não foi possível confirmar a atualização do título após a resposta "
                "do servidor."
            )
            self.admin_catalog_title_action_title_id = title_id
            self.admin_catalog_title_action_message = (
                "Não foi possível confirmar a atualização do título."
            )
            self.admin_catalog_title_action_error = True
            return

        refreshed_active = (
            refreshed_entry["titulo"].get("ativo") is not False
        )
        if refreshed_active != active:
            active_response = (
                update_result.get("ativo")
                if isinstance(update_result, dict)
                and type(update_result.get("ativo")) is bool
                else None
            )
            reference = registrar_resultado_xano(
                action="desativar_titulo" if not active else "reativar_titulo",
                profile="bibliotecario",
                method="PATCH",
                path=f"/catalogo/titulos/{title_id}",
                status=200,
                result="valor ativo diverge após PATCH e releitura",
                sent_keys=tuple(sorted((*payload.keys(), "ativo"))),
                active_diagnostics=(
                    active,
                    active_response,
                    refreshed_active,
                ),
            )
            _diagnostico_desativacao(
                title_id=title_id,
                status_code=200,
                body_keys=sorted(payload.keys()),
                response_keys=(
                    sorted(update_result.keys())
                    if isinstance(update_result, dict)
                    else []
                ),
                active_sent=active,
                active_response=active_response,
                active_reloaded=refreshed_active,
            )
            if not active:
                self.admin_catalog_message = (
                    "O servidor respondeu, mas o título continua ativo. "
                    "A atualização do servidor pode não estar publicada. "
                    f"(ref. {reference})"
                )
            else:
                self.admin_catalog_message = (
                    "O servidor respondeu, mas o título continua desativado. "
                    "A atualização do servidor pode não estar publicada. "
                    f"(ref. {reference})"
                )
            self.admin_catalog_has_error = True
            self.admin_catalog_confirm_title_id = None
            self.admin_catalog_title_action_title_id = title_id
            self.admin_catalog_title_action_message = (
                self.admin_catalog_message
            )
            self.admin_catalog_title_action_error = True
            return

        _diagnostico_desativacao(
            title_id=title_id,
            status_code=200,
            body_keys=sorted(payload.keys()),
            response_keys=(
                sorted(update_result.keys())
                if isinstance(update_result, dict)
                else []
            ),
            active_sent=active,
            active_response=(
                update_result.get("ativo")
                if isinstance(update_result, dict)
                else None
            ),
            active_reloaded=refreshed_active,
        )
        self.admin_catalog_message = (
            "Título reativado." if active else "Título desativado."
        )
        self.admin_catalog_has_error = False
        self.admin_catalog_confirm_title_id = None
        self.admin_catalog_title_action_title_id = title_id
        self.admin_catalog_title_action_message = self.admin_catalog_message
        self.admin_catalog_title_action_error = False

    @rx.event
    async def add_copy_to_title(self, title_id: int):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.admin_catalog_pending:
            self.admin_catalog_message = "Aguarde a operação atual do acervo."
            self.admin_catalog_has_error = True
            return
        if self.admin_catalog_needs_manual_check:
            self.admin_catalog_message = (
                "Confira os exemplares no acervo antes de iniciar outra criação."
            )
            self.admin_catalog_has_error = True
            return
        if type(title_id) is not int or title_id < 1:
            self.admin_catalog_message = "Não foi possível identificar o título."
            self.admin_catalog_has_error = True
            return

        self.admin_catalog_pending = True
        try:
            await create_copy(title_id, self._session_token)
        except XanoWriteSucceededWithUnreadableResponse:
            await self._refresh_admin_catalog()
            self.admin_catalog_message = (
                "Exemplar criado. Não foi possível ler a resposta; "
                "confira o Acervo."
            )
            if self.admin_catalog_has_error:
                self.admin_catalog_message += (
                    " A lista também não pôde ser atualizada."
                )
            return
        except XanoResponseError as error:
            if error.status_code >= 500:
                self.admin_catalog_needs_manual_check = True
                self.admin_catalog_message = (
                    "O resultado da criação do exemplar é incerto. Confira o acervo "
                    "antes de iniciar outra criação."
                )
                self.admin_catalog_has_error = True
                return
            self.admin_catalog_message = catalog_error_message(error)
            self.admin_catalog_has_error = True
            return
        except XanoRequestError:
            self.admin_catalog_needs_manual_check = True
            self.admin_catalog_message = (
                "O resultado da criação do exemplar é incerto. Confira o acervo "
                "antes de iniciar outra criação."
            )
            self.admin_catalog_has_error = True
            return
        except XanoConfigurationError as error:
            self.admin_catalog_message = catalog_error_message(error)
            self.admin_catalog_has_error = True
            return
        finally:
            self.admin_catalog_pending = False

        self.admin_catalog_message = "Exemplar adicionado."
        self.admin_catalog_has_error = False
        await self._refresh_admin_catalog()

    @rx.event
    def acknowledge_admin_catalog_check(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self.admin_catalog_pending:
            self.admin_catalog_message = "Aguarde a operação atual do acervo."
            self.admin_catalog_has_error = True
            return
        if self.admin_catalog_needs_manual_check:
            self.admin_catalog_needs_manual_check = False
            self.admin_catalog_message = (
                "Operações liberadas. Confira os exemplares antes de criar novamente."
            )
            self.admin_catalog_has_error = False

    @rx.event
    def toggle_catalog_category(self, category_id: int, selected: bool):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if not any(item["id"] == category_id for item in self.catalog_categories):
            return
        if selected and category_id not in self.selected_category_ids:
            self.selected_category_ids.append(category_id)
        elif not selected and category_id in self.selected_category_ids:
            self.selected_category_ids.remove(category_id)

    @rx.event
    async def submit_catalog_title(self, form_data: dict[str, Any]):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self._catalog_title_uncertain or self._catalog_title_id is not None:
            self.catalog_has_error = True
            self.catalog_message = (
                "Conclua ou confira o cadastro atual antes de iniciar outro título."
            )
            return

        self.catalog_message = ""
        self.catalog_has_error = False
        self.catalog_needs_manual_check = False
        try:
            payload = build_title_payload(form_data)
        except CatalogValidationError as error:
            self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return

        try:
            title = await create_title(payload, self._session_token)
        except XanoWriteSucceededWithUnreadableResponse:
            await self._refresh_admin_catalog()
            self.catalog_message = (
                "Título enviado. Não foi possível ler a resposta; confira o "
                "Acervo antes de cadastrar novamente."
            )
            self.catalog_has_error = False
            return
        except XanoResponseError as error:
            if error.status_code >= 500:
                self._catalog_title_uncertain = True
                self.catalog_needs_manual_check = True
                self.catalog_message = (
                    "O resultado do cadastro do título é incerto. Confira o acervo "
                    "antes de iniciar outro cadastro."
                )
            else:
                self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return
        except XanoConfigurationError as error:
            self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return
        except XanoRequestError:
            self._catalog_title_uncertain = True
            self.catalog_needs_manual_check = True
            self.catalog_message = (
                "O resultado do cadastro do título é incerto. Confira o acervo "
                "antes de iniciar outro cadastro."
            )
            self.catalog_has_error = True
            return

        self._catalog_title_id = title["id"]
        self.catalog_title_created = True
        self._pending_category_ids = list(self.selected_category_ids)
        self._sync_catalog_progress()
        write_warning = await self._process_pending_categories()
        if (
            write_warning
            or (
                not self.catalog_categories_pending
                and not self.catalog_has_error
            )
        ):
            await self._refresh_admin_catalog()

    async def _process_pending_categories(self) -> bool:
        if self._catalog_title_id is None:
            return False
        write_warning = False
        for category_id in list(self._pending_category_ids):
            try:
                await associate_category(
                    self._catalog_title_id,
                    category_id,
                    self._session_token,
                )
            except XanoConfigurationError as error:
                self.catalog_message = catalog_error_message(error)
                self.catalog_has_error = True
                break
            except XanoWriteSucceededWithUnreadableResponse:
                write_warning = True
                self._pending_category_ids.remove(category_id)
                self._sync_catalog_progress()
                break
            except XanoRequestError as error:
                try:
                    associated = await category_contains_title(
                        category_id,
                        self._catalog_title_id,
                    )
                except (XanoConfigurationError, XanoRequestError):
                    if category_id not in self._uncertain_category_ids:
                        self._uncertain_category_ids.append(category_id)
                    self._sync_catalog_progress()
                    self.catalog_needs_manual_check = True
                    self.catalog_message = (
                        "Não foi possível confirmar uma associação. Confira o título "
                        "antes de repetir a etapa."
                    )
                    self.catalog_has_error = True
                    break

                if associated:
                    self._pending_category_ids.remove(category_id)
                    if category_id in self._uncertain_category_ids:
                        self._uncertain_category_ids.remove(category_id)
                    continue

                if isinstance(error, XanoResponseError):
                    if error.status_code >= 500 and category_id not in self._uncertain_category_ids:
                        self._uncertain_category_ids.append(category_id)
                        self.catalog_needs_manual_check = True
                self._sync_catalog_progress()
                self.catalog_message = catalog_error_message(error)
                self.catalog_has_error = True
                break

            self._pending_category_ids.remove(category_id)
            if category_id in self._uncertain_category_ids:
                self._uncertain_category_ids.remove(category_id)
            self._sync_catalog_progress()

        self._sync_catalog_progress()
        if write_warning:
            self.catalog_message = (
                "Categoria associada. Não foi possível ler a resposta; "
                "confira o Acervo."
            )
            self.catalog_has_error = False
            self.catalog_needs_manual_check = False
        elif not self.catalog_categories_pending:
            self.catalog_message = "Título e categorias cadastrados."
            self.catalog_has_error = False
            self.catalog_needs_manual_check = False
        return write_warning

    @rx.event
    async def retry_catalog_categories(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if self._catalog_title_id is None or self._catalog_title_uncertain:
            return
        for category_id in list(self._uncertain_category_ids):
            try:
                associated = await category_contains_title(
                    category_id,
                    self._catalog_title_id,
                )
            except (XanoConfigurationError, XanoRequestError):
                self.catalog_message = (
                    "Ainda não foi possível confirmar a associação. Tente novamente "
                    "ou confira o acervo."
                )
                self.catalog_has_error = True
                self.catalog_needs_manual_check = True
                return
            self._uncertain_category_ids.remove(category_id)
            if associated and category_id in self._pending_category_ids:
                self._pending_category_ids.remove(category_id)
            self._sync_catalog_progress()
        self.catalog_needs_manual_check = False
        self.catalog_has_error = False
        write_warning = await self._process_pending_categories()
        if (
            write_warning
            or (
                not self.catalog_categories_pending
                and not self.catalog_has_error
            )
        ):
            await self._refresh_admin_catalog()

    @rx.event
    async def create_catalog_copy(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if (
            self._catalog_title_id is None
            or self._catalog_title_uncertain
            or self._catalog_copy_uncertain
            or self._pending_category_ids
            or self._uncertain_category_ids
        ):
            self.catalog_message = (
                "Conclua ou confira as etapas anteriores antes de criar exemplares."
            )
            self.catalog_has_error = True
            return

        try:
            copy = await create_copy(self._catalog_title_id, self._session_token)
        except XanoWriteSucceededWithUnreadableResponse:
            await self._refresh_admin_catalog()
            self.catalog_message = (
                "Exemplar criado. Não foi possível ler a resposta; confira o "
                "Acervo."
            )
            self.catalog_has_error = False
            return
        except XanoResponseError as error:
            if error.status_code >= 500:
                self._catalog_copy_uncertain = True
                self.catalog_needs_manual_check = True
                self.catalog_message = (
                    "O resultado da criação do exemplar é incerto. Confira o acervo "
                    "antes de solicitar outro."
                )
            else:
                self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return
        except XanoConfigurationError as error:
            self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return
        except XanoRequestError:
            self._catalog_copy_uncertain = True
            self.catalog_needs_manual_check = True
            self.catalog_message = (
                "O resultado da criação do exemplar é incerto. Confira o acervo "
                "antes de solicitar outro."
            )
            self.catalog_has_error = True
            return

        self.catalog_created_codes.append(copy["codigo_tombo"])
        self.catalog_message = "Exemplar criado."
        self.catalog_has_error = False
        await self._refresh_admin_catalog()

    @rx.event
    def start_new_catalog_title(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        if (
            self._pending_category_ids
            or self._uncertain_category_ids
            or self._catalog_title_uncertain
            or self._catalog_copy_uncertain
        ):
            self.catalog_message = (
                "Confira as etapas pendentes antes de iniciar outro título."
            )
            self.catalog_has_error = True
            return
        self._catalog_title_id = None
        self._pending_category_ids = []
        self._uncertain_category_ids = []
        self.catalog_title_created = False
        self.catalog_created_codes = []
        self.selected_category_ids = []
        self.catalog_message = ""
        self.catalog_has_error = False
        self.catalog_needs_manual_check = False
        return rx.call_script(
            "document.getElementById('form-cadastro-titulo')?.reset()"
        )


def site_primary_nav() -> rx.Component:
    return rx.el.nav(
        rx.link(
            rx.el.span("🔎", aria_hidden="true"),
            rx.text(" Catálogo"),
            href="/catalogo",
            class_name="site-nav-link",
        ),
        rx.cond(
            State.active_navigation_role == "Estudante",
            rx.link(
                rx.el.span("🙋", aria_hidden="true"),
                rx.text(" Reservas"),
                href="/reservas",
                class_name="site-nav-link",
            ),
            rx.fragment(),
        ),
        rx.cond(
            State.active_navigation_role == "Bibliotecária",
            rx.fragment(
                rx.link(
                    rx.el.span("🗂️", aria_hidden="true"),
                    rx.text(" Acervo"),
                    href="/admin/acervo",
                    class_name="site-nav-link",
                ),
                rx.link(
                    rx.el.span("📬", aria_hidden="true"),
                    rx.text(" Reservas"),
                    href="/admin/reservas",
                    class_name="site-nav-link",
                ),
            ),
            rx.cond(
                State.active_navigation_role == "Admin",
                    rx.fragment(
                        rx.link(
                            rx.el.span("👥", aria_hidden="true"),
                            rx.text(" Contas"),
                            href="/admin/bibliotecarios",
                            class_name="site-nav-link",
                        ),
                        rx.cond(
                            State.admin_view_mode == "bibliotecaria",
                            rx.fragment(
                                rx.link(
                                    rx.el.span("🗂️", aria_hidden="true"),
                                    rx.text(" Acervo"),
                                    href="/admin/acervo",
                                    class_name="site-nav-link",
                                ),
                                rx.link(
                                    rx.el.span("📬", aria_hidden="true"),
                                    rx.text(" Reservas"),
                                    href="/admin/reservas",
                                    class_name="site-nav-link",
                                ),
                            ),
                            rx.cond(
                                State.admin_view_mode == "estudante",
                                rx.link(
                                    rx.el.span("🙋", aria_hidden="true"),
                                    rx.text(" Reservas"),
                                    href="/reservas",
                                    class_name="site-nav-link",
                                ),
                                rx.fragment(),
                            ),
                        ),
                    ),
                rx.fragment(),
            ),
        ),
        aria_label="Navegação principal",
        class_name="site-primary-nav",
    )


def admin_view_status() -> rx.Component:
    return rx.cond(
        State.can_manage_librarians & (State.admin_view_mode != ""),
        rx.el.div(
            rx.el.div(
                "Modo de visualização: ",
                rx.cond(
                    State.admin_view_mode == "estudante",
                    "Estudante",
                    rx.cond(
                        State.admin_view_mode == "bibliotecaria",
                        "Bibliotecária",
                        "Administrador",
                    ),
                ),
                role="status",
                aria_live="polite",
                class_name="admin-view-mode-label",
            ),
            rx.cond(
                State.admin_view_mode != "",
                rx.button(
                    conteudo_acao("restaurar_visao"),
                    type="button",
                    on_click=State.reset_admin_view_mode,
                    class_name="admin-view-reset",
                    **atributos_acao("restaurar_visao"),
                ),
                rx.fragment(),
            ),
            role="group",
            aria_label="Modo de visualização atual",
            class_name="admin-view-band",
        ),
        rx.fragment(),
    )


_APPEARANCE_SCRIPT = r"""
(() => {
  if (window.__bibliotecaAppearanceInstalled) return;
  window.__bibliotecaAppearanceInstalled = true;
  const hideFailedCover = (image) => {
    if (!image.complete || image.naturalWidth !== 0 ||
        !image.getAttribute("src")) return;
    image.style.display = "none";
    image.closest(".catalog-cover-stack")
      ?.classList.add("catalog-cover-real-failed");
  };
  const scanCoverImages = (root) => {
    if (root instanceof HTMLImageElement) hideFailedCover(root);
    if (!root || typeof root.querySelectorAll !== "function") return;
    root.querySelectorAll("img.catalog-real-cover-image")
      .forEach(hideFailedCover);
  };
  document.addEventListener("error", (event) => {
    const image = event.target;
    if (image instanceof HTMLImageElement &&
        image.classList.contains("catalog-real-cover-image")) {
      hideFailedCover(image);
    }
  }, true);
  const coverObserver = new MutationObserver((records) => {
    records.forEach((record) => {
      record.addedNodes.forEach(scanCoverImages);
      if (record.type === "attributes") scanCoverImages(record.target);
    });
  });
  coverObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class", "src"],
    childList: true,
    subtree: true
  });
  const scanExistingCoverImages = () => scanCoverImages(document);
  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      scanExistingCoverImages,
      { once: true }
    );
  } else {
    scanExistingCoverImages();
  }
  const key = "biblioteca-aparencia";
  const legacyKeys = [
    "biblioteca-acessibilidade-fonte",
    "biblioteca-acessibilidade-contraste",
    "biblioteca-acessibilidade-movimento"
  ];
  const defaults = {
    theme: "system",
    fontScale: 100,
    highContrast: false,
    reduceMotion: false
  };
  const normalize = (value) => {
    const source = value && typeof value === "object" ? value : {};
    const scale = Number(source.fontScale);
    return {
      theme: ["system", "dark", "light"].includes(source.theme)
        ? source.theme : "system",
      fontScale: Number.isInteger(scale) && scale >= 100 &&
        scale <= 150 && scale % 10 === 0 ? scale : 100,
      highContrast: source.highContrast === true,
      reduceMotion: source.reduceMotion === true
    };
  };
  const load = () => {
    try {
      const saved = window.localStorage.getItem(key);
      if (saved !== null) {
        const preferences = normalize(JSON.parse(saved));
        const sanitized = JSON.stringify(preferences);
        if (saved !== sanitized) window.localStorage.setItem(key, sanitized);
        return preferences;
      }
      const migrated = { ...defaults };
      const oldFont = window.localStorage.getItem(legacyKeys[0]);
      const oldContrast = window.localStorage.getItem(legacyKeys[1]);
      const oldMotion = window.localStorage.getItem(legacyKeys[2]);
      const hasLegacy = oldFont !== null || oldContrast !== null ||
        oldMotion !== null;
      if (oldFont !== null) migrated.fontScale = Number(oldFont);
      if (oldContrast !== null) migrated.highContrast = oldContrast === "true";
      if (oldMotion !== null) migrated.reduceMotion = oldMotion === "true";
      const preferences = normalize(migrated);
      if (hasLegacy) {
        window.localStorage.setItem(key, JSON.stringify(preferences));
        legacyKeys.forEach((oldKey) => window.localStorage.removeItem(oldKey));
      }
      return preferences;
    } catch {
      return { ...defaults };
    }
  };
  let preferences = load();
  const colorScheme = window.matchMedia("(prefers-color-scheme: dark)");
  const save = () => {
    try {
      window.localStorage.setItem(key, JSON.stringify(normalize(preferences)));
    } catch {}
  };
  const setText = (element, value) => {
    if (element && element.textContent !== value) element.textContent = value;
  };
  window.__bibliotecaDisclosureInstalled = true;
  const syncControls = () => {
    document.querySelectorAll("[data-appearance-action]").forEach((button) => {
      const action = button.getAttribute("data-appearance-action");
      if (action === "font-decrease") button.disabled = preferences.fontScale <= 100;
      if (action === "font-increase") button.disabled = preferences.fontScale >= 150;
      if (action === "font-reset") {
        setText(button.querySelector("[data-appearance-font-value]"),
          `${preferences.fontScale}%`);
      }
      if (action === "high-contrast") {
        const enabled = preferences.highContrast;
        const state = enabled ? "Ligado" : "Desligado";
        const status = button.querySelector(
          `[data-appearance-value="${action}"]`
        );
        if (status) setText(status, state);
        const label = status
          ? `Alto contraste: ${state}`
          : enabled ? "Alto contraste ativo" : "Ativar alto contraste";
        setText(button.querySelector("[data-action-label]"), label);
        button.setAttribute("aria-label", label);
        button.setAttribute("title", label);
        if (button.getAttribute("role") === "switch") {
          button.setAttribute("aria-checked", String(enabled));
        } else {
          button.setAttribute("aria-pressed", String(enabled));
        }
      }
      if (action === "reduce-motion") {
        const enabled = preferences.reduceMotion;
        const state = enabled ? "Ligado" : "Desligado";
        const status = button.querySelector(
          `[data-appearance-value="${action}"]`
        );
        if (status) setText(status, state);
        const label = status
          ? `Reduzir movimento: ${state}`
          : enabled ? "Movimento reduzido" : "Reduzir movimento";
        setText(button.querySelector("[data-action-label]"), label);
        button.setAttribute("aria-label", label);
        button.setAttribute("title", label);
        if (button.getAttribute("role") === "switch") {
          button.setAttribute("aria-checked", String(enabled));
        } else {
          button.setAttribute("aria-pressed", String(enabled));
        }
      }
      if (action === "theme") {
        const dark = preferences.theme === "dark" ||
          (preferences.theme === "system" && colorScheme.matches);
        const label = dark ? "Modo claro" : "Modo escuro";
        const status = button.querySelector("[data-appearance-value='theme']");
        if (status) {
          setText(status, dark ? "Ligado" : "Desligado");
        }
        const accessibleLabel = status
          ? `Modo escuro: ${dark ? "Ligado" : "Desligado"}`
          : label;
        setText(
          button.querySelector("[data-appearance-theme-label]"),
          label
        );
        button.setAttribute("aria-label", accessibleLabel);
        button.setAttribute("title", accessibleLabel);
        const emoji = button.querySelector("[data-appearance-theme-emoji]");
        if (emoji) setText(emoji, dark ? "☀️" : "🌙");
        button.setAttribute("aria-checked", String(dark));
      }
    });
  };
  const syncCurrentNav = () => {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    document.querySelectorAll(".site-nav-link").forEach((link) => {
      const target = (link.getAttribute("href") || "").replace(/\/+$/, "") || "/";
      if (target === path || (target === "/catalogo" && path.startsWith("/catalogo"))) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  };
  const apply = () => {
    const dark = preferences.theme === "dark" ||
      (preferences.theme === "system" && colorScheme.matches);
    document.querySelectorAll(".a11y-shell").forEach((shell) => {
      shell.classList.toggle("a11y-dark", dark);
      shell.classList.toggle("a11y-light", !dark);
      shell.classList.toggle("a11y-high-contrast", preferences.highContrast);
      shell.classList.toggle("a11y-reduce-motion", preferences.reduceMotion);
      shell.style.fontSize = `${preferences.fontScale}%`;
    });
    syncControls();
    syncCurrentNav();
  };
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-appearance-action]");
    if (button) {
      const action = button.getAttribute("data-appearance-action");
      if (action === "font-decrease") {
        preferences.fontScale = Math.max(100, preferences.fontScale - 10);
      } else if (action === "font-increase") {
        preferences.fontScale = Math.min(150, preferences.fontScale + 10);
      } else if (action === "font-reset") {
        preferences.fontScale = 100;
      } else if (action === "high-contrast") {
        preferences.highContrast = !preferences.highContrast;
      } else if (action === "reduce-motion") {
        preferences.reduceMotion = !preferences.reduceMotion;
      } else if (action === "theme") {
        const dark = preferences.theme === "dark" ||
          (preferences.theme === "system" && colorScheme.matches);
        preferences.theme = dark ? "light" : "dark";
      } else {
        return;
      }
      save();
      apply();
    }
    document.querySelectorAll("details.site-disclosure[open]").forEach((item) => {
      if (!item.contains(event.target)) item.open = false;
    });
  });
  document.addEventListener("toggle", (event) => {
    const disclosure = event.target;
    if (!(disclosure instanceof HTMLDetailsElement) ||
        !disclosure.matches("details.site-disclosure") || !disclosure.open) {
      return;
    }
    document.querySelectorAll("details.site-disclosure[open]").forEach((item) => {
      if (item !== disclosure) item.open = false;
    });
  }, true);
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const disclosure = document.querySelector("details.site-disclosure[open]");
    if (!disclosure) return;
    document.querySelectorAll("details.site-disclosure[open]").forEach((item) => {
      item.open = false;
    });
    disclosure.querySelector("summary")?.focus();
    event.preventDefault();
  });
  colorScheme.addEventListener("change", () => {
    if (preferences.theme === "system") apply();
  });
  window.addEventListener("storage", (event) => {
    if (event.key !== key || event.newValue === null) return;
    try {
      preferences = normalize(JSON.parse(event.newValue));
    } catch {
      preferences = { ...defaults };
    }
    apply();
  });
  new MutationObserver(apply).observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["class"]
  });
  apply();
})();
"""


def profile_appearance_controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                "Tamanho da fonte",
                class_name="accessibility-setting-label",
            ),
            rx.el.div(
                rx.button(
                    "A−",
                    type="button",
                    data_appearance_action="font-decrease",
                    aria_label="Diminuir fonte",
                    title="Diminuir fonte",
                    class_name="appearance-font-button",
                ),
                rx.button(
                    rx.el.span(
                        "100%",
                        data_appearance_font_value="true",
                    ),
                    type="button",
                    data_appearance_action="font-reset",
                    aria_label="Restaurar fonte padrão",
                    title="Restaurar fonte padrão",
                    class_name="appearance-font-button",
                ),
                rx.button(
                    "A+",
                    type="button",
                    data_appearance_action="font-increase",
                    aria_label="Aumentar fonte",
                    title="Aumentar fonte",
                    class_name="appearance-font-button",
                ),
                class_name="appearance-font-controls",
            ),
            class_name="accessibility-setting-row",
        ),
        rx.el.div(
            rx.el.span(
                "Alto contraste",
                class_name="accessibility-setting-label",
            ),
            rx.button(
                rx.el.span(
                    "Desligado",
                    data_appearance_value="high-contrast",
                ),
                type="button",
                role="switch",
                aria_checked=False,
                aria_label="Alto contraste",
                title="Alto contraste",
                data_appearance_action="high-contrast",
                class_name="appearance-switch",
            ),
            class_name="accessibility-setting-row",
        ),
        rx.el.div(
            rx.el.span(
                "Reduzir movimento",
                class_name="accessibility-setting-label",
            ),
            rx.button(
                rx.el.span(
                    "Desligado",
                    data_appearance_value="reduce-motion",
                ),
                type="button",
                role="switch",
                aria_checked=False,
                aria_label="Reduzir movimento",
                title="Reduzir movimento",
                data_appearance_action="reduce-motion",
                class_name="appearance-switch",
            ),
            class_name="accessibility-setting-row",
        ),
        rx.el.div(
            rx.el.span(
                "Modo escuro",
                class_name="accessibility-setting-label",
            ),
            rx.button(
                rx.el.span(
                    "Desligado",
                    data_appearance_value="theme",
                ),
                type="button",
                role="switch",
                aria_checked=False,
                aria_label="Modo escuro",
                title="Modo escuro",
                data_appearance_action="theme",
                class_name="appearance-switch",
            ),
            class_name="accessibility-setting-row",
        ),
        class_name="profile-appearance-controls",
    )


def profile_menu() -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            rx.cond(
                State.is_authenticated,
                conteudo_acao("perfil", State.greeting_name),
                conteudo_acao("entrar"),
            ),
            title=rx.cond(
                State.is_authenticated, State.greeting_name, "Entrar"
            ),
            aria_label=rx.cond(
                State.is_authenticated, State.greeting_name, "Entrar"
            ),
            class_name="profile-menu-trigger",
        ),
        rx.el.div(
            rx.cond(
                State.is_authenticated,
                rx.fragment(
                    rx.el.div(
                        State.greeting_name,
                        class_name="profile-menu-identity",
                    ),
                    rx.el.div(
                        State.session_email,
                        class_name="profile-menu-identity",
                    ),
                    rx.el.div(
                        State.session_role_label,
                        class_name="profile-menu-identity",
                    ),
                    rx.cond(
                        State.can_manage_librarians,
                        rx.fragment(
                            rx.el.div(
                                "Modo de visualização",
                                class_name="profile-menu-identity",
                            ),
                            rx.el.button(
                                conteudo_acao(
                                    "administrador",
                                    rx.cond(
                                        State.admin_view_mode == "",
                                        "✓ Administrador",
                                        "Administrador",
                                    ),
                                ),
                                type="button",
                                role="radio",
                                aria_checked=State.admin_view_mode == "",
                                on_click=State.reset_admin_view_mode,
                                class_name="profile-menu-item",
                                **atributos_acao(
                                    "administrador",
                                    rx.cond(
                                        State.admin_view_mode == "",
                                        "✓ Administrador",
                                        "Administrador",
                                    ),
                                ),
                            ),
                            rx.el.button(
                                conteudo_acao(
                                    "bibliotecario",
                                    rx.cond(
                                        State.admin_view_mode == "bibliotecaria",
                                        "✓ Bibliotecário",
                                        "Bibliotecário",
                                    ),
                                ),
                                type="button",
                                role="radio",
                                aria_checked=(
                                    State.admin_view_mode == "bibliotecaria"
                                ),
                                on_click=State.set_admin_view_mode(
                                    "bibliotecaria"
                                ),
                                class_name="profile-menu-item",
                                **atributos_acao(
                                    "bibliotecario",
                                    rx.cond(
                                        State.admin_view_mode == "bibliotecaria",
                                        "✓ Bibliotecário",
                                        "Bibliotecário",
                                    ),
                                ),
                            ),
                            rx.el.button(
                                conteudo_acao(
                                    "estudante",
                                    rx.cond(
                                        State.admin_view_mode == "estudante",
                                        "✓ Estudante",
                                        "Estudante",
                                    ),
                                ),
                                type="button",
                                role="radio",
                                aria_checked=(
                                    State.admin_view_mode == "estudante"
                                ),
                                on_click=State.set_admin_view_mode(
                                    "estudante"
                                ),
                                class_name="profile-menu-item",
                                **atributos_acao(
                                    "estudante",
                                    rx.cond(
                                        State.admin_view_mode == "estudante",
                                        "✓ Estudante",
                                        "Estudante",
                                    ),
                                ),
                            ),
                        ),
                        rx.fragment(),
                    ),
                    rx.button(
                        conteudo_acao("sair"),
                        type="button",
                        on_click=State.logout,
                        class_name="profile-menu-item",
                        **atributos_acao("sair"),
                    ),
                ),
                rx.fragment(
                    rx.link(
                        conteudo_acao("entrar"),
                        href="/login",
                        class_name="profile-menu-item",
                        **atributos_acao("entrar"),
                    ),
                    rx.link(
                        conteudo_acao("cadastrar"),
                        href="/cadastro",
                        class_name="profile-menu-item",
                        **atributos_acao("cadastrar"),
                    ),
                ),
            ),
            class_name="profile-menu-content",
        ),
        class_name="site-disclosure profile-menu",
    )


def accessibility_menu() -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            conteudo_acao("acessibilidade"),
            class_name="accessibility-menu-trigger",
            **atributos_acao("acessibilidade"),
        ),
        rx.el.div(
            profile_appearance_controls(),
            class_name="profile-menu-content accessibility-menu-content",
        ),
        class_name="site-disclosure accessibility-menu",
    )


def site_header() -> rx.Component:
    brand = rx.link(
        rx.el.span("📚", aria_hidden="true"),
        rx.text(" Biblioteca escolar", class_name="brand-link-label"),
        href="/",
        class_name="brand-link",
        title="Biblioteca escolar",
        aria_label="Biblioteca escolar",
    )
    header = rx.el.header(
        brand,
        site_primary_nav(),
        rx.el.form(
            rx.el.input(
                name="q",
                type="search",
                placeholder="Buscar livros…",
                value=State.public_catalog_search,
                on_change=State.set_public_catalog_search,
                aria_label="Buscar livros",
                class_name="site-header-search",
            ),
            rx.el.span("🔎", aria_hidden="true", class_name="site-header-search-icon"),
            on_submit=State.submit_global_search,
            class_name="site-header-search-form",
        ),
        rx.el.div(
            accessibility_menu(),
            profile_menu(),
            class_name="site-header-actions",
        ),
        class_name="site-header",
    )
    return rx.fragment(header, admin_view_status())


def site_footer() -> rx.Component:
    return rx.el.footer(
        rx.el.section(
            rx.text(
                rx.text(" Biblioteca escolar"),
                class_name="footer-about-title",
            ),
            class_name="footer-about",
        ),
        rx.el.nav(
            rx.link(
                "Catálogo",
                href="/catalogo",
                class_name="footer-link",
            ),
            aria_label="Links úteis",
            class_name="footer-links",
        ),
        class_name="site-footer",
    )


def _catalog_search_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


def _capa_busca_key(titulo: object, autoria: object) -> str:
    titulo_normalizado = " ".join(normalizar_texto(titulo).split())
    primeira_autoria = str(autoria or "").split(";")[0]
    autoria_normalizada = " ".join(
        normalizar_texto(primeira_autoria).split()
    )
    return f"{titulo_normalizado}\x1f{autoria_normalizada}"


def _example_book_key(title: str, authors: str) -> tuple[str, str]:
    return (
        _catalog_search_key(" ".join(title.split())),
        _catalog_search_key(" ".join(authors.split())),
    )


def _example_book_plan(
    entries: list[AdminCatalogEntry],
    categories: list[dict[str, Any]],
    books: list[dict[str, Any]],
) -> dict[str, Any]:
    existing_pairs = {
        _example_book_key(
            entry["titulo"]["titulo"],
            entry["titulo"]["autores"],
        )
        for entry in entries
    }
    category_ids = {
        _catalog_search_key(" ".join(category["nome"].split())): category["id"]
        for category in categories
    }
    creatable: list[dict[str, Any]] = []
    missing_categories: list[str] = []
    existing_count = 0
    for book in books:
        pair = _example_book_key(book["titulo"], book["autores"])
        if pair in existing_pairs:
            existing_count += 1
            continue
        category_key = _catalog_search_key(
            " ".join(book["categoria"].split())
        )
        if category_key not in category_ids:
            if book["categoria"] not in missing_categories:
                missing_categories.append(book["categoria"])
            continue
        creatable.append(book)

    return {
        "criar": creatable,
        "existentes": existing_count,
        "categorias_ausentes": missing_categories,
        "pares_existentes": existing_pairs,
        "ids_categoria": category_ids,
    }


def _catalog_cover_identity(category_text: str, title_name: str) -> tuple[str, int]:
    category_name = category_text.split(",", maxsplit=1)[0].strip()
    cover_source = (
        category_name
        if category_name and category_name != "Sem categoria"
        else title_name.strip()
    )
    initial = next(
        (character.upper() for character in cover_source if character.isalpha()),
        "?",
    )
    normalized = _catalog_search_key(cover_source)
    variant = sum(
        position * ord(character)
        for position, character in enumerate(normalized, start=1)
        if character.isalnum()
    ) % 5
    return initial, variant


def _home_catalog_cards(
    entries: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    cover_lookups: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    cover_lookups = cover_lookups or {}
    category_names = {
        category["id"]: category["nome"]
        for category in categories
    }
    cards: list[dict[str, Any]] = []
    for entry in entries:
        title = entry["titulo"]
        if title.get("ativo") is False:
            continue
        category_ids = {
            association["categoria_id"]
            for association in entry["categorias"]
        }
        category_text = ", ".join(
            category_names[category_id]
            for category_id in sorted(category_ids)
            if category_id in category_names
        ) or "Sem categoria"
        initial, variant = _catalog_cover_identity(
            category_text,
            title["titulo"],
        )
        cover_key = _capa_busca_key(title["titulo"], title["autores"])
        capa_real = (
            resolver_capa_url(
                capa_resolvida=cover_lookups[cover_key],
                isbn=title.get("isbn"),
            )
            if cover_key in cover_lookups
            else ""
        )
        cards.append(
            {
                "id": title["id"],
                "titulo": title["titulo"],
                "autores": title["autores"],
                "created_at": title.get("created_at"),
                "capa_url": title.get("capa_url") or "",
                "capa_real": capa_real,
                "capa_gerada": gerar_capa_svg(
                    title["titulo"],
                    title["autores"],
                    category_text,
                ),
                "categorias": category_text,
                "exemplares_disponiveis": entry[
                    "exemplares_disponiveis"
                ],
                "href": f"/catalogo/{title['id']}",
                "cover_initial": initial,
                "cover_variant": variant,
            }
        )
    return cards


def _as_utc_datetime(value: object) -> datetime | None:
    if type(value) in {int, float}:
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_timestamp(value: object) -> str:
    parsed = _as_utc_datetime(value)
    if parsed is None:
        return "Não informado"
    return parsed.strftime("%d/%m/%Y %H:%M UTC")


def _format_sao_paulo_deadline(value: str | None) -> str:
    if not value:
        return "Sem prazo de retirada"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%d/%m/%Y %H:%M")


def _is_overdue(vence_em: object, devolvido_em: object) -> bool:
    if devolvido_em not in (None, 0):
        return False
    due = _as_utc_datetime(vence_em)
    return due is not None and due < datetime.now(timezone.utc)


def _calendar_days_until(vence_em: object) -> int | None:
    due = _as_utc_datetime(vence_em)
    if due is None:
        return None
    return (due.date() - datetime.now(timezone.utc).date()).days


def _format_known_timestamp(value: object) -> str:
    if _as_utc_datetime(value) is None:
        return "Data indisponível"
    return _format_timestamp(value)


def _request_status_label(status: str) -> str:
    return {
        "pendente": "Aguardando confirmação da retirada",
        "em_reserva": "Vinculada a uma reserva",
        "atendida": "Atendida",
        "recusada": "Recusada",
    }.get(status, status)


def _reservation_status_label(status: str) -> str:
    return {
        "aguardando": "Aguardando na fila",
        "ofertada": "Disponível para retirada",
        "retirada": "Retirada",
        "expirada": "Oferta expirada",
    }.get(status, status)


def public_catalog_category_option(
    category: rx.Var[dict[str, Any]],
) -> rx.Component:
    return rx.el.option(category["nome"], value=category["id"])


def home_category_chip(category: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.link(
        rx.text(category["nome"], " (", category["quantidade"], ")"),
        href="/catalogo",
        class_name="home-category-chip",
    )


def home_book_section(
    *,
    heading: str,
    subtitle: str,
    books: rx.Var[list[dict[str, Any]]],
    section_id: str,
) -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.vstack(
                    rx.heading(heading, size="5"),
                    rx.text(subtitle, class_name="home-section-subtitle"),
                    align="start",
                    spacing="1",
                    class_name="home-section-copy",
                ),
                rx.link(
                    "Ver mais",
                    href="/catalogo",
                    class_name="home-view-more",
                ),
                class_name="home-section-heading",
            ),
            rx.cond(
                State.public_catalog_has_error,
                rx.fragment(),
                rx.el.div(
                    rx.foreach(books, public_catalog_card),
                    class_name="catalog-grid home-book-grid",
                ),
            ),
            rx.cond(
                (~State.public_catalog_pending)
                & (~State.public_catalog_has_error)
                & (books.length() == 0),
                rx.text(
                    "Nenhum título disponível nesta seção.",
                    role="status",
                    class_name="home-empty-state",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.public_catalog_pending,
                rx.text("Carregando o acervo...", role="status"),
                rx.fragment(),
            ),
            rx.cond(
                State.public_catalog_has_error,
                rx.el.p(
                    State.public_catalog_message,
                    role="alert",
                    aria_live="polite",
                    class_name="signup-feedback signup-feedback-error",
                ),
                rx.fragment(),
            ),
            class_name="home-book-section-content",
        ),
        id=section_id,
        class_name="content-section home-book-section",
    )


def home_profile_summary() -> rx.Component:
    student_metrics = rx.el.div(
        rx.el.div(
            rx.el.strong(State.student_active_loan_count),
            rx.text("Emprestados"),
            class_name="home-summary-metric",
        ),
        rx.el.div(
            rx.el.strong(State.student_awaiting_count),
            rx.text("Aguardando"),
            class_name="home-summary-metric",
        ),
        rx.el.div(
            rx.el.strong(State.student_overdue_loans.length()),
            rx.text("Atrasos"),
            class_name="home-summary-metric",
        ),
        class_name="home-summary-metrics",
    )
    staff_metrics = rx.el.div(
        rx.el.div(
            rx.el.strong(State.circulation_pending_request_count),
            rx.text("Pedidos pendentes"),
            class_name="home-summary-metric",
        ),
        rx.el.div(
            rx.el.strong(State.circulation_overdue_loan_count),
            rx.text("Atrasos"),
            class_name="home-summary-metric",
        ),
        class_name="home-summary-metrics",
    )
    student_summary = rx.cond(
        State.student_library_pending,
        rx.text("Carregando seu resumo...", role="status"),
        rx.cond(
            State.student_library_has_error,
            rx.el.p(
                State.student_library_message,
                role="alert",
                class_name="signup-feedback signup-feedback-error",
            ),
            student_metrics,
        ),
    )
    staff_summary = rx.cond(
        State.circulation_pending,
        rx.text("Carregando o resumo operacional...", role="status"),
        rx.cond(
            State.circulation_has_error,
            rx.el.p(
                State.circulation_message,
                role="alert",
                class_name="signup-feedback signup-feedback-error",
            ),
            staff_metrics,
        ),
    )
    return rx.cond(
        State.is_authenticated,
        rx.el.section(
            rx.heading("Resumo da biblioteca", size="4"),
            rx.cond(State.is_student, student_summary, staff_summary),
            class_name="content-section home-profile-summary",
        ),
        rx.fragment(),
    )


def home_reservation_steps() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.heading("Como reservar", size="5"),
            rx.text(
                "Escolha um livro, faça a solicitação e retire na biblioteca."
            ),
            class_name="home-section-copy",
        ),
        rx.el.ol(
            rx.el.li(rx.el.strong("Escolha"), rx.text(" um livro do catálogo.")),
            rx.el.li(rx.el.strong("Reserve"), rx.text(" pelo botão da página do livro.")),
            rx.el.li(rx.el.strong("Retire"), rx.text(" na biblioteca após a confirmação.")),
            class_name="home-reservation-steps",
        ),
        class_name="content-section home-reservation-section",
    )


def home_stat_card(value: rx.Var[int], label: str) -> rx.Component:
    return rx.el.div(
        rx.el.strong(value, class_name="hero-stat-value"),
        rx.text(label, class_name="hero-stat-label"),
        class_name="hero-stat-card",
    )


def home_pending_stat_card(label: str) -> rx.Component:
    return rx.el.div(
        rx.el.strong("…", class_name="hero-stat-value"),
        rx.text(label, class_name="hero-stat-label"),
        rx.text("Carregando…", role="status"),
        class_name="hero-stat-card",
    )


def home_indicators() -> rx.Component:
    return rx.el.div(
        rx.cond(
            State.home_titles_pending,
            home_pending_stat_card("Títulos"),
            rx.cond(
                State.home_titles_has_error,
                rx.el.div(
                    rx.el.strong("—", class_name="hero-stat-value"),
                    rx.text("Títulos", class_name="hero-stat-label"),
                    rx.button(
                        conteudo_acao("atualizar_lista", "Tentar de novo"),
                        type="button",
                        on_click=State.retry_home_titles,
                        class_name="nav-logout",
                        **atributos_acao("atualizar_lista", "Tentar de novo"),
                    ),
                    class_name="hero-stat-card",
                ),
                home_stat_card(State.home_total_titles, "Títulos"),
            ),
        ),
        rx.cond(
            State.home_titles_pending,
            home_pending_stat_card("Exemplares disponíveis"),
            rx.cond(
                State.home_titles_has_error,
                rx.el.div(
                    rx.el.strong("—", class_name="hero-stat-value"),
                    rx.text("Exemplares disponíveis", class_name="hero-stat-label"),
                    rx.button(
                        conteudo_acao("atualizar_lista", "Tentar de novo"),
                        type="button",
                        on_click=State.retry_home_titles,
                        class_name="nav-logout",
                        **atributos_acao("atualizar_lista", "Tentar de novo"),
                    ),
                    class_name="hero-stat-card",
                ),
                home_stat_card(
                    State.home_available_copies,
                    "Exemplares disponíveis",
                ),
            ),
        ),
        rx.cond(
            State.home_categories_pending,
            home_pending_stat_card("Categorias"),
            rx.cond(
                State.home_categories_has_error,
                rx.el.div(
                    rx.el.strong("—", class_name="hero-stat-value"),
                    rx.text("Categorias", class_name="hero-stat-label"),
                    rx.button(
                        conteudo_acao("atualizar_lista", "Tentar de novo"),
                        type="button",
                        on_click=State.retry_home_categories,
                        class_name="nav-logout",
                        **atributos_acao("atualizar_lista", "Tentar de novo"),
                    ),
                    class_name="hero-stat-card",
                ),
                home_stat_card(State.home_category_count, "Categorias"),
            ),
        ),
        class_name="hero-stat-grid",
    )


def _catalog_cover_class(cover_variant: rx.Var[int]) -> rx.Var[str]:
    return rx.cond(
        cover_variant == 0,
        "catalog-card-cover catalog-cover-stack catalog-cover-0",
        rx.cond(
            cover_variant == 1,
            "catalog-card-cover catalog-cover-stack catalog-cover-1",
            rx.cond(
                cover_variant == 2,
                "catalog-card-cover catalog-cover-stack catalog-cover-2",
                rx.cond(
                    cover_variant == 3,
                    "catalog-card-cover catalog-cover-stack catalog-cover-3",
                    "catalog-card-cover catalog-cover-stack catalog-cover-4",
                ),
            ),
        ),
    )


def catalog_cover_layers(
    titulo: rx.Var[str],
    capa_gerada: rx.Var[str],
    capa_real: rx.Var[str],
    *,
    container_class: str | rx.Var[str],
    real_class: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.img(
            src=capa_gerada,
            alt="",
            aria_hidden=True,
            class_name="catalog-cover-generated",
        ),
        rx.cond(
            capa_real.to(str) != "",
            rx.el.img(
                src=capa_real,
                alt="",
                aria_hidden=True,
                loading="lazy",
                class_name=f"{real_class} catalog-real-cover-image",
            ),
            rx.fragment(),
        ),
        role="img",
        aria_label=f"Capa de «{titulo}»",
        class_name=container_class,
    )


def public_catalog_card(title: rx.Var[dict[str, Any]]) -> rx.Component:
    title_name = title["titulo"].to(str)
    category_text = title["categorias"].to(str)
    available_count = title["exemplares_disponiveis"].to(int)
    cover_variant = title["cover_variant"].to(int)
    cover_class = _catalog_cover_class(cover_variant)
    return rx.el.article(
        rx.el.div(
            catalog_cover_layers(
                title_name,
                title["capa_gerada"].to(str),
                rx.cond(
                    title["capa_url"].to(str) != "",
                    title["capa_url"].to(str),
                    title["capa_real"].to(str),
                ),
                container_class=cover_class,
                real_class="catalog-card-cover-image",
            ),
            rx.el.span(
                rx.cond(
                    category_text != "",
                    category_text,
                    "Livro",
                ),
                class_name="catalog-tag",
            ),
            class_name="catalog-card-visual",
        ),
        rx.el.h2(title_name, class_name="catalog-card-heading"),
        rx.text("Autoria: ", title["autores"]),
        rx.el.div(
            rx.cond(
                available_count > 0,
                rx.el.span(
                    conteudo_selo("disponivel"),
                    class_name="status-pill status-pill-success",
                ),
                rx.el.span(
                    conteudo_selo("indisponivel"),
                    class_name="status-pill status-pill-muted",
                ),
            ),
            rx.text(
                "Exemplares disponíveis: ",
                available_count,
                class_name="catalog-card-meta",
            ),
            class_name="catalog-card-meta-row",
        ),
        rx.link(
            "Ver detalhes",
            href=title["href"],
            class_name="catalog-card-link",
        ),
        rx.cond(
            State.is_librarian,
            rx.link(
                conteudo_acao("editar"),
                href="/admin/acervo?titulo=" + title["id"].to(str),
                class_name="catalog-card-link",
                **atributos_acao("editar"),
            ),
            rx.fragment(),
        ),
        class_name="catalog-card",
    )


def student_loan_card(loan: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.el.h3(loan["titulo"], class_name="catalog-card-heading"),
            rx.cond(
                loan["em_atraso"],
                rx.el.span(
                    conteudo_selo("atraso"),
                    class_name="status-pill status-pill-warning",
                ),
                rx.el.span(
                    conteudo_selo("emprestado"),
                    class_name="status-pill status-pill-success",
                ),
            ),
            class_name="card-header-row",
        ),
        rx.text("Exemplar: ", loan["exemplar_id"]),
        rx.text("Retirada: ", loan["retirado_em"]),
        rx.text("Devolução: ", loan["vence_em"]),
        rx.cond(
            loan["em_atraso"],
            rx.el.p(
                "Em atraso há ",
                loan["dias_atraso"],
                " dias. Procure a equipe da biblioteca.",
                role="alert",
                class_name="signup-feedback signup-feedback-error",
            ),
            rx.el.p(
                "Vence em ",
                loan["dias_restantes"],
                " dias.",
                class_name="student-loan-deadline",
            ),
        ),
        class_name="catalog-card",
    )


def student_request_card(request: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.el.h3(
                rx.link(
                    conteudo_acao("detalhes"),
                    href=request["href"],
                    **atributos_acao("detalhes"),
                ),
                class_name="catalog-card-heading",
            ),
            rx.el.span(request["estado"], class_name="status-pill status-pill-muted"),
            class_name="card-header-row",
        ),
        rx.text("Solicitação: ", request["estado"]),
        rx.text("Enviada em: ", request["solicitada_em"]),
        class_name="catalog-card",
    )


def student_reservation_card(reservation: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.el.h3(
                rx.link(
                    conteudo_acao("detalhes"),
                    href=reservation["href"],
                    **atributos_acao("detalhes"),
                ),
                class_name="catalog-card-heading",
            ),
            rx.el.span(reservation["estado"], class_name="status-pill status-pill-muted"),
            class_name="card-header-row",
        ),
        rx.text("Reserva: ", reservation["estado"]),
        rx.text("Prazo: ", reservation["prazo"]),
        class_name="catalog-card",
    )


def public_catalog() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-catalogo",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Catálogo", size="7"),
                rx.text(
                    "Consulte os títulos e a quantidade de exemplares disponíveis."
                ),
                rx.el.div(
                    rx.foreach(
                        State.home_category_shelves,
                        home_category_chip,
                    ),
                    class_name="home-category-rail catalog-category-rail",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Buscar por título ou autoria",
                            html_for="catalog-search",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-search",
                            type="search",
                            value=State.public_catalog_search,
                            on_change=State.set_public_catalog_search,
                            aria_label="Buscar por título ou autoria",
                            class_name="campo",
                        ),
                        class_name="catalog-filter",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Categoria",
                            html_for="catalog-category",
                            class_name="signup-label",
                        ),
                        rx.el.select(
                            rx.el.option("Todas as categorias", value=""),
                            rx.foreach(
                                State.public_catalog_categories,
                                public_catalog_category_option,
                            ),
                            id="catalog-category",
                            value=State.public_catalog_category_id,
                            on_change=State.set_public_catalog_category,
                            class_name="campo-select",
                        ),
                        class_name="catalog-filter",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Ordenação",
                            html_for="catalog-sort",
                            class_name="signup-label",
                        ),
                        rx.el.select(
                            rx.el.option("A-Z", value="asc"),
                            rx.el.option("Z-A", value="desc"),
                            id="catalog-sort",
                            value=State.public_catalog_sort,
                            on_change=State.set_public_catalog_sort,
                            class_name="campo-select",
                        ),
                        class_name="catalog-filter",
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=State.public_catalog_only_available,
                            on_change=State.set_public_catalog_only_available,
                            class_name="campo-check",
                        ),
                        "Somente disponíveis",
                        class_name="campo-check-row",
                    ),
                    class_name="catalog-controls",
                ),
                rx.cond(
                    State.public_catalog_pending,
                    rx.text("Carregando catálogo…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.public_catalog_message != "",
                    rx.el.p(
                        State.public_catalog_message,
                        role=rx.cond(
                            State.public_catalog_has_error,
                            "alert",
                            "status",
                        ),
                        aria_live="polite",
                        class_name="signup-feedback signup-feedback-error",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.public_catalog_categories_skipped > 0,
                    rx.el.p(
                        State.public_catalog_categories_skipped,
                        " registros não puderam ser lidos.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.public_catalog_has_error,
                    rx.button(
                        conteudo_acao("atualizar_lista", "Tentar de novo"),
                        type="button",
                        on_click=State.retry_public_catalog,
                        class_name="nav-logout",
                        **atributos_acao("atualizar_lista", "Tentar de novo"),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    (~State.public_catalog_pending)
                    & (State.public_catalog_message == "")
                    & (State.filtered_public_catalog.length() == 0),
                    rx.text(
                        "Nenhum título corresponde aos critérios atuais.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.filtered_public_catalog.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            State.filtered_public_catalog,
                            public_catalog_card,
                        ),
                        class_name="catalog-grid",
                    ),
                    rx.fragment(),
                ),
                id="conteudo-catalogo",
                class_name="content-section catalog-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def public_catalog_detail() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-detalhe",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Detalhes do título", size="7"),
                rx.cond(
                    State.public_catalog_detail_pending,
                    rx.text("Carregando título…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.public_catalog_detail_message != "",
                    rx.el.p(
                        State.public_catalog_detail_message,
                        role="alert",
                        aria_live="polite",
                        class_name="signup-feedback signup-feedback-error",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.public_catalog_detail_has_error,
                    rx.button(
                        conteudo_acao("atualizar_lista", "Tentar de novo"),
                        type="button",
                        on_click=State.retry_public_catalog_detail,
                        class_name="nav-logout",
                        **atributos_acao("atualizar_lista", "Tentar de novo"),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.public_catalog_detail_not_found,
                    rx.vstack(
                        rx.text("O título não foi encontrado.", role="status"),
                        align="start",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.has_public_catalog_detail,
                    rx.el.article(
                        catalog_cover_layers(
                            State.public_catalog_detail["titulo"].to(str),
                            State.public_catalog_detail["capa_gerada"].to(str),
                            rx.cond(
                                State.public_catalog_detail["capa_url"] != "",
                                State.public_catalog_detail["capa_url"].to(str),
                                State.public_catalog_detail["capa_real"].to(str),
                            ),
                            container_class=(
                                "catalog-cover-stack catalog-detail-visual"
                            ),
                            real_class="catalog-detail-cover-image",
                        ),
                        rx.el.h2(
                            State.public_catalog_detail["titulo"],
                            class_name="catalog-detail-heading",
                        ),
                        rx.text(
                            "Autoria: ",
                            State.public_catalog_detail["autores"],
                        ),
                        rx.text(
                            "Categorias: ",
                            State.public_catalog_detail_categories,
                        ),
                        rx.text(
                            "Exemplares disponíveis: ",
                            State.public_catalog_detail["exemplares_disponiveis"],
                        ),
                        rx.cond(
                            State.public_catalog_detail["isbn"] != "",
                            rx.text("ISBN: ", State.public_catalog_detail["isbn"]),
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.public_catalog_detail["editora"] != "",
                            rx.text(
                                "Editora: ",
                                State.public_catalog_detail["editora"],
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.public_catalog_detail["edicao"] != "",
                            rx.text(
                                "Edição: ",
                                State.public_catalog_detail["edicao"],
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.public_catalog_detail["ano_publicacao"] != "",
                            rx.text(
                                "Ano de publicação: ",
                                State.public_catalog_detail["ano_publicacao"],
                            ),
                            rx.fragment(),
                        ),
                        rx.text(
                            State.public_catalog_detail["descricao"],
                            class_name="catalog-description",
                        ),
                        class_name="catalog-detail-card",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.is_student,
                    rx.vstack(
                        rx.el.p(
                            State.student_request_message,
                            role=rx.cond(
                                State.student_request_has_error,
                                "alert",
                                "status",
                            ),
                            aria_live="polite",
                            class_name=rx.cond(
                                State.student_request_has_error,
                                "signup-feedback signup-feedback-error",
                                "signup-feedback signup-feedback-success",
                            ),
                        ),
                        rx.button(
                            conteudo_acao("reservar", "Reservar"),
                            type="button",
                            disabled=State.student_request_pending,
                            on_click=State.request_catalog_title(
                                State.public_catalog_detail["id"]
                            ),
                            class_name="focus-demo-button",
                            **atributos_acao("reservar", "Reservar"),
                        ),
                        align="start",
                        width="100%",
                        class_name="catalog-detail-actions",
                    ),
                    rx.cond(
                        State.is_authenticated,
                        rx.fragment(),
                        rx.link(
                            conteudo_acao("entrar", "Entrar para reservar"),
                            href="/login",
                            class_name="primary-cta",
                            **atributos_acao("entrar", "Entrar para reservar"),
                        ),
                    ),
                ),
                rx.cond(
                    State.is_librarian,
                    rx.link(
                        conteudo_acao("editar"),
                        href="/admin/acervo?titulo=" + State.public_catalog_detail["id"].to(str),
                        class_name="primary-cta",
                        **atributos_acao("editar"),
                    ),
                    rx.fragment(),
                ),
                id="conteudo-detalhe",
                class_name="content-section catalog-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def student_reservations() -> rx.Component:
    awaiting_approval_section = rx.el.section(
        rx.el.div(
            rx.heading(
                conteudo_selo("aguardando", "Aguardando aprovação"),
                size="5",
            ),
            rx.el.span(
                State.student_awaiting_approval_requests.length(),
                class_name="student-reservations-count",
            ),
            class_name="student-reservations-heading",
        ),
        rx.cond(
            State.student_awaiting_approval_requests.length() > 0,
            rx.el.div(
                rx.foreach(
                    State.student_awaiting_approval_requests,
                    student_request_card,
                ),
                class_name="catalog-grid",
            ),
            rx.text(
                "Você não tem pedidos aguardando aprovação.",
                role="status",
            ),
        ),
        class_name="student-library-section",
        aria_label="Aguardando aprovação",
    )
    approved_section = rx.el.section(
        rx.el.div(
            rx.heading(
                conteudo_selo("aprovada", "Aprovadas"),
                size="5",
            ),
            rx.el.span(
                State.student_approved_reservations.length(),
                class_name="student-reservations-count",
            ),
            class_name="student-reservations-heading",
        ),
        rx.cond(
            State.student_approved_reservations.length() > 0,
            rx.el.div(
                rx.foreach(
                    State.student_approved_reservations,
                    student_reservation_card,
                ),
                class_name="catalog-grid",
            ),
            rx.text(
                "Você não tem reservas aprovadas aguardando retirada.",
                role="status",
            ),
        ),
        class_name="student-library-section",
        aria_label="Reservas aprovadas",
    )
    borrowed_section = rx.el.section(
        rx.el.div(
            rx.heading(
                conteudo_selo("emprestado", "Emprestados"),
                size="5",
            ),
            rx.el.span(
                State.student_current_loans.length(),
                class_name="student-reservations-count",
            ),
            class_name="student-reservations-heading",
        ),
        rx.cond(
            State.student_current_loans.length() > 0,
            rx.el.div(
                rx.foreach(State.student_current_loans, student_loan_card),
                class_name="catalog-grid",
            ),
            rx.text(
                "Você não tem livros emprestados no momento.",
                role="status",
            ),
        ),
        class_name="student-library-section",
        aria_label="Livros emprestados",
    )
    overdue_section = rx.el.section(
        rx.el.div(
            rx.heading(
                conteudo_selo("atraso"),
                size="5",
            ),
            rx.el.span(
                State.student_overdue_loans.length(),
                class_name="student-reservations-count",
            ),
            class_name="student-reservations-heading",
        ),
        rx.cond(
            State.student_overdue_loans.length() > 0,
            rx.el.div(
                rx.foreach(State.student_overdue_loans, student_loan_card),
                class_name="catalog-grid",
            ),
            rx.text(
                "Você não tem empréstimos em atraso.",
                role="status",
            ),
        ),
        class_name="student-library-section student-overdue-section",
        aria_label="Em atraso",
    )
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-reservas",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.cond(
                (~State.student_library_pending)
                & (~State.student_library_has_error)
                & (State.student_overdue_loans.length() > 0),
                rx.el.p(
                    "Você tem ",
                    State.student_overdue_loans.length(),
                    " empréstimo(s) em atraso.",
                    role="alert",
                    class_name="student-overdue-alert",
                ),
                rx.fragment(),
            ),
            rx.cond(
                (~State.student_library_pending)
                & (~State.student_library_has_error)
                & (State.student_overdue_loans.length() > 0),
                rx.fragment(),
                rx.fragment(),
            ),
            rx.el.section(
                rx.heading("Reservas e empréstimos", size="7"),
                rx.text(
                    "Acompanhe pedidos, retiradas e prazos da sua conta."
                ),
                rx.el.div(
                    rx.button(
                        conteudo_acao("pedidos_reserva", "Aguardando"),
                        type="button",
                        on_click=State.set_student_reservation_tab("aguardando"),
                        class_name="reservation-tab",
                        **atributos_acao("pedidos_reserva", "Aguardando"),
                    ),
                    rx.button(
                        conteudo_acao("aceitar", "Aprovadas"),
                        type="button",
                        on_click=State.set_student_reservation_tab("aprovadas"),
                        class_name="reservation-tab",
                        **atributos_acao("aceitar", "Aprovadas"),
                    ),
                    rx.button(
                        conteudo_acao("emprestar", "Emprestados"),
                        type="button",
                        on_click=State.set_student_reservation_tab("emprestados"),
                        class_name="reservation-tab",
                        **atributos_acao("emprestar", "Emprestados"),
                    ),
                    rx.button(
                        conteudo_acao("regras", "Atrasos"),
                        type="button",
                        on_click=State.set_student_reservation_tab("atrasos"),
                        class_name="reservation-tab",
                        **atributos_acao("regras", "Atrasos"),
                    ),
                    role="tablist",
                    aria_label="Acompanhamento de reservas",
                    class_name="reservation-tabs",
                ),
                rx.cond(
                    State.student_library_pending,
                    rx.text("Carregando seus registros…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.student_library_has_error,
                    rx.el.div(
                        rx.el.p(State.student_library_message),
                        rx.cond(
                            State.student_library_requires_login,
                            rx.link(
                                conteudo_acao("entrar"),
                                href="/login",
                                **atributos_acao("entrar"),
                            ),
                            rx.button(
                                conteudo_acao("atualizar_lista", "Tentar de novo"),
                                type="button",
                                on_click=State.retry_student_library,
                                class_name="nav-logout",
                                **atributos_acao("atualizar_lista", "Tentar de novo"),
                            ),
                        ),
                        role="alert",
                        aria_live="polite",
                        class_name="signup-feedback signup-feedback-error",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    (~State.student_library_pending)
                    & (~State.student_library_has_error),
                    rx.fragment(
                        rx.cond(
                            State.student_library_skipped > 0,
                            rx.el.p(
                                State.student_library_skipped,
                                " registros não puderam ser lidos.",
                                role="status",
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.student_reservation_tab == "aguardando",
                            awaiting_approval_section,
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.student_reservation_tab == "aprovadas",
                            approved_section,
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.student_reservation_tab == "emprestados",
                            borrowed_section,
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.student_reservation_tab == "atrasos",
                            overdue_section,
                            rx.fragment(),
                        ),
                    ),
                    rx.fragment(),
                ),
                id="conteudo-reservas",
                class_name="content-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def student_library() -> rx.Component:
    return student_reservations()


def student_library_redirect() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-redirecionamento-reservas",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Redirecionando para suas reservas", size="7"),
                rx.text("Aguarde enquanto abrimos sua biblioteca."),
                id="conteudo-redirecionamento-reservas",
                class_name="content-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def index() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-home",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.el.div(
                    rx.vstack(
                        rx.el.span(
                            "Biblioteca contemporânea e acolhedora",
                            class_name="eyebrow",
                        ),
                        rx.heading(
                            "Descubra o próximo livro que vai mudar seu dia.",
                            size="7",
                        ),
                        rx.text(
                            "Explore o acervo, acompanhe empréstimos e reservas "
                            "e aproveite uma biblioteca que combina tradição e "
                            "praticidade.",
                            class_name="hero-copy",
                        ),
                        align="start",
                        spacing="3",
                        class_name="hero-copy-wrap",
                    ),
                    rx.el.aside(
                        home_indicators(),
                        aria_label="Estatísticas do catálogo público",
                        class_name="hero-stat-panel",
                    ),
                    class_name="hero-layout",
                ),
                id="conteudo-home",
                class_name="content-section home-hero",
            ),
            home_profile_summary(),
            home_book_section(
                heading="📚 Livros em destaque",
                subtitle="Explore títulos do acervo disponíveis para leitura.",
                books=State.home_featured_titles,
                section_id="estante-home",
            ),
            home_book_section(
                heading="Novidades no acervo",
                subtitle="Títulos adicionados mais recentemente ao catálogo.",
                books=State.home_new_arrivals,
                section_id="novidades-home",
            ),
            rx.el.section(
                rx.el.div(
                    rx.heading("Categorias", size="5"),
                    rx.text(
                        "Explore os títulos por assunto.",
                        class_name="home-section-subtitle",
                    ),
                    class_name="home-section-copy",
                ),
                rx.el.div(
                    rx.foreach(State.home_category_shelves, home_category_chip),
                    class_name="home-category-rail",
                ),
                rx.link(
                    "Ver mais",
                    href="/catalogo",
                    class_name="home-view-more",
                ),
                id="categorias-home",
                class_name="content-section home-category-section",
            ),
            home_reservation_steps(),
            rx.el.section(
                rx.heading("Sobre a biblioteca", size="5"),
                rx.text(
                    "Um espaço de leitura, pesquisa e descoberta, com um acervo "
                    "para apoiar a aprendizagem de toda a comunidade escolar."
                ),
                id="sobre-biblioteca",
                class_name="content-section home-about-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def student_signup() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-cadastro",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.el.nav(
                    rx.link(
                        "Entrar",
                        href="/login",
                        class_name="auth-tab",
                    ),
                    rx.link(
                        "Criar conta",
                        href="/cadastro",
                        class_name="auth-tab auth-tab-active",
                        aria_current="page",
                    ),
                    aria_label="Acesso",
                    class_name="auth-tabs",
                ),
                rx.heading("Cadastro de estudante", size="7"),
                rx.text(
                    "Crie sua conta para acessar os serviços da biblioteca."
                ),
                rx.cond(
                    State.signup_message != "",
                    rx.el.p(
                        State.signup_message,
                        role=rx.cond(State.signup_has_error, "alert", "status"),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.signup_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.form(
                    rx.el.label(
                        "Nome",
                        html_for="signup-nome",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="signup-nome",
                        name="nome",
                        type="text",
                        required=True,
                        aria_label="Nome",
                        class_name="campo",
                    ),
                    rx.el.label(
                        "E-mail",
                        html_for="signup-email",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="signup-email",
                        name="email",
                        type="email",
                        required=True,
                        aria_label="E-mail",
                        class_name="campo",
                    ),
                    rx.el.label(
                        "Senha",
                        html_for="signup-senha",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="signup-senha",
                        name="senha",
                        type="password",
                        required=True,
                        aria_label="Senha",
                        class_name="campo",
                    ),
                    rx.button(
                        conteudo_acao("cadastrar"),
                        type="submit",
                        class_name="focus-demo-button",
                        **atributos_acao("cadastrar"),
                    ),
                    id="form-cadastro-estudante",
                    on_submit=State.submit_signup,
                    reset_on_submit=False,
                    class_name="signup-form",
                ),
                rx.text(
                    "O perfil de estudante é atribuído pelo sistema.",
                    class_name="signup-note",
                ),
                id="conteudo-cadastro",
                class_name="content-section signup-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def login_page() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-login",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.el.nav(
                    rx.link(
                        "Entrar",
                        href="/login",
                        class_name="auth-tab auth-tab-active",
                        aria_current="page",
                    ),
                    rx.link(
                        "Criar conta",
                        href="/cadastro",
                        class_name="auth-tab",
                    ),
                    aria_label="Acesso",
                    class_name="auth-tabs",
                ),
                rx.heading("Entrar", size="7"),
                rx.text("Acesse sua conta com e-mail e senha."),
                rx.cond(
                    State.login_message != "",
                    rx.el.p(
                        State.login_message,
                        role=rx.cond(State.login_has_error, "alert", "status"),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.login_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.form(
                    rx.el.label(
                        "E-mail",
                        html_for="login-email",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="login-email",
                        name="email",
                        type="email",
                        required=True,
                        aria_label="E-mail",
                        class_name="campo",
                    ),
                    rx.el.label(
                        "Senha",
                        html_for="login-senha",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="login-senha",
                        name="senha",
                        type="password",
                        required=True,
                        aria_label="Senha",
                        class_name="campo",
                    ),
                    rx.button(
                        conteudo_acao("entrar"),
                        type="submit",
                        class_name="focus-demo-button",
                        **atributos_acao("entrar"),
                    ),
                    id="form-login",
                    on_submit=State.submit_login,
                    reset_on_submit=False,
                    class_name="signup-form",
                ),
                id="conteudo-login",
                class_name="content-section signup-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def profile_page() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-perfil",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Meu perfil", size="7"),
                rx.text(
                    "Informações da conta vinculada à sua sessão.",
                    class_name="hero-copy",
                ),
                rx.el.dl(
                    rx.el.dt("Nome"),
                    rx.el.dd(State.greeting_name),
                    rx.el.dt("E-mail"),
                    rx.el.dd(State.session_email),
                    rx.el.dt("Papel"),
                    rx.el.dd(State.session_role_label),
                    class_name="profile-details",
                ),
                id="conteudo-perfil",
                class_name="content-section signup-section",
            ),
            rx.cond(
                State.is_authenticated,
                rx.el.section(
                    rx.heading("Diagnóstico da comunicação", size="5"),
                    rx.text(
                        "Executa somente leituras públicas e autorizadas pelo "
                        "seu perfil. O relatório mostra estrutura e tipos, sem "
                        "valores pessoais."
                    ),
                    rx.button(
                        conteudo_acao("diagnostico", "Testar conexão"),
                        type="button",
                        on_click=State.test_xano_connection,
                        disabled=State.connection_test_pending,
                        class_name="nav-logout",
                        **atributos_acao("diagnostico", "Testar conexão"),
                    ),
                    rx.cond(
                        State.connection_test_message != "",
                        rx.el.p(
                            State.connection_test_message,
                            role=rx.cond(
                                State.connection_test_has_error,
                                "alert",
                                "status",
                            ),
                            aria_live="polite",
                            class_name=rx.cond(
                                State.connection_test_has_error,
                                "signup-feedback signup-feedback-error",
                                "signup-feedback signup-feedback-success",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.connection_diagnostic_report != "",
                        rx.fragment(
                            rx.el.div(
                                rx.el.table(
                                    rx.el.caption(
                                        "Resultados estruturais das leituras"
                                    ),
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("Consulta", scope="col"),
                                            rx.el.th("HTTP", scope="col"),
                                            rx.el.th("Duração", scope="col"),
                                            rx.el.th("Topo", scope="col"),
                                            rx.el.th("Registros", scope="col"),
                                            rx.el.th("Campos e tipos", scope="col"),
                                            rx.el.th("Validação", scope="col"),
                                            rx.el.th(
                                                "Problemas e motivo",
                                                scope="col",
                                            ),
                                            rx.el.th("Referência", scope="col"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            State.connection_diagnostic_results,
                                            xano_diagnostic_table_row,
                                        )
                                    ),
                                    class_name="xano-diagnostic-table",
                                ),
                                style={"overflow_x": "auto", "width": "100%"},
                            ),
                            rx.button(
                                conteudo_acao(
                                    "copiar_relatorio",
                                    complemento="Copiar relatório",
                                ),
                                type="button",
                                on_click=rx.set_clipboard(
                                    State.connection_diagnostic_report
                                ),
                                class_name="nav-logout",
                                **atributos_acao(
                                    "copiar_relatorio",
                                    "Copiar relatório",
                                ),
                            ),
                            rx.el.pre(
                                State.connection_diagnostic_report,
                                class_name="xano-diagnostic-report",
                                style={
                                    "white_space": "pre-wrap",
                                    "overflow_wrap": "anywhere",
                                },
                            ),
                        ),
                        rx.fragment(),
                    ),
                    class_name="content-section profile-xano-diagnostic",
                ),
                rx.fragment(),
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def xano_diagnostic_table_row(
    result: rx.Var[XanoDiagnosticResult],
) -> rx.Component:
    return rx.el.tr(
        rx.el.td(result["name"]),
        rx.el.td(result["status"]),
        rx.el.td(result["duration_ms"], " ms"),
        rx.el.td(result["top_type"]),
        rx.el.td(result["record_count"]),
        rx.el.td(result["fields"]),
        rx.el.td(result["validation"]),
        rx.el.td(
            result["problematic_fields"],
            ": ",
            result["reason"],
        ),
        rx.el.td(result["reference"]),
    )


def accessibility_controls() -> rx.Component:
    return rx.el.section(
        rx.heading("Controles de acessibilidade", size="5"),
        rx.text(
            "Tamanho atual da fonte: ",
            rx.el.span("100%", data_appearance_font_value="true"),
            role="status",
            aria_live="polite",
        ),
        rx.el.div(
            rx.button(
                conteudo_acao("diminuir_fonte"),
                type="button",
                data_appearance_action="font-decrease",
                class_name="a11y-control-button",
                **atributos_acao("diminuir_fonte"),
            ),
            rx.button(
                conteudo_acao(
                    "fonte_padrao",
                    complemento=rx.el.span(
                        "100%",
                        data_appearance_font_value="true",
                        class_name="appearance-font-value",
                    ),
                ),
                type="button",
                data_appearance_action="font-reset",
                class_name="a11y-control-button",
                **atributos_acao("fonte_padrao"),
            ),
            rx.button(
                conteudo_acao("aumentar_fonte"),
                type="button",
                data_appearance_action="font-increase",
                class_name="a11y-control-button",
                **atributos_acao("aumentar_fonte"),
            ),
            class_name="a11y-controls",
        ),
        rx.el.div(
            rx.button(
                conteudo_acao("alto_contraste"),
                type="button",
                aria_pressed=False,
                data_appearance_action="high-contrast",
                class_name="a11y-control-button",
                **atributos_acao("alto_contraste"),
            ),
            rx.button(
                conteudo_acao("reduzir_movimento"),
                type="button",
                aria_pressed=False,
                data_appearance_action="reduce-motion",
                class_name="a11y-control-button",
                **atributos_acao("reduzir_movimento"),
            ),
            class_name="a11y-controls",
        ),
        id="controles-acessibilidade",
        class_name="content-section accessibility-controls-section",
    )


def accessibility_page() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-acessibilidade",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Acessibilidade", size="7"),
                rx.text(
                    "Personalize a leitura para tornar a navegação mais confortável."
                ),
                accessibility_controls(),
                id="conteudo-acessibilidade",
                class_name="content-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def catalog_category_option(category: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            checked=State.selected_category_ids.contains(category["id"]),
            disabled=State.catalog_title_created,
            on_change=State.toggle_catalog_category(category["id"]),
            class_name="campo-check",
        ),
        category["nome"],
        class_name="category-checkbox-row",
    )


def admin_copy_row(copy: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.li(
        rx.text(copy["codigo_tombo"], " — ", copy["estado"]),
        class_name="admin-copy-row",
    )


def admin_title_card(title: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            catalog_cover_layers(
                title["titulo"].to(str),
                title["capa_gerada"].to(str),
                rx.cond(
                    title["capa_url"].to(str) != "",
                    title["capa_url"].to(str),
                    title["capa_real"].to(str),
                ),
                container_class="admin-title-cover catalog-cover-stack",
                real_class="admin-catalog-cover-image",
            ),
            rx.el.div(
                rx.heading(title["titulo"], size="4"),
                rx.el.p("Autoria: ", title["autores"]),
                rx.el.p("Categorias: ", title["categorias"]),
                rx.el.p(
                    "Estado: ",
                    rx.cond(title["ativo"], "Ativo", "Desativado"),
                    role="status",
                ),
                rx.el.p(
                    "Exemplares disponíveis: ",
                    title["exemplares_disponiveis"],
                    " / ",
                    title["exemplares"].length(),
                ),
                class_name="admin-title-data",
            ),
            rx.el.div(
                rx.button(
                    conteudo_acao("editar"),
                    type="button",
                    on_click=State.open_admin_title_edit(title["id"]),
                    aria_expanded=(
                        State.admin_catalog_edit_title_id == title["id"]
                    ),
                    aria_controls=(
                        "painel-edicao-titulo-" + title["id"].to(str)
                    ),
                    disabled=State.admin_catalog_pending,
                    class_name="focus-demo-button",
                    **atributos_acao("editar"),
                ),
                rx.button(
                    conteudo_acao("exemplares"),
                    type="button",
                    on_click=State.toggle_admin_title_copies(title["id"]),
                    aria_expanded=(
                        State.admin_catalog_copy_title_id == title["id"]
                    ),
                    aria_controls=(
                        "painel-exemplares-titulo-" + title["id"].to(str)
                    ),
                    disabled=State.admin_catalog_pending,
                    class_name="focus-demo-button",
                    **atributos_acao("exemplares"),
                ),
                rx.cond(
                    title["ativo"],
                    rx.cond(
                        State.admin_catalog_confirm_title_id == title["id"],
                        rx.fragment(
                            rx.button(
                                conteudo_acao("confirmar_desativacao"),
                                type="button",
                                on_click=State.set_title_active(
                                    title["id"], False
                                ),
                                disabled=State.admin_catalog_pending,
                                class_name="destructive-action",
                                **atributos_acao("confirmar_desativacao"),
                            ),
                            rx.button(
                                conteudo_acao("nao_confirmar"),
                                type="button",
                                on_click=State.cancel_title_deactivation,
                                disabled=State.admin_catalog_pending,
                                class_name="focus-demo-button",
                                **atributos_acao("nao_confirmar"),
                            ),
                        ),
                        rx.button(
                            conteudo_acao("desativar"),
                            type="button",
                            on_click=State.request_title_deactivation(
                                title["id"]
                            ),
                            disabled=State.admin_catalog_pending,
                            class_name="destructive-action",
                            **atributos_acao("desativar"),
                        ),
                    ),
                    rx.button(
                        conteudo_acao("reativar"),
                        type="button",
                        on_click=State.set_title_active(title["id"], True),
                        disabled=State.admin_catalog_pending,
                        class_name="focus-demo-button",
                        **atributos_acao("reativar"),
                    ),
                ),
                class_name="admin-title-actions",
            ),
            class_name="admin-title-row",
        ),
        rx.cond(
            State.admin_catalog_edit_title_id == title["id"],
            rx.el.section(
                rx.form(
                    rx.el.input(type="hidden", name="titulo_id", value=title["id"]),
                    rx.el.label(
                        "Título",
                        rx.el.input(
                            name="titulo",
                            type="text",
                            required=True,
                            default_value=title["titulo"],
                            aria_label="Título",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "Autores",
                        rx.el.input(
                            name="autores",
                            type="text",
                            required=True,
                            default_value=title["autores"],
                            aria_label="Autores",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "ISBN (opcional)",
                        rx.el.input(
                            name="isbn",
                            type="text",
                            default_value=title["isbn"],
                            aria_label="ISBN (opcional)",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "Editora (opcional)",
                        rx.el.input(
                            name="editora",
                            type="text",
                            default_value=title["editora"],
                            aria_label="Editora (opcional)",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "Edição (opcional)",
                        rx.el.input(
                            name="edicao",
                            type="text",
                            default_value=title["edicao"],
                            aria_label="Edição (opcional)",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "Ano de publicação (opcional)",
                        rx.el.input(
                            name="ano_publicacao",
                            type="number",
                            default_value=title["ano_publicacao"],
                            aria_label="Ano de publicação (opcional)",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "Descrição (opcional)",
                        rx.el.textarea(
                            name="descricao",
                            default_value=title["descricao"],
                            aria_label="Descrição (opcional)",
                            class_name="campo-area",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.label(
                        "Link da imagem da capa (HTTPS, opcional)",
                        rx.el.input(
                            name="capa_url",
                            type="url",
                            default_value=title["capa_url"],
                            aria_label="Link da imagem da capa (HTTPS, opcional)",
                            class_name="campo",
                        ),
                        class_name="signup-label",
                    ),
                    rx.el.div(
                        rx.button(
                            conteudo_acao("salvar", "Salvar alterações"),
                            type="submit",
                            disabled=State.admin_catalog_pending,
                            class_name="focus-demo-button",
                            **atributos_acao("salvar", "Salvar alterações"),
                        ),
                        rx.button(
                            conteudo_acao("voltar"),
                            type="button",
                            on_click=State.close_admin_title_edit,
                            class_name="nav-logout",
                            **atributos_acao("voltar"),
                        ),
                        class_name="admin-panel-actions",
                    ),
                    on_submit=State.save_admin_title,
                    reset_on_submit=False,
                    class_name="admin-title-edit-form",
                ),
                id="painel-edicao-titulo-" + title["id"].to(str),
                class_name="admin-title-panel",
            ),
            rx.fragment(),
        ),
        rx.cond(
            State.admin_catalog_copy_title_id == title["id"],
            rx.el.section(
                rx.heading("Exemplares", size="5"),
                rx.cond(
                    title["exemplares"].length() > 0,
                    rx.el.ul(
                        rx.foreach(title["exemplares"], admin_copy_row),
                        class_name="admin-copy-list",
                    ),
                    rx.text("Nenhum exemplar cadastrado.", role="status"),
                ),
                rx.el.div(
                    rx.button(
                        conteudo_acao("criar_exemplar", "Adicionar exemplar"),
                        type="button",
                        on_click=State.add_copy_to_title(title["id"]),
                        disabled=State.admin_catalog_pending
                        | State.admin_catalog_needs_manual_check,
                        class_name="focus-demo-button",
                        **atributos_acao("criar_exemplar", "Adicionar exemplar"),
                    ),
                    rx.button(
                        conteudo_acao("voltar"),
                        type="button",
                        on_click=State.toggle_admin_title_copies(title["id"]),
                        class_name="nav-logout",
                        **atributos_acao("voltar"),
                    ),
                    class_name="admin-panel-actions",
                ),
                id="painel-exemplares-titulo-" + title["id"].to(str),
                class_name="admin-title-panel admin-copies-panel",
            ),
            rx.fragment(),
        ),
        rx.cond(
            State.admin_catalog_title_action_title_id == title["id"],
            rx.el.p(
                State.admin_catalog_title_action_message,
                role=rx.cond(
                    State.admin_catalog_title_action_error,
                    "alert",
                    "status",
                ),
                aria_live="polite",
                class_name=rx.cond(
                    State.admin_catalog_title_action_error,
                    "signup-feedback signup-feedback-error",
                    "signup-feedback signup-feedback-success",
                ),
            ),
            rx.fragment(),
        ),
        class_name="admin-title-card",
    )


def example_books_import_section() -> rx.Component:
    return rx.cond(
        State.can_manage_librarians,
        rx.el.details(
            rx.el.summary(
                "📥 Livros de exemplo",
                class_name="admin-example-seed-summary",
            ),
            rx.text(
                "Adiciona 30 livros reais ao acervo, com 2 ou 3 exemplares "
                "cada. Livros que já existem são ignorados."
            ),
            rx.button(
                conteudo_acao("detalhes", "Ver o que será adicionado"),
                type="button",
                on_click=State.preview_example_books,
                disabled=State.example_seed_pending,
                class_name="nav-logout",
                **atributos_acao("detalhes", "Ver o que será adicionado"),
            ),
            rx.cond(
                State.example_seed_preview_ready,
                rx.vstack(
                    rx.text(
                        "Serão criados: ",
                        State.example_seed_preview_create_count,
                    ),
                    rx.text(
                        "Já existem: ",
                        State.example_seed_preview_existing_count,
                    ),
                    rx.cond(
                        State.example_seed_missing_categories.length() > 0,
                        rx.vstack(
                            rx.text("Categorias que não existem no acervo:"),
                            rx.foreach(
                                State.example_seed_missing_categories,
                                lambda category: rx.text(category),
                            ),
                            align="start",
                        ),
                        rx.text("Todas as categorias necessárias existem."),
                    ),
                    align="start",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.example_seed_confirming,
                rx.hstack(
                    rx.button(
                        conteudo_acao("confirmar_desativacao", "Confirmar"),
                        type="button",
                        on_click=State.confirm_example_books_import,
                        disabled=State.example_seed_pending,
                        class_name="focus-demo-button",
                        **atributos_acao(
                            "confirmar_desativacao",
                            "Confirmar",
                        ),
                    ),
                    rx.button(
                        conteudo_acao("nao_confirmar", "Cancelar"),
                        type="button",
                        on_click=State.cancel_example_books_import,
                        disabled=State.example_seed_pending,
                        class_name="nav-logout",
                        **atributos_acao("nao_confirmar", "Cancelar"),
                    ),
                    wrap="wrap",
                ),
                rx.button(
                    conteudo_acao("novo_titulo", "Adicionar agora"),
                    type="button",
                    on_click=State.request_example_books_import,
                    disabled=State.example_seed_pending,
                    class_name="focus-demo-button",
                    **atributos_acao("novo_titulo", "Adicionar agora"),
                ),
            ),
            rx.cond(
                State.example_seed_pending,
                rx.text(
                    State.example_seed_progress,
                    " de 30",
                    role="status",
                    aria_live="polite",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.example_seed_message != "",
                rx.el.p(
                    State.example_seed_message,
                    role=rx.cond(
                        State.example_seed_has_error,
                        "alert",
                        "status",
                    ),
                    aria_live="polite",
                    class_name=rx.cond(
                        State.example_seed_has_error,
                        "signup-feedback signup-feedback-error",
                        "signup-feedback signup-feedback-success",
                    ),
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.example_seed_can_resume,
                rx.button(
                    conteudo_acao("retomar_categorias", "Continuar importação"),
                    type="button",
                    on_click=State.continue_example_books_import,
                    disabled=State.example_seed_pending,
                    class_name="focus-demo-button",
                    **atributos_acao(
                        "retomar_categorias",
                        "Continuar importação",
                    ),
                ),
                rx.fragment(),
            ),
            class_name="admin-example-seed",
        ),
        rx.fragment(),
    )


def catalog_admin() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-acervo",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Cadastro de título e exemplares", size="7"),
                rx.text(
                    "Acesso restrito a bibliotecários e admins. As categorias disponíveis "
                    "são carregadas do catálogo."
                ),
                rx.el.div(
                    rx.el.input(
                        id="admin-acervo-busca",
                        type="search",
                        value=State.admin_catalog_search,
                        on_change=State.set_admin_catalog_search,
                        placeholder="🔎 Buscar por título, autoria ou ISBN",
                        aria_label="Buscar por título, autoria ou ISBN",
                        class_name="campo",
                    ),
                    rx.button(
                        conteudo_acao("novo_titulo"),
                        type="button",
                        on_click=State.open_admin_new_title,
                        class_name="focus-demo-button",
                        **atributos_acao("novo_titulo"),
                    ),
                    rx.cond(
                        State.admin_catalog_new_title_open,
                        rx.button(
                            conteudo_acao("fechar_cadastro"),
                            type="button",
                            on_click=State.close_admin_new_title,
                            class_name="nav-logout",
                            **atributos_acao("fechar_cadastro"),
                        ),
                        rx.fragment(),
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=State.admin_catalog_show_inactive,
                            on_change=State.set_admin_catalog_show_inactive,
                            class_name="campo-check",
                            aria_label="Mostrar desativados",
                        ),
                        "Mostrar desativados",
                        class_name="campo-check-row",
                    ),
                    class_name="admin-acervo-toolbar",
                ),
                rx.cond(
                    State.catalog_message != "",
                    rx.el.p(
                        State.catalog_message,
                        role=rx.cond(State.catalog_has_error, "alert", "status"),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.catalog_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.catalog_categories_skipped > 0,
                    rx.el.p(
                        State.catalog_categories_skipped,
                        " registros não puderam ser lidos.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.catalog_needs_manual_check,
                    rx.el.p(
                        "Não repita automaticamente a etapa até conferir o resultado.",
                        role="alert",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.catalog_title_created,
                    rx.vstack(
                        rx.heading("Categorias selecionadas", size="4"),
                        rx.cond(
                            State.catalog_categories.length() > 0,
                            rx.foreach(
                                State.catalog_categories,
                                catalog_category_option,
                            ),
                            rx.text("Nenhuma categoria disponível."),
                        ),
                        rx.cond(
                            State.catalog_categories_pending,
                            rx.button(
                                conteudo_acao("retomar_categorias"),
                                type="button",
                                on_click=State.retry_catalog_categories,
                                class_name="focus-demo-button",
                                **atributos_acao("retomar_categorias"),
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.catalog_created_codes.length() > 0,
                            rx.vstack(
                                rx.heading("Códigos de tombo criados", size="4"),
                                rx.foreach(
                                    State.catalog_created_codes,
                                    lambda code: rx.text(code),
                                ),
                                align="start",
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            ~State.catalog_categories_pending,
                            rx.button(
                                conteudo_acao("criar_exemplar"),
                                type="button",
                                on_click=State.create_catalog_copy,
                                class_name="focus-demo-button",
                                disabled=State.catalog_needs_manual_check
                                | State.catalog_categories_pending,
                                **atributos_acao("criar_exemplar"),
                            ),
                            rx.fragment(),
                        ),
                        rx.button(
                            conteudo_acao("novo_cadastro"),
                            type="button",
                            on_click=State.start_new_catalog_title,
                            class_name="focus-demo-button",
                            disabled=State.catalog_needs_manual_check
                            | State.catalog_categories_pending,
                            **atributos_acao("novo_cadastro"),
                        ),
                        align="start",
                        width="100%",
                    ),
                    rx.cond(
                        State.admin_catalog_new_title_open,
                        rx.form(
                        rx.el.label(
                            "Título",
                            html_for="catalog-titulo",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-titulo",
                            name="titulo",
                            type="text",
                            required=True,
                            aria_label="Título",
                            class_name="campo",
                        ),
                        rx.el.label(
                            "Autores",
                            html_for="catalog-autores",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-autores",
                            name="autores",
                            type="text",
                            required=True,
                            aria_label="Autores",
                            class_name="campo",
                        ),
                        rx.el.label(
                            "ISBN (opcional)",
                            html_for="catalog-isbn",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-isbn",
                            name="isbn",
                            type="text",
                            aria_label="ISBN (opcional)",
                            class_name="campo",
                        ),
                        rx.el.label(
                            "Editora (opcional)",
                            html_for="catalog-editora",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-editora",
                            name="editora",
                            type="text",
                            aria_label="Editora (opcional)",
                            class_name="campo",
                        ),
                        rx.el.label(
                            "Edição (opcional)",
                            html_for="catalog-edicao",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-edicao",
                            name="edicao",
                            type="text",
                            aria_label="Edição (opcional)",
                            class_name="campo",
                        ),
                        rx.el.label(
                            "Ano de publicação (opcional)",
                            html_for="catalog-ano-publicacao",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-ano-publicacao",
                            name="ano_publicacao",
                            type="number",
                            aria_label="Ano de publicação (opcional)",
                            class_name="campo",
                        ),
                        rx.el.label(
                            "Descrição (opcional)",
                            html_for="catalog-descricao",
                            class_name="signup-label",
                        ),
                        rx.el.textarea(
                            id="catalog-descricao",
                            name="descricao",
                            aria_label="Descrição (opcional)",
                            class_name="campo-area",
                        ),
                        rx.el.label(
                            "Link da imagem da capa (HTTPS, opcional)",
                            html_for="catalog-capa-url",
                            class_name="signup-label",
                        ),
                        rx.el.input(
                            id="catalog-capa-url",
                            name="capa_url",
                            type="url",
                            aria_label="Link da imagem da capa (HTTPS, opcional)",
                            class_name="campo",
                        ),
                        rx.heading("Categorias existentes", size="4"),
                        rx.cond(
                            State.catalog_categories.length() > 0,
                            rx.foreach(
                                State.catalog_categories,
                                catalog_category_option,
                            ),
                            rx.text("Nenhuma categoria disponível."),
                        ),
                        rx.button(
                            conteudo_acao("novo_titulo"),
                            type="submit",
                            class_name="focus-demo-button",
                            **atributos_acao("novo_titulo"),
                        ),
                        id="form-cadastro-titulo",
                        on_submit=State.submit_catalog_title,
                        reset_on_submit=False,
                        class_name="signup-form",
                        ),
                        rx.fragment(),
                    ),
                ),
                id="conteudo-acervo",
                class_name="content-section admin-acervo-content",
            ),
            example_books_import_section(),
            rx.el.section(
                rx.heading("Acervo completo", size="6"),
                rx.text(
                    "Inclui títulos ativos e desativados e mostra o estado de "
                    "cada exemplar."
                ),
                rx.cond(
                    State.admin_catalog_message != "",
                    rx.el.p(
                        State.admin_catalog_message,
                        role=rx.cond(
                            State.admin_catalog_has_error,
                            "alert",
                            "status",
                        ),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.admin_catalog_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.admin_catalog_skipped > 0,
                    rx.el.p(
                        State.admin_catalog_skipped,
                        " registros não puderam ser lidos.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.admin_catalog_pending,
                    rx.text("Carregando acervo…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.filtered_admin_catalog_entries.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            State.filtered_admin_catalog_entries,
                            admin_title_card,
                        ),
                        class_name="admin-catalog-grid",
                    ),
                    rx.cond(
                        State.admin_catalog_pending,
                        rx.fragment(),
                        rx.cond(
                            State.admin_catalog_has_error,
                            rx.fragment(),
                            rx.cond(
                                State.admin_catalog_search != "",
                                rx.text("Nenhum título encontrado.", role="status"),
                                rx.text("Nenhum título cadastrado.", role="status"),
                            ),
                        ),
                    ),
                ),
                rx.cond(
                    State.admin_catalog_has_more,
                    rx.button(
                        conteudo_acao("mostrar_mais"),
                        type="button",
                        on_click=State.show_more_admin_catalog,
                        class_name="focus-demo-button",
                        **atributos_acao("mostrar_mais"),
                    ),
                    rx.fragment(),
                ),
                rx.button(
                    conteudo_acao("atualizar_acervo"),
                    type="button",
                    on_click=State.refresh_admin_catalog,
                    disabled=State.admin_catalog_pending,
                    class_name="nav-logout",
                    **atributos_acao("atualizar_acervo"),
                ),
                rx.cond(
                    State.admin_catalog_needs_manual_check,
                    rx.button(
                        conteudo_acao("liberar_acervo"),
                        type="button",
                        on_click=State.acknowledge_admin_catalog_check,
                        disabled=State.admin_catalog_pending,
                        class_name="focus-demo-button",
                        **atributos_acao("liberar_acervo"),
                    ),
                    rx.fragment(),
                ),
                id="conteudo-acervo-completo",
                class_name="content-section admin-catalog-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def librarian_card(librarian: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.heading(librarian["nome"], size="4"),
        rx.text(librarian["email"]),
        rx.text(
            rx.cond(librarian["ativo"], "Ativo", "Desativado"),
            role="status",
        ),
        rx.cond(
            librarian["ativo"],
            rx.cond(
                State.librarian_management_confirm_id == librarian["id"],
                rx.fragment(
                    rx.button(
                        conteudo_acao("confirmar_desativacao"),
                        type="button",
                        on_click=State.set_librarian_active(
                            librarian["id"], False
                        ),
                        disabled=State.librarian_management_pending,
                        class_name="destructive-action",
                        **atributos_acao("confirmar_desativacao"),
                    ),
                    rx.button(
                        conteudo_acao("nao_confirmar"),
                        type="button",
                        on_click=State.cancel_librarian_deactivation,
                        disabled=State.librarian_management_pending,
                        class_name="focus-demo-button",
                        **atributos_acao("nao_confirmar"),
                    ),
                ),
                rx.button(
                    conteudo_acao("desativar"),
                    type="button",
                    on_click=State.request_librarian_deactivation(
                        librarian["id"]
                    ),
                    disabled=State.librarian_management_pending,
                    class_name="destructive-action",
                    **atributos_acao("desativar"),
                ),
            ),
            rx.button(
                conteudo_acao("reativar"),
                type="button",
                on_click=State.set_librarian_active(librarian["id"], True),
                disabled=State.librarian_management_pending,
                class_name="focus-demo-button",
                **atributos_acao("reativar"),
            ),
        ),
        class_name="librarian-card",
    )


def librarian_management() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-bibliotecarios",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Gestão de bibliotecários", size="7"),
                rx.text(
                    "Somente administradores podem cadastrar, desativar e "
                    "reativar contas bibliotecárias."
                ),
                rx.cond(
                    State.librarian_management_message != "",
                    rx.el.p(
                        State.librarian_management_message,
                        role=rx.cond(
                            State.librarian_management_has_error,
                            "alert",
                            "status",
                        ),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.librarian_management_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.form(
                    rx.el.label(
                        "Nome",
                        html_for="bibliotecario-nome",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="bibliotecario-nome",
                        name="nome",
                        type="text",
                        required=True,
                        aria_label="Nome do bibliotecário",
                        class_name="campo",
                    ),
                    rx.el.label(
                        "E-mail",
                        html_for="bibliotecario-email",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="bibliotecario-email",
                        name="email",
                        type="email",
                        required=True,
                        aria_label="E-mail do bibliotecário",
                        class_name="campo",
                    ),
                    rx.el.label(
                        "Senha inicial",
                        html_for="bibliotecario-senha",
                        class_name="signup-label",
                    ),
                    rx.el.input(
                        id="bibliotecario-senha",
                        name="senha",
                        type="password",
                        required=True,
                        aria_label="Senha inicial do bibliotecário",
                        class_name="campo",
                    ),
                    rx.button(
                        conteudo_acao("cadastrar_bibliotecario"),
                        type="submit",
                        disabled=State.librarian_management_pending,
                        class_name="focus-demo-button",
                        **atributos_acao("cadastrar_bibliotecario"),
                    ),
                    id="form-cadastro-bibliotecario",
                    on_submit=State.submit_librarian,
                    reset_on_submit=False,
                    class_name="signup-form librarian-form",
                ),
                rx.heading("Contas bibliotecárias", size="5"),
                rx.cond(
                    State.librarian_management_skipped > 0,
                    rx.el.p(
                        State.librarian_management_skipped,
                        " registros não puderam ser lidos.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.el.label(
                    "Buscar conta por nome ou e-mail",
                    html_for="busca-contas-bibliotecarias",
                    class_name="signup-label",
                ),
                rx.el.input(
                    id="busca-contas-bibliotecarias",
                    type="search",
                    value=State.librarian_management_search,
                    on_change=State.update_librarian_management_search,
                    aria_label="Buscar conta por nome ou e-mail",
                    class_name="campo",
                ),
                rx.cond(
                    State.librarian_management_pending,
                    rx.text("Carregando bibliotecários…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.filtered_managed_librarians.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            State.filtered_managed_librarians,
                            librarian_card,
                        ),
                        class_name="librarian-list",
                    ),
                    rx.cond(
                        State.librarian_management_pending
                        | State.librarian_management_has_error,
                        rx.fragment(),
                        rx.cond(
                            State.managed_librarians.length() > 0,
                            rx.text(
                                "Nenhuma conta corresponde à busca.",
                                role="status",
                            ),
                            rx.text(
                                "Nenhum bibliotecário cadastrado.",
                                role="status",
                            ),
                        ),
                    ),
                ),
                rx.button(
                    conteudo_acao("atualizar_lista"),
                    type="button",
                    on_click=State.load_librarians,
                    disabled=State.librarian_management_pending,
                    class_name="nav-logout",
                    **atributos_acao("atualizar_lista"),
                ),
                id="conteudo-bibliotecarios",
                class_name="content-section librarian-management-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def staff_reservation_page() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-reservas",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Reservar para estudante", size="7"),
                rx.text(
                    "A busca exige o e-mail completo. A reserva segue as "
                    "mesmas regras e a fila normal do catálogo."
                ),
                rx.cond(
                    State.staff_reservation_message != "",
                    rx.el.p(
                        State.staff_reservation_message,
                        role=rx.cond(
                            State.staff_reservation_has_error,
                            "alert",
                            "status",
                        ),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.staff_reservation_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.staff_reservation_skipped > 0,
                    rx.el.p(
                        State.staff_reservation_skipped,
                        " registros não puderam ser lidos.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.el.label(
                    "E-mail completo do estudante",
                    html_for="reserva-estudante-email",
                    class_name="signup-label",
                ),
                rx.el.input(
                    id="reserva-estudante-email",
                    type="email",
                    value=State.staff_reservation_email,
                    on_change=State.update_staff_reservation_email,
                    required=True,
                    aria_label="E-mail completo do estudante",
                    class_name="campo",
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check,
                ),
                rx.button(
                    conteudo_acao("buscar_estudante"),
                    type="button",
                    on_click=State.search_staff_reservation_student,
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check,
                    class_name="focus-demo-button",
                    **atributos_acao("buscar_estudante"),
                ),
                rx.cond(
                    State.has_staff_reservation_student,
                    rx.el.div(
                        rx.heading("Confirme o estudante", size="5"),
                        rx.text(
                            State.staff_reservation_student["nome"],
                            aria_label="Nome do estudante localizado",
                        ),
                        class_name="librarian-card",
                    ),
                    rx.fragment(),
                ),
                rx.el.label(
                    "Título ativo",
                    html_for="reserva-titulo-id",
                    class_name="signup-label",
                ),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Selecione um título ativo",
                        aria_label="Título para reserva",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.foreach(
                                State.staff_reservation_title_options,
                                lambda option: rx.select.item(
                                    option["label"],
                                    value=option["id"],
                                ),
                            )
                        )
                    ),
                    value=State.staff_reservation_title_id,
                    on_change=State.update_staff_reservation_title_id,
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check,
                    id="reserva-titulo-id",
                ),
                rx.button(
                    conteudo_acao("registrar_reserva"),
                    type="button",
                    on_click=State.submit_staff_reservation,
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check
                    | ~State.has_staff_reservation_student,
                    class_name="focus-demo-button",
                    **atributos_acao("registrar_reserva"),
                ),
                rx.cond(
                    State.staff_reservation_pending,
                    rx.text("Processando…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.staff_reservation_needs_manual_check,
                    rx.button(
                        conteudo_acao("liberar_fila"),
                        type="button",
                        on_click=State.acknowledge_staff_reservation_check,
                        disabled=State.staff_reservation_pending,
                        class_name="nav-logout",
                        **atributos_acao("liberar_fila"),
                    ),
                    rx.fragment(),
                ),
                id="conteudo-reservas",
                class_name="content-section librarian-management-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def staff_reservation_form() -> rx.Component:
    return rx.el.section(
        rx.heading("Reservar para estudante", size="5"),
        rx.text(
            "A busca exige o e-mail completo. A reserva segue as mesmas "
            "regras e a fila normal do catálogo."
        ),
        rx.cond(
            State.staff_reservation_message != "",
            rx.el.p(
                State.staff_reservation_message,
                role=rx.cond(
                    State.staff_reservation_has_error,
                    "alert",
                    "status",
                ),
                aria_live="polite",
                class_name=rx.cond(
                    State.staff_reservation_has_error,
                    "signup-feedback signup-feedback-error",
                    "signup-feedback signup-feedback-success",
                ),
            ),
            rx.fragment(),
        ),
        rx.el.label(
            "E-mail completo do estudante",
            html_for="reserva-estudante-email",
            class_name="signup-label",
        ),
        rx.el.input(
            id="reserva-estudante-email",
            type="email",
            value=State.staff_reservation_email,
            on_change=State.update_staff_reservation_email,
            required=True,
            aria_label="E-mail completo do estudante",
            class_name="campo",
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check,
        ),
        rx.button(
            conteudo_acao("buscar_estudante"),
            type="button",
            on_click=State.search_staff_reservation_student,
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check,
            class_name="focus-demo-button",
            **atributos_acao("buscar_estudante"),
        ),
        rx.cond(
            State.has_staff_reservation_student,
            rx.el.div(
                rx.heading("Confirme o estudante", size="6"),
                rx.text(
                    State.staff_reservation_student["nome"],
                    aria_label="Nome do estudante localizado",
                ),
                class_name="librarian-card",
            ),
            rx.fragment(),
        ),
        rx.el.label(
            "Título ativo",
            html_for="reserva-titulo-id",
            class_name="signup-label",
        ),
        rx.select.root(
            rx.select.trigger(
                placeholder="Selecione um título ativo",
                aria_label="Título para reserva",
            ),
            rx.select.content(
                rx.select.group(
                    rx.foreach(
                        State.staff_reservation_title_options,
                        lambda option: rx.select.item(
                            option["label"],
                            value=option["id"],
                        ),
                    )
                )
            ),
            value=State.staff_reservation_title_id,
            on_change=State.update_staff_reservation_title_id,
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check,
            id="reserva-titulo-id",
        ),
        rx.button(
            conteudo_acao("registrar_reserva"),
            type="button",
            on_click=State.submit_staff_reservation,
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check
            | ~State.has_staff_reservation_student,
            class_name="focus-demo-button",
            **atributos_acao("registrar_reserva"),
        ),
        rx.cond(
            State.staff_reservation_pending,
            rx.text("Processando…", role="status"),
            rx.fragment(),
        ),
        rx.cond(
            State.staff_reservation_needs_manual_check,
            rx.button(
                conteudo_acao("liberar_fila"),
                type="button",
                on_click=State.acknowledge_staff_reservation_check,
                disabled=State.staff_reservation_pending,
                class_name="nav-logout",
                **atributos_acao("liberar_fila"),
            ),
            rx.fragment(),
        ),
        class_name="content-section staff-reservation-form",
    )


def circulation_request_card(request: LoanRequest) -> rx.Component:
    return rx.el.article(
        rx.heading(f"Solicitação #{request['id']}", size="4"),
        rx.text(f"Estudante #{request['usuario_id']}"),
        rx.text(f"Título #{request['titulo_id']}"),
        rx.text("Status: pendente"),
        rx.button(
            conteudo_acao("retirada"),
            type="button",
            on_click=State.circulation_pickup_request(request["id"]),
            disabled=State.circulation_pending
            | State.circulation_needs_manual_check,
            class_name="focus-demo-button",
            **atributos_acao("retirada"),
        ),
        rx.button(
            conteudo_acao("recusar"),
            type="button",
            on_click=State.circulation_refuse_request(request["id"]),
            disabled=State.circulation_pending
            | State.circulation_needs_manual_check,
            class_name="destructive-action",
            **atributos_acao("recusar"),
        ),
        class_name="librarian-card",
    )


def circulation_reservation_card(
    reservation: AdminReservation,
) -> rx.Component:
    return rx.el.article(
        rx.heading(reservation["titulo"], size="4"),
        rx.text(f"Estudante: {reservation['usuario_nome']}"),
        rx.text(
            f"Reserva #{reservation['id']} — status: {reservation['estado']}"
        ),
        rx.cond(
            reservation["expira_em_sao_paulo"] != None,
            rx.text(
                "Prazo da oferta: ",
                reservation["expira_em_sao_paulo"],
            ),
            rx.fragment(),
        ),
        rx.cond(
            reservation["estado"] == "aguardando",
            rx.fragment(
                rx.button(
                    conteudo_acao("oferecer_reserva"),
                    type="button",
                    on_click=State.circulation_offer_reservation(
                        reservation["titulo_id"]
                    ),
                    disabled=State.circulation_pending
                    | State.circulation_needs_manual_check,
                    class_name="focus-demo-button",
                    **atributos_acao("oferecer_reserva"),
                ),
                rx.button(
                    conteudo_acao("recusar"),
                    type="button",
                    on_click=State.circulation_refuse_reservation(
                        reservation["id"]
                    ),
                    disabled=State.circulation_pending
                    | State.circulation_needs_manual_check,
                    class_name="destructive-action",
                    **atributos_acao("recusar"),
                ),
            ),
            rx.cond(
                reservation["estado"] == "ofertada",
                rx.button(
                    conteudo_acao("retirada", "Retirar reserva"),
                    type="button",
                    on_click=State.circulation_pickup_reservation(
                        reservation["id"]
                    ),
                    disabled=State.circulation_pending
                    | State.circulation_needs_manual_check,
                    class_name="focus-demo-button",
                    **atributos_acao("retirada", "Retirar reserva"),
                ),
                rx.fragment(),
            ),
        ),
        class_name="librarian-card",
    )


def circulation_loan_card(loan: dict[str, Any]) -> rx.Component:
    return rx.el.article(
        rx.heading(loan["titulo"], size="4"),
        rx.text(f"Autor: {loan['autores']}"),
        rx.text(f"Estudante: {loan['usuario_nome']}"),
        rx.text(f"Devolução prevista: {loan['vence_em']}"),
        rx.cond(
            loan["atrasado"],
            rx.el.p(
                conteudo_selo("atraso"),
                role="status",
            ),
            rx.el.p(
                conteudo_selo("emprestado", "Em dia"),
                role="status",
            ),
        ),
        rx.button(
            conteudo_acao("devolver"),
            type="button",
            on_click=State.circulation_return_loan(loan["id"]),
            disabled=State.circulation_pending
            | State.circulation_needs_manual_check,
            class_name="focus-demo-button",
            **atributos_acao("devolver"),
        ),
        class_name="librarian-card",
    )


def circulation_page() -> rx.Component:
    return rx.box(
        rx.link(
            conteudo_acao("pular_conteudo"),
            href="#conteudo-circulacao",
            class_name="skip-link",
            **atributos_acao("pular_conteudo"),
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Reservas e circulação", size="7"),
                rx.text(
                    "Acompanhe pedidos, reservas e devoluções usando os "
                    "registros atuais do acervo."
                ),
                rx.cond(
                    State.circulation_message != "",
                    rx.el.p(
                        State.circulation_message,
                        role=rx.cond(
                            State.circulation_has_error,
                            "alert",
                            "status",
                        ),
                        aria_live="polite",
                        class_name=rx.cond(
                            State.circulation_has_error,
                            "signup-feedback signup-feedback-error",
                            "signup-feedback signup-feedback-success",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.circulation_skipped > 0,
                    rx.el.p(
                        State.circulation_skipped,
                        " registros não puderam ser lidos.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    (~State.circulation_pending)
                    & (~State.circulation_has_error),
                    rx.el.div(
                        rx.el.div(
                            rx.text(
                                "Pedidos pendentes",
                                class_name="operational-count-label",
                            ),
                            rx.heading(
                                State.circulation_pending_request_count,
                                size="6",
                            ),
                            class_name="operational-count",
                        ),
                        rx.el.div(
                            rx.text(
                                "Atrasados",
                                class_name="operational-count-label",
                            ),
                            rx.heading(
                                State.circulation_overdue_loan_count,
                                size="6",
                            ),
                            class_name="operational-count",
                        ),
                        rx.el.div(
                            rx.text(
                                "Empréstimos ativos",
                                class_name="operational-count-label",
                            ),
                            rx.heading(
                                State.circulation_active_loan_count,
                                size="6",
                            ),
                            class_name="operational-count",
                        ),
                        rx.el.div(
                            rx.text(
                                "Devoluções previstas hoje",
                                class_name="operational-count-label",
                            ),
                            rx.heading(
                                State.circulation_due_today_count,
                                size="6",
                            ),
                            class_name="operational-count",
                        ),
                        class_name="operational-counts",
                    ),
                    rx.fragment(),
                ),
                rx.button(
                    conteudo_acao("atualizar_circulacao"),
                    type="button",
                    on_click=State.load_staff_reservations_dashboard,
                    disabled=State.circulation_pending,
                    class_name="nav-logout",
                    **atributos_acao("atualizar_circulacao"),
                ),
                rx.cond(
                    State.circulation_pending,
                    rx.text("Carregando reservas e circulação…", role="status"),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.button(
                        conteudo_acao("pedidos_reserva", "Pedidos"),
                        id="aba-pedidos",
                        type="button",
                        role="tab",
                        aria_selected=State.circulation_active_tab == "pedidos",
                        aria_controls="painel-pedidos",
                        on_click=State.select_circulation_tab("pedidos"),
                        class_name="circulation-tab",
                        **atributos_acao("pedidos_reserva", "Pedidos"),
                    ),
                    rx.button(
                        conteudo_acao("emprestimos", "Empréstimos"),
                        id="aba-emprestimos",
                        type="button",
                        role="tab",
                        aria_selected=(
                            State.circulation_active_tab == "emprestimos"
                        ),
                        aria_controls="painel-emprestimos",
                        on_click=State.select_circulation_tab("emprestimos"),
                        class_name="circulation-tab",
                        **atributos_acao("emprestimos", "Empréstimos"),
                    ),
                    role="tablist",
                    aria_label="Seções de reservas e circulação",
                    class_name="circulation-tabs",
                ),
                rx.cond(
                    State.circulation_active_tab == "pedidos",
                    rx.el.div(
                        rx.heading("Solicitações pendentes", size="5"),
                        rx.cond(
                            State.has_circulation_requests,
                            rx.el.div(
                                rx.foreach(
                                    State.circulation_requests,
                                    circulation_request_card,
                                ),
                                class_name="librarian-list",
                            ),
                            rx.cond(
                                State.circulation_pending
                                | State.circulation_has_error,
                                rx.fragment(),
                                rx.text(
                                    "Não há solicitações pendentes.",
                                    role="status",
                                ),
                            ),
                        ),
                        rx.heading("Fila e ofertas de reserva", size="5"),
                        rx.cond(
                            State.has_circulation_reservations,
                            rx.el.div(
                                rx.foreach(
                                    State.circulation_reservations,
                                    circulation_reservation_card,
                                ),
                                class_name="librarian-list",
                            ),
                            rx.cond(
                                State.circulation_pending
                                | State.circulation_has_error,
                                rx.fragment(),
                                rx.text(
                                    "Não há reservas aguardando ou ofertadas.",
                                    role="status",
                                ),
                            ),
                        ),
                        staff_reservation_form(),
                        id="painel-pedidos",
                        role="tabpanel",
                        aria_labelledby="aba-pedidos",
                        class_name="circulation-tab-panel",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.circulation_active_tab == "emprestimos",
                    rx.el.div(
                        rx.heading("Empréstimos e devoluções", size="5"),
                        rx.el.div(
                    rx.text(
                        "Empréstimos ativos: ",
                        State.circulation_active_loan_count,
                    ),
                    rx.text(
                        "Atrasados: ",
                        State.circulation_overdue_loan_count,
                    ),
                            class_name="librarian-card",
                        ),
                        rx.cond(
                            State.has_circulation_loans,
                            rx.el.div(
                                rx.foreach(
                                    State.circulation_loans,
                                    circulation_loan_card,
                                ),
                                class_name="librarian-list",
                            ),
                            rx.cond(
                                State.circulation_pending
                                | State.circulation_has_error,
                                rx.fragment(),
                                rx.text(
                                    "Não há empréstimos ativos.",
                                    role="status",
                                ),
                            ),
                        ),
                        id="painel-emprestimos",
                        role="tabpanel",
                        aria_labelledby="aba-emprestimos",
                        class_name="circulation-tab-panel",
                    ),
                    rx.fragment(),
                ),
                id="conteudo-circulacao",
                class_name="content-section librarian-management-section",
            ),
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
    )


def accessible_page(page: Callable[[], rx.Component]) -> Callable[[], rx.Component]:
    @wraps(page)
    def wrapped() -> rx.Component:
        return rx.el.div(
            page(),
            class_name="a11y-shell",
            style={
                "width": "100%",
                "min_height": "100vh",
            },
        )

    return wrapped


dark_theme_tokens = {
    "--bg-page": "#111827",
    "--bg-panel": "#1f2937",
    "--bg-soft": "#273449",
    "--text": "#f3f4f6",
    "--brand-900": "#0f172a",
    "--brand-700": "#9bd6e3",
    "--brand-500": "#70bfd2",
    "--brand-100": "#243e4b",
    "--brand-text": "#9bd6e3",
    "--success-700": "#a3e6bf",
    "--success-100": "#1f4533",
    "--warning-700": "#f5ca75",
    "--warning-100": "#4a391c",
    "--danger-700": "#ffb4ab",
    "--danger-100": "#512b31",
    "--slate-900": "#f3f4f6",
    "--slate-700": "#cbd5e1",
    "--slate-500": "#c3ced8",
    "--sand-200": "#364152",
    "--sand-100": "#283342",
    "--line": "#8292a8",
    "--shadow-soft": "0 0.7rem 1.5rem rgba(0, 0, 0, 0.3)",
    "--button-primary-bg": "#9bd6e3",
    "--button-primary-text": "#183a4a",
    "--button-primary-hover-bg": "#70bfd2",
    "--button-primary-border": "#9bd6e3",
    "--button-secondary-bg": "#1f2937",
    "--button-secondary-text": "#f3f4f6",
    "--button-secondary-hover-bg": "#273449",
    "--button-secondary-border": "#8292a8",
    "--button-danger-bg": "#ffb4ab",
    "--button-danger-text": "#512b31",
    "--button-danger-hover-bg": "#f8918a",
    "--button-danger-border": "#ffb4ab",
    "--button-warning-bg": "#f5ca75",
    "--button-warning-text": "#35230c",
    "--button-warning-hover-bg": "#e6b958",
    "--button-warning-border": "#f5ca75",
    "--button-subtle-bg": "#273449",
    "--button-subtle-text": "#f3f4f6",
    "--button-subtle-hover-bg": "#364152",
    "--button-subtle-border": "#8292a8",
    "--action-confirm-bg": "#a3e6bf",
    "--action-confirm-text": "#143526",
    "--action-confirm-hover-bg": "#79d49e",
}


def _handle_backend_exception(exception: Exception):
    reference = registrar_excecao_backend(exception)
    from reflex_components_sonner.toast import toast

    return toast(
        "Ocorreu um erro.",
        level="error",
        fallback_to_alert=True,
        description=(
            "A falha foi registrada no terminal do backend "
            f"(ref. {reference})."
        ),
        position="top-center",
        id="backend_error",
        style={"width": "500px", "white-space": "pre-wrap"},
    )


app = rx.App(
    backend_exception_handler=_handle_backend_exception,
    style={
        "@keyframes biblioteca-page-enter": {
            "from": {"opacity": "0", "transform": "translateY(8px)"},
            "to": {"opacity": "1", "transform": "translateY(0)"},
        },
        "@keyframes biblioteca-profile-enter": {
            "from": {"opacity": "0", "transform": "translateY(-4px)"},
            "to": {"opacity": "1", "transform": "translateY(0)"},
        },
        "@keyframes biblioteca-availability-pulse": {
            "0%, 100%": {"transform": "scale(1)", "box_shadow": "none"},
            "50%": {"transform": "scale(1.03)", "box_shadow": "0 0 0 0.25rem rgba(36, 92, 69, 0.12)"},
        },
        ".a11y-shell": {
            "--bg-page": "#f5efe4",
            "--bg-panel": "#fffdf8",
            "--bg-soft": "#edf4ef",
            "--text": "#1f2c38",
            "--brand-900": "#183a4a",
            "--brand-700": "#245d6d",
            "--brand-500": "#2d7287",
            "--brand-100": "#dfeef2",
            "--brand-text": "#183a4a",
            "--success-700": "#245c45",
            "--success-100": "#dfeee7",
            "--warning-700": "#8b5e17",
            "--warning-100": "#f9ebcb",
            "--danger-700": "#8b2d2d",
            "--danger-100": "#f9d8d8",
            "--slate-900": "#1f2c38",
            "--slate-700": "#405468",
            "--slate-500": "#526371",
            "--sand-200": "#efe4d0",
            "--sand-100": "#f8f4ee",
            "--line": "#d8d2c7",
            "--shadow-soft": "0 0.7rem 1.5rem rgba(24, 35, 46, 0.08)",
            "--button-primary-bg": "#245d6d",
            "--button-primary-text": "#ffffff",
            "--button-primary-hover-bg": "#183a4a",
            "--button-primary-border": "#245d6d",
            "--button-secondary-bg": "#fffdf8",
            "--button-secondary-text": "#245d6d",
            "--button-secondary-hover-bg": "#edf4ef",
            "--button-secondary-border": "#245d6d",
            "--button-danger-bg": "#8b2d2d",
            "--button-danger-text": "#ffffff",
            "--button-danger-hover-bg": "#701f1f",
            "--button-danger-border": "#8b2d2d",
            "--button-warning-bg": "#f9ebcb",
            "--button-warning-text": "#45320b",
            "--button-warning-hover-bg": "#f2dfad",
            "--button-warning-border": "#8b5e17",
            "--button-subtle-bg": "#edf4ef",
            "--button-subtle-text": "#1f2c38",
            "--button-subtle-hover-bg": "#dfeef2",
            "--button-subtle-border": "#d8d2c7",
            "--action-confirm-bg": "#245c45",
            "--action-confirm-text": "#ffffff",
            "--action-confirm-hover-bg": "#194634",
        },
        ".a11y-shell.a11y-dark": dark_theme_tokens,
        "@media (prefers-color-scheme: dark)": {
            ".a11y-shell:not(.a11y-light):not(.a11y-dark)": dark_theme_tokens,
        },
        "font_family": "system-ui, 'Segoe UI', sans-serif",
        "color": "var(--slate-900)",
        "background_color": "var(--bg-page)",
        "*, *::before, *::after": {
            "box_sizing": "border-box",
        },
        "button, [role='button'], [role='checkbox'], [role='switch'], [role='radio']": {
            "min_height": "2.75rem",
        },
        "body": {
            "margin": "0",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-page)",
            "line_height": "1.55",
        },
        "h1, h2, h3, h4, h5, h6": {
            "color": "var(--slate-900)",
            "line_height": "1.2",
            "font_family": "Georgia, 'Times New Roman', serif",
            "letter_spacing": "-0.02em",
        },
        ".app-shell": {
            "min_height": "100vh",
            "padding": "0 1rem",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-page)",
            "animation": "biblioteca-page-enter 300ms ease-out both",
            "transition": "background-color 200ms ease, color 200ms ease",
        },
        ".site-header": {
            "position": "sticky",
            "top": "0",
            "z_index": "50",
            "display": "grid",
            "grid_template_columns": "auto minmax(0, 1fr) minmax(10rem, 17rem) auto",
            "grid_template_areas": "\"logo nav busca acoes\"",
            "align_items": "center",
            "gap": "0.75rem",
            "width": "100%",
            "max_width": "72rem",
            "margin": "0 auto 0.75rem",
            "min_height": "4rem",
            "padding": "0.75rem 1rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".site-header > .brand-link": {
            "grid_area": "logo",
        },
        ".site-header > .site-primary-nav": {
            "grid_area": "nav",
        },
        ".site-header > .site-header-search-form": {
            "grid_area": "busca",
        },
        ".site-header > .site-header-actions": {
            "grid_area": "acoes",
        },
        ".brand-link": {
            "display": "inline-flex",
            "align_items": "center",
            "gap": "0.45rem",
            "white_space": "nowrap",
            "background": "transparent",
            "border": "none",
            "border_radius": "999px",
            "color": "var(--brand-text)",
            "font_weight": "800",
            "text_decoration": "none",
            "font_family": "Georgia, 'Times New Roman', serif",
            "font_size": "1.35rem",
        },
        ".brand-link:hover": {
            "color": "var(--brand-text)",
        },
        ".site-header-search-form": {
            "display": "grid",
            "grid_template_columns": "minmax(0, 1fr) auto",
            "align_items": "center",
            "gap": "0.25rem",
            "width": "100%",
            "min_width": "0",
            "padding": "0.15rem 0.2rem 0.15rem 0.7rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.7rem",
            "background_color": "var(--bg-soft)",
        },
        ".site-header-search": {
            "width": "100%",
            "min_width": "0",
            "min_height": "2.25rem",
            "border": "none",
            "outline": "none",
            "background": "transparent",
            "color": "var(--text)",
        },
        ".site-header-search-icon": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "width": "2rem",
            "min_height": "2rem",
        },
        ".site-header-desktop": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "1rem",
            "flex": "1",
            "min_width": "0",
        },
        ".site-primary-nav": {
            "display": "flex",
            "flex_wrap": "nowrap",
            "align_items": "center",
            "justify_content": "center",
            "gap": "0.35rem",
            "min_width": "0",
            "overflow_x": "auto",
            "padding_block": "0.25rem",
        },
        ".site-header-actions": {
            "display": "flex",
            "flex_wrap": "nowrap",
            "align_items": "center",
            "justify_content": "flex-end",
            "gap": "0.5rem",
            "min_width": "0",
            "white_space": "nowrap",
        },
        ".site-header-actions > .profile-menu, .site-header-actions > .accessibility-menu": {
            "flex": "0 0 auto",
        },
        ".site-menu-toggle": {
            "display": "none",
            "align_items": "center",
            "justify_content": "center",
            "width": "2.75rem",
            "min_width": "2.75rem",
            "min_height": "2.75rem",
            "padding": "0.5rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.55rem",
            "background_color": "var(--bg-panel)",
            "color": "var(--brand-text)",
            "cursor": "pointer",
        },
        ".menu-hamburger-icon": {
            "display": "flex",
            "flex_direction": "column",
            "justify_content": "center",
            "gap": "0.25rem",
            "width": "1.25rem",
        },
        ".menu-hamburger-line": {
            "display": "block",
            "width": "100%",
            "height": "2px",
            "border_radius": "2px",
            "background_color": "currentColor",
        },
        ".site-header-mobile-panel": {
            "display": "none",
            "grid_column": "1 / -1",
            "width": "100%",
        },
        ".site-primary-nav a": {
            "display": "inline-flex",
            "align_items": "center",
            "gap": "0.4rem",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.85rem",
            "border_radius": "999px",
            "background_color": "transparent",
            "color": "var(--text)",
            "font_weight": "600",
            "white_space": "nowrap",
            "cursor": "pointer",
            "text_decoration": "none",
        },
        ".site-header .brand-link, .site-header .site-nav-link, .site-header .profile-menu-trigger, .site-header .accessibility-menu-trigger": {
            "display": "inline-flex",
            "align_items": "center",
            "gap": "0.4rem",
            "padding": "0.5rem 0.85rem",
            "flex": "0 0 auto",
            "white_space": "nowrap",
            "overflow": "visible",
            "background_color": "transparent",
        },
        ".site-header .brand-link:hover, .site-header .site-nav-link:hover, .site-header .profile-menu-trigger:hover, .site-header .accessibility-menu-trigger:hover": {
            "background_color": "var(--bg-soft)",
        },
        ".site-header .emoji-acao, .site-header .rotulo-acao, .site-header .site-nav-link > span": {
            "background_color": "transparent",
            "margin": "0",
        },
        ".site-primary-nav a:hover": {
            "background_color": "var(--bg-soft)",
        },
        ".site-nav-link[aria-current='page']": {
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
        },
        ".profile-menu-trigger, .accessibility-menu-trigger": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.55rem",
            "font_weight": "700",
            "list_style": "none",
            "white_space": "nowrap",
            "cursor": "pointer",
        },
        ".accessibility-menu-trigger": {
            "background_color": "transparent",
            "color": "var(--button-subtle-text)",
        },
        ".profile-menu-trigger": {
            "background_color": "transparent",
            "color": "var(--brand-text)",
        },
        ".profile-menu-trigger:hover": {
            "background_color": "var(--bg-soft)",
            "color": "var(--brand-text)",
        },
        ".accessibility-menu-trigger:hover": {
            "background_color": "var(--bg-soft)",
            "color": "var(--button-subtle-text)",
        },
        ".profile-menu-trigger::-webkit-details-marker, .accessibility-menu-trigger::-webkit-details-marker": {
            "display": "none",
        },
        ".profile-menu, .accessibility-menu": {
            "position": "relative",
        },
        ".profile-menu-content": {
            "position": "absolute",
            "top": "calc(100% + 0.4rem)",
            "right": "0",
            "z_index": "20",
            "display": "grid",
            "gap": "0.2rem",
            "min_width": "13rem",
            "max_width": "min(20rem, calc(100vw - 1rem))",
            "padding": "0.4rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".profile-menu[open] .profile-menu-content, .accessibility-menu[open] .profile-menu-content": {
            "animation": "biblioteca-profile-enter 180ms ease-out both",
        },
        ".profile-menu-item": {
            "display": "flex",
            "align_items": "center",
            "width": "100%",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.65rem",
            "border": "1px solid var(--button-subtle-border)",
            "border_radius": "0.4rem",
            "background_color": "var(--button-subtle-bg)",
            "color": "var(--button-subtle-text)",
            "font": "inherit",
            "text_align": "left",
            "overflow_wrap": "anywhere",
            "text_decoration": "none",
            "cursor": "pointer",
        },
        ".profile-menu-item:hover": {
            "background_color": "var(--button-subtle-hover-bg)",
        },
        ".profile-menu-item:focus-visible": {
            "outline": "3px solid var(--brand-700)",
            "outline_offset": "2px",
        },
        ".profile-menu-identity": {
            "padding": "0.45rem 0.65rem",
            "color": "var(--slate-700)",
            "overflow_wrap": "anywhere",
        },
        ".profile-menu-controls": {
            "display": "grid",
            "grid_template_columns": "repeat(3, minmax(0, 1fr))",
            "gap": "0.2rem",
        },
        ".accessibility-menu-content": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.5rem",
            "width": "min(20rem, 92vw)",
            "max_width": "min(20rem, 92vw)",
            "padding": "0.75rem",
        },
        ".profile-appearance-controls": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.5rem",
            "width": "100%",
            "min_width": "0",
        },
        ".accessibility-setting-row": {
            "display": "flex",
            "flex_wrap": "nowrap",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "0.75rem",
            "width": "100%",
            "min_width": "0",
        },
        ".accessibility-setting-label": {
            "flex": "1 1 auto",
            "min_width": "0",
            "color": "var(--slate-900)",
            "font_size": "0.9rem",
        },
        ".appearance-font-controls": {
            "display": "flex",
            "flex": "0 0 auto",
            "gap": "0.25rem",
        },
        ".appearance-font-button": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "width": "2.75rem",
            "min_width": "2.75rem",
            "min_height": "2.75rem",
            "padding": "0.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-900)",
            "font": "inherit",
            "cursor": "pointer",
        },
        ".appearance-switch": {
            "display": "inline-flex",
            "flex": "0 0 auto",
            "align_items": "center",
            "justify_content": "center",
            "min_width": "6rem",
            "min_height": "2.75rem",
            "padding": "0.35rem 0.65rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-900)",
            "font": "inherit",
            "cursor": "pointer",
        },
        ".appearance-switch[aria-checked='true']": {
            "border_color": "var(--brand-700)",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
        },
        ".profile-menu-content [role='separator']": {
            "height": "1px",
            "margin": "0.3rem 0",
            "background_color": "var(--line)",
        },
        ".profile-details": {
            "display": "grid",
            "grid_template_columns": "minmax(7rem, 0.35fr) minmax(0, 1fr)",
            "gap": "0.75rem 1rem",
            "max_width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-panel)",
        },
        ".profile-details dt": {
            "font_weight": "700",
            "color": "var(--slate-700)",
        },
        ".profile-details dd": {
            "margin": "0",
            "overflow_wrap": "anywhere",
            "color": "var(--slate-900)",
        },
        ".admin-view-band": {
            "display": "flex",
            "flex_wrap": "nowrap",
            "align_items": "center",
            "justify_content": "center",
            "gap": "0.5rem",
            "width": "100%",
            "max_width": "72rem",
            "min_height": "2.25rem",
            "margin": "0 auto 0.75rem",
            "padding": "0.15rem 0.5rem",
            "border_bottom": "1px solid var(--line)",
            "background_color": "var(--bg-soft)",
        },
        ".admin-view-mode-label": {
            "font_weight": "700",
            "color": "var(--brand-text)",
            "font_size": "0.75rem",
            "white_space": "nowrap",
        },
        ".admin-view-reset": {
            "min_height": "2.75rem",
            "padding": "0.25rem 0.5rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "transparent",
            "color": "var(--slate-900)",
            "font_weight": "600",
            "font_size": "0.75rem",
            "white_space": "nowrap",
            "cursor": "pointer",
        },
        ".a11y-menu": {
            "max_width": "100%",
            "padding": "0.5rem 0",
        },
        ".a11y-menu summary": {
            "min_height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "font_weight": "600",
            "cursor": "pointer",
            "border": "1px solid var(--line)",
            "border_radius": "0.55rem",
            "background_color": "var(--bg-panel)",
        },
        ".a11y-controls": {
            "display": "flex",
            "flex_wrap": "wrap",
            "gap": "0.5rem",
            "max_width": "100%",
            "padding": "0.5rem 0",
        },
        ".a11y-controls button": {
            "min_height": "2.75rem",
            "max_width": "100%",
            "padding": "0.4rem 0.65rem",
            "border": "1px solid var(--button-subtle-border)",
            "border_radius": "0.4rem",
            "background_color": "var(--button-subtle-bg)",
            "color": "var(--button-subtle-text)",
            "cursor": "pointer",
            "overflow_wrap": "anywhere",
        },
        ".a11y-controls button:hover": {
            "background_color": "var(--button-subtle-hover-bg)",
        },
        ".a11y-controls button:disabled": {
            "border_style": "dashed",
            "cursor": "not-allowed",
        },
        ".a11y-high-contrast, .a11y-high-contrast *": {
            "color": "#000000 !important",
            "background_color": "#ffffff !important",
            "border_color": "#000000 !important",
            "box_shadow": "none !important",
        },
        ".a11y-high-contrast a": {
            "color": "#00008b !important",
        },
        ".a11y-high-contrast button, .a11y-high-contrast [role='button']": {
            "color": "#ffffff !important",
            "background_color": "#000000 !important",
        },
        ".a11y-high-contrast input::placeholder, .a11y-high-contrast textarea::placeholder": {
            "color": "#000000 !important",
            "opacity": "1 !important",
        },
        ".a11y-high-contrast :focus-visible": {
            "outline": "3px solid #000000 !important",
            "outline_offset": "3px",
        },
        ".a11y-reduce-motion *, .a11y-reduce-motion *::before, .a11y-reduce-motion *::after": {
            "animation_duration": "0.01ms !important",
            "animation_iteration_count": "1 !important",
            "animation_name": "none !important",
            "scroll_behavior": "auto !important",
            "transition_duration": "0.01ms !important",
        },
        ".nav-logout": {
            "min_height": "2.75rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--button-secondary-border)",
            "border_radius": "0.5rem",
            "background_color": "var(--button-secondary-bg)",
            "color": "var(--button-secondary-text)",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".nav-logout:hover": {
            "background_color": "var(--button-secondary-hover-bg)",
        },
        ".destructive-action": {
            "min_height": "2.75rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--button-danger-border)",
            "border_radius": "0.5rem",
            "background_color": "var(--button-danger-bg)",
            "color": "var(--button-danger-text)",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".destructive-action:hover": {
            "background_color": "var(--button-danger-hover-bg)",
        },
        ".warning-action": {
            "min_height": "2.75rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--button-warning-border)",
            "border_radius": "0.5rem",
            "background_color": "var(--button-warning-bg)",
            "color": "var(--button-warning-text)",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".warning-action:hover": {
            "background_color": "var(--button-warning-hover-bg)",
        },
        ".subtle-action": {
            "min_height": "2.75rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--button-subtle-border)",
            "border_radius": "0.5rem",
            "background_color": "var(--button-subtle-bg)",
            "color": "var(--button-subtle-text)",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".subtle-action:hover": {
            "background_color": "var(--button-subtle-hover-bg)",
        },
        ".main-content": {
            "width": "100%",
            "max_width": "75rem",
            "margin": "0 auto",
            "padding": "0",
        },
        ".content-section": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "flex-start",
            "gap": "1.25rem",
            "width": "100%",
            "max_width": "75rem",
            "margin": "0 auto 1.5rem",
            "padding": "1.5rem 0",
        },
        "*": {
            "min_width": "0",
        },
        ".home-hero": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "0 auto 1.5rem",
            "padding": "1.5rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".hero-layout": {
            "display": "grid",
            "grid_template_columns": "minmax(0, 1fr) minmax(14rem, 0.42fr)",
            "align_items": "center",
            "width": "100%",
            "gap": "1.5rem",
            "min_width": "0",
        },
        ".hero-copy-wrap": {
            "min_width": "0",
            "width": "100%",
        },
        ".eyebrow": {
            "display": "inline-flex",
            "padding": "0.25rem 0.6rem",
            "border_radius": "999px",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-700)",
            "font_size": "0.75rem",
            "font_weight": "700",
            "text_transform": "uppercase",
            "letter_spacing": "0.08em",
        },
        ".hero-copy": {
            "color": "var(--slate-700)",
            "font_size": "1.05rem",
            "max_width": "40rem",
        },
        ".hero-stat-panel": {
            "width": "100%",
            "min_width": "0",
        },
        ".hero-stat-grid": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.65rem",
            "width": "100%",
            "min_width": "0",
        },
        ".hero-stat-card": {
            "display": "flex",
            "flex_direction": "column",
            "justify_content": "center",
            "gap": "0.1rem",
            "width": "100%",
            "min_width": "0",
            "padding": "0.75rem 1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-soft)",
        },
        ".hero-stat-value": {
            "color": "var(--brand-700)",
            "font_family": "Georgia, 'Times New Roman', serif",
            "font_size": "1.75rem",
            "line_height": "1.1",
        },
        ".hero-stat-label": {
            "color": "var(--slate-700)",
            "font_size": "0.7rem",
            "letter_spacing": "0.08em",
            "text_transform": "uppercase",
        },
        ".home-stat-status": {
            "width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-700)",
        },
        ".primary-cta, .secondary-cta, .feature-card": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "min_height": "2.75rem",
            "padding": "0.65rem 1rem",
            "border_radius": "0.75rem",
            "text_decoration": "none",
            "font_weight": "700",
            "transition": "transform 150ms ease, box-shadow 150ms ease",
        },
        ".primary-cta": {
            "background_color": "var(--button-primary-bg)",
            "color": "var(--button-primary-text)",
            "box_shadow": "0 0.45rem 1rem rgba(24, 58, 74, 0.18)",
        },
        ".secondary-cta": {
            "border": "1px solid var(--button-secondary-border)",
            "background_color": "var(--button-secondary-bg)",
            "color": "var(--button-secondary-text)",
        },
        ".secondary-cta:hover": {
            "background_color": "var(--button-secondary-hover-bg)",
        },
        ".feature-card": {
            "flex": "1 1 12rem",
            "border": "1px solid var(--line)",
            "background_color": "var(--sand-100)",
            "color": "var(--brand-text)",
        },
        ".catalog-section": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "0 auto 1.5rem",
        },
        ".home-profile-summary": {
            "gap": "0.75rem",
            "padding": "1rem 1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
        },
        ".home-profile-summary h2": {
            "margin": "0",
        },
        ".home-summary-metrics": {
            "display": "flex",
            "flex_wrap": "wrap",
            "gap": "0.75rem",
            "width": "100%",
        },
        ".home-summary-metric": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.2rem",
            "min_width": "8rem",
            "padding": "0.65rem 0.85rem",
            "border_radius": "0.65rem",
            "background_color": "var(--bg-soft)",
        },
        ".home-section-copy": {
            "min_width": "0",
        },
        ".home-section-copy h2": {
            "margin": "0",
            "font_weight": "800",
        },
        ".home-section-subtitle": {
            "color": "var(--slate-700)",
        },
        ".home-book-section": {
            "gap": "1rem",
            "margin_bottom": "1.5rem",
            "padding": "1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".home-section-heading": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "1rem",
            "width": "100%",
            "min_width": "0",
        },
        ".home-book-section-content": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "stretch",
            "gap": "1rem",
            "width": "100%",
            "min_width": "0",
        },
        ".home-book-grid": {
            "grid_template_columns": "repeat(auto-fill, minmax(190px, 220px))",
            "align_items": "stretch",
            "justify_content": "start",
            "width": "100%",
        },
        ".home-empty-state": {
            "width": "100%",
            "padding": "0.75rem 1rem",
            "border_radius": "0.65rem",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-700)",
        },
        ".home-view-more": {
            "display": "inline-flex",
            "flex": "0 0 auto",
            "align_items": "center",
            "justify_content": "center",
            "align_self": "center",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.8rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.55rem",
            "background_color": "transparent",
            "color": "var(--text)",
            "font_weight": "600",
            "text_decoration": "none",
        },
        ".home-view-more:hover": {
            "background_color": "var(--bg-soft)",
            "color": "var(--text)",
        },
        ".home-category-section": {
            "gap": "0.75rem",
            "margin_bottom": "1.5rem",
            "padding": "1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".home-reservation-section": {
            "gap": "0.75rem",
            "margin_bottom": "1.5rem",
            "padding": "1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".home-about-section": {
            "padding": "1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".home-reservation-steps": {
            "display": "grid",
            "grid_template_columns": "repeat(3, minmax(0, 1fr))",
            "gap": "1rem",
            "width": "100%",
            "margin": "0",
            "padding_left": "1.25rem",
        },
        ".student-library-section": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "1rem",
            "width": "100%",
            "margin": "0 0 0.5rem",
            "padding": "clamp(1.1rem, 2.5vw, 1.6rem)",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".student-library-section h2": {
            "margin": "0",
            "color": "var(--slate-900)",
        },
        ".student-reservations-heading": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "0.75rem",
            "width": "100%",
        },
        ".student-reservations-heading h2": {
            "margin": "0",
        },
        ".student-reservations-count": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "min_width": "2.75rem",
            "min_height": "2.75rem",
            "padding": "0.4rem",
            "border_radius": "999px",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
            "font_weight": "700",
        },
        ".student-overdue-alert": {
            "width": "100%",
            "margin": "0 auto",
            "padding": "0.85rem 1rem",
            "border_left": "0.3rem solid var(--danger-700)",
            "border_radius": "0.5rem",
            "background_color": "var(--danger-100)",
            "color": "var(--danger-700)",
            "font_weight": "700",
        },
        ".student-overdue-section": {
            "border_color": "var(--danger-700)",
            "background_color": "var(--danger-100)",
        },
        ".student-overdue-section .catalog-card": {
            "border_color": "var(--danger-700)",
        },
        ".student-loan-deadline": {
            "padding": "0.5rem 0.75rem",
            "border_radius": "0.5rem",
            "background_color": "var(--warning-100)",
            "color": "var(--warning-700)",
            "font_weight": "700",
        },
        ".student-library-section > p": {
            "margin": "0",
            "color": "var(--slate-700)",
        },
        ".student-library-section > p[role='status']": {
            "width": "100%",
            "padding": "0.85rem 1rem",
            "border": "1px dashed var(--line)",
            "border_radius": "0.65rem",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-900)",
        },
        ".catalog-controls": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 12rem), 1fr))",
            "align_items": "end",
            "gap": "0.9rem",
            "width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".catalog-filter": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.5rem",
            "min_width": "0",
        },
        ".catalog-filter .signup-label": {
            "color": "var(--brand-text)",
            "font_size": "0.9rem",
        },
        ".catalog-grid": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fill, minmax(190px, 220px))",
            "gap": "1.1rem",
            "width": "100%",
            "justify_content": "start",
        },
        ".home-category-rail": {
            "display": "flex",
            "flex_wrap": "nowrap",
            "gap": "0.6rem",
            "width": "100%",
            "overflow_x": "auto",
            "margin_top": "1rem",
            "padding": "0.25rem 0",
        },
        ".home-category-chip": {
            "display": "inline-flex",
            "align_items": "center",
            "flex": "0 0 auto",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.9rem",
            "border": "1px solid var(--line)",
            "border_radius": "999px",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-700)",
            "font_weight": "700",
            "text_decoration": "none",
        },
        ".catalog-category-rail": {
            "margin": "0 0 0.75rem",
        },
        ".catalog-detail-card": {
            "display": "grid",
            "grid_template_columns": "minmax(12rem, 18rem) minmax(0, 1fr)",
            "align_items": "start",
            "gap": "1.5rem",
            "min_width": "0",
            "padding": "1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "0 0.35rem 1rem rgba(24, 43, 73, 0.06)",
        },
        ".reservation-tabs": {
            "display": "flex",
            "flex_wrap": "nowrap",
            "gap": "0.5rem",
            "width": "100%",
            "overflow_x": "auto",
        },
        ".reservation-tab": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "flex": "0 0 auto",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.9rem",
            "border": "1px solid var(--line)",
            "border_radius": "999px",
            "background_color": "var(--bg-panel)",
            "color": "var(--text)",
        },
        ".admin-catalog-grid": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "1.1rem",
            "width": "100%",
            "max_width": "100%",
            "min_width": "0",
            "overflow_x": "auto",
        },
        ".admin-catalog-section": {
            "width": "min(100%, 72rem)",
            "margin": "1.5rem auto",
            "padding": "clamp(1.25rem, 3vw, 2rem)",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".admin-title-card": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "stretch",
            "gap": "0.75rem",
            "min_width": "0",
            "width": "100%",
            "padding": "1.1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".admin-title-row": {
            "display": "grid",
            "grid_template_columns": "72px minmax(0, 1fr) auto",
            "align_items": "start",
            "gap": "1rem",
            "width": "100%",
        },
        ".admin-title-cover": {
            "display": "grid",
            "width": "72px",
            "aspect_ratio": "2 / 3",
            "overflow": "hidden",
            "border": "1px solid var(--line)",
            "border_radius": "0.45rem",
        },
        ".admin-catalog-cover-image, .admin-catalog-cover-fallback": {
            "width": "72px",
            "aspect_ratio": "2 / 3",
            "object_fit": "cover",
            "border_radius": "0.45rem",
            "border": "1px solid var(--line)",
        },
        ".admin-catalog-cover-fallback": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "padding": "0.35rem",
            "overflow_wrap": "anywhere",
            "background": "var(--bg-soft)",
            "color": "var(--slate-900)",
            "font_size": "0.72rem",
            "text_align": "center",
        },
        ".admin-title-data": {
            "min_width": "0",
        },
        ".admin-title-data p": {
            "margin": "0.25rem 0",
        },
        ".admin-title-actions, .admin-panel-actions": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "gap": "0.5rem",
        },
        ".admin-title-panel": {
            "width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background": "var(--bg-soft)",
        },
        ".admin-title-edit-form": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 12rem), 1fr))",
            "gap": "0.75rem",
            "width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-soft)",
        },
        ".admin-copy-list": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.25rem",
            "margin": "0",
            "padding_left": "1.25rem",
        },
        ".catalog-card": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "flex-start",
            "gap": "0.75rem",
            "min_width": "0",
            "padding": "1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "0 0.35rem 1rem rgba(24, 43, 73, 0.06)",
            "transition": "border-color 120ms ease, box-shadow 120ms ease, transform 120ms ease",
        },
        ".catalog-grid > :nth-child(-n+8), .admin-catalog-grid > :nth-child(-n+8), .librarian-list > :nth-child(-n+8)": {
            "animation": "biblioteca-page-enter 300ms ease-out both",
        },
        ".catalog-grid > :nth-child(2), .admin-catalog-grid > :nth-child(2), .librarian-list > :nth-child(2)": {
            "animation_delay": "40ms",
        },
        ".catalog-grid > :nth-child(3), .admin-catalog-grid > :nth-child(3), .librarian-list > :nth-child(3)": {
            "animation_delay": "80ms",
        },
        ".catalog-grid > :nth-child(4), .admin-catalog-grid > :nth-child(4), .librarian-list > :nth-child(4)": {
            "animation_delay": "120ms",
        },
        ".catalog-grid > :nth-child(5), .admin-catalog-grid > :nth-child(5), .librarian-list > :nth-child(5)": {
            "animation_delay": "160ms",
        },
        ".catalog-grid > :nth-child(6), .admin-catalog-grid > :nth-child(6), .librarian-list > :nth-child(6)": {
            "animation_delay": "200ms",
        },
        ".catalog-grid > :nth-child(7), .admin-catalog-grid > :nth-child(7), .librarian-list > :nth-child(7)": {
            "animation_delay": "240ms",
        },
        ".catalog-grid > :nth-child(8), .admin-catalog-grid > :nth-child(8), .librarian-list > :nth-child(8)": {
            "animation_delay": "280ms",
        },
        ".catalog-card:hover": {
            "transform": "translateY(-2px)",
            "border_color": "var(--brand-500)",
            "box_shadow": "0 0.6rem 1.25rem rgba(24, 43, 73, 0.1)",
        },
        ".admin-title-card:hover, .librarian-card:hover, .circulation-card:hover": {
            "transform": "translateY(-2px)",
            "box_shadow": "0 0.6rem 1.25rem rgba(24, 43, 73, 0.12)",
        },
        "button:hover": {
            "transform": "translateY(-2px)",
            "transition": "transform 150ms ease, box-shadow 150ms ease, background-color 150ms ease",
        },
        ".catalog-card-visual": {
            "display": "flex",
            "flex_direction": "column",
            "width": "100%",
            "gap": "0.6rem",
        },
        ".catalog-card-cover": {
            "display": "grid",
            "width": "100%",
            "aspect_ratio": "2 / 3",
            "overflow": "hidden",
            "border": "1px solid var(--line)",
            "border_radius": "0.8rem",
            "background_color": "var(--brand-900)",
            "color": "#ffffff",
        },
        ".catalog-cover-stack": {
            "display": "grid",
            "overflow": "hidden",
        },
        ".catalog-cover-generated, .catalog-real-cover-image": {
            "display": "block",
            "grid_area": "1 / 1",
            "width": "100%",
            "aspect_ratio": "2 / 3",
            "border_radius": "inherit",
            "object_fit": "cover",
        },
        ".catalog-card-cover-image": {
            "transition": "transform 150ms ease",
        },
        ".catalog-card-cover:hover .catalog-real-cover-image": {
            "transform": "scale(1.03)",
        },
        ".catalog-detail-visual": {
            "display": "grid",
            "width": "100%",
            "max_width": "22rem",
            "aspect_ratio": "2 / 3",
            "border_radius": "0.8rem",
            "border": "1px solid var(--line)",
        },
        ".catalog-cover-real-failed .catalog-real-cover-image": {
            "display": "none",
        },
        ".catalog-cover-0": {
            "background_color": "var(--brand-900)",
        },
        ".catalog-cover-1": {
            "background_color": "var(--success-700)",
        },
        ".catalog-cover-2": {
            "background_color": "var(--warning-700)",
        },
        ".catalog-cover-3": {
            "background_color": "var(--danger-700)",
        },
        ".catalog-cover-4": {
            "background_color": "#3f4f6b",
        },
        ".catalog-cover-initial": {
            "font_family": "Georgia, 'Times New Roman', serif",
            "font_size": "2rem",
            "font_weight": "700",
        },
        ".a11y-shell.a11y-dark .catalog-cover-0": {
            "background_color": "#163b5c",
        },
        ".a11y-shell.a11y-dark .catalog-cover-1": {
            "background_color": "#14532d",
        },
        ".a11y-shell.a11y-dark .catalog-cover-2": {
            "background_color": "#7c2d12",
        },
        ".a11y-shell.a11y-dark .catalog-cover-3": {
            "background_color": "#7f1d1d",
        },
        ".a11y-shell.a11y-dark .catalog-cover-4": {
            "background_color": "#312e81",
        },
        ".catalog-tag": {
            "display": "inline-flex",
            "align_self": "flex-start",
            "padding": "0.25rem 0.5rem",
            "border": "1px solid var(--line)",
            "border_radius": "999px",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-700)",
            "font_size": "0.75rem",
            "font_weight": "700",
        },
        ".catalog-card-heading, .catalog-detail-heading": {
            "overflow_wrap": "anywhere",
            "margin": "0",
            "line_height": "1.3",
        },
        ".catalog-card p": {
            "margin": "0",
            "color": "var(--slate-700)",
            "font_size": "0.95rem",
        },
        ".card-header-row": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "0.75rem",
            "width": "100%",
        },
        ".catalog-card-meta-row": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "0.75rem",
            "width": "100%",
            "flex_wrap": "wrap",
        },
        ".catalog-card-meta": {
            "color": "var(--slate-700)",
        },
        ".status-pill": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "1.8rem",
            "padding": "0.2rem 0.55rem",
            "border_radius": "999px",
            "font_size": "0.7rem",
            "font_weight": "700",
            "letter_spacing": "0.02em",
        },
        ".status-pill-success": {
            "background_color": "var(--success-100)",
            "color": "var(--success-700)",
            "animation": "biblioteca-availability-pulse 600ms ease-out 1",
        },
        ".status-pill-warning": {
            "background_color": "var(--warning-100)",
            "color": "var(--warning-700)",
        },
        ".status-pill-muted": {
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-700)",
        },
        ".catalog-card-link": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "transparent",
            "color": "var(--text)",
            "font_weight": "600",
            "text_decoration": "none",
        },
        ".catalog-card-link:hover": {
            "background_color": "var(--bg-soft)",
            "color": "var(--text)",
        },
        ".catalog-description": {
            "max_width": "100%",
            "white_space": "pre-wrap",
            "overflow_wrap": "anywhere",
        },
        ".signup-section": {
            "width": "min(100%, 34rem)",
            "margin": "2rem auto",
            "padding": "2rem",
            "align_items": "stretch",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".auth-tabs": {
            "display": "grid",
            "grid_template_columns": "repeat(2, minmax(0, 1fr))",
            "gap": "0.5rem",
            "width": "100%",
            "margin_bottom": "0.75rem",
        },
        ".auth-tab": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "min_height": "2.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "999px",
            "background_color": "var(--bg-panel)",
            "color": "var(--text)",
            "font_weight": "700",
            "text_decoration": "none",
        },
        ".auth-tab-active": {
            "border": "1px solid var(--brand-700)",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
        },
        ".admin-acervo-content": {
            "width": "100%",
            "max_width": "75rem",
            "margin": "1.5rem auto",
            "padding": "1.25rem 0",
            "align_items": "stretch",
        },
        ".admin-example-seed": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.75rem",
            "width": "min(100%, 75rem)",
            "min_width": "0",
            "margin": "0 auto",
            "padding": "1rem 1.25rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".admin-example-seed-summary": {
            "cursor": "pointer",
            "font_weight": "700",
        },
        ".librarian-management-section": {
            "width": "min(100%, 72rem)",
            "margin": "1rem auto",
            "padding": "clamp(1.25rem, 3vw, 2rem)",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".operational-counts": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 10rem), 1fr))",
            "gap": "0.75rem",
            "width": "100%",
        },
        ".operational-count": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.25rem",
            "padding": "0.85rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-soft)",
        },
        ".operational-count h1, .operational-count h2, .operational-count h3": {
            "margin": "0",
        },
        ".operational-count-label": {
            "color": "var(--slate-700)",
            "font_weight": "600",
        },
        ".circulation-tabs": {
            "display": "flex",
            "flex_wrap": "wrap",
            "gap": "0.5rem",
            "width": "100%",
            "border_bottom": "1px solid var(--line)",
        },
        ".circulation-tab": {
            "min_height": "44px",
            "padding": "0.65rem 1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.65rem 0.65rem 0 0",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-900)",
            "font_weight": "700",
            "cursor": "pointer",
        },
        ".circulation-tab[aria-selected='true']": {
            "border_color": "var(--brand-700)",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
        },
        ".circulation-tab-panel": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "flex-start",
            "gap": "1rem",
            "width": "100%",
        },
        ".staff-reservation-form": {
            "width": "100%",
            "margin": "1rem 0 0",
        },
        ".librarian-form": {
            "width": "min(100%, 34rem)",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.75rem",
            "background_color": "var(--bg-soft)",
        },
        ".librarian-list": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "1rem",
            "width": "100%",
            "max_width": "100%",
            "min_width": "0",
            "overflow_x": "auto",
        },
        ".librarian-card": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "flex-start",
            "gap": "0.75rem",
            "min_width": "0",
            "padding": "1.1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.85rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
            "overflow_wrap": "anywhere",
        },
        ".librarian-card h2, .librarian-card h3, .admin-title-card h2": {
            "margin": "0",
            "line_height": "1.3",
        },
        ".librarian-card p, .admin-title-card p": {
            "margin": "0",
            "color": "var(--slate-700)",
        },
        ".signup-form": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.75rem",
            "width": "100%",
        },
        ".acervo-new-title-closed": {
            "display": "none",
        },
        ".admin-acervo-toolbar": {
            "display": "grid",
            "grid_template_columns": "minmax(0, 1fr) auto",
            "align_items": "center",
            "gap": "0.75rem",
            "width": "100%",
            "max_width": "72rem",
        },
        ".signup-label": {
            "font_weight": "600",
            "margin_top": "0.5rem",
            "color": "var(--slate-900)",
        },
        ".campo": {
            "width": "100%",
            "min_height": "2.75rem",
            "height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-panel)",
            "caret_color": "var(--slate-900)",
            "box_shadow": "none",
            "line_height": "normal",
            "transition": "border-color 120ms ease, background-color 120ms ease",
        },
        ".campo-area": {
            "width": "100%",
            "min_height": "5.5rem",
            "height": "auto",
            "padding": "0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-panel)",
            "caret_color": "var(--slate-900)",
            "line_height": "1.5",
            "resize": "vertical",
        },
        ".campo-select": {
            "width": "100%",
            "min_height": "2.75rem",
            "height": "2.75rem",
            "padding": "0 0.75rem",
            "color": "var(--slate-900)",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "var(--bg-panel)",
            "caret_color": "var(--slate-900)",
            "line_height": "normal",
        },
        ".campo-check": {
            "width": "1.25rem",
            "height": "1.25rem",
            "min_height": "1.25rem",
            "margin": "0",
            "accent_color": "var(--brand-700)",
        },
        "input.campo:-webkit-autofill, input.campo:autofill": {
            "-webkit_text_fill_color": "var(--slate-900)",
            "caret_color": "var(--slate-900)",
            "box_shadow": "inset 0 0 0 1000px var(--bg-panel)",
            "transition": "background-color 9999s ease-out 0s",
        },
        ".category-checkbox-row": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
            "gap": "0.5rem",
        },
        ".campo-check-row": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
            "gap": "0.5rem",
            "cursor": "pointer",
        },
        ".campo:focus-visible, .campo-area:focus-visible, .campo-select:focus-visible, .campo-check:focus-visible": {
            "outline": "3px solid var(--brand-700)",
            "outline_offset": "2px",
        },
        ".campo::placeholder, .campo-area::placeholder": {
            "color": "var(--slate-700)",
            "opacity": "1",
        },
        "select option": {
            "color": "var(--slate-900)",
            "background_color": "var(--bg-panel)",
        },
        ".signup-feedback": {
            "width": "min(100%, 38rem)",
            "padding": "0.85rem 1rem",
            "border_radius": "0.5rem",
            "border": "1px solid var(--line)",
            "overflow_wrap": "anywhere",
            "line_height": "1.5",
        },
        ".signup-feedback-error": {
            "border_left": "4px solid var(--danger-700)",
            "background_color": "var(--danger-100)",
            "color": "var(--danger-700)",
        },
        ".signup-feedback-success": {
            "border_left": "4px solid var(--success-700)",
            "background_color": "var(--success-100)",
            "color": "var(--success-700)",
        },
        ".content-section > [role='status'], .catalog-section > [role='status']": {
            "width": "100%",
            "padding": "0.8rem 1rem",
            "border": "1px solid var(--brand-100)",
            "border_left": "4px solid var(--brand-700)",
            "border_radius": "0.6rem",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
        },
        ".content-section > [role='alert']:not(.signup-feedback)": {
            "width": "100%",
            "padding": "0.8rem 1rem",
            "border": "1px solid var(--warning-100)",
            "border_left": "4px solid var(--warning-700)",
            "border_radius": "0.6rem",
            "background_color": "var(--warning-100)",
            "color": "var(--warning-700)",
        },
        ".signup-confirmation": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "gap": "0.75rem",
            "width": "100%",
        },
        ".signup-note": {
            "max_width": "28rem",
            "font_size": "0.9rem",
        },
        ".focus-demo-field": {
            "width": "min(100%, 24rem)",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-panel)",
        },
        ".focus-demo-button": {
            "min_height": "2.75rem",
            "padding": "0.5rem 1rem",
            "border": "1px solid var(--button-primary-border)",
            "border_radius": "0.5rem",
            "background_color": "var(--button-primary-bg)",
            "color": "var(--button-primary-text)",
            "font_weight": "600",
            "cursor": "pointer",
            "transition": "background-color 120ms ease, transform 120ms ease",
        },
        ".focus-demo-button:hover": {
            "background_color": "var(--button-primary-hover-bg)",
        },
        ".focus-demo-button:active": {
            "transform": "translateY(1px)",
        },
        ".focus-demo-button:disabled, .nav-logout:disabled, .destructive-action:disabled, .warning-action:disabled, .subtle-action:disabled": {
            "border_style": "dashed",
            "cursor": "not-allowed",
        },
        ".emoji-acao, .emoji-selo": {
            "display": "inline-block",
            "font_size": "1.25em",
            "line_height": "1",
            "margin_right": "0.35em",
        },
        "[data-action-type]": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "gap": "0.25rem",
        },
        "[data-action-type='confirmar']": {
            "border_color": "var(--action-confirm-bg)",
            "background_color": "var(--action-confirm-bg)",
            "color": "var(--action-confirm-text)",
        },
        "[data-action-type='confirmar']:hover": {
            "background_color": "var(--action-confirm-hover-bg)",
            "color": "var(--action-confirm-text)",
        },
        "[data-action-type='perigo']": {
            "border_color": "var(--button-danger-border)",
            "background_color": "var(--button-danger-bg)",
            "color": "var(--button-danger-text)",
        },
        "[data-action-type='perigo']:hover": {
            "background_color": "var(--button-danger-hover-bg)",
            "color": "var(--button-danger-text)",
        },
        "[data-action-type='navegar']": {
            "border_color": "var(--button-primary-border)",
            "background_color": "var(--button-primary-bg)",
            "color": "var(--button-primary-text)",
        },
        "[data-action-type='navegar']:hover": {
            "background_color": "var(--button-primary-hover-bg)",
            "color": "var(--button-primary-text)",
        },
        "[data-action-type='atencao']": {
            "border_color": "var(--button-warning-border)",
            "background_color": "var(--button-warning-bg)",
            "color": "var(--button-warning-text)",
        },
        "[data-action-type='atencao']:hover": {
            "background_color": "var(--button-warning-hover-bg)",
            "color": "var(--button-warning-text)",
        },
        "a": {
            "color": "var(--brand-700)",
            "text_underline_offset": "0.2em",
        },
        ".site-footer": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "0.75rem 1.5rem",
            "max_width": "72rem",
            "margin": "0 auto",
            "padding": "0.75rem 1rem",
            "border_top": "1px solid var(--line)",
            "color": "var(--slate-700)",
            "font_size": "0.9rem",
        },
        ".footer-links a": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
            "padding": "0",
            "border": "none",
            "border_radius": "0",
            "background": "transparent",
            "color": "var(--text)",
            "text_decoration": "underline",
        },
        ".footer-about": {
            "display": "flex",
            "align_items": "baseline",
            "gap": "0.4rem",
            "margin": "0",
        },
        ".footer-about p, .footer-about-title": {
            "margin": "0",
        },
        ".footer-about-title": {
            "font_weight": "700",
            "color": "var(--slate-900)",
        },
        ".footer-links": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "gap": "0.75rem",
        },
        ".footer-links a, .brand-link": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
        },
        ".skip-link": {
            "position": "absolute",
            "top": "-5rem",
            "left": "1rem",
            "z_index": "10",
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
            "padding": "0.75rem 1rem",
            "border_radius": "0.5rem",
            "background_color": "var(--bg-panel)",
            "color": "var(--brand-700)",
        },
        ".skip-link:focus-visible": {
            "top": "1rem",
        },
        ":focus-visible": {
            "outline": "3px solid var(--brand-700)",
            "outline_offset": "3px",
        },
        "@media (prefers-reduced-motion: reduce)": {
            "*, *::before, *::after": {
                "animation_duration": "0.01ms !important",
                "animation_iteration_count": "1 !important",
                "animation_name": "none !important",
                "scroll_behavior": "auto !important",
                "transition_duration": "0.01ms !important",
            },
        },
        "@media screen and (max-width: 48rem)": {
            "a": {
                "display": "inline-flex",
                "align_items": "center",
                "min_height": "2.75rem",
            },
            ".app-shell": {
                "padding": "0.5rem",
            },
            ".site-header": {
                "display": "grid",
                "grid_template_columns": "minmax(0, 1fr)",
                "grid_template_areas": "\"logo\" \"nav\" \"busca\" \"acoes\"",
                "align_items": "center",
                "gap": "0.5rem",
                "padding": "0.75rem",
            },
            ".site-header > .brand-link": {
                "grid_area": "logo",
            },
            ".site-header > .site-primary-nav": {
                "grid_area": "nav",
                "overflow_x": "auto",
                "white_space": "nowrap",
            },
            ".site-header > .site-header-search-form": {
                "grid_area": "busca",
            },
            ".site-header > .site-header-actions": {
                "grid_area": "acoes",
            },
            ".hero-layout": {
                "align_items": "center",
                "grid_template_columns": "minmax(0, 1fr)",
            },
            ".hero-copy-wrap": {
                "width": "100%",
                "max_width": "100%",
            },
            ".home-reservation-steps": {
                "grid_template_columns": "minmax(0, 1fr)",
            },
            ".site-header-desktop": {
                "display": "none",
            },
            ".site-menu-toggle": {
                "display": "none",
            },
            ".brand-link": {
                "font_size": "1.2rem",
                "justify_content": "flex-start",
            },
            ".brand-link-label": {
                "display": "inline",
            },
            ".site-primary-nav": {
                "align_items": "stretch",
                "justify_content": "flex-start",
                "gap": "0.2rem",
                "width": "100%",
            },
            ".site-header-actions": {
                "align_items": "center",
                "justify_content": "flex-start",
                "flex_wrap": "wrap",
                "gap": "0.6rem",
                "width": "100%",
            },
            ".accessibility-menu-content": {
                "width": "min(20rem, 92vw)",
                "max_width": "min(20rem, 92vw)",
            },
            ".accessibility-menu .accessibility-menu-content": {
                "left": "0",
                "right": "auto",
            },
            ".footer-links": {
                "width": "100%",
            },
            ".admin-view-band": {
                "align_items": "center",
                "justify_content": "space-between",
                "gap": "0.25rem",
                "width": "100%",
            },
            ".admin-view-mode-label, .admin-view-reset": {
                "font_size": "0.65rem",
            },
            ".admin-view-reset": {
                "padding": "0.25rem",
            },
            ".content-section": {
                "padding": "1.25rem 0.25rem",
            },
            ".circulation-tabs": {
                "align_items": "stretch",
                "flex_direction": "column",
            },
            ".circulation-tab": {
                "width": "100%",
                "border_radius": "0.65rem",
            },
            ".signup-section": {
                "margin": "1rem auto",
                "padding": "1.25rem 1rem",
            },
            ".catalog-controls": {
                "grid_template_columns": "minmax(0, 1fr)",
                "padding": "0.75rem",
            },
            ".catalog-detail-card": {
                "grid_template_columns": "minmax(0, 1fr)",
            },
            ".catalog-detail-actions": {
                "align_items": "stretch",
                "width": "100%",
            },
            ".catalog-detail-actions button, .catalog-detail-actions a": {
                "width": "100%",
                "justify_content": "center",
            },
            ".librarian-card": {
                "width": "100%",
            },
            ".admin-catalog-section, .librarian-management-section": {
                "padding": "1.1rem 0.75rem",
            },
            ".admin-title-row": {
                "grid_template_columns": "72px minmax(0, 1fr)",
            },
            ".admin-title-actions": {
                "grid_column": "1 / -1",
                "width": "100%",
            },
            ".admin-title-actions button": {
                "flex": "1 1 8rem",
            },
            ".admin-title-edit-form, .librarian-form": {
                "padding": "0.75rem",
            },
        },
    },
    head_components=[rx.script(_APPEARANCE_SCRIPT)],
)
app.add_page(
    accessible_page(index),
    title="Biblioteca escolar",
    on_load=State.load_home,
)
app.add_page(
    accessible_page(student_signup),
    route="/cadastro",
    title="Cadastro de estudante",
    on_load=State.redirect_authenticated_auth_page,
)
app.add_page(
    accessible_page(login_page),
    route="/login",
    title="Entrar",
    on_load=State.redirect_authenticated_auth_page,
)
app.add_page(
    accessible_page(profile_page),
    route="/perfil",
    title="Meu perfil",
    on_load=State.require_authenticated_user,
)
app.add_page(
    accessible_page(accessibility_page),
    route="/acessibilidade",
    title="Acessibilidade",
)
app.add_page(
    accessible_page(public_catalog),
    route="/catalogo",
    title="Catálogo",
    on_load=State.load_public_catalog,
)
app.add_page(
    accessible_page(public_catalog_detail),
    route="/catalogo/[titulo_id]",
    title="Detalhes do título",
    on_load=State.load_public_catalog_detail,
)
app.add_page(
    accessible_page(student_reservations),
    route="/reservas",
    title="Reservas e empréstimos",
    on_load=State.load_student_library,
)
app.add_page(
    accessible_page(student_library_redirect),
    route="/minha-biblioteca",
    title="Redirecionando para reservas",
    on_load=State.redirect_student_library,
)
app.add_page(
    accessible_page(catalog_admin),
    route="/admin/acervo",
    title="Cadastro de acervo",
    on_load=State.load_catalog_page,
)
app.add_page(
    accessible_page(librarian_management),
    route="/admin/bibliotecarios",
    title="Gestão de bibliotecários",
    on_load=State.load_librarians,
)
app.add_page(
    accessible_page(circulation_page),
    route="/admin/reservas",
    title="Reservas e circulação",
    on_load=State.load_staff_reservations_dashboard,
)
app.add_page(
    accessible_page(circulation_page),
    route="/admin/circulacao",
    title="Empréstimos e devoluções",
    on_load=State.load_circulation_loans_tab,
)

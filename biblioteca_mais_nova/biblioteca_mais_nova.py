"""Estrutura inicial da interface da Biblioteca."""

import unicodedata
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Awaitable, Callable

import reflex as rx

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
    list_admin_catalog,
    list_categories,
    list_public_titles,
    update_title,
)
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
from biblioteca_mais_nova.xano_client import (
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
)


def _timestamp_is_past(
    value: str | int | float,
    now: datetime,
) -> bool:
    if type(value) in {int, float}:
        deadline = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        deadline = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
    return deadline < now


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
    selected_category_ids: list[int] = []
    catalog_categories_pending: bool = False
    catalog_title_created: bool = False
    catalog_created_codes: list[str] = []
    catalog_needs_manual_check: bool = False
    admin_catalog_entries: list[AdminCatalogEntry] = []
    admin_catalog_message: str = ""
    admin_catalog_has_error: bool = False
    admin_catalog_pending: bool = False
    admin_catalog_needs_manual_check: bool = False
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
    public_catalog_message: str = ""
    public_catalog_has_error: bool = False
    public_catalog_pending: bool = True
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
    student_request_pending: bool = False
    student_request_message: str = ""
    student_request_has_error: bool = False
    librarian_management_pending: bool = False
    librarian_management_message: str = ""
    librarian_management_has_error: bool = False
    librarian_management_success: bool = False
    librarian_management_search: str = ""
    managed_librarians: list[dict[str, Any]] = []
    staff_reservation_pending: bool = False
    staff_reservation_message: str = ""
    staff_reservation_has_error: bool = False
    staff_reservation_email: str = ""
    staff_reservation_student: dict[str, Any] = {}
    staff_reservation_title_options: list[dict[str, str]] = []
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
            visible.append(
                {
                    "id": title["id"],
                    "titulo": title["titulo"],
                    "autores": title["autores"],
                    "capa_url": title.get("capa_url") or "",
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
        category_names = {
            category["id"]: category["nome"]
            for category in self.public_catalog_categories
        }
        featured: list[dict[str, Any]] = []
        for entry in self.public_catalog_entries:
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
            cover_initial, cover_variant = _catalog_cover_identity(
                category_text,
                title["titulo"],
            )
            featured.append(
                {
                    "id": title["id"],
                    "titulo": title["titulo"],
                    "autores": title["autores"],
                    "capa_url": title.get("capa_url") or "",
                    "categorias": category_text,
                    "exemplares_disponiveis": entry[
                        "exemplares_disponiveis"
                    ],
                    "href": f"/catalogo/{title['id']}",
                    "cover_initial": cover_initial,
                    "cover_variant": cover_variant,
                }
            )
        return sorted(
            featured,
            key=lambda item: _catalog_search_key(item["titulo"]),
        )[:4]

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
        self.student_request_message = ""
        self.student_request_has_error = False
        self.librarian_management_pending = False
        self.librarian_management_message = ""
        self.librarian_management_has_error = False
        self.librarian_management_success = False
        self.managed_librarians = []
        self.staff_reservation_pending = False
        self.staff_reservation_message = ""
        self.staff_reservation_has_error = False
        self.staff_reservation_email = ""
        self.staff_reservation_student = {}
        self.staff_reservation_title_options = []
        self.staff_reservation_title_id = ""
        self.staff_reservation_needs_manual_check = False
        self.catalog_categories = []
        self.selected_category_ids = []
        self.catalog_categories_pending = False
        self.catalog_title_created = False
        self.catalog_created_codes = []
        self.catalog_needs_manual_check = False
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
    async def load_home(self):
        await self.load_public_catalog()

    @rx.event
    async def load_public_catalog(self):
        self.public_catalog_pending = True
        self.public_catalog_message = ""
        self.public_catalog_has_error = False
        try:
            titles = await list_public_titles()
            categories = await list_categories()
        except (XanoConfigurationError, XanoRequestError, XanoResponseError) as error:
            self.public_catalog_message = catalog_error_message(error)
            self.public_catalog_has_error = True
            self.public_catalog_pending = False
            return

        self.public_catalog_entries = titles
        self.public_catalog_categories = categories
        self.public_catalog_pending = False

    @rx.event
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
        self.public_catalog_detail = {
            "id": entry["titulo"]["id"],
            "titulo": entry["titulo"]["titulo"],
            "autores": entry["titulo"]["autores"],
            "capa_url": entry["titulo"].get("capa_url") or "",
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
        if self.public_catalog_detail.get("id") != title_id:
            return

        self.student_request_pending = True
        self.student_request_message = ""
        self.student_request_has_error = False
        try:
            result = await request_title_loan(title_id, self._session_token)
        except XanoResponseError as error:
            self.student_request_has_error = True
            if error.public_detail:
                self.student_request_message = error.public_detail
            elif error.status_code == 403:
                self.student_request_message = (
                    "Seu perfil não está autorizado a solicitar este título."
                )
            elif error.status_code == 409:
                self.student_request_message = (
                    "A solicitação foi recusada. Verifique se há atraso, uma reserva "
                    "ativa ou outro impedimento antes de tentar novamente."
                )
            elif error.status_code >= 500:
                self.student_request_message = (
                    "Não foi possível confirmar o resultado. Confira Minha biblioteca "
                    "antes de fazer outra solicitação."
                )
            else:
                self.student_request_message = (
                    "Não foi possível solicitar este título. Confira sua sessão e "
                    "tente novamente."
                )
        except (XanoConfigurationError, XanoRequestError) as error:
            self.student_request_has_error = True
            self.student_request_message = (
                "Não foi possível confirmar o resultado. Confira Minha biblioteca "
                "antes de fazer outra solicitação."
                if isinstance(error, XanoRequestError)
                else catalog_error_message(error)
            )
        else:
            if result["estado"] == "em_reserva":
                self.student_request_message = (
                    "Sua solicitação foi registrada na fila de reservas."
                )
            else:
                self.student_request_message = (
                    "Sua solicitação foi registrada. A equipe da biblioteca "
                    "confirmará a retirada."
                )
        self.student_request_pending = False

    @rx.event
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
        try:
            loans = await list_my_loans(self._session_token)
            requests = await list_my_requests(self._session_token)
            reservations = await list_my_reservations(self._session_token)
            titles = await list_public_titles()
        except (XanoConfigurationError, XanoRequestError, XanoResponseError) as error:
            self.student_library_message = catalog_error_message(error)
            self.student_library_has_error = True
            if isinstance(error, XanoResponseError) and error.status_code == 401:
                self._clear_session_token()
                self.student_library_requires_login = True
            self.student_library_pending = False
            return

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
        self.student_library_pending = False

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
    async def load_librarians(self):
        if not self._is_admin():
            return self._redirect_non_admin()

        self.librarian_management_pending = True
        self.librarian_management_message = ""
        self.librarian_management_has_error = False
        try:
            self.managed_librarians = await list_librarians(
                self._session_token
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
        try:
            await action()
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
        try:
            self.catalog_categories = await list_categories()
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
    async def load_catalog_page(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        await self._load_catalog_categories()
        if not self.catalog_has_error:
            await self._refresh_admin_catalog()

    async def _refresh_admin_catalog(self):
        self.admin_catalog_pending = True
        self.admin_catalog_has_error = False
        try:
            self.admin_catalog_entries = await list_admin_catalog(
                self._session_token
            )
        except (
            XanoConfigurationError,
            XanoRequestError,
            XanoResponseError,
        ) as error:
            self.admin_catalog_message = catalog_error_message(error)
            self.admin_catalog_has_error = True
        finally:
            self.admin_catalog_pending = False

    @rx.event
    async def refresh_admin_catalog(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        self.admin_catalog_message = ""
        await self._refresh_admin_catalog()

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
        try:
            self.admin_catalog_pending = True
            payload = build_title_payload(form_data)
            await update_title(
                title_id,
                payload,
                self._session_token,
                active=active,
            )
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

        self.admin_catalog_message = (
            "Título reativado." if active else "Título desativado."
        )
        self.admin_catalog_has_error = False
        await self._refresh_admin_catalog()

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
        await self._process_pending_categories()
        if not self.catalog_categories_pending and not self.catalog_has_error:
            await self._refresh_admin_catalog()

    async def _process_pending_categories(self):
        if self._catalog_title_id is None:
            return
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
        if not self.catalog_categories_pending:
            self.catalog_message = "Título e categorias cadastrados."
            self.catalog_has_error = False
            self.catalog_needs_manual_check = False

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
        await self._process_pending_categories()
        if not self.catalog_categories_pending and not self.catalog_has_error:
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
        rx.link("Catálogo", href="/catalogo"),
        rx.cond(
            State.active_navigation_role == "Estudante",
            rx.link("Reservas", href="/reservas"),
            rx.fragment(),
        ),
        rx.cond(
            State.active_navigation_role == "Bibliotecária",
            rx.fragment(
                rx.link("Acervo", href="/admin/acervo"),
                rx.link("Reservas", href="/admin/reservas"),
            ),
            rx.cond(
                State.active_navigation_role == "Admin",
                rx.link("Contas", href="/admin/bibliotecarios"),
                rx.fragment(),
            ),
        ),
        aria_label="Navegação principal",
        class_name="site-primary-nav",
    )


def admin_view_status() -> rx.Component:
    return rx.cond(
        State.can_manage_librarians,
        rx.el.div(
            rx.text(
                "Modo de visualização: ",
                rx.cond(
                    State.admin_view_mode == "estudante",
                    "Estudante",
                    rx.cond(
                        State.admin_view_mode == "bibliotecaria",
                        "Bibliotecária",
                        "Admin",
                    ),
                ),
                role="status",
                aria_live="polite",
                class_name="admin-view-mode-label",
            ),
            rx.cond(
                State.admin_view_mode != "",
                rx.button(
                    "Voltar à visão de admin",
                    type="button",
                    on_click=State.reset_admin_view_mode,
                    class_name="admin-view-reset",
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
  window.__bibliotecaProfileDisclosureInstalled = true;
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
        setText(button, preferences.highContrast
          ? "Alto contraste: ativo" : "Ativar alto contraste");
        button.setAttribute("aria-pressed", String(preferences.highContrast));
      }
      if (action === "reduce-motion") {
        setText(button, preferences.reduceMotion
          ? "Movimento reduzido: ativo" : "Reduzir movimento");
        button.setAttribute("aria-pressed", String(preferences.reduceMotion));
      }
      if (action === "theme") {
        const dark = preferences.theme === "dark" ||
          (preferences.theme === "system" && colorScheme.matches);
        button.setAttribute("aria-checked", String(dark));
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
    document.querySelectorAll("details.profile-menu[open]").forEach((item) => {
      if (!item.contains(event.target)) item.open = false;
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const disclosure = document.querySelector("details.profile-menu[open]");
    if (!disclosure) return;
    document.querySelectorAll("details.profile-menu[open]").forEach((item) => {
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
        rx.el.div("Tamanho da fonte", class_name="profile-menu-identity"),
        rx.el.div(
            rx.button(
                "A−",
                type="button",
                aria_label="Diminuir fonte",
                data_appearance_action="font-decrease",
                class_name="profile-menu-item",
            ),
            rx.button(
                rx.el.span("100%", data_appearance_font_value="true"),
                type="button",
                aria_label="Tamanho atual da fonte",
                data_appearance_action="font-reset",
                class_name="profile-menu-item",
            ),
            rx.button(
                "A+",
                type="button",
                aria_label="Aumentar fonte",
                data_appearance_action="font-increase",
                class_name="profile-menu-item",
            ),
            class_name="profile-menu-controls",
        ),
        rx.button(
            "Ativar alto contraste",
            type="button",
            aria_pressed=False,
            data_appearance_action="high-contrast",
            class_name="profile-menu-item",
        ),
        rx.button(
            "Reduzir movimento",
            type="button",
            aria_pressed=False,
            data_appearance_action="reduce-motion",
            class_name="profile-menu-item",
        ),
        rx.el.button(
            "Modo escuro",
            type="button",
            role="switch",
            aria_checked=False,
            data_appearance_action="theme",
            class_name="profile-menu-item",
        ),
        class_name="profile-appearance-controls",
    )


def profile_menu() -> rx.Component:
    return rx.fragment(
        rx.el.details(
            rx.el.summary(
                "Perfil",
                aria_label="Abrir menu Perfil",
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
                        profile_appearance_controls(),
                        rx.cond(
                            State.can_manage_librarians,
                            rx.fragment(
                                rx.el.div(
                                    "Modo de visualização",
                                    class_name="profile-menu-identity",
                                ),
                                rx.el.button(
                                    rx.cond(
                                        State.admin_view_mode == "",
                                        "✓ Admin",
                                        "Admin",
                                    ),
                                    type="button",
                                    role="radio",
                                    aria_checked=State.admin_view_mode == "",
                                    on_click=State.reset_admin_view_mode,
                                    class_name="profile-menu-item",
                                ),
                                rx.el.button(
                                    rx.cond(
                                        State.admin_view_mode == "bibliotecaria",
                                        "✓ Bibliotecária",
                                        "Bibliotecária",
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
                                ),
                                rx.el.button(
                                    rx.cond(
                                        State.admin_view_mode == "estudante",
                                        "✓ Estudante",
                                        "Estudante",
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
                                ),
                            ),
                            rx.fragment(),
                        ),
                        rx.button(
                            "Sair",
                            type="button",
                            on_click=State.logout,
                            class_name="profile-menu-item",
                        ),
                    ),
                    rx.fragment(
                        rx.link(
                            "Entrar",
                            href="/login",
                            class_name="profile-menu-item",
                        ),
                        rx.link(
                            "Cadastrar-se",
                            href="/cadastro",
                            class_name="profile-menu-item",
                        ),
                        profile_appearance_controls(),
                    ),
                ),
                class_name="profile-menu-content",
            ),
            class_name="profile-menu",
        ),
    )


def site_header() -> rx.Component:
    brand = rx.link(
        "Biblioteca escolar",
        href="/",
        class_name="brand-link",
    )
    mobile_profile_actions = rx.el.div(
        admin_view_status(),
        profile_menu(),
        class_name="site-header-actions",
    )
    return rx.el.header(
        brand,
        rx.button(
            rx.el.span(
                rx.el.span(class_name="menu-hamburger-line"),
                rx.el.span(class_name="menu-hamburger-line"),
                rx.el.span(class_name="menu-hamburger-line"),
                aria_hidden="true",
                class_name="menu-hamburger-icon",
            ),
            type="button",
            aria_label=rx.cond(
                State.mobile_navigation_open,
                "Fechar menu",
                "Abrir menu",
            ),
            aria_expanded=State.mobile_navigation_open,
            aria_controls="navegacao-movel",
            on_click=State.toggle_mobile_navigation,
            class_name="site-menu-toggle",
        ),
        rx.el.div(
            site_primary_nav(),
            rx.el.div(
                admin_view_status(),
                profile_menu(),
                class_name="site-header-actions",
            ),
            class_name="site-header-desktop",
        ),
        rx.el.div(
            site_primary_nav(),
            mobile_profile_actions,
            id="navegacao-movel",
            aria_hidden=~State.mobile_navigation_open,
            class_name=rx.cond(
                State.mobile_navigation_open,
                "site-header-mobile-panel is-open",
                "site-header-mobile-panel",
            ),
        ),
        class_name="site-header",
    )


def site_footer() -> rx.Component:
    return rx.el.footer(
        rx.el.section(
            rx.text(
                "Biblioteca escolar",
                class_name="footer-about-title",
            ),
            class_name="footer-about",
        ),
        rx.el.nav(
            rx.link("Catálogo", href="/catalogo"),
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
    return rx.el.span(category["nome"], class_name="home-category-chip")


def _catalog_cover_class(cover_variant: rx.Var[int]) -> rx.Var[str]:
    return rx.cond(
        cover_variant == 0,
        "catalog-card-cover catalog-cover-0",
        rx.cond(
            cover_variant == 1,
            "catalog-card-cover catalog-cover-1",
            rx.cond(
                cover_variant == 2,
                "catalog-card-cover catalog-cover-2",
                rx.cond(
                    cover_variant == 3,
                    "catalog-card-cover catalog-cover-3",
                    "catalog-card-cover catalog-cover-4",
                ),
            ),
        ),
    )


def public_catalog_card(title: rx.Var[dict[str, Any]]) -> rx.Component:
    title_name = title["titulo"].to(str)
    category_text = title["categorias"].to(str)
    available_count = title["exemplares_disponiveis"].to(int)
    cover_variant = title["cover_variant"].to(int)
    cover_class = _catalog_cover_class(cover_variant)
    return rx.el.article(
        rx.el.div(
            rx.cond(
                title["capa_url"].to(str) != "",
                rx.el.img(
                    src=title["capa_url"],
                    alt="Capa do livro",
                    loading="lazy",
                    class_name="catalog-card-cover-image",
                ),
                rx.el.div(
                    rx.el.span(
                        title["cover_initial"],
                        class_name="catalog-cover-initial",
                    ),
                    class_name=cover_class,
                    aria_hidden="true",
                ),
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
                rx.el.span("Disponível", class_name="status-pill status-pill-success"),
                rx.el.span(
                    "Indisponível",
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
        rx.link("Ver detalhes", href=title["href"], class_name="catalog-card-link"),
        class_name="catalog-card",
    )


def student_loan_card(loan: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.el.h3(loan["titulo"], class_name="catalog-card-heading"),
            rx.cond(
                loan["em_atraso"],
                rx.el.span("Atrasado", class_name="status-pill status-pill-warning"),
                rx.el.span("Em andamento", class_name="status-pill status-pill-success"),
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
                rx.link(request["titulo"], href=request["href"]),
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
                rx.link(reservation["titulo"], href=reservation["href"]),
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
            "Pular para o conteúdo",
            href="#conteudo-catalogo",
            class_name="skip-link",
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Catálogo", size="7"),
                rx.text(
                    "Consulte os títulos e a quantidade de exemplares disponíveis."
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Buscar por título ou autoria",
                            html_for="catalog-search",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-search",
                            type="search",
                            value=State.public_catalog_search,
                            on_change=State.set_public_catalog_search,
                            aria_label="Buscar por título ou autoria",
                            class_name="signup-input",
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
                            class_name="signup-input",
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
                            class_name="signup-input",
                        ),
                        class_name="catalog-filter",
                    ),
                    rx.checkbox(
                        text="Somente disponíveis",
                        checked=State.public_catalog_only_available,
                        on_change=State.set_public_catalog_only_available,
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
            "Pular para o conteúdo",
            href="#conteudo-detalhe",
            class_name="skip-link",
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
                        rx.el.div(
                            rx.cond(
                                State.public_catalog_detail["capa_url"] != "",
                                rx.el.img(
                                    src=State.public_catalog_detail["capa_url"],
                                    alt="Capa do título",
                                    loading="lazy",
                                    class_name="catalog-detail-cover-image",
                                ),
                                rx.el.div(
                                    rx.el.span(
                                        State.public_catalog_detail[
                                            "cover_initial"
                                        ],
                                        class_name="catalog-cover-initial",
                                    ),
                                    class_name=_catalog_cover_class(
                                        State.public_catalog_detail[
                                            "cover_variant"
                                        ].to(int)
                                    ),
                                    aria_hidden="true",
                                ),
                            ),
                            class_name="catalog-detail-visual",
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
                            "Reservar",
                            type="button",
                            disabled=State.student_request_pending,
                            on_click=State.request_catalog_title(
                                State.public_catalog_detail["id"]
                            ),
                            class_name="focus-demo-button",
                        ),
                        align="start",
                        width="100%",
                    ),
                    rx.cond(
                        State.is_authenticated,
                        rx.fragment(),
                        rx.link(
                            "Entrar para reservar",
                            href="/login",
                            class_name="primary-cta",
                        ),
                    ),
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
            rx.heading("Aguardando aprovação", size="5"),
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
            rx.heading("Aprovadas", size="5"),
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
            rx.heading("Emprestados", size="5"),
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
            rx.heading("Em atraso", size="5"),
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
            "Pular para o conteúdo",
            href="#conteudo-reservas",
            class_name="skip-link",
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
                overdue_section,
                rx.fragment(),
            ),
            rx.el.section(
                rx.heading("Reservas e empréstimos", size="7"),
                rx.text(
                    "Acompanhe pedidos, retiradas e prazos da sua conta."
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
                            rx.link("Entrar novamente", href="/login"),
                            rx.fragment(),
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
                        awaiting_approval_section,
                        approved_section,
                        borrowed_section,
                        rx.cond(
                            State.student_overdue_loans.length() == 0,
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
            "Pular para o conteúdo",
            href="#conteudo-redirecionamento-reservas",
            class_name="skip-link",
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
            "Pular para o conteúdo",
            href="#conteudo-home",
            class_name="skip-link",
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
                            "Explore o acervo, acompanhe empréstimos e reservas e aproveite uma biblioteca que combina tradição e praticidade.",
                            class_name="hero-copy",
                        ),
                        align="start",
                        spacing="3",
                        class_name="hero-copy-wrap",
                    ),
                    rx.cond(
                        State.public_catalog_pending,
                        rx.text(
                            "Carregando indicadores do acervo...",
                            role="status",
                            class_name="home-stat-status",
                        ),
                        rx.cond(
                            State.public_catalog_has_error,
                            rx.text(
                                "Indicadores do acervo indisponíveis.",
                                role="status",
                                class_name="home-stat-status",
                            ),
                            rx.el.aside(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.strong(
                                            State.home_total_titles,
                                            class_name="hero-stat-value",
                                        ),
                                        rx.text(
                                            "Títulos",
                                            class_name="hero-stat-label",
                                        ),
                                        class_name="hero-stat-card",
                                    ),
                                    rx.el.div(
                                        rx.el.strong(
                                            State.home_available_copies,
                                            class_name="hero-stat-value",
                                        ),
                                        rx.text(
                                            "Exemplares disponíveis",
                                            class_name="hero-stat-label",
                                        ),
                                        class_name="hero-stat-card",
                                    ),
                                    rx.el.div(
                                        rx.el.strong(
                                            State.home_category_count,
                                            class_name="hero-stat-value",
                                        ),
                                        rx.text(
                                            "Categorias",
                                            class_name="hero-stat-label",
                                        ),
                                        class_name="hero-stat-card",
                                    ),
                                    class_name="hero-stat-grid",
                                ),
                                aria_label="Estatísticas do catálogo público",
                            ),
                        ),
                    ),
                    class_name="hero-layout",
                ),
                id="conteudo-home",
                class_name="content-section home-hero",
            ),
            rx.el.section(
                rx.el.div(
                    rx.vstack(
                        rx.heading("📚 Livros em destaque", size="5"),
                        rx.text(
                            "Alguns títulos disponíveis no catálogo da biblioteca."
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.link(
                        "Ver mais",
                        href="/catalogo",
                        class_name="section-more-link",
                    ),
                    class_name="home-section-heading",
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
                rx.cond(
                    (~State.public_catalog_pending)
                    & (~State.public_catalog_has_error)
                    & (State.home_featured_titles.length() == 0),
                    rx.text(
                        "Nenhum título disponível no catálogo no momento.",
                        role="status",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    (~State.public_catalog_has_error)
                    & (State.home_featured_titles.length() > 0),
                    rx.el.div(
                        rx.foreach(
                            State.home_featured_titles,
                            public_catalog_card,
                        ),
                        class_name="catalog-grid",
                    ),
                    rx.fragment(),
                ),
                id="livros-destaque",
                class_name="content-section catalog-section home-catalog-section",
            ),
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
        rx.link("Pular para o conteúdo", href="#conteudo-cadastro", class_name="skip-link"),
        site_header(),
        rx.el.main(
            rx.el.section(
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
                    rx.input(
                        id="signup-nome",
                        name="nome",
                        type="text",
                        required=True,
                        aria_label="Nome",
                        class_name="signup-input",
                    ),
                    rx.el.label(
                        "E-mail",
                        html_for="signup-email",
                        class_name="signup-label",
                    ),
                    rx.input(
                        id="signup-email",
                        name="email",
                        type="email",
                        required=True,
                        aria_label="E-mail",
                        class_name="signup-input",
                    ),
                    rx.el.label(
                        "Senha",
                        html_for="signup-senha",
                        class_name="signup-label",
                    ),
                    rx.input(
                        id="signup-senha",
                        name="senha",
                        type="password",
                        required=True,
                        aria_label="Senha",
                        class_name="signup-input",
                    ),
                    rx.button(
                        "Criar conta",
                        type="submit",
                        class_name="focus-demo-button",
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
                rx.link("Já tem conta? Entrar", href="/login"),
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
        rx.link("Pular para o conteúdo", href="#conteudo-login", class_name="skip-link"),
        site_header(),
        rx.el.main(
            rx.el.section(
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
                    rx.input(
                        id="login-email",
                        name="email",
                        type="email",
                        required=True,
                        aria_label="E-mail",
                        class_name="signup-input",
                    ),
                    rx.el.label(
                        "Senha",
                        html_for="login-senha",
                        class_name="signup-label",
                    ),
                    rx.input(
                        id="login-senha",
                        name="senha",
                        type="password",
                        required=True,
                        aria_label="Senha",
                        class_name="signup-input",
                    ),
                    rx.button(
                        "Entrar",
                        type="submit",
                        class_name="focus-demo-button",
                    ),
                    id="form-login",
                    on_submit=State.submit_login,
                    reset_on_submit=False,
                    class_name="signup-form",
                ),
                rx.link("Ver catálogo sem entrar", href="/catalogo"),
                rx.link("Não tem conta? Cadastre-se", href="/cadastro"),
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
            "Pular para o conteúdo",
            href="#conteudo-perfil",
            class_name="skip-link",
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
            class_name="main-content",
        ),
        site_footer(),
        class_name="app-shell",
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
                "Diminuir fonte",
                type="button",
                data_appearance_action="font-decrease",
                class_name="a11y-control-button",
            ),
            rx.button(
                "Tamanho padrão",
                type="button",
                data_appearance_action="font-reset",
                class_name="a11y-control-button",
            ),
            rx.button(
                "Aumentar fonte",
                type="button",
                data_appearance_action="font-increase",
                class_name="a11y-control-button",
            ),
            class_name="a11y-controls",
        ),
        rx.el.div(
            rx.button(
                "Ativar alto contraste",
                type="button",
                aria_pressed=False,
                data_appearance_action="high-contrast",
                class_name="a11y-control-button",
            ),
            rx.button(
                "Reduzir movimento",
                type="button",
                aria_pressed=False,
                data_appearance_action="reduce-motion",
                class_name="a11y-control-button",
            ),
            class_name="a11y-controls",
        ),
        id="controles-acessibilidade",
        class_name="content-section accessibility-controls-section",
    )


def accessibility_page() -> rx.Component:
    return rx.box(
        rx.link(
            "Pular para o conteúdo",
            href="#conteudo-acessibilidade",
            class_name="skip-link",
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
    return rx.checkbox(
        text=category["nome"],
        checked=State.selected_category_ids.contains(category["id"]),
        disabled=State.catalog_title_created,
        on_change=State.toggle_catalog_category(category["id"]),
    )


def admin_copy_row(copy: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.li(
        rx.text(copy["codigo_tombo"], " — ", copy["estado"]),
        class_name="admin-copy-row",
    )


def admin_title_card(title: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.heading(title["titulo"], size="4"),
        rx.text("Autores: ", title["autores"]),
        rx.text("Estado: ", rx.cond(title["ativo"], "Ativo", "Desativado")),
        rx.text("Categorias: ", title["categorias"]),
        rx.text(
            "Exemplares disponíveis: ",
            title["exemplares_disponiveis"],
        ),
        rx.cond(
            title["exemplares"].length() > 0,
            rx.el.ul(
                rx.foreach(title["exemplares"], admin_copy_row),
                class_name="admin-copy-list",
            ),
            rx.text("Nenhum exemplar cadastrado.", role="status"),
        ),
        rx.form(
            rx.input(type="hidden", name="titulo_id", value=title["id"]),
            rx.el.label(
                "Título",
                rx.input(
                    name="titulo",
                    type="text",
                    required=True,
                    default_value=title["titulo"],
                    aria_label="Título",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "Autores",
                rx.input(
                    name="autores",
                    type="text",
                    required=True,
                    default_value=title["autores"],
                    aria_label="Autores",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "ISBN (opcional)",
                rx.input(
                    name="isbn",
                    type="text",
                    default_value=title["isbn"],
                    aria_label="ISBN (opcional)",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "Editora (opcional)",
                rx.input(
                    name="editora",
                    type="text",
                    default_value=title["editora"],
                    aria_label="Editora (opcional)",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "Edição (opcional)",
                rx.input(
                    name="edicao",
                    type="text",
                    default_value=title["edicao"],
                    aria_label="Edição (opcional)",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "Ano de publicação (opcional)",
                rx.input(
                    name="ano_publicacao",
                    type="number",
                    default_value=title["ano_publicacao"],
                    aria_label="Ano de publicação (opcional)",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "Descrição (opcional)",
                rx.text_area(
                    name="descricao",
                    default_value=title["descricao"],
                    aria_label="Descrição (opcional)",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.el.label(
                "Link da imagem da capa (HTTPS, opcional)",
                rx.input(
                    name="capa_url",
                    type="url",
                    default_value=title["capa_url"],
                    aria_label="Link da imagem da capa (HTTPS, opcional)",
                    class_name="signup-input",
                ),
                class_name="signup-label",
            ),
            rx.button(
                "Salvar alterações",
                type="submit",
                disabled=State.admin_catalog_pending,
                class_name="focus-demo-button",
            ),
            on_submit=State.save_admin_title,
            reset_on_submit=False,
            class_name="admin-title-edit-form",
        ),
        rx.hstack(
            rx.button(
                "Adicionar exemplar",
                type="button",
                on_click=State.add_copy_to_title(title["id"]),
                disabled=State.admin_catalog_pending
                | State.admin_catalog_needs_manual_check,
                class_name="focus-demo-button",
            ),
            rx.cond(
                title["ativo"],
                rx.button(
                    "Desativar título",
                    type="button",
                    on_click=State.set_title_active(title["id"], False),
                    disabled=State.admin_catalog_pending,
                    class_name="destructive-action",
                ),
                rx.button(
                    "Reativar título",
                    type="button",
                    on_click=State.set_title_active(title["id"], True),
                    disabled=State.admin_catalog_pending,
                    class_name="focus-demo-button",
                ),
            ),
            flex_wrap="wrap",
            align="center",
        ),
        class_name="admin-title-card",
    )


def catalog_admin() -> rx.Component:
    return rx.box(
        rx.link("Pular para o conteúdo", href="#conteudo-acervo", class_name="skip-link"),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Cadastro de título e exemplares", size="7"),
                rx.text(
                    "Acesso restrito a bibliotecários e admins. As categorias disponíveis "
                    "são carregadas do catálogo."
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
                                "Retomar associações de categorias",
                                type="button",
                                on_click=State.retry_catalog_categories,
                                class_name="focus-demo-button",
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
                                "Criar um exemplar",
                                type="button",
                                on_click=State.create_catalog_copy,
                                class_name="focus-demo-button",
                                disabled=State.catalog_needs_manual_check
                                | State.catalog_categories_pending,
                            ),
                            rx.fragment(),
                        ),
                        rx.button(
                            "Iniciar outro título",
                            type="button",
                            on_click=State.start_new_catalog_title,
                            class_name="focus-demo-button",
                            disabled=State.catalog_needs_manual_check
                            | State.catalog_categories_pending,
                        ),
                        align="start",
                        width="100%",
                    ),
                    rx.form(
                        rx.el.label(
                            "Título",
                            html_for="catalog-titulo",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-titulo",
                            name="titulo",
                            type="text",
                            required=True,
                            aria_label="Título",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "Autores",
                            html_for="catalog-autores",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-autores",
                            name="autores",
                            type="text",
                            required=True,
                            aria_label="Autores",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "ISBN (opcional)",
                            html_for="catalog-isbn",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-isbn",
                            name="isbn",
                            type="text",
                            aria_label="ISBN (opcional)",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "Editora (opcional)",
                            html_for="catalog-editora",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-editora",
                            name="editora",
                            type="text",
                            aria_label="Editora (opcional)",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "Edição (opcional)",
                            html_for="catalog-edicao",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-edicao",
                            name="edicao",
                            type="text",
                            aria_label="Edição (opcional)",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "Ano de publicação (opcional)",
                            html_for="catalog-ano-publicacao",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-ano-publicacao",
                            name="ano_publicacao",
                            type="number",
                            aria_label="Ano de publicação (opcional)",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "Descrição (opcional)",
                            html_for="catalog-descricao",
                            class_name="signup-label",
                        ),
                        rx.text_area(
                            id="catalog-descricao",
                            name="descricao",
                            aria_label="Descrição (opcional)",
                            class_name="signup-input",
                        ),
                        rx.el.label(
                            "Link da imagem da capa (HTTPS, opcional)",
                            html_for="catalog-capa-url",
                            class_name="signup-label",
                        ),
                        rx.input(
                            id="catalog-capa-url",
                            name="capa_url",
                            type="url",
                            aria_label="Link da imagem da capa (HTTPS, opcional)",
                            class_name="signup-input",
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
                            "Cadastrar título",
                            type="submit",
                            class_name="focus-demo-button",
                        ),
                        id="form-cadastro-titulo",
                        on_submit=State.submit_catalog_title,
                        reset_on_submit=False,
                        class_name="signup-form",
                    ),
                ),
                id="conteudo-acervo",
                class_name="content-section signup-section",
            ),
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
                    State.admin_catalog_pending,
                    rx.text("Carregando acervo…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.admin_catalog_display_entries.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            State.admin_catalog_display_entries,
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
                            rx.text(
                                "Nenhum título cadastrado.",
                                role="status",
                            ),
                        ),
                    ),
                ),
                rx.button(
                    "Atualizar acervo",
                    type="button",
                    on_click=State.refresh_admin_catalog,
                    disabled=State.admin_catalog_pending,
                    class_name="nav-logout",
                ),
                rx.cond(
                    State.admin_catalog_needs_manual_check,
                    rx.button(
                        "Conferi a lista; liberar novas operações",
                        type="button",
                        on_click=State.acknowledge_admin_catalog_check,
                        disabled=State.admin_catalog_pending,
                        class_name="focus-demo-button",
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
            rx.button(
                "Desativar",
                type="button",
                on_click=State.set_librarian_active(librarian["id"], False),
                disabled=State.librarian_management_pending,
                class_name="destructive-action",
            ),
            rx.button(
                "Reativar",
                type="button",
                on_click=State.set_librarian_active(librarian["id"], True),
                disabled=State.librarian_management_pending,
                class_name="focus-demo-button",
            ),
        ),
        class_name="librarian-card",
    )


def librarian_management() -> rx.Component:
    return rx.box(
        rx.link(
            "Pular para o conteúdo",
            href="#conteudo-bibliotecarios",
            class_name="skip-link",
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
                    rx.input(
                        id="bibliotecario-nome",
                        name="nome",
                        type="text",
                        required=True,
                        aria_label="Nome do bibliotecário",
                        class_name="signup-input",
                    ),
                    rx.el.label(
                        "E-mail",
                        html_for="bibliotecario-email",
                        class_name="signup-label",
                    ),
                    rx.input(
                        id="bibliotecario-email",
                        name="email",
                        type="email",
                        required=True,
                        aria_label="E-mail do bibliotecário",
                        class_name="signup-input",
                    ),
                    rx.el.label(
                        "Senha inicial",
                        html_for="bibliotecario-senha",
                        class_name="signup-label",
                    ),
                    rx.input(
                        id="bibliotecario-senha",
                        name="senha",
                        type="password",
                        required=True,
                        aria_label="Senha inicial do bibliotecário",
                        class_name="signup-input",
                    ),
                    rx.button(
                        "Cadastrar bibliotecário",
                        type="submit",
                        disabled=State.librarian_management_pending,
                        class_name="focus-demo-button",
                    ),
                    id="form-cadastro-bibliotecario",
                    on_submit=State.submit_librarian,
                    reset_on_submit=False,
                    class_name="signup-form librarian-form",
                ),
                rx.heading("Contas bibliotecárias", size="5"),
                rx.el.label(
                    "Buscar conta por nome ou e-mail",
                    html_for="busca-contas-bibliotecarias",
                    class_name="signup-label",
                ),
                rx.input(
                    id="busca-contas-bibliotecarias",
                    type="search",
                    value=State.librarian_management_search,
                    on_change=State.update_librarian_management_search,
                    aria_label="Buscar conta por nome ou e-mail",
                    class_name="signup-input",
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
                    "Atualizar lista",
                    type="button",
                    on_click=State.load_librarians,
                    disabled=State.librarian_management_pending,
                    class_name="nav-logout",
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
            "Pular para o conteúdo",
            href="#conteudo-reservas",
            class_name="skip-link",
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
                rx.el.label(
                    "E-mail completo do estudante",
                    html_for="reserva-estudante-email",
                    class_name="signup-label",
                ),
                rx.input(
                    id="reserva-estudante-email",
                    type="email",
                    value=State.staff_reservation_email,
                    on_change=State.update_staff_reservation_email,
                    required=True,
                    aria_label="E-mail completo do estudante",
                    class_name="signup-input",
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check,
                ),
                rx.button(
                    "Buscar estudante",
                    type="button",
                    on_click=State.search_staff_reservation_student,
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check,
                    class_name="focus-demo-button",
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
                    "Registrar reserva na fila",
                    type="button",
                    on_click=State.submit_staff_reservation,
                    disabled=State.staff_reservation_pending
                    | State.staff_reservation_needs_manual_check
                    | ~State.has_staff_reservation_student,
                    class_name="focus-demo-button",
                ),
                rx.cond(
                    State.staff_reservation_pending,
                    rx.text("Processando…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.staff_reservation_needs_manual_check,
                    rx.button(
                        "Já conferi a fila no Xano; permitir nova tentativa",
                        type="button",
                        on_click=State.acknowledge_staff_reservation_check,
                        disabled=State.staff_reservation_pending,
                        class_name="nav-logout",
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
        rx.input(
            id="reserva-estudante-email",
            type="email",
            value=State.staff_reservation_email,
            on_change=State.update_staff_reservation_email,
            required=True,
            aria_label="E-mail completo do estudante",
            class_name="signup-input",
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check,
        ),
        rx.button(
            "Buscar estudante",
            type="button",
            on_click=State.search_staff_reservation_student,
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check,
            class_name="focus-demo-button",
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
            "Registrar reserva na fila",
            type="button",
            on_click=State.submit_staff_reservation,
            disabled=State.staff_reservation_pending
            | State.staff_reservation_needs_manual_check
            | ~State.has_staff_reservation_student,
            class_name="focus-demo-button",
        ),
        rx.cond(
            State.staff_reservation_pending,
            rx.text("Processando…", role="status"),
            rx.fragment(),
        ),
        rx.cond(
            State.staff_reservation_needs_manual_check,
            rx.button(
                "Já conferi a fila no Xano; permitir nova tentativa",
                type="button",
                on_click=State.acknowledge_staff_reservation_check,
                disabled=State.staff_reservation_pending,
                class_name="nav-logout",
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
            "Registrar retirada",
            type="button",
            on_click=State.circulation_pickup_request(request["id"]),
            disabled=State.circulation_pending
            | State.circulation_needs_manual_check,
            class_name="focus-demo-button",
        ),
        rx.button(
            "Recusar solicitação",
            type="button",
            on_click=State.circulation_refuse_request(request["id"]),
            disabled=State.circulation_pending
            | State.circulation_needs_manual_check,
            class_name="destructive-action",
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
                    "Oferecer ao próximo da fila",
                    type="button",
                    on_click=State.circulation_offer_reservation(
                        reservation["titulo_id"]
                    ),
                    disabled=State.circulation_pending
                    | State.circulation_needs_manual_check,
                    class_name="focus-demo-button",
                ),
                rx.button(
                    "Recusar reserva",
                    type="button",
                    on_click=State.circulation_refuse_reservation(
                        reservation["id"]
                    ),
                    disabled=State.circulation_pending
                    | State.circulation_needs_manual_check,
                    class_name="destructive-action",
                ),
            ),
            rx.cond(
                reservation["estado"] == "ofertada",
                rx.button(
                    "Registrar retirada da reserva",
                    type="button",
                    on_click=State.circulation_pickup_reservation(
                        reservation["id"]
                    ),
                    disabled=State.circulation_pending
                    | State.circulation_needs_manual_check,
                    class_name="focus-demo-button",
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
            rx.text("Em atraso", role="status"),
            rx.text("Em dia", role="status"),
        ),
        rx.button(
            "Registrar devolução",
            type="button",
            on_click=State.circulation_return_loan(loan["id"]),
            disabled=State.circulation_pending
            | State.circulation_needs_manual_check,
            class_name="focus-demo-button",
        ),
        class_name="librarian-card",
    )


def circulation_page() -> rx.Component:
    return rx.box(
        rx.link(
            "Pular para o conteúdo",
            href="#conteudo-circulacao",
            class_name="skip-link",
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
                    "Atualizar reservas e circulação",
                    type="button",
                    on_click=State.load_staff_reservations_dashboard,
                    disabled=State.circulation_pending,
                    class_name="nav-logout",
                ),
                rx.cond(
                    State.circulation_pending,
                    rx.text("Carregando reservas e circulação…", role="status"),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.button(
                        "Pedidos",
                        id="aba-pedidos",
                        type="button",
                        role="tab",
                        aria_selected=State.circulation_active_tab == "pedidos",
                        aria_controls="painel-pedidos",
                        on_click=State.select_circulation_tab("pedidos"),
                        class_name="circulation-tab",
                    ),
                    rx.button(
                        "Empréstimos e devoluções",
                        id="aba-emprestimos",
                        type="button",
                        role="tab",
                        aria_selected=(
                            State.circulation_active_tab == "emprestimos"
                        ),
                        aria_controls="painel-emprestimos",
                        on_click=State.select_circulation_tab("emprestimos"),
                        class_name="circulation-tab",
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
}


app = rx.App(
    style={
        ".a11y-shell": {
            "--bg-page": "#f5efe4",
            "--bg-panel": "#fffdf8",
            "--bg-soft": "#edf4ef",
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
            "padding": "clamp(0.5rem, 3vw, 2rem)",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-page)",
        },
        ".site-header": {
            "display": "flex",
            "align_items": "center",
            "gap": "1rem",
            "max_width": "72rem",
            "margin": "0 auto",
            "padding": "1rem 1.2rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".brand-link": {
            "display": "inline-flex",
            "align_items": "center",
            "white_space": "nowrap",
            "color": "var(--brand-text)",
            "font_weight": "800",
            "text_decoration": "none",
            "font_family": "Georgia, 'Times New Roman', serif",
            "font_size": "1.4rem",
        },
        ".brand-link:hover": {
            "color": "var(--brand-700)",
        },
        ".site-header-desktop": {
            "display": "grid",
            "grid_template_columns": "minmax(0, 1fr) auto",
            "align_items": "center",
            "gap": "1rem",
            "width": "100%",
            "min_width": "0",
        },
        ".site-primary-nav": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "center",
            "gap": "0.35rem",
            "min_width": "0",
            "max_width": "100%",
        },
        ".site-header-actions": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "flex-end",
            "gap": "0.5rem",
            "min_width": "0",
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
        ".site-header-mobile-panel.is-open": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.75rem",
            "padding_top": "0.75rem",
            "border_top": "1px solid var(--line)",
        },
        ".site-header-mobile-panel .site-primary-nav": {
            "flex_direction": "column",
            "align_items": "stretch",
            "width": "100%",
        },
        ".site-header-mobile-panel .site-header-actions": {
            "flex_direction": "column",
            "align_items": "stretch",
            "width": "100%",
        },
        ".site-header-mobile-panel .site-header-actions > *": {
            "width": "100%",
        },
        ".site-header-mobile-panel .admin-view-band": {
            "justify_content": "flex-start",
            "width": "100%",
        },
        ".site-primary-nav a": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.75rem",
            "border_radius": "0.5rem",
            "color": "var(--brand-700)",
            "font_weight": "600",
            "cursor": "pointer",
            "text_decoration": "none",
            "overflow_wrap": "anywhere",
        },
        ".site-primary-nav a:hover": {
            "background_color": "var(--brand-100)",
        },
        ".profile-menu-trigger": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.9rem",
            "border": "1px solid var(--brand-700)",
            "border_radius": "0.55rem",
            "background_color": "var(--brand-900)",
            "color": "#ffffff",
            "font_weight": "700",
            "list_style": "none",
            "cursor": "pointer",
        },
        ".profile-menu-trigger::-webkit-details-marker": {
            "display": "none",
        },
        ".profile-menu": {
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
        ".profile-menu-item": {
            "display": "flex",
            "align_items": "center",
            "width": "100%",
            "min_height": "2.75rem",
            "padding": "0.45rem 0.65rem",
            "border": "0",
            "border_radius": "0.4rem",
            "background_color": "transparent",
            "color": "var(--slate-900)",
            "font": "inherit",
            "text_align": "left",
            "overflow_wrap": "anywhere",
            "text_decoration": "none",
            "cursor": "pointer",
        },
        ".profile-menu-item:hover": {
            "background_color": "var(--brand-100)",
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
            "flex_wrap": "wrap",
            "align_items": "center",
            "gap": "0.5rem",
            "padding": "0.3rem 0.45rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "var(--bg-soft)",
        },
        ".admin-view-mode-label": {
            "font_weight": "700",
            "color": "var(--brand-text)",
            "font_size": "0.8rem",
        },
        ".admin-view-reset": {
            "min_height": "2.75rem",
            "padding": "0.35rem 0.65rem",
            "border": "1px solid var(--brand-700)",
            "border_radius": "0.5rem",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
            "font_weight": "600",
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
            "border": "1px solid var(--line)",
            "border_radius": "0.4rem",
            "background_color": "var(--bg-panel)",
            "color": "var(--slate-900)",
            "cursor": "pointer",
            "overflow_wrap": "anywhere",
        },
        ".a11y-controls button:disabled": {
            "opacity": "0.65",
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
            "scroll_behavior": "auto !important",
            "transition_duration": "0.01ms !important",
        },
        ".nav-logout": {
            "min_height": "2.75rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".nav-logout:hover": {
            "background_color": "var(--bg-soft)",
        },
        ".destructive-action": {
            "min_height": "2.75rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--danger-700)",
            "border_radius": "0.5rem",
            "background_color": "var(--danger-100)",
            "color": "var(--danger-700)",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".destructive-action:hover": {
            "background_color": "var(--danger-700)",
            "color": "var(--danger-100)",
        },
        ".main-content": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "0 auto",
        },
        ".content-section": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "flex-start",
            "gap": "1.25rem",
            "padding": "clamp(1.5rem, 3vw, 2.5rem) 1rem",
        },
        ".home-hero": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "1rem auto",
            "padding": "clamp(1.5rem, 3vw, 2.5rem)",
            "border": "1px solid var(--line)",
            "border_radius": "1.2rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".hero-layout": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "space-between",
            "width": "100%",
            "gap": "1.5rem",
        },
        ".hero-copy-wrap": {
            "flex": "1 1 20rem",
            "max_width": "36rem",
        },
        ".eyebrow": {
            "display": "inline-flex",
            "padding": "0.25rem 0.6rem",
            "border_radius": "999px",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
            "font_size": "0.75rem",
            "font_weight": "700",
            "text_transform": "uppercase",
            "letter_spacing": "0.08em",
        },
        ".hero-copy": {
            "color": "var(--slate-700)",
            "font_size": "1.05rem",
            "max_width": "32rem",
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
            "background_color": "var(--brand-900)",
            "color": "#ffffff",
            "box_shadow": "0 0.45rem 1rem rgba(24, 58, 74, 0.18)",
        },
        ".secondary-cta": {
            "border": "1px solid var(--line)",
            "background_color": "var(--bg-soft)",
            "color": "var(--brand-text)",
        },
        ".feature-card": {
            "flex": "1 1 12rem",
            "border": "1px solid var(--line)",
            "background_color": "var(--sand-100)",
            "color": "var(--brand-text)",
        },
        ".hero-stat-grid": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 10rem), 1fr))",
            "gap": "0.9rem",
            "flex": "1 1 18rem",
            "min_width": "0",
        },
        ".hero-stat-card": {
            "display": "flex",
            "flex_direction": "column",
            "justify_content": "center",
            "min_height": "6.5rem",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--sand-100)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".hero-stat-value": {
            "color": "var(--brand-text)",
            "font_family": "Georgia, 'Times New Roman', serif",
            "font_size": "1.75rem",
            "line_height": "1.1",
        },
        ".hero-stat-label": {
            "font_size": "0.7rem",
            "text_transform": "uppercase",
            "letter_spacing": "0.08em",
            "color": "var(--slate-500)",
        },
        ".catalog-section": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "1rem auto",
        },
        ".home-catalog-section": {
            "padding": "clamp(1.1rem, 2.5vw, 1.6rem)",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
        },
        ".home-about-section": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "1rem auto",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--bg-soft)",
        },
        ".home-about-section p": {
            "max_width": "50rem",
            "color": "var(--slate-700)",
        },
        ".home-stat-status": {
            "display": "flex",
            "align_items": "center",
            "min_height": "6.5rem",
            "padding": "1rem",
            "border": "1px solid var(--line)",
            "border_radius": "1rem",
            "background_color": "var(--sand-100)",
            "color": "var(--slate-700)",
        },
        ".home-section-heading": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "1rem",
            "width": "100%",
        },
        ".section-more-link": {
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "min_height": "2.75rem",
            "padding": "0.55rem 0.9rem",
            "border_radius": "0.65rem",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
            "font_weight": "700",
            "text_decoration": "none",
        },
        ".home-category-list": {
            "display": "flex",
            "flex_wrap": "wrap",
            "gap": "0.6rem",
            "width": "100%",
        },
        ".home-category-chip": {
            "display": "inline-flex",
            "align_items": "center",
            "min_height": "2.5rem",
            "padding": "0.4rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "999px",
            "background_color": "var(--bg-soft)",
            "color": "var(--slate-900)",
            "font_weight": "600",
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
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 16rem), 1fr))",
            "gap": "1.1rem",
            "width": "100%",
        },
        ".admin-catalog-grid": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 20rem), 1fr))",
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
            "padding": "1.1rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.9rem",
            "background_color": "var(--bg-panel)",
            "box_shadow": "var(--shadow-soft)",
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
        ".catalog-card, .catalog-detail-card": {
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
        ".catalog-card:hover": {
            "transform": "translateY(-2px)",
            "border_color": "var(--brand-500)",
            "box_shadow": "0 0.6rem 1.25rem rgba(24, 43, 73, 0.1)",
        },
        ".catalog-card-visual": {
            "display": "flex",
            "flex_direction": "column",
            "width": "100%",
            "gap": "0.6rem",
        },
        ".catalog-card-cover": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "width": "100%",
            "min_height": "11rem",
            "aspect_ratio": "0.72",
            "border": "1px solid var(--line)",
            "border_radius": "0.8rem",
            "background_color": "var(--brand-900)",
            "color": "#ffffff",
        },
        ".catalog-card-cover-image": {
            "display": "block",
            "width": "100%",
            "min_height": "11rem",
            "aspect_ratio": "0.72",
            "border_radius": "0.8rem",
            "object_fit": "cover",
        },
        ".catalog-detail-visual": {
            "width": "100%",
            "max_width": "22rem",
        },
        ".catalog-detail-visual .catalog-card-cover": {
            "min_height": "22rem",
        },
        ".catalog-detail-cover-image": {
            "display": "block",
            "width": "100%",
            "min_height": "22rem",
            "aspect_ratio": "0.72",
            "border_radius": "0.8rem",
            "object_fit": "cover",
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
        ".a11y-shell.a11y-dark .focus-demo-button": {
            "background_color": "var(--brand-700)",
            "color": "#183a4a",
        },
        ".a11y-shell.a11y-dark .focus-demo-button:hover": {
            "background_color": "#b6e3ee",
            "color": "#183a4a",
        },
        ".a11y-shell.a11y-dark .primary-cta": {
            "background_color": "var(--brand-700)",
            "color": "#183a4a",
        },
        ".a11y-shell.a11y-dark .primary-cta:hover": {
            "background_color": "#b6e3ee",
            "color": "#183a4a",
        },
        ".catalog-tag": {
            "display": "inline-flex",
            "align_self": "flex-start",
            "padding": "0.25rem 0.5rem",
            "border_radius": "999px",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
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
            "border_radius": "0.5rem",
            "background_color": "var(--brand-100)",
            "color": "var(--brand-text)",
            "font_weight": "700",
            "text_decoration": "none",
        },
        ".catalog-card-link:hover": {
            "background_color": "var(--bg-soft)",
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
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 18rem), 1fr))",
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
        ".signup-label": {
            "font_weight": "600",
            "margin_top": "0.5rem",
            "color": "var(--slate-900)",
        },
        ".signup-input": {
            "width": "100%",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-panel)",
            "box_shadow": "none",
            "transition": "border-color 120ms ease, box-shadow 120ms ease",
        },
        ".signup-input input, .rt-TextFieldInput": {
            "color": "var(--slate-900)",
            "border": "0 !important",
            "border_radius": "0 !important",
            "box_shadow": "none !important",
            "outline": "none !important",
            "background_color": "transparent !important",
            "min_height": "2.75rem",
        },
        "input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput), textarea, select": {
            "min_height": "2.75rem",
            "color": "var(--slate-900)",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "background_color": "var(--bg-panel)",
            "caret_color": "var(--slate-900)",
        },
        ".rt-SelectTrigger": {
            "min_height": "2.75rem",
            "border": "1px solid var(--line)",
            "border_radius": "0.5rem",
            "color": "var(--slate-900)",
            "background_color": "var(--bg-panel)",
            "box_shadow": "none",
        },
        ".signup-input:focus-within, .rt-TextFieldRoot:focus-within, .rt-SelectTrigger:focus-visible, input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput):focus-visible, textarea:focus-visible, select:focus-visible": {
            "outline": "3px solid var(--brand-700)",
            "outline_offset": "2px",
        },
        ".signup-input input:focus-visible, .rt-TextFieldInput:focus-visible": {
            "outline": "none !important",
        },
        ".signup-input input::placeholder, .rt-TextFieldInput::placeholder, input:not([type='checkbox']):not([type='radio']):not(.rt-TextFieldInput)::placeholder, textarea::placeholder": {
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
            "border": "0",
            "border_radius": "0.5rem",
            "background_color": "var(--brand-700)",
            "color": "#ffffff",
            "font_weight": "600",
            "cursor": "pointer",
            "transition": "background-color 120ms ease, transform 120ms ease",
        },
        ".focus-demo-button:hover": {
            "background_color": "var(--brand-900)",
        },
        ".focus-demo-button:active": {
            "transform": "translateY(1px)",
        },
        ".focus-demo-button:disabled, .nav-logout:disabled": {
            "opacity": "0.65",
            "cursor": "not-allowed",
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
                "scroll_behavior": "auto !important",
                "transition_duration": "0.01ms !important",
            },
        },
        "@media screen and (max-width: 40rem)": {
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
                "grid_template_columns": "minmax(0, 1fr) auto",
                "align_items": "center",
                "gap": "0.5rem",
                "padding": "0.75rem",
            },
            ".hero-layout": {
                "align_items": "stretch",
                "flex_direction": "column",
            },
            ".hero-copy-wrap, .hero-stat-grid": {
                "width": "100%",
                "max_width": "100%",
            },
            ".hero-stat-card": {
                "min_width": "0",
            },
            ".site-header-desktop": {
                "display": "none",
            },
            ".site-menu-toggle": {
                "display": "inline-flex",
            },
            ".brand-link": {
                "min_width": "0",
                "font_size": "1.2rem",
            },
            ".site-primary-nav": {
                "align_items": "stretch",
                "justify_content": "flex-start",
                "gap": "0.2rem",
                "width": "100%",
            },
            ".site-header-actions": {
                "align_items": "stretch",
                "gap": "0.6rem",
                "width": "100%",
            },
            ".site-header-mobile-panel .profile-menu-trigger": {
                "width": "100%",
                "justify_content": "center",
            },
            ".profile-menu-content": {
                "width": "calc(100vw - 2rem)",
                "max_width": "calc(100vw - 2rem)",
            },
            ".footer-links": {
                "width": "100%",
            },
            ".admin-view-band": {
                "align_items": "flex-start",
                "flex_direction": "column",
                "width": "100%",
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
            ".librarian-card": {
                "width": "100%",
            },
            ".admin-catalog-section, .librarian-management-section": {
                "padding": "1.1rem 0.75rem",
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

"""Estrutura inicial da interface da Biblioteca."""

import unicodedata
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable

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
    list_my_loans,
    list_my_requests,
    list_my_reservations,
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


class State(rx.State):
    is_authenticated: bool = False
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
    accessibility_font_scale_raw: str = rx.LocalStorage(
        "100", name="biblioteca-acessibilidade-fonte", sync=True
    )
    accessibility_high_contrast_raw: str = rx.LocalStorage(
        "false", name="biblioteca-acessibilidade-contraste", sync=True
    )
    accessibility_reduce_motion_raw: str = rx.LocalStorage(
        "false", name="biblioteca-acessibilidade-movimento", sync=True
    )
    _catalog_title_id: int | None = None
    _pending_category_ids: list[int] = []
    _uncertain_category_ids: list[int] = []
    _catalog_title_uncertain: bool = False
    _catalog_copy_uncertain: bool = False
    public_catalog_entries: list[dict[str, Any]] = []
    public_catalog_categories: list[dict[str, Any]] = []
    public_catalog_message: str = ""
    public_catalog_has_error: bool = False
    public_catalog_pending: bool = False
    public_catalog_search: str = ""
    public_catalog_category_id: str = ""
    public_catalog_only_available: bool = False
    public_catalog_sort: str = "asc"
    public_catalog_detail: dict[str, Any] = {}
    public_catalog_detail_message: str = ""
    public_catalog_detail_has_error: bool = False
    public_catalog_detail_not_found: bool = False
    public_catalog_detail_pending: bool = False
    student_library_pending: bool = False
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
    managed_librarians: list[dict[str, Any]] = []
    staff_reservation_pending: bool = False
    staff_reservation_message: str = ""
    staff_reservation_has_error: bool = False
    staff_reservation_email: str = ""
    staff_reservation_student: dict[str, Any] = {}
    staff_reservation_title_options: list[dict[str, str]] = []
    staff_reservation_title_id: str = ""
    staff_reservation_needs_manual_check: bool = False

    def _store_session_token(self, token: str) -> None:
        if not token:
            raise ValueError("O token de sessão não pode ser vazio.")
        self._session_token = token
        self.is_authenticated = True

    def _store_session(self, token: str, profile: str, name: str = "") -> None:
        if profile not in {"estudante", "bibliotecario", "admin"}:
            raise ValueError("O perfil de sessão retornado não é válido.")
        self._store_session_token(token)
        self._session_profile = profile
        self._session_name = name.strip()

    @rx.var
    def greeting_name(self) -> str:
        return self._session_name if self._session_token else ""

    def _valid_accessibility_font_scale(self) -> int:
        try:
            scale = int(self.accessibility_font_scale_raw)
        except (TypeError, ValueError):
            return 100
        return scale if scale in range(100, 151, 10) else 100

    @rx.var
    def accessibility_font_scale(self) -> int:
        return self._valid_accessibility_font_scale()

    @rx.var
    def accessibility_font_size(self) -> str:
        return f"{self.accessibility_font_scale}%"

    @rx.var
    def accessibility_high_contrast(self) -> bool:
        return self.accessibility_high_contrast_raw == "true"

    @rx.var
    def accessibility_reduce_motion(self) -> bool:
        return self.accessibility_reduce_motion_raw == "true"

    @rx.var
    def accessibility_classes(self) -> str:
        classes = ["a11y-shell"]
        if self.accessibility_high_contrast:
            classes.append("a11y-high-contrast")
        if self.accessibility_reduce_motion:
            classes.append("a11y-reduce-motion")
        return " ".join(classes)

    @rx.event
    def increase_accessibility_font(self):
        scale = self._valid_accessibility_font_scale()
        self.accessibility_font_scale_raw = str(min(150, scale + 10))

    @rx.event
    def decrease_accessibility_font(self):
        scale = self._valid_accessibility_font_scale()
        self.accessibility_font_scale_raw = str(max(100, scale - 10))

    @rx.event
    def reset_accessibility_font(self):
        self.accessibility_font_scale_raw = "100"

    @rx.event
    def toggle_accessibility_high_contrast(self):
        self.accessibility_high_contrast_raw = (
            "false" if self.accessibility_high_contrast else "true"
        )

    @rx.event
    def toggle_accessibility_reduce_motion(self):
        self.accessibility_reduce_motion_raw = (
            "false" if self.accessibility_reduce_motion else "true"
        )

    def _read_session_token(self) -> str | None:
        return self._session_token or None

    def _clear_session_token(self) -> None:
        self._session_token = ""
        self._session_profile = ""
        self._session_name = ""
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
            visible.append(
                {
                    "id": title["id"],
                    "titulo": title["titulo"],
                    "autores": title["autores"],
                    "categorias": ", ".join(
                        category_names[category_id]
                        for category_id in sorted(category_ids)
                        if category_id in category_names
                    )
                    or "Sem categoria",
                    "exemplares_disponiveis": available,
                    "href": f"/catalogo/{title['id']}",
                }
            )
        return sorted(
            visible,
            key=lambda item: _catalog_search_key(item["titulo"]),
            reverse=self.public_catalog_sort == "desc",
        )

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
    def has_staff_reservation_student(self) -> bool:
        return bool(self.staff_reservation_student)

    def _redirect_non_librarian(self):
        if not self._session_token:
            return rx.redirect("/login")
        return rx.redirect("/")

    def _redirect_non_admin(self):
        if not self._session_token:
            return rx.redirect("/login")
        return rx.redirect("/")

    @rx.event
    def redirect_authenticated_home(self):
        if self._session_token:
            return rx.redirect("/catalogo")

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
        self.public_catalog_detail = {
            "id": entry["titulo"]["id"],
            "titulo": entry["titulo"]["titulo"],
            "autores": entry["titulo"]["autores"],
            "isbn": entry["titulo"].get("isbn") or "",
            "editora": entry["titulo"].get("editora") or "",
            "edicao": entry["titulo"].get("edicao") or "",
            "ano_publicacao": (
                str(entry["titulo"]["ano_publicacao"])
                if entry["titulo"].get("ano_publicacao") is not None
                else ""
            ),
            "descricao": entry["titulo"].get("descricao") or "",
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
            if error.status_code == 403:
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
        if not self.is_student:
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
                "exemplar_id": loan["exemplar_id"],
                "retirado_em": _format_timestamp(loan["retirado_em"]),
                "vence_em": _format_timestamp(loan["vence_em"]),
                "devolvido": loan["devolvido_em"] not in (None, 0),
                "em_atraso": _is_overdue(loan["vence_em"], loan["devolvido_em"]),
            }
            for loan in loans
        ]
        self.student_library_requests = [
            {
                "id": request["id"],
                "titulo": title_names.get(
                    request["titulo_id"], f"Título #{request['titulo_id']}"
                ),
                "href": f"/catalogo/{request['titulo_id']}",
                "estado": _request_status_label(request["estado"]),
                "solicitada_em": _format_timestamp(
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
                    reservation["titulo_id"],
                    f"Título #{reservation['titulo_id']}",
                ),
                "href": f"/catalogo/{reservation['titulo_id']}",
                "estado": _reservation_status_label(reservation["estado"]),
                "prazo": _format_sao_paulo_deadline(
                    reservation["expira_em_sao_paulo"]
                ),
            }
            for reservation in reservations
        ]
        self.student_library_pending = False

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
        )
        if self._is_librarian():
            return rx.redirect("/admin/acervo")
        return rx.redirect("/")

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


def site_header() -> rx.Component:
    return rx.el.header(
        rx.link(
            rx.heading("Biblioteca escolar", size="6"),
            href="/",
            class_name="brand-link",
        ),
        rx.el.nav(
            rx.link("Catálogo", href="/catalogo"),
            rx.cond(
                State.is_authenticated,
                rx.fragment(
                    rx.text(
                        "Olá, ",
                        State.greeting_name,
                        class_name="session-greeting",
                    ),
                    rx.cond(
                        State.is_student,
                        rx.link("Minha biblioteca", href="/minha-biblioteca"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.is_librarian,
                        rx.link("Cadastrar livro", href="/admin/acervo"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.is_librarian,
                        rx.link(
                            "Reservas para estudantes",
                            href="/admin/reservas",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.can_manage_librarians,
                        rx.link(
                            "Bibliotecários",
                            href="/admin/bibliotecarios",
                        ),
                        rx.fragment(),
                    ),
                    rx.button(
                        "Sair",
                        type="button",
                        on_click=State.logout,
                        class_name="nav-logout",
                    ),
                ),
                rx.fragment(
                    rx.link("Entrar", href="/login"),
                    rx.link("Cadastrar-se", href="/cadastro"),
                ),
            ),
            aria_label="Navegação principal",
            class_name="site-nav",
        ),
        rx.el.details(
            rx.el.summary("Acessibilidade"),
            rx.el.div(
                rx.button(
                    "Aumentar fonte",
                    type="button",
                    on_click=State.increase_accessibility_font,
                    disabled=State.accessibility_font_scale >= 150,
                    aria_label="Aumentar fonte",
                ),
                rx.button(
                    "Diminuir fonte",
                    type="button",
                    on_click=State.decrease_accessibility_font,
                    disabled=State.accessibility_font_scale <= 100,
                    aria_label="Diminuir fonte",
                ),
                rx.button(
                    "Restaurar fonte",
                    type="button",
                    on_click=State.reset_accessibility_font,
                    aria_label="Restaurar fonte ao tamanho padrão",
                ),
                rx.button(
                    rx.cond(
                        State.accessibility_high_contrast,
                        "Alto contraste: ligado",
                        "Alto contraste: desligado",
                    ),
                    type="button",
                    on_click=State.toggle_accessibility_high_contrast,
                    aria_pressed=State.accessibility_high_contrast,
                    aria_label="Alternar alto contraste",
                ),
                rx.button(
                    rx.cond(
                        State.accessibility_reduce_motion,
                        "Reduzir animações: ligado",
                        "Reduzir animações: desligado",
                    ),
                    type="button",
                    on_click=State.toggle_accessibility_reduce_motion,
                    aria_pressed=State.accessibility_reduce_motion,
                    aria_label="Alternar redução de animações",
                ),
                class_name="a11y-controls",
                aria_label="Controles de acessibilidade",
            ),
            class_name="a11y-menu",
        ),
        class_name="site-header",
    )


def _catalog_search_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


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


def public_catalog_card(title: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.h2(title["titulo"], class_name="catalog-card-heading"),
        rx.text("Autoria: ", title["autores"]),
        rx.text("Categorias: ", title["categorias"]),
        rx.text(
            "Exemplares disponíveis: ",
            title["exemplares_disponiveis"],
        ),
        rx.link("Ver detalhes", href=title["href"], class_name="catalog-card-link"),
        class_name="catalog-card",
    )


def student_loan_card(loan: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.h3(f"Empréstimo #{loan['id']}", class_name="catalog-card-heading"),
        rx.text("Exemplar: ", loan["exemplar_id"]),
        rx.text("Retirada: ", loan["retirado_em"]),
        rx.text("Vencimento: ", loan["vence_em"]),
        rx.cond(
            loan["devolvido"],
            rx.text("Devolvido"),
            rx.cond(
                loan["em_atraso"],
                rx.el.p(
                    "Em atraso. Procure a equipe da biblioteca; novas solicitações "
                    "e reservas podem ser bloqueadas.",
                    role="alert",
                    class_name="signup-feedback signup-feedback-error",
                ),
                rx.text("Em andamento"),
            ),
        ),
        class_name="catalog-card",
    )


def student_request_card(request: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.h3(
            rx.link(request["titulo"], href=request["href"]),
            class_name="catalog-card-heading",
        ),
        rx.text("Solicitação: ", request["estado"]),
        rx.text("Enviada em: ", request["solicitada_em"]),
        class_name="catalog-card",
    )


def student_reservation_card(reservation: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.el.article(
        rx.el.h3(
            rx.link(reservation["titulo"], href=reservation["href"]),
            class_name="catalog-card-heading",
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
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
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
                        rx.link("Voltar ao catálogo", href="/catalogo"),
                        align="start",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.has_public_catalog_detail,
                    rx.el.article(
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
                        rx.cond(
                            State.public_catalog_detail["descricao"] != "",
                            rx.text(
                                State.public_catalog_detail["descricao"],
                                class_name="catalog-description",
                            ),
                            rx.fragment(),
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
                            rx.cond(
                                State.public_catalog_has_available_copies,
                                "Solicitar empréstimo",
                                "Entrar na fila de reserva",
                            ),
                            type="button",
                            disabled=State.student_request_pending,
                            on_click=State.request_catalog_title(
                                State.public_catalog_detail["id"]
                            ),
                            class_name="focus-demo-button",
                        ),
                        rx.link("Acompanhar em Minha biblioteca", href="/minha-biblioteca"),
                        align="start",
                        width="100%",
                    ),
                    rx.cond(
                        State.is_authenticated,
                        rx.fragment(),
                        rx.link(
                            "Entre como estudante para solicitar este título",
                            href="/login",
                        ),
                    ),
                ),
                rx.link("Voltar ao catálogo", href="/catalogo"),
                id="conteudo-detalhe",
                class_name="content-section catalog-section",
            ),
            class_name="main-content",
        ),
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
        class_name="app-shell",
    )


def student_library() -> rx.Component:
    records = rx.fragment(
        rx.el.section(
            rx.heading("Empréstimos", size="5"),
            rx.cond(
                State.has_student_library_loans,
                rx.box(
                    rx.foreach(State.student_library_loans, student_loan_card),
                    class_name="catalog-grid",
                ),
                rx.text(
                    "Você ainda não possui empréstimos.",
                    role="status",
                ),
            ),
            class_name="student-library-section",
            aria_label="Meus empréstimos",
        ),
        rx.el.section(
            rx.heading("Solicitações", size="5"),
            rx.cond(
                State.has_student_library_requests,
                rx.box(
                    rx.foreach(
                        State.student_library_requests,
                        student_request_card,
                    ),
                    class_name="catalog-grid",
                ),
                rx.text(
                    "Você não possui solicitações pendentes ou recentes.",
                    role="status",
                ),
            ),
            class_name="student-library-section",
            aria_label="Minhas solicitações",
        ),
        rx.el.section(
            rx.heading("Reservas", size="5"),
            rx.cond(
                State.has_student_library_reservations,
                rx.box(
                    rx.foreach(
                        State.student_library_reservations,
                        student_reservation_card,
                    ),
                    class_name="catalog-grid",
                ),
                rx.text("Você ainda não possui reservas.", role="status"),
            ),
            class_name="student-library-section",
            aria_label="Minhas reservas",
        ),
    )

    return rx.box(
        rx.link(
            "Pular para o conteúdo",
            href="#conteudo-minha-biblioteca",
            class_name="skip-link",
        ),
        site_header(),
        rx.el.main(
            rx.el.section(
                rx.heading("Minha biblioteca", size="7"),
                rx.text(
                    "Consulte seus empréstimos, solicitações, reservas e prazos."
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
                    State.student_library_has_error,
                    rx.fragment(),
                    records,
                ),
                rx.link("Voltar ao catálogo", href="/catalogo"),
                id="conteudo-minha-biblioteca",
                class_name="content-section",
            ),
            class_name="main-content",
        ),
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
        class_name="app-shell",
    )


def index() -> rx.Component:
    return login_page()


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
        rx.el.footer(
            rx.text("Biblioteca escolar"),
            class_name="site-footer",
        ),
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
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
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
                    class_name="nav-logout",
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
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
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
                class_name="nav-logout",
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
                rx.cond(
                    State.librarian_management_pending,
                    rx.text("Carregando bibliotecários…", role="status"),
                    rx.fragment(),
                ),
                rx.cond(
                    State.managed_librarians.length() > 0,
                    rx.el.div(
                        rx.foreach(State.managed_librarians, librarian_card),
                        class_name="librarian-list",
                    ),
                    rx.cond(
                        State.librarian_management_pending,
                        rx.fragment(),
                        rx.cond(
                            State.librarian_management_has_error,
                            rx.fragment(),
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
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
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
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
        class_name="app-shell",
    )


def accessible_page(page: Callable[[], rx.Component]) -> Callable[[], rx.Component]:
    @wraps(page)
    def wrapped() -> rx.Component:
        return rx.el.div(
            page(),
            class_name=State.accessibility_classes,
            style={
                "width": "100%",
                "min_height": "100vh",
                "font_size": State.accessibility_font_size,
            },
        )

    return wrapped


app = rx.App(
    style={
        "font_family": "system-ui, sans-serif",
        "color": "var(--gray-12)",
        "background_color": "var(--gray-2)",
        "*, *::before, *::after": {
            "box_sizing": "border-box",
        },
        "body": {
            "margin": "0",
            "color": "var(--gray-12)",
            "background_color": "var(--gray-2)",
        },
        ".app-shell": {
            "min_height": "100vh",
            "padding": "clamp(0.5rem, 3vw, 2rem)",
            "color": "var(--gray-12)",
            "background_color": "var(--gray-2)",
        },
        ".site-header": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "1rem",
            "max_width": "72rem",
            "margin": "0 auto",
            "padding": "1rem",
            "border_bottom": "1px solid #cbd5e1",
        },
        ".brand-link": {
            "color": "var(--gray-12)",
            "text_decoration": "none",
        },
        ".site-nav": {
            "display": "flex",
            "flex_wrap": "wrap",
            "align_items": "center",
            "gap": "1rem",
            "min_width": "0",
            "max_width": "100%",
        },
        ".session-greeting": {
            "font_weight": "700",
            "overflow_wrap": "anywhere",
        },
        ".a11y-menu": {
            "max_width": "100%",
            "padding": "0.5rem 0",
        },
        ".a11y-menu summary": {
            "min_height": "2.5rem",
            "padding": "0.5rem 0.75rem",
            "font_weight": "600",
            "cursor": "pointer",
        },
        ".a11y-controls": {
            "display": "flex",
            "flex_wrap": "wrap",
            "gap": "0.5rem",
            "max_width": "100%",
            "padding": "0.5rem 0",
        },
        ".a11y-controls button": {
            "min_height": "2.5rem",
            "max_width": "100%",
            "padding": "0.4rem 0.65rem",
            "border": "1px solid var(--gray-7)",
            "border_radius": "0.4rem",
            "background_color": "var(--gray-1)",
            "color": "var(--gray-12)",
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
            "min_height": "2.5rem",
            "padding": "0.4rem 0.9rem",
            "border": "1px solid var(--blue-8)",
            "border_radius": "0.5rem",
            "background_color": "transparent",
            "color": "var(--blue-11)",
            "font_weight": "600",
            "cursor": "pointer",
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
            "gap": "1rem",
            "padding": "2rem 1rem",
        },
        ".catalog-section": {
            "width": "100%",
            "max_width": "72rem",
            "margin": "1rem auto",
        },
        ".student-library-section": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "1rem",
            "width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--gray-6)",
            "border_radius": "0.75rem",
            "background_color": "var(--gray-1)",
        },
        ".catalog-controls": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 12rem), 1fr))",
            "align_items": "end",
            "gap": "1rem",
            "width": "100%",
            "padding": "1rem",
            "border": "1px solid var(--gray-6)",
            "border_radius": "0.75rem",
            "background_color": "var(--gray-1)",
        },
        ".catalog-filter": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.4rem",
            "min_width": "0",
        },
        ".catalog-grid": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 16rem), 1fr))",
            "gap": "1rem",
            "width": "100%",
        },
        ".admin-catalog-grid": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 20rem), 1fr))",
            "gap": "1rem",
            "width": "100%",
        },
        ".admin-title-card": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "stretch",
            "gap": "0.75rem",
            "min_width": "0",
            "padding": "1rem",
            "border": "1px solid var(--gray-6)",
            "border_radius": "0.75rem",
            "background_color": "var(--gray-1)",
        },
        ".admin-title-edit-form": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 12rem), 1fr))",
            "gap": "0.75rem",
            "width": "100%",
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
            "border": "1px solid var(--gray-6)",
            "border_radius": "0.75rem",
            "background_color": "var(--gray-1)",
            "box_shadow": "0 0.5rem 1.5rem rgba(0, 0, 0, 0.08)",
        },
        ".catalog-card-heading, .catalog-detail-heading": {
            "overflow_wrap": "anywhere",
        },
        ".catalog-card-link": {
            "font_weight": "700",
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
            "border": "1px solid var(--gray-6)",
            "border_radius": "1rem",
            "background_color": "var(--gray-1)",
            "box_shadow": "0 1rem 2.5rem rgba(0, 0, 0, 0.12)",
        },
        ".librarian-management-section": {
            "width": "min(100%, 72rem)",
            "margin": "1rem auto",
        },
        ".librarian-form": {
            "width": "min(100%, 34rem)",
        },
        ".librarian-list": {
            "display": "grid",
            "grid_template_columns": "repeat(auto-fit, minmax(min(100%, 18rem), 1fr))",
            "gap": "1rem",
            "width": "100%",
        },
        ".librarian-card": {
            "display": "flex",
            "flex_direction": "column",
            "align_items": "flex-start",
            "gap": "0.75rem",
            "min_width": "0",
            "padding": "1rem",
            "border": "1px solid var(--gray-6)",
            "border_radius": "0.75rem",
            "background_color": "var(--gray-1)",
            "overflow_wrap": "anywhere",
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
            "color": "var(--gray-12)",
        },
        ".signup-input": {
            "width": "100%",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "border": "1px solid var(--gray-7)",
            "border_radius": "0.5rem",
            "color": "var(--gray-12)",
            "background_color": "var(--gray-1)",
            "transition": "border-color 120ms ease, box-shadow 120ms ease",
        },
        ".signup-input input": {
            "color": "var(--gray-12)",
            "background_color": "transparent",
        },
        "input:not([type='checkbox']):not([type='radio']), textarea, select": {
            "color": "var(--gray-12)",
            "background_color": "var(--gray-1)",
            "caret_color": "var(--gray-12)",
        },
        ".signup-input input::placeholder, input:not([type='checkbox']):not([type='radio'])::placeholder, textarea::placeholder": {
            "color": "var(--gray-11)",
            "opacity": "1",
        },
        "select option": {
            "color": "var(--gray-12)",
            "background_color": "var(--gray-1)",
        },
        ".signup-feedback": {
            "max_width": "28rem",
            "padding": "0.75rem",
            "border_radius": "0.5rem",
            "border": "1px solid var(--gray-6)",
            "overflow_wrap": "anywhere",
        },
        ".signup-feedback-error": {
            "border_left": "4px solid var(--red-9)",
            "background_color": "var(--red-3)",
            "color": "var(--red-12)",
        },
        ".signup-feedback-success": {
            "border_left": "4px solid var(--green-9)",
            "background_color": "var(--green-3)",
            "color": "var(--green-12)",
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
            "border": "1px solid var(--gray-7)",
            "border_radius": "0.5rem",
            "color": "var(--gray-12)",
            "background_color": "var(--gray-1)",
        },
        ".focus-demo-button": {
            "min_height": "2.75rem",
            "padding": "0.5rem 1rem",
            "border": "0",
            "border_radius": "0.5rem",
            "background_color": "#174ea6",
            "color": "#ffffff",
            "font_weight": "600",
            "cursor": "pointer",
            "transition": "background-color 120ms ease, transform 120ms ease",
        },
        ".focus-demo-button:hover": {
            "background_color": "#123f88",
        },
        ".focus-demo-button:active": {
            "transform": "translateY(1px)",
        },
        ".site-nav a": {
            "color": "var(--blue-11)",
            "font_weight": "600",
        },
        "a": {
            "color": "var(--blue-11)",
            "text_underline_offset": "0.2em",
        },
        ".site-footer": {
            "max_width": "72rem",
            "margin": "0 auto",
            "padding": "1rem",
            "border_top": "1px solid var(--gray-6)",
        },
        ".skip-link": {
            "position": "absolute",
            "top": "-5rem",
            "left": "1rem",
            "z_index": "10",
            "padding": "0.75rem 1rem",
            "border_radius": "0.5rem",
            "background_color": "var(--gray-1)",
            "color": "var(--blue-11)",
        },
        ".skip-link:focus-visible": {
            "top": "1rem",
        },
        ":focus-visible": {
            "outline": "3px solid var(--blue-9)",
            "outline_offset": "3px",
        },
        "@media screen and (max-width: 40rem)": {
            ".app-shell": {
                "padding": "0.5rem",
            },
            ".site-header": {
                "align_items": "flex-start",
                "flex_direction": "column",
                "padding": "0.75rem 0.5rem",
            },
            ".site-nav": {
                "gap": "0.5rem",
                "width": "100%",
            },
            ".a11y-menu": {
                "width": "100%",
            },
            ".content-section": {
                "padding": "1.25rem 0.25rem",
            },
            ".signup-section": {
                "margin": "1rem auto",
                "padding": "1.25rem 1rem",
            },
            ".librarian-card": {
                "width": "100%",
            },
        },
    }
)
app.add_page(
    accessible_page(index),
    title="Biblioteca escolar",
    on_load=State.redirect_authenticated_home,
)
app.add_page(
    accessible_page(student_signup),
    route="/cadastro",
    title="Cadastro de estudante",
)
app.add_page(accessible_page(login_page), route="/login", title="Entrar")
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
    accessible_page(student_library),
    route="/minha-biblioteca",
    title="Minha biblioteca",
    on_load=State.load_student_library,
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
    accessible_page(staff_reservation_page),
    route="/admin/reservas",
    title="Reservar para estudante",
    on_load=State.load_staff_reservation_page,
)

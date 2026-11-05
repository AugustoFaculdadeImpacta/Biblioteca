"""Estrutura inicial da interface da Biblioteca."""

from typing import Any

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
    CatalogValidationError,
    associate_category,
    build_title_payload,
    catalog_error_message,
    category_contains_title,
    create_copy,
    create_title,
    list_categories,
)
from biblioteca_mais_nova.xano_client import (
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
)


class State(rx.State):
    is_authenticated: bool = False
    signup_message: str = ""
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
    _session_token: str = ""
    _session_profile: str = ""
    _catalog_title_id: int | None = None
    _pending_category_ids: list[int] = []
    _uncertain_category_ids: list[int] = []
    _catalog_title_uncertain: bool = False
    _catalog_copy_uncertain: bool = False

    def _store_session_token(self, token: str) -> None:
        if not token:
            raise ValueError("O token de sessão não pode ser vazio.")
        self._session_token = token
        self.is_authenticated = True

    def _store_session(self, token: str, profile: str) -> None:
        if profile not in {"estudante", "bibliotecario"}:
            raise ValueError("O perfil de sessão retornado não é válido.")
        self._store_session_token(token)
        self._session_profile = profile

    def _read_session_token(self) -> str | None:
        return self._session_token or None

    def _clear_session_token(self) -> None:
        self._session_token = ""
        self._session_profile = ""
        self.is_authenticated = False

    def _is_librarian(self) -> bool:
        return bool(self._session_token) and self._session_profile == "bibliotecario"

    def _redirect_non_librarian(self):
        if not self._session_token:
            return rx.redirect("/login")
        return rx.redirect("/")

    def _sync_catalog_progress(self) -> None:
        self.catalog_categories_pending = bool(
            self._pending_category_ids or self._uncertain_category_ids
        )

    @rx.event
    async def submit_signup(self, form_data: dict[str, Any]):
        self.signup_message = ""
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

        self._store_session(session["authToken"], "estudante")
        self.signup_message = "Cadastro realizado. Seu acesso de estudante está ativo."
        return rx.call_script(
            "document.getElementById('form-cadastro-estudante')?.reset()"
        )

    @rx.event
    async def submit_login(self, form_data: dict[str, Any]):
        self.login_message = ""
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

        self._store_session(session["authToken"], session["usuario"]["perfil"])
        if self._session_profile == "bibliotecario":
            return rx.redirect("/admin/acervo")
        return rx.redirect("/")

    @rx.event
    async def load_catalog_categories(self):
        if not self._is_librarian():
            return self._redirect_non_librarian()
        try:
            self.catalog_categories = await list_categories()
        except (XanoConfigurationError, XanoRequestError, XanoResponseError) as error:
            self.catalog_message = catalog_error_message(error)
            self.catalog_has_error = True
            return

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


def index() -> rx.Component:
    return rx.box(
        rx.link("Pular para o conteúdo", href="#conteudo", class_name="skip-link"),
        rx.el.header(
            rx.heading("Biblioteca escolar", size="6"),
            rx.text(
                rx.cond(State.is_authenticated, "Sessão autenticada", "Acesso público"),
                class_name="session-status",
            ),
            rx.el.nav(
                rx.link("Início", href="#inicio"),
                rx.link("Acessibilidade", href="#acessibilidade"),
                rx.link("Cadastrar-se", href="/cadastro"),
                rx.link("Entrar", href="/login"),
                rx.link("Acervo", href="/admin/acervo"),
                aria_label="Navegação principal",
                class_name="site-nav",
            ),
            class_name="site-header",
        ),
        rx.el.main(
            rx.el.section(
                rx.heading("Bem-vindo à biblioteca", size="8"),
                rx.text(
                    "Esta é a estrutura inicial da aplicação. "
                    "As funcionalidades serão adicionadas em etapas próprias."
                ),
                id="inicio",
                class_name="content-section",
            ),
            rx.el.section(
                rx.heading("Acessibilidade", size="5"),
                rx.text(
                    "Use a tecla Tab para percorrer a busca demonstrativa e "
                    "o botão, verificando o indicador de foco."
                ),
                rx.input(
                    type="search",
                    placeholder="Busca do catálogo (demonstração)",
                    aria_label="Busca do catálogo (demonstração)",
                    read_only=True,
                    class_name="focus-demo-field",
                ),
                rx.button(
                    "Botão de demonstração",
                    type="button",
                    class_name="focus-demo-button",
                ),
                id="acessibilidade",
                class_name="content-section",
            ),
            id="conteudo",
            class_name="main-content",
        ),
        rx.el.footer(
            rx.text("Biblioteca escolar"),
            class_name="site-footer",
        ),
        class_name="app-shell",
    )


def student_signup() -> rx.Component:
    return rx.box(
        rx.link("Pular para o conteúdo", href="#conteudo-cadastro", class_name="skip-link"),
        rx.el.header(
            rx.heading("Biblioteca escolar", size="6"),
            rx.link("Voltar ao início", href="/"),
            class_name="site-header",
        ),
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
                        class_name="signup-feedback",
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
        rx.el.header(
            rx.heading("Biblioteca escolar", size="6"),
            rx.link("Voltar ao início", href="/"),
            class_name="site-header",
        ),
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
                        class_name="signup-feedback",
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


def catalog_admin() -> rx.Component:
    return rx.box(
        rx.link("Pular para o conteúdo", href="#conteudo-acervo", class_name="skip-link"),
        rx.el.header(
            rx.heading("Biblioteca escolar", size="6"),
            rx.link("Voltar ao início", href="/"),
            class_name="site-header",
        ),
        rx.el.main(
            rx.el.section(
                rx.heading("Cadastro de título e exemplares", size="7"),
                rx.text(
                    "Acesso restrito a bibliotecários. As categorias disponíveis "
                    "são carregadas do catálogo."
                ),
                rx.cond(
                    State.catalog_message != "",
                    rx.el.p(
                        State.catalog_message,
                        role=rx.cond(State.catalog_has_error, "alert", "status"),
                        aria_live="polite",
                        class_name="signup-feedback",
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
            class_name="main-content",
        ),
        rx.el.footer(rx.text("Biblioteca escolar"), class_name="site-footer"),
        class_name="app-shell",
    )


app = rx.App(
    style={
        "font_family": "system-ui, sans-serif",
        "color": "#172b4d",
        "background_color": "#f7f9fc",
        ".app-shell": {
            "min_height": "100vh",
            "padding": "1rem",
        },
        ".site-header": {
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "gap": "1rem",
            "max_width": "72rem",
            "margin": "0 auto",
            "padding": "1rem",
            "border_bottom": "1px solid #cbd5e1",
        },
        ".site-nav": {
            "display": "flex",
            "flex_wrap": "wrap",
            "gap": "1rem",
        },
        ".main-content": {
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
        ".signup-form": {
            "display": "flex",
            "flex_direction": "column",
            "gap": "0.5rem",
            "width": "min(100%, 28rem)",
        },
        ".signup-label": {
            "font_weight": "600",
            "margin_top": "0.5rem",
        },
        ".signup-input": {
            "width": "100%",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "border": "1px solid #64748b",
            "border_radius": "0.375rem",
            "background_color": "#ffffff",
        },
        ".signup-feedback": {
            "max_width": "28rem",
            "padding": "0.75rem",
            "border_radius": "0.375rem",
            "background_color": "#e8f1fb",
        },
        ".signup-note": {
            "max_width": "28rem",
            "font_size": "0.9rem",
        },
        ".focus-demo-field": {
            "width": "min(100%, 24rem)",
            "min_height": "2.75rem",
            "padding": "0.5rem 0.75rem",
            "border": "1px solid #64748b",
            "border_radius": "0.375rem",
            "background_color": "#ffffff",
        },
        ".focus-demo-button": {
            "min_height": "2.75rem",
            "padding": "0.5rem 1rem",
            "border": "0",
            "border_radius": "0.375rem",
            "background_color": "#174ea6",
            "color": "#ffffff",
            "cursor": "pointer",
        },
        ".site-nav a": {
            "color": "#174ea6",
            "font_weight": "600",
        },
        ".site-footer": {
            "max_width": "72rem",
            "margin": "0 auto",
            "padding": "1rem",
            "border_top": "1px solid #cbd5e1",
        },
        ".skip-link": {
            "position": "absolute",
            "top": "-5rem",
            "left": "1rem",
            "z_index": "10",
            "padding": "0.75rem 1rem",
            "background_color": "#ffffff",
            "color": "#174ea6",
        },
        ".skip-link:focus-visible": {
            "top": "1rem",
        },
        ":focus-visible": {
            "outline": "3px solid #005fcc",
            "outline_offset": "3px",
        },
        "@media screen and (max-width: 40rem)": {
            ".site-header": {
                "align_items": "flex-start",
                "flex_direction": "column",
            },
            ".content-section": {
                "padding": "1.5rem 0.5rem",
            },
        },
    }
)
app.add_page(index, title="Biblioteca escolar")
app.add_page(student_signup, route="/cadastro", title="Cadastro de estudante")
app.add_page(login_page, route="/login", title="Entrar")
app.add_page(
    catalog_admin,
    route="/admin/acervo",
    title="Cadastro de acervo",
    on_load=State.load_catalog_categories,
)

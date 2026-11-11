"""API somente para demonstração; não substitui nem simula a segurança do Xano real."""

from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

if __package__:
    from .demo_seed_data import CATEGORY_NAMES, DEMO_USERS, SEED_TITLES
else:
    from demo_seed_data import CATEGORY_NAMES, DEMO_USERS, SEED_TITLES


HOST = "127.0.0.1"
PORT = 8765
PASSWORD = "demo123"


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _title(
    title_id: int,
    name: str,
    authors: str,
    *,
    active: bool = True,
    **optional: object,
) -> dict[str, object]:
    return {
        "id": title_id,
        "titulo": name,
        "autores": authors,
        "isbn": optional.get("isbn"),
        "editora": optional.get("editora"),
        "edicao": optional.get("edicao"),
        "ano_publicacao": optional.get("ano_publicacao"),
        "descricao": optional.get("descricao"),
        "ativo": active,
        "created_at": _now(),
    }


def _copy(copy_id: int, title_id: int, state: str) -> dict[str, object]:
    return {
        "id": copy_id,
        "titulo_id": title_id,
        "estado": state,
        "codigo_tombo": f"EX-{copy_id:06d}",
        "created_at": _now(),
    }


class DemoData:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.categories: list[dict[str, object]] = []
        self.titles: list[dict[str, object]] = []
        self.title_categories: list[dict[str, object]] = []
        self.copies: list[dict[str, object]] = []
        self.students: list[dict[str, object]] = []
        self.users: dict[str, dict[str, object]] = {}
        self.reservations: list[dict[str, object]] = []
        self.loans = [
            {
                "usuario_id": 101,
                "titulo_id": 2,
                "devolvido_em": None,
                "vence_em": "2099-12-31T23:59:59Z",
            }
        ]
        self.next_title_id = 1
        self.next_copy_id = 1
        self.next_category_link_id = 1
        self.next_reservation_id = 1

        seed_demo_data(self)

    def categories_for(self, title_id: int) -> list[dict[str, object]]:
        return [
            dict(item)
            for item in self.title_categories
            if item["titulo_id"] == title_id
        ]

    def available_count(self, title_id: int) -> int:
        return sum(
            item["titulo_id"] == title_id and item["estado"] == "disponivel"
            for item in self.copies
        )

    def public_entry(self, title: dict[str, object]) -> dict[str, object]:
        return {
            "titulo": dict(title),
            "categorias": self.categories_for(int(title["id"])),
            "exemplares_disponiveis": self.available_count(int(title["id"])),
        }

    def admin_entry(self, title: dict[str, object]) -> dict[str, object]:
        entry = self.public_entry(title)
        entry["exemplares"] = [
            dict(item)
            for item in self.copies
            if item["titulo_id"] == title["id"]
        ]
        return entry


def _normalized(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def seed_demo_data(data: DemoData) -> None:
    with data.lock:
        category_ids = {
            _normalized(str(item["nome"])): int(item["id"])
            for item in data.categories
        }
        next_category_id = max(category_ids.values(), default=0) + 1
        for name in CATEGORY_NAMES:
            key = _normalized(name)
            if key not in category_ids:
                category_ids[key] = next_category_id
                data.categories.append(
                    {"id": next_category_id, "nome": name, "created_at": _now()}
                )
                next_category_id += 1

        title_ids = {
            (_normalized(str(item["titulo"])), _normalized(str(item["autores"]))): int(
                item["id"]
            )
            for item in data.titles
        }
        for seed in SEED_TITLES:
            identity = (_normalized(seed.title), _normalized(seed.author))
            title_id = title_ids.get(identity)
            if title_id is None:
                title_id = max(
                    (int(item["id"]) for item in data.titles), default=0
                ) + 1
                data.titles.append(
                    _title(
                        title_id,
                        seed.title,
                        seed.author,
                        active=seed.active,
                    )
                )
                title_ids[identity] = title_id

            for category_name in seed.categories:
                category_id = category_ids[_normalized(category_name)]
                if not any(
                    int(link["titulo_id"]) == title_id
                    and int(link["categoria_id"]) == category_id
                    for link in data.title_categories
                ):
                    link_id = max(
                        (int(link["id"]) for link in data.title_categories),
                        default=0,
                    ) + 1
                    data.title_categories.append(
                        {
                            "id": link_id,
                            "titulo_id": title_id,
                            "categoria_id": category_id,
                            "created_at": _now(),
                        }
                    )

            current_copies = [
                item for item in data.copies if int(item["titulo_id"]) == title_id
            ]
            for index in range(len(current_copies), seed.copies):
                copy_id = max(
                    (int(item["id"]) for item in data.copies), default=0
                ) + 1
                state = (
                    seed.initial_copy_states[index]
                    if index < len(seed.initial_copy_states)
                    else "disponivel"
                )
                data.copies.append(_copy(copy_id, title_id, state))

        existing_emails = {_normalized(email) for email in data.users}
        for seed_user in DEMO_USERS:
            email = str(seed_user["email"])
            if _normalized(email) in existing_emails:
                continue
            user = {
                **seed_user,
                "ativo": True,
            }
            data.users[email] = user
            if seed_user["perfil"] == "estudante" and not any(
                _normalized(str(student["email"])) == _normalized(email)
                for student in data.students
            ):
                data.students.append(
                    {
                        key: user[key]
                        for key in ("id", "nome", "email", "perfil", "ativo")
                    }
                )
            existing_emails.add(_normalized(email))

        data.next_title_id = max(
            (int(item["id"]) for item in data.titles), default=0
        ) + 1
        data.next_copy_id = max(
            (int(item["id"]) for item in data.copies), default=0
        ) + 1
        data.next_category_link_id = max(
            (int(item["id"]) for item in data.title_categories), default=0
        ) + 1


DATA = DemoData()


def _int_field(body: dict[str, object], key: str) -> int:
    value = body.get(key)
    if type(value) is not int or value < 1:
        raise ApiError(400, f"Campo inválido: {key}.")
    return value


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "BibliotecaDemo/1.0"

    def log_message(self, _format: str, *args: object) -> None:
        return

    def _send_json(self, status: int, result: object) -> None:
        payload = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 65536:
                raise ValueError
            value = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            raise ApiError(400, "Corpo JSON inválido.") from None
        if not isinstance(value, dict):
            raise ApiError(400, "Corpo JSON inválido.")
        return value

    def _profile(self, *, required: str | None = None) -> dict[str, object]:
        authorization = self.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise ApiError(401, "Autenticação necessária.")
        user = next(
            (item for item in DATA.users.values() if item["token"] == token),
            None,
        )
        if user is None:
            raise ApiError(401, "Autenticação necessária.")
        if not user["ativo"]:
            raise ApiError(403, "Conta desativada.")
        if required == "bibliotecario" and user["perfil"] not in {
            "bibliotecario",
            "admin",
        }:
            raise ApiError(403, "Perfil insuficiente.")
        return user

    def _handle(self) -> tuple[int, object]:
        parsed = urlsplit(self.path)
        path = unquote(parsed.path)
        method = self.command

        if method == "POST" and path == "/auth/login":
            body = self._read_json()
            email = body.get("email")
            password = body.get("senha")
            user = DATA.users.get(email.strip().lower()) if isinstance(email, str) else None
            if user is None or password != PASSWORD or not user["ativo"]:
                raise ApiError(401, "Credenciais inválidas.")
            return 200, {
                "authToken": user["token"],
                "usuario": {
                    "id": user["id"],
                    "nome": user["nome"],
                    "email": user["email"],
                    "perfil": user["perfil"],
                },
            }

        if method == "GET" and path == "/catalogo/categorias":
            return 200, [dict(item) for item in DATA.categories]

        if method == "GET" and path == "/catalogo/titulos":
            with DATA.lock:
                return 200, [
                    DATA.public_entry(title)
                    for title in DATA.titles
                    if title.get("ativo") is not False
                ]

        match = re.fullmatch(r"/catalogo/titulos/(\d+)", path)
        if method == "GET" and match:
            title_id = int(match.group(1))
            with DATA.lock:
                title = next(
                    (item for item in DATA.titles if item["id"] == title_id),
                    None,
                )
                if title is None or title.get("ativo") is False:
                    raise ApiError(404, "Título não encontrado.")
                return 200, DATA.public_entry(title)

        match = re.fullmatch(r"/catalogo/categorias/(\d+)/titulos", path)
        if method == "GET" and match:
            category_id = int(match.group(1))
            with DATA.lock:
                ids = {
                    item["titulo_id"]
                    for item in DATA.title_categories
                    if item["categoria_id"] == category_id
                }
                return 200, [
                    dict(title)
                    for title in DATA.titles
                    if title["id"] in ids and title.get("ativo") is not False
                ]

        if path.startswith("/admin/"):
            self._profile(required="bibliotecario")

        if method == "GET" and path == "/admin/acervo":
            with DATA.lock:
                return 200, [DATA.admin_entry(title) for title in DATA.titles]

        if method == "GET" and path == "/admin/estudantes":
            user = self._profile(required="bibliotecario")
            email_values = parse_qs(parsed.query, keep_blank_values=True).get(
                "email", [""]
            )
            email = email_values[0].strip().lower()
            if " " in email:
                raise ApiError(400, "O e-mail não pode conter espaços internos.")
            if user["perfil"] not in {"bibliotecario", "admin"}:
                raise ApiError(403, "Perfil insuficiente.")
            return 200, [
                {"id": student["id"], "nome": student["nome"]}
                for student in DATA.students
                if student["perfil"] == "estudante"
                and student["ativo"] is not False
                and student["email"] == email
            ]

        if method == "POST" and path in {"/catalogo/titulos", "/admin/titulos"}:
            self._profile(required="bibliotecario")
            body = self._read_json()
            title_name = body.get("titulo")
            authors = body.get("autores")
            if not isinstance(title_name, str) or not title_name.strip():
                raise ApiError(400, "Título obrigatório.")
            if not isinstance(authors, str) or not authors.strip():
                raise ApiError(400, "Autores obrigatórios.")
            allowed = {
                "titulo",
                "autores",
                "isbn",
                "editora",
                "edicao",
                "ano_publicacao",
                "descricao",
            }
            optional = {key: value for key, value in body.items() if key in allowed}
            if "ano_publicacao" in optional:
                try:
                    optional["ano_publicacao"] = int(optional["ano_publicacao"])
                except (TypeError, ValueError):
                    raise ApiError(400, "Ano de publicação inválido.") from None
            with DATA.lock:
                title = _title(
                    DATA.next_title_id,
                    title_name.strip(),
                    authors.strip(),
                    **{k: v for k, v in optional.items() if k not in {"titulo", "autores"}},
                )
                DATA.next_title_id += 1
                DATA.titles.append(title)
                return 201, dict(title)

        match = re.fullmatch(r"/admin/titulos/(\d+)/categorias", path)
        if method == "POST" and match:
            self._profile(required="bibliotecario")
            body = self._read_json()
            title_id = int(match.group(1))
            category_id = _int_field(body, "categoria_id")
            with DATA.lock:
                if not any(item["id"] == title_id for item in DATA.titles):
                    raise ApiError(404, "Título não encontrado.")
                if not any(item["id"] == category_id for item in DATA.categories):
                    raise ApiError(404, "Categoria não encontrada.")
                existing = next(
                    (
                        item
                        for item in DATA.title_categories
                        if item["titulo_id"] == title_id
                        and item["categoria_id"] == category_id
                    ),
                    None,
                )
                if existing:
                    raise ApiError(409, "Categoria já associada ao título.")
                association = {
                    "id": DATA.next_category_link_id,
                    "titulo_id": title_id,
                    "categoria_id": category_id,
                    "created_at": _now(),
                }
                DATA.next_category_link_id += 1
                DATA.title_categories.append(association)
                return 201, dict(association)

        if method == "POST" and path == "/admin/exemplares":
            self._profile(required="bibliotecario")
            body = self._read_json()
            title_id = _int_field(body, "titulo_id")
            with DATA.lock:
                if not any(item["id"] == title_id for item in DATA.titles):
                    raise ApiError(404, "Título não encontrado.")
                copy = _copy(DATA.next_copy_id, title_id, "disponivel")
                DATA.next_copy_id += 1
                DATA.copies.append(copy)
                return 201, dict(copy)

        match = re.fullmatch(r"/catalogo/titulos/(\d+)", path)
        if method == "PATCH" and match:
            self._profile(required="bibliotecario")
            body = self._read_json()
            title_id = int(match.group(1))
            with DATA.lock:
                title = next(
                    (item for item in DATA.titles if item["id"] == title_id),
                    None,
                )
                if title is None:
                    raise ApiError(404, "Título não encontrado.")
                for required_field in ("titulo", "autores"):
                    value = body.get(required_field)
                    if not isinstance(value, str) or not value.strip():
                        raise ApiError(400, f"Campo obrigatório: {required_field}.")
                if body.get("ativo") is False:
                    if any(
                        loan["titulo_id"] == title_id
                        and loan["devolvido_em"] in (None, 0)
                        for loan in DATA.loans
                    ):
                        raise ApiError(
                            403,
                            "A desativação foi recusada: há empréstimo ativo.",
                        )
                    if any(
                        reservation["titulo_id"] == title_id
                        and reservation["estado"] in {"aguardando", "ofertada"}
                        for reservation in DATA.reservations
                    ):
                        raise ApiError(
                            403,
                            "A desativação foi recusada: há reserva ativa.",
                        )
                for key in (
                    "titulo",
                    "autores",
                    "isbn",
                    "editora",
                    "edicao",
                    "ano_publicacao",
                    "descricao",
                    "ativo",
                ):
                    if key in body:
                        title[key] = body[key]
                return 200, {
                    key: title.get(key)
                    for key in (
                        "id",
                        "titulo",
                        "autores",
                        "isbn",
                        "editora",
                        "edicao",
                        "ano_publicacao",
                        "descricao",
                        "ativo",
                    )
                }

        if method == "POST" and path == "/admin/reservas":
            self._profile(required="bibliotecario")
            body = self._read_json()
            student_id = _int_field(body, "usuario_id")
            title_id = _int_field(body, "titulo_id")
            with DATA.lock:
                student = next(
                    (item for item in DATA.students if item["id"] == student_id),
                    None,
                )
                if (
                    student is None
                    or student["perfil"] != "estudante"
                    or student["ativo"] is False
                ):
                    raise ApiError(404, "Estudante não encontrado ou inativo.")
                title = next(
                    (item for item in DATA.titles if item["id"] == title_id),
                    None,
                )
                if title is None:
                    raise ApiError(404, "Título não encontrado.")
                if title.get("ativo") is False:
                    raise ApiError(403, "Título inativo não aceita novas reservas.")
                now = datetime.now(timezone.utc)
                if any(
                    loan["usuario_id"] == student_id
                    and loan["devolvido_em"] in (None, 0)
                    and datetime.fromisoformat(
                        str(loan["vence_em"]).replace("Z", "+00:00")
                    )
                    < now
                    for loan in DATA.loans
                ):
                    raise ApiError(403, "Estudante possui empréstimo atrasado.")
                if any(
                    loan["usuario_id"] == student_id
                    and loan["titulo_id"] == title_id
                    and loan["devolvido_em"] in (None, 0)
                    for loan in DATA.loans
                ):
                    raise ApiError(
                        403,
                        "Estudante já possui o título emprestado.",
                    )
                if any(
                    reservation["usuario_id"] == student_id
                    and reservation["titulo_id"] == title_id
                    and reservation["estado"] in {"aguardando", "ofertada"}
                    for reservation in DATA.reservations
                ):
                    raise ApiError(
                        403,
                        "Estudante já possui reserva ativa para este título.",
                    )
                reservation = {
                    "id": DATA.next_reservation_id,
                    "usuario_id": student_id,
                    "titulo_id": title_id,
                    "criada_em": _now(),
                    "estado": "aguardando",
                    "exemplar_id": None,
                    "ofertada_em": None,
                    "expira_em": None,
                }
                DATA.next_reservation_id += 1
                DATA.reservations.append(reservation)
                return 201, dict(reservation)

        return 404, {"message": "Rota não encontrada."}

    def _dispatch(self) -> None:
        try:
            status, result = self._handle()
        except ApiError as error:
            status, result = error.status, {"message": error.message}
        self._send_json(status, result)

    do_GET = _dispatch
    do_POST = _dispatch
    do_PATCH = _dispatch


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), DemoHandler)
    print(
        f"API de demonstração ativa em http://{HOST}:{PORT} "
        "(dados em memória; Ctrl+C para encerrar)."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("API de demonstração encerrada.")


if __name__ == "__main__":
    main()

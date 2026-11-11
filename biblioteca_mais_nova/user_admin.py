"""Operações de gestão de bibliotecários no contrato local do Xano."""

import json
from typing import TypedDict

import httpx

from biblioteca_mais_nova.signup import SignupValidationError, normalize_email
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
)


class Librarian(TypedDict):
    id: int
    nome: str
    email: str
    ativo: bool


class LibrarianPayload(TypedDict):
    nome: str
    email: str
    senha: str


class UserAdminValidationError(ValueError):
    """Entrada inválida para a gestão de bibliotecários."""


def build_librarian_payload(form_data: dict[str, str]) -> LibrarianPayload:
    nome = form_data.get("nome", "").strip()
    if not nome:
        raise UserAdminValidationError("Informe o nome.")

    try:
        email = normalize_email(form_data.get("email", ""))
    except SignupValidationError as error:
        raise UserAdminValidationError(str(error)) from None

    senha = form_data.get("senha", "")
    if not senha:
        raise UserAdminValidationError("Informe a senha.")
    return {"nome": nome, "email": email, "senha": senha}


def _response_json(response: httpx.Response) -> object:
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        raise XanoRequestError(
            "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
        ) from None


def _response_error() -> XanoRequestError:
    return XanoRequestError(
        "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
    )


def _parse_librarian(value: object) -> Librarian:
    if (
        not isinstance(value, dict)
        or type(value.get("id")) is not int
        or value.get("id", 0) < 1
        or not isinstance(value.get("nome"), str)
        or not isinstance(value.get("email"), str)
        or (
            "perfil" in value
            and value.get("perfil") != "bibliotecario"
        )
        or (value.get("ativo") is not None and type(value.get("ativo")) is not bool)
    ):
        raise _response_error()

    return {
        "id": value["id"],
        "nome": value["nome"],
        "email": value["email"],
        "ativo": value.get("ativo") is not False,
    }


async def list_librarians(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[Librarian]:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", "/admin/usuarios", token=token)
    data = _response_json(response)
    if not isinstance(data, list):
        raise _response_error()
    return [_parse_librarian(item) for item in data]


async def create_librarian(
    payload: LibrarianPayload,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Librarian:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "POST",
        "/admin/usuarios",
        token=token,
        json=payload,
    )
    return _parse_librarian(_response_json(response))


async def set_librarian_active(
    librarian_id: int,
    active: bool,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Librarian:
    if type(librarian_id) is not int or librarian_id < 1 or type(active) is not bool:
        raise _response_error()

    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "PATCH",
        f"/admin/usuarios/{librarian_id}",
        token=token,
        json={"ativo": active},
    )
    return _parse_librarian(_response_json(response))


def user_admin_error_message(error: Exception) -> str:
    if isinstance(error, UserAdminValidationError):
        return str(error)
    if isinstance(error, XanoResponseError) and error.status_code in {400, 401, 403}:
        return "Não foi possível concluir a operação. Confira sua permissão e os dados."
    if isinstance(error, XanoConfigurationError):
        return "A gestão de bibliotecários está temporariamente indisponível."
    if isinstance(error, XanoRequestError):
        return "Não foi possível concluir a operação. Tente novamente mais tarde."
    return "Ocorreu um erro inesperado. Tente novamente mais tarde."

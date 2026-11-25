"""Operações de gestão de bibliotecários no contrato local do Xano."""

from typing import TypedDict

import httpx

from biblioteca_mais_nova.response_parsing import (
    ParsedRecords,
    parse_xano_bool,
    parse_xano_id,
    parse_xano_records,
)
from biblioteca_mais_nova.signup import SignupValidationError, normalize_email
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    parse_xano_response_json,
    parse_xano_write_response,
    xano_message_with_reference,
    xano_public_error_message,
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
    return parse_xano_response_json(response)


def _response_error() -> XanoRequestError:
    return XanoInvalidResponseError()


def _parse_librarian(value: object) -> Librarian:
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("nome"), str)
        or not isinstance(value.get("email"), str)
        or (
            "perfil" in value
            and value.get("perfil") != "bibliotecario"
        )
    ):
        raise _response_error()

    active = value.get("ativo", True)
    if active is None:
        active = True
    return {
        "id": parse_xano_id(value.get("id")),
        "nome": value["nome"],
        "email": value["email"],
        "ativo": parse_xano_bool(active),
    }


async def list_librarians(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ParsedRecords[Librarian]:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", "/admin/usuarios", token=token)
    return parse_xano_records(_response_json(response), _parse_librarian)


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
    return parse_xano_write_response(response, _parse_librarian)


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
    return parse_xano_write_response(response, _parse_librarian)


def user_admin_error_message(error: Exception) -> str:
    if isinstance(error, UserAdminValidationError):
        return str(error)
    common_message = xano_public_error_message(error)
    if common_message is not None:
        return common_message
    if isinstance(error, XanoResponseError) and error.public_detail:
        return xano_message_with_reference(error.public_detail, error)
    if isinstance(error, XanoResponseError) and error.status_code in {400, 401, 403}:
        return xano_message_with_reference(
            "Não foi possível concluir a operação. Confira sua permissão e os dados.",
            error,
        )
    if isinstance(error, XanoConfigurationError):
        return xano_message_with_reference(
            "A gestão de bibliotecários está temporariamente indisponível.",
            error,
        )
    if isinstance(error, XanoRequestError):
        return xano_message_with_reference(
            "Não foi possível concluir a operação. Tente novamente mais tarde.",
            error,
        )
    return xano_message_with_reference(
        "Ocorreu um erro inesperado. Tente novamente mais tarde.",
        error,
    )

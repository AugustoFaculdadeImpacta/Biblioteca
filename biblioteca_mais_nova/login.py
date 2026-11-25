"""Autenticação de usuários pelo contrato local do Xano."""

from typing import Literal, TypedDict

import httpx

from biblioteca_mais_nova.signup import SignupValidationError, normalize_email
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    parse_xano_response_json,
    xano_message_with_reference,
    xano_public_error_message,
)


class LoginPayload(TypedDict):
    email: str
    senha: str


class LoginUser(TypedDict):
    id: int
    nome: str
    email: str
    perfil: Literal["estudante", "bibliotecario", "admin"]


class LoginSession(TypedDict):
    authToken: str
    usuario: LoginUser


class LoginValidationError(ValueError):
    """Entrada de login inválida para exibição."""


def build_login_payload(form_data: dict[str, str]) -> LoginPayload:
    try:
        email = normalize_email(form_data.get("email", ""))
    except SignupValidationError as error:
        raise LoginValidationError(str(error)) from None

    senha = form_data.get("senha", "")
    if not senha:
        raise LoginValidationError("Informe sua senha.")
    return {"email": email, "senha": senha}


async def submit_login(
    payload: LoginPayload,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> LoginSession:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("POST", "/auth/login", json=payload)

    session = parse_xano_response_json(response)

    if not isinstance(session, dict):
        raise XanoInvalidResponseError()

    token = session.get("authToken")
    user = session.get("usuario")
    if (
        not isinstance(token, str)
        or not token
        or not isinstance(user, dict)
        or type(user.get("id")) is not int
        or not isinstance(user.get("nome"), str)
        or not isinstance(user.get("email"), str)
        or not isinstance(user.get("perfil"), str)
        or user["perfil"] not in {"estudante", "bibliotecario", "admin"}
    ):
        raise XanoInvalidResponseError()

    return {
        "authToken": token,
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "perfil": user["perfil"],
        },
    }


def login_error_message(error: Exception) -> str:
    if isinstance(error, LoginValidationError):
        return str(error)
    common_message = xano_public_error_message(error)
    if common_message is not None:
        return common_message
    if (
        isinstance(error, XanoResponseError)
        and error.status_code == 403
        and error.public_detail
        == "A conta está desativada. Procure a administração da biblioteca."
    ):
        return xano_message_with_reference(error.public_detail, error)
    if isinstance(error, XanoResponseError) and error.public_detail:
        return xano_message_with_reference(error.public_detail, error)
    if isinstance(error, XanoResponseError) and error.status_code in {
        400,
        401,
        403,
    }:
        return xano_message_with_reference(
            "Não foi possível autenticar. Confira os dados e tente novamente.",
            error,
        )
    if isinstance(error, XanoConfigurationError):
        return xano_message_with_reference(
            "O login está temporariamente indisponível. Tente novamente mais tarde.",
            error,
        )
    if isinstance(error, XanoRequestError):
        return xano_message_with_reference(
            "Não foi possível concluir o login. Tente novamente mais tarde.",
            error,
        )
    return xano_message_with_reference(
        "Ocorreu um erro inesperado. Tente novamente mais tarde.",
        error,
    )

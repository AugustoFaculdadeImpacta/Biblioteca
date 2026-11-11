"""Autenticação de usuários pelo contrato local do Xano."""

import json
from typing import Literal, TypedDict

import httpx

from biblioteca_mais_nova.signup import SignupValidationError, normalize_email
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
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

    try:
        session = response.json()
    except (json.JSONDecodeError, ValueError):
        raise XanoRequestError(
            "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
        ) from None

    if not isinstance(session, dict):
        raise XanoRequestError(
            "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
        )

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
        raise XanoRequestError(
            "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
        )

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
    if isinstance(error, XanoResponseError) and error.status_code in {
        400,
        401,
        403,
    }:
        return "Não foi possível autenticar. Confira os dados e tente novamente."
    if isinstance(error, XanoConfigurationError):
        return "O login está temporariamente indisponível. Tente novamente mais tarde."
    if isinstance(error, XanoRequestError):
        return "Não foi possível concluir o login. Tente novamente mais tarde."
    return "Ocorreu um erro inesperado. Tente novamente mais tarde."

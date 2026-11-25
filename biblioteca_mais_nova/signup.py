"""Regras de entrada e integração do autocadastro de estudantes."""

import re
from typing import TypedDict

import httpx

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    parse_xano_write_response,
    xano_message_with_reference,
    xano_public_error_message,
)


class SignupPayload(TypedDict):
    nome: str
    email: str
    senha: str


class SignupSession(TypedDict):
    authToken: str
    usuario: dict[str, object]


class SignupValidationError(ValueError):
    """Entrada de autocadastro inválida, segura para exibição."""


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not email:
        raise SignupValidationError("Informe seu e-mail.")
    if any(character.isspace() for character in email):
        raise SignupValidationError("O e-mail não pode conter espaços internos.")
    if not re.fullmatch(r"[^@\s]+@[^@\s.]+(?:\.[^@\s.]+)+", email):
        raise SignupValidationError("Informe um endereço de e-mail válido.")
    return email


def build_signup_payload(form_data: dict[str, str]) -> SignupPayload:
    nome = form_data.get("nome", "")
    email = normalize_email(form_data.get("email", ""))
    senha = form_data.get("senha", "")

    if not nome or not nome.strip():
        raise SignupValidationError("Informe seu nome.")
    if not senha:
        raise SignupValidationError("Informe sua senha.")

    return {"nome": nome, "email": email, "senha": senha}


async def submit_student_signup(
    payload: SignupPayload,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> SignupSession:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("POST", "/auth/signup", json=payload)

    def parse_session(session: object) -> SignupSession:
        if not isinstance(session, dict):
            raise XanoInvalidResponseError()

        token = session.get("authToken")
        user = session.get("usuario")
        if (
            not isinstance(token, str)
            or not token
            or not isinstance(user, dict)
            or not isinstance(user.get("id"), int)
            or not isinstance(user.get("nome"), str)
            or not isinstance(user.get("email"), str)
            or user.get("perfil") != "estudante"
        ):
            raise XanoInvalidResponseError()

        return {"authToken": token, "usuario": user}

    return parse_xano_write_response(response, parse_session)


def signup_error_message(error: Exception) -> str:
    if isinstance(error, SignupValidationError):
        return str(error)
    common_message = xano_public_error_message(error)
    if common_message is not None:
        return common_message
    if isinstance(error, XanoResponseError):
        if error.status_code == 409:
            return xano_message_with_reference(
                "Este e-mail já está cadastrado. Tente entrar com sua conta.",
                error,
            )
        if error.status_code == 403 and error.public_detail == (
            "Este e-mail já está cadastrado. Tente entrar com sua conta."
        ):
            return xano_message_with_reference(error.public_detail, error)
        if error.status_code == 400:
            return xano_message_with_reference(
                "Confira os dados informados e tente novamente.",
                error,
            )
        if error.public_detail:
            return xano_message_with_reference(error.public_detail, error)
    if isinstance(error, XanoConfigurationError):
        return xano_message_with_reference(
            "O cadastro está temporariamente indisponível. Tente novamente mais tarde.",
            error,
        )
    if isinstance(error, XanoRequestError):
        return xano_message_with_reference(
            "Não foi possível concluir o cadastro. Tente novamente mais tarde.",
            error,
        )
    return xano_message_with_reference(
        "Ocorreu um erro inesperado. Tente novamente mais tarde.",
        error,
    )

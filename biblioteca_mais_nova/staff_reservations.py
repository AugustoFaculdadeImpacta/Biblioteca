"""Busca de estudantes e reservas administrativas no contrato local do Xano."""

import json
from urllib.parse import quote
from typing import TypedDict

import httpx

from biblioteca_mais_nova.signup import SignupValidationError, normalize_email
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
)


class StudentIdentity(TypedDict):
    id: int
    nome: str


class StaffReservation(TypedDict):
    id: int
    usuario_id: int
    titulo_id: int
    estado: str


class StaffReservationValidationError(ValueError):
    """Entrada inválida para busca de estudante ou criação de reserva."""


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


def _positive_id(value: object) -> bool:
    return type(value) is int and value > 0


def _parse_student(value: object) -> StudentIdentity:
    if (
        not isinstance(value, dict)
        or not _positive_id(value.get("id"))
        or not isinstance(value.get("nome"), str)
        or not value["nome"].strip()
    ):
        raise _response_error()
    return {"id": value["id"], "nome": value["nome"]}


async def find_student_by_email(
    email: str,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> StudentIdentity | None:
    try:
        normalized_email = normalize_email(email)
    except SignupValidationError as error:
        raise StaffReservationValidationError(str(error)) from None

    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "GET",
        f"/admin/estudantes?email={quote(normalized_email, safe='')}",
        token=token,
    )
    result = _response_json(response)
    if not isinstance(result, list) or len(result) > 1:
        raise _response_error()
    if not result:
        return None
    return _parse_student(result[0])


def _parse_staff_reservation(value: object) -> StaffReservation:
    if (
        not isinstance(value, dict)
        or not _positive_id(value.get("id"))
        or not _positive_id(value.get("usuario_id"))
        or not _positive_id(value.get("titulo_id"))
        or value.get("estado") != "aguardando"
    ):
        raise _response_error()
    return {
        "id": value["id"],
        "usuario_id": value["usuario_id"],
        "titulo_id": value["titulo_id"],
        "estado": "aguardando",
    }


async def create_staff_reservation(
    student_id: int,
    title_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> StaffReservation:
    if not _positive_id(student_id) or not _positive_id(title_id):
        raise _response_error()

    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "POST",
        "/admin/reservas",
        token=token,
        json={"usuario_id": student_id, "titulo_id": title_id},
    )
    return _parse_staff_reservation(_response_json(response))


def staff_reservation_error_message(error: Exception) -> str:
    if isinstance(error, StaffReservationValidationError):
        return str(error)
    if isinstance(error, XanoResponseError) and error.public_detail:
        return error.public_detail
    if isinstance(error, XanoResponseError) and error.status_code in {401, 403}:
        return "Seu perfil não tem permissão para realizar esta operação."
    if isinstance(error, XanoConfigurationError):
        return "A gestão de reservas está temporariamente indisponível."
    if isinstance(error, XanoRequestError):
        return "Não foi possível concluir a operação. Tente novamente mais tarde."
    return "Ocorreu um erro inesperado. Tente novamente mais tarde."

"""Operações autenticadas de circulação disponíveis ao estudante."""

import json
from datetime import datetime, timezone
from typing import Callable, NotRequired, TypeVar, TypedDict

import httpx

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoInvalidResponseError,
    XanoRequestError,
)


class Loan(TypedDict):
    id: int
    usuario_id: int
    exemplar_id: int
    solicitacao_id: NotRequired[int | None]
    retirado_em: str | int | float
    vence_em: str | int | float
    devolvido_em: str | int | float | None


class LoanRequest(TypedDict):
    id: int
    usuario_id: int
    titulo_id: int
    solicitada_em: NotRequired[str | int | float | None]
    estado: str
    reserva_id: NotRequired[int | None]
    atendida_em: NotRequired[str | int | float | None]


class Reservation(TypedDict):
    id: int
    usuario_id: int
    titulo_id: int
    criada_em: str | int | float
    estado: str
    exemplar_id: int | None
    ofertada_em: str | int | float | None
    expira_em: str | int | float | None
    expira_em_sao_paulo: str | None


class LoanRequestResult(TypedDict):
    id: int
    titulo_id: int
    estado: str
    reserva_id: NotRequired[int | None]


Record = TypeVar("Record")


def _response_error() -> XanoRequestError:
    return XanoInvalidResponseError(
        "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
    )


def _response_json(response: httpx.Response) -> object:
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        raise _response_error() from None


def _timestamp(value: object, *, nullable: bool = False) -> bool:
    if nullable and (value is None or (type(value) is int and value == 0)):
        return True
    if type(value) in {int, float}:
        try:
            datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return False
        return True
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is None or parsed.utcoffset() is not None


def _positive_id(value: object) -> bool:
    return type(value) is int and value > 0


def _parse_loan(value: object) -> Loan:
    if (
        not isinstance(value, dict)
        or not _positive_id(value.get("id"))
        or not _positive_id(value.get("usuario_id"))
        or not _positive_id(value.get("exemplar_id"))
        or not _timestamp(value.get("retirado_em"))
        or not _timestamp(value.get("vence_em"))
        or "devolvido_em" not in value
        or not _timestamp(value["devolvido_em"], nullable=True)
    ):
        raise _response_error()

    loan: Loan = {
        "id": value["id"],
        "usuario_id": value["usuario_id"],
        "exemplar_id": value["exemplar_id"],
        "retirado_em": value["retirado_em"],
        "vence_em": value["vence_em"],
        "devolvido_em": value["devolvido_em"],
    }
    request_id = value.get("solicitacao_id")
    if request_id is not None and not _positive_id(request_id):
        raise _response_error()
    if "solicitacao_id" in value:
        loan["solicitacao_id"] = request_id
    return loan


def _parse_request(value: object) -> LoanRequest:
    if (
        not isinstance(value, dict)
        or not _positive_id(value.get("id"))
        or not _positive_id(value.get("usuario_id"))
        or not _positive_id(value.get("titulo_id"))
        or not isinstance(value.get("estado"), str)
        or value["estado"] not in {"pendente", "em_reserva", "atendida", "recusada"}
    ):
        raise _response_error()

    for field in ("solicitada_em", "atendida_em"):
        if field in value and not _timestamp(value[field], nullable=True):
            raise _response_error()
    reservation_id = value.get("reserva_id")
    if reservation_id is not None and not _positive_id(reservation_id):
        raise _response_error()

    request: LoanRequest = {
        "id": value["id"],
        "usuario_id": value["usuario_id"],
        "titulo_id": value["titulo_id"],
        "estado": value["estado"],
    }
    for field in ("solicitada_em", "reserva_id", "atendida_em"):
        if field in value:
            request[field] = value[field]
    return request


def _parse_reservation(value: object) -> Reservation:
    if (
        not isinstance(value, dict)
        or not _positive_id(value.get("id"))
        or not _positive_id(value.get("usuario_id"))
        or not _positive_id(value.get("titulo_id"))
        or not _timestamp(value.get("criada_em"))
        or not isinstance(value.get("estado"), str)
        or value["estado"] not in {"aguardando", "ofertada", "retirada", "expirada"}
        or not _timestamp(value.get("ofertada_em"), nullable=True)
        or not _timestamp(value.get("expira_em"), nullable=True)
        or "expira_em_sao_paulo" not in value
        or not (
            value.get("expira_em_sao_paulo") is None
            or _sao_paulo_timestamp(value.get("expira_em_sao_paulo"))
        )
    ):
        raise _response_error()

    copy_id = value.get("exemplar_id")
    if copy_id is not None and not _positive_id(copy_id):
        raise _response_error()
    return {
        "id": value["id"],
        "usuario_id": value["usuario_id"],
        "titulo_id": value["titulo_id"],
        "criada_em": value["criada_em"],
        "estado": value["estado"],
        "exemplar_id": copy_id,
        "ofertada_em": value.get("ofertada_em"),
        "expira_em": value.get("expira_em"),
        "expira_em_sao_paulo": value.get("expira_em_sao_paulo"),
    }


def _sao_paulo_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    return True


async def _list_personal_records(
    path: str,
    parser: Callable[[object], Record],
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[Record]:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", path, token=token)
    records = _response_json(response)
    if not isinstance(records, list):
        raise _response_error()
    return [parser(record) for record in records]


async def list_my_loans(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[Loan]:
    return await _list_personal_records(
        "/minhas/emprestimos",
        _parse_loan,
        token,
        transport=transport,
    )


async def list_my_requests(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[LoanRequest]:
    return await _list_personal_records(
        "/minhas/solicitacoes",
        _parse_request,
        token,
        transport=transport,
    )


async def list_my_reservations(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[Reservation]:
    return await _list_personal_records(
        "/minhas/reservas",
        _parse_reservation,
        token,
        transport=transport,
    )


async def request_title_loan(
    title_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> LoanRequestResult:
    if not _positive_id(title_id):
        raise _response_error()
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "POST",
        "/solicitacoes-emprestimo",
        token=token,
        json={"titulo_id": title_id},
    )
    result = _parse_request(_response_json(response))
    if result["titulo_id"] != title_id:
        raise _response_error()
    return {
        "id": result["id"],
        "titulo_id": result["titulo_id"],
        "estado": result["estado"],
        **(
            {"reserva_id": result["reserva_id"]}
            if "reserva_id" in result
            else {}
        ),
    }

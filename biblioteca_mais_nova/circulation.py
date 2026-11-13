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


class AdminLoan(TypedDict):
    id: int
    usuario_id: int
    usuario_nome: str
    titulo_id: int
    titulo: str
    autores: str
    exemplar_id: int
    retirado_em: str | int | float
    vence_em: str | int | float


class AdminReservation(Reservation):
    usuario_nome: str
    titulo: str


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
        or value["estado"]
        not in {"aguardando", "ofertada", "retirada", "expirada", "recusada"}
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


def _parse_admin_loan(value: object) -> AdminLoan:
    if (
        not isinstance(value, dict)
        or not _positive_id(value.get("id"))
        or not _positive_id(value.get("usuario_id"))
        or not isinstance(value.get("usuario_nome"), str)
        or not value["usuario_nome"].strip()
        or not _positive_id(value.get("titulo_id"))
        or not isinstance(value.get("titulo"), str)
        or not value["titulo"].strip()
        or not isinstance(value.get("autores"), str)
        or not _positive_id(value.get("exemplar_id"))
        or not _timestamp(value.get("retirado_em"))
        or not _timestamp(value.get("vence_em"))
    ):
        raise _response_error()
    return {
        "id": value["id"],
        "usuario_id": value["usuario_id"],
        "usuario_nome": value["usuario_nome"],
        "titulo_id": value["titulo_id"],
        "titulo": value["titulo"],
        "autores": value["autores"],
        "exemplar_id": value["exemplar_id"],
        "retirado_em": value["retirado_em"],
        "vence_em": value["vence_em"],
    }


def _parse_admin_reservation(value: object) -> AdminReservation:
    if not isinstance(value, dict):
        raise _response_error()
    reservation = _parse_reservation(value)
    if (
        not isinstance(value.get("usuario_nome"), str)
        or not value["usuario_nome"].strip()
        or not isinstance(value.get("titulo"), str)
        or not value["titulo"].strip()
    ):
        raise _response_error()
    return {
        **reservation,
        "usuario_nome": value["usuario_nome"],
        "titulo": value["titulo"],
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


async def list_admin_requests(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[LoanRequest]:
    return await _list_personal_records(
        "/admin/solicitacoes",
        _parse_request,
        token,
        transport=transport,
    )


async def list_admin_reservations(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[AdminReservation]:
    return await _list_personal_records(
        "/admin/reservas",
        _parse_admin_reservation,
        token,
        transport=transport,
    )


async def list_admin_loans(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[AdminLoan]:
    return await _list_personal_records(
        "/admin/emprestimos",
        _parse_admin_loan,
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


def _admin_id_path(path: str, record_id: int) -> str:
    if not _positive_id(record_id):
        raise _response_error()
    return path.format(record_id=record_id)


async def _admin_post(
    path: str,
    token: str,
    *,
    body: dict[str, int] | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> object:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("POST", path, token=token, json=body)
    return _response_json(response)


async def register_request_pickup(
    request_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Loan:
    result = await _admin_post(
        _admin_id_path("/admin/solicitacoes/{record_id}/retirada", request_id),
        token,
        transport=transport,
    )
    loan = _parse_loan(result)
    if loan.get("solicitacao_id") not in {None, request_id}:
        raise _response_error()
    return loan


async def refuse_loan_request(
    request_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> LoanRequest:
    result = await _admin_post(
        _admin_id_path("/admin/solicitacoes/{record_id}/recusar", request_id),
        token,
        transport=transport,
    )
    request = _parse_request(result)
    if request["id"] != request_id or request["estado"] != "recusada":
        raise _response_error()
    return request


async def offer_next_reservation(
    title_id: int,
    copy_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    if not _positive_id(title_id) or not _positive_id(copy_id):
        raise _response_error()
    result = await _admin_post(
        "/admin/reservas/ofertar-proxima",
        token,
        body={"titulo_id": title_id, "exemplar_id": copy_id},
        transport=transport,
    )
    if (
        not isinstance(result, dict)
        or not isinstance(result.get("reserva"), dict)
        or not _positive_id(result["reserva"].get("id"))
        or result["reserva"].get("titulo_id") != title_id
        or result["reserva"].get("estado") != "ofertada"
        or not _timestamp(result.get("expira_em_utc"))
        or not _sao_paulo_timestamp(result.get("expira_em_sao_paulo"))
    ):
        raise _response_error()


async def register_reservation_pickup(
    reservation_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Loan:
    result = await _admin_post(
        _admin_id_path("/admin/reservas/{record_id}/retirada", reservation_id),
        token,
        transport=transport,
    )
    return _parse_loan(result)


async def refuse_reservation(
    reservation_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    result = await _admin_post(
        _admin_id_path("/admin/reservas/{record_id}/recusar", reservation_id),
        token,
        transport=transport,
    )
    if (
        not isinstance(result, dict)
        or result.get("id") != reservation_id
        or result.get("estado") != "recusada"
    ):
        raise _response_error()


async def register_loan_return(
    loan_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    result = await _admin_post(
        _admin_id_path("/admin/emprestimos/{record_id}/devolucao", loan_id),
        token,
        transport=transport,
    )
    if not isinstance(result, dict) or not isinstance(result.get("emprestimo"), dict):
        raise _response_error()
    loan = _parse_loan(result["emprestimo"])
    if loan["id"] != loan_id or not _timestamp(loan["devolvido_em"], nullable=True):
        raise _response_error()

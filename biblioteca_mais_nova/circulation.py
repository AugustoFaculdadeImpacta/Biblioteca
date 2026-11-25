"""Operações autenticadas de circulação disponíveis ao estudante."""

from datetime import datetime
from typing import Callable, NotRequired, TypeVar, TypedDict

import httpx

from biblioteca_mais_nova.response_parsing import (
    ParsedRecords,
    parse_optional_xano_id,
    parse_xano_id,
    parse_xano_records,
    parse_xano_timestamp,
)
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    parse_xano_response_json,
    parse_xano_write_response,
    xano_message_with_reference,
    xano_public_error_message,
)


class Loan(TypedDict):
    id: int
    usuario_id: int
    exemplar_id: int
    solicitacao_id: NotRequired[int | None]
    retirado_em: str | None
    vence_em: str | None
    devolvido_em: str | None


class LoanRequest(TypedDict):
    id: int
    usuario_id: int
    titulo_id: int
    solicitada_em: NotRequired[str | None]
    estado: str
    reserva_id: NotRequired[int | None]
    atendida_em: NotRequired[str | None]


class Reservation(TypedDict):
    id: int
    usuario_id: int
    titulo_id: int
    criada_em: str | None
    estado: str
    exemplar_id: int | None
    ofertada_em: str | None
    expira_em: str | None
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
    retirado_em: str | None
    vence_em: str | None


class AdminReservation(Reservation):
    usuario_nome: str
    titulo: str


Record = TypeVar("Record")


def _response_error() -> XanoRequestError:
    return XanoInvalidResponseError()


def _response_json(response: httpx.Response) -> object:
    return parse_xano_response_json(response)


def _timestamp(value: object, *, nullable: bool = False) -> bool:
    try:
        parse_xano_timestamp(value)
    except XanoInvalidResponseError:
        return False
    return True


def _positive_id(value: object) -> bool:
    return type(value) is int and value > 0


def _parse_loan(value: object) -> Loan:
    if (
        not isinstance(value, dict)
        or "retirado_em" not in value
        or "vence_em" not in value
    ):
        raise _response_error()

    loan: Loan = {
        "id": parse_xano_id(value.get("id")),
        "usuario_id": parse_xano_id(value.get("usuario_id")),
        "exemplar_id": parse_xano_id(value.get("exemplar_id")),
        "retirado_em": parse_xano_timestamp(value.get("retirado_em")),
        "vence_em": parse_xano_timestamp(value.get("vence_em")),
        "devolvido_em": parse_xano_timestamp(value.get("devolvido_em")),
    }
    request_id = value.get("solicitacao_id")
    loan["solicitacao_id"] = parse_optional_xano_id(request_id)
    return loan


def _parse_request(value: object) -> LoanRequest:
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("estado"), str)
        or value["estado"] not in {"pendente", "em_reserva", "atendida", "recusada"}
    ):
        raise _response_error()

    request: LoanRequest = {
        "id": parse_xano_id(value.get("id")),
        "usuario_id": parse_xano_id(value.get("usuario_id")),
        "titulo_id": parse_xano_id(value.get("titulo_id")),
        "estado": value["estado"],
        "solicitada_em": parse_xano_timestamp(value.get("solicitada_em")),
        "reserva_id": parse_optional_xano_id(value.get("reserva_id")),
        "atendida_em": parse_xano_timestamp(value.get("atendida_em")),
    }
    return request


def _parse_reservation(value: object) -> Reservation:
    if (
        not isinstance(value, dict)
        or "criada_em" not in value
        or not isinstance(value.get("estado"), str)
        or value["estado"]
        not in {"aguardando", "ofertada", "retirada", "expirada", "recusada"}
    ):
        raise _response_error()

    return {
        "id": parse_xano_id(value.get("id")),
        "usuario_id": parse_xano_id(value.get("usuario_id")),
        "titulo_id": parse_xano_id(value.get("titulo_id")),
        "criada_em": parse_xano_timestamp(value.get("criada_em")),
        "estado": value["estado"],
        "exemplar_id": parse_optional_xano_id(value.get("exemplar_id")),
        "ofertada_em": parse_xano_timestamp(value.get("ofertada_em")),
        "expira_em": parse_xano_timestamp(value.get("expira_em")),
        "expira_em_sao_paulo": _parse_local_timestamp(
            value.get("expira_em_sao_paulo")
        ),
    }


def _parse_admin_loan(value: object) -> AdminLoan:
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("usuario_nome"), str)
        or not value["usuario_nome"].strip()
        or not isinstance(value.get("titulo"), str)
        or not value["titulo"].strip()
        or not isinstance(value.get("autores"), str)
        or "retirado_em" not in value
        or "vence_em" not in value
    ):
        raise _response_error()
    return {
        "id": parse_xano_id(value.get("id")),
        "usuario_id": parse_xano_id(value.get("usuario_id")),
        "usuario_nome": value["usuario_nome"],
        "titulo_id": parse_xano_id(value.get("titulo_id")),
        "titulo": value["titulo"],
        "autores": value["autores"],
        "exemplar_id": parse_xano_id(value.get("exemplar_id")),
        "retirado_em": parse_xano_timestamp(value.get("retirado_em")),
        "vence_em": parse_xano_timestamp(value.get("vence_em")),
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


def _parse_local_timestamp(value: object) -> str | None:
    if value is None or (type(value) in {int, float} and value == 0):
        return None
    if isinstance(value, str) and _sao_paulo_timestamp(value):
        return value
    return parse_xano_timestamp(value)


async def _list_personal_records(
    path: str,
    parser: Callable[[object], Record],
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ParsedRecords[Record]:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", path, token=token)
    return parse_xano_records(_response_json(response), parser)


async def list_my_loans(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ParsedRecords[Loan]:
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
) -> ParsedRecords[LoanRequest]:
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
) -> ParsedRecords[Reservation]:
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
) -> ParsedRecords[LoanRequest]:
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
) -> ParsedRecords[AdminReservation]:
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
) -> ParsedRecords[AdminLoan]:
    return await _list_personal_records(
        "/admin/emprestimos",
        _parse_admin_loan,
        token,
        transport=transport,
    )


def reservation_request_error_message(error: Exception) -> str:
    common_message = xano_public_error_message(error)
    if common_message is not None:
        return common_message
    if isinstance(error, XanoResponseError):
        if error.status_code == 401:
            message = "[RES-401] Sua sessão expirou, entre de novo"
            if error.public_detail:
                message = f"{message} — {error.public_detail}"
            return xano_message_with_reference(
                message,
                error,
            )
        if error.status_code == 403:
            message = "[RES-403] Seu perfil não pode reservar"
            if error.public_detail:
                message = f"{message} — {error.public_detail}"
            return xano_message_with_reference(
                message,
                error,
            )
        if error.status_code == 404:
            message = "[RES-404] Este recurso ainda não está disponível no servidor"
            if error.public_detail:
                message = f"{message} — {error.public_detail}"
            return xano_message_with_reference(
                message,
                error,
            )
        if error.status_code == 409:
            if error.public_detail:
                return xano_message_with_reference(
                    f"[RES-409] {error.public_detail}",
                    error,
                )
            return xano_message_with_reference(
                "[RES-409] Há limite ou duplicidade nesta reserva",
                error,
            )
        if error.status_code >= 500:
            return xano_message_with_reference(
                "[RES-5XX] O servidor teve um problema (código 5xx)",
                error,
            )
        if error.public_detail:
            return xano_message_with_reference(
                f"[RES-{error.status_code}] {error.public_detail}",
                error,
            )
        return xano_message_with_reference(
            f"[RES-{error.status_code}] Não foi possível confirmar a reserva",
            error,
        )
    if isinstance(error, XanoInvalidResponseError):
        return xano_message_with_reference(
            "[RES-INVALID] Não foi possível confirmar a reserva",
            error,
        )
    if isinstance(error, XanoRequestError):
        return xano_message_with_reference(
            "[RES-NORESPONSE] Não foi possível confirmar a reserva. "
            "Confira Minhas reservas antes de tentar de novo.",
            error,
        )
    return "Erro — Não foi possível confirmar a reserva"


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
    def parse_result(value: object) -> LoanRequestResult:
        result = _parse_request(value)
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

    return parse_xano_write_response(response, parse_result)


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
) -> httpx.Response:
    client = XanoClient.from_environment(transport=transport)
    return await client.request("POST", path, token=token, json=body)


async def register_request_pickup(
    request_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Loan:
    response = await _admin_post(
        _admin_id_path("/admin/solicitacoes/{record_id}/retirada", request_id),
        token,
        transport=transport,
    )

    def parse_result(value: object) -> Loan:
        loan = _parse_loan(value)
        if loan.get("solicitacao_id") not in {None, request_id}:
            raise _response_error()
        return loan

    return parse_xano_write_response(response, parse_result)


async def refuse_loan_request(
    request_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> LoanRequest:
    response = await _admin_post(
        _admin_id_path("/admin/solicitacoes/{record_id}/recusar", request_id),
        token,
        transport=transport,
    )

    def parse_result(value: object) -> LoanRequest:
        request = _parse_request(value)
        if request["id"] != request_id or request["estado"] != "recusada":
            raise _response_error()
        return request

    return parse_xano_write_response(response, parse_result)


async def offer_next_reservation(
    title_id: int,
    copy_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    if not _positive_id(title_id) or not _positive_id(copy_id):
        raise _response_error()
    response = await _admin_post(
        "/admin/reservas/ofertar-proxima",
        token,
        body={"titulo_id": title_id, "exemplar_id": copy_id},
        transport=transport,
    )

    def parse_result(result: object) -> None:
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

    parse_xano_write_response(response, parse_result)


async def register_reservation_pickup(
    reservation_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Loan:
    response = await _admin_post(
        _admin_id_path("/admin/reservas/{record_id}/retirada", reservation_id),
        token,
        transport=transport,
    )
    return parse_xano_write_response(response, _parse_loan)


async def refuse_reservation(
    reservation_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    response = await _admin_post(
        _admin_id_path("/admin/reservas/{record_id}/recusar", reservation_id),
        token,
        transport=transport,
    )

    def parse_result(result: object) -> None:
        if (
            not isinstance(result, dict)
            or result.get("id") != reservation_id
            or result.get("estado") != "recusada"
        ):
            raise _response_error()

    parse_xano_write_response(response, parse_result)


async def register_loan_return(
    loan_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    response = await _admin_post(
        _admin_id_path("/admin/emprestimos/{record_id}/devolucao", loan_id),
        token,
        transport=transport,
    )

    def parse_result(result: object) -> None:
        if not isinstance(result, dict) or not isinstance(
            result.get("emprestimo"),
            dict,
        ):
            raise _response_error()
        loan = _parse_loan(result["emprestimo"])
        if loan["id"] != loan_id or not _timestamp(loan["devolvido_em"]):
            raise _response_error()

    parse_xano_write_response(response, parse_result)

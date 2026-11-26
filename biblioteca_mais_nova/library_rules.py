"""Leitura, validação e gravação das regras da biblioteca."""

from collections.abc import Mapping
from typing import TypedDict

import httpx

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoInvalidResponseError,
    parse_xano_response_json,
    parse_xano_write_response,
)


class LibraryRulesPayload(TypedDict):
    limite_emprestimos_ativos: int
    limite_pedidos_em_aberto: int
    permitir_pedido_com_reserva_ativa: bool
    bloquear_com_atraso: bool
    exigir_autorizacao_bibliotecaria: bool
    prazo_emprestimo_dias: int
    prazo_retirada_horas: int


class LibraryRules(LibraryRulesPayload, total=False):
    atualizado_em: str | None
    atualizado_por: str | None


class LibraryRulesValidationError(ValueError):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


def _integer(
    rules: Mapping[str, object],
    field: str,
    minimum: int,
    maximum: int,
) -> int:
    value = rules.get(field)
    if type(value) is not int or not minimum <= value <= maximum:
        raise LibraryRulesValidationError(
            field,
            f"{field} deve ser um número inteiro entre {minimum} e {maximum}.",
        )
    return value


def _boolean(rules: Mapping[str, object], field: str) -> bool:
    value = rules.get(field)
    if type(value) is not bool:
        raise LibraryRulesValidationError(
            field,
            f"{field} deve ser verdadeiro ou falso.",
        )
    return value


def validate_library_rules(
    rules: Mapping[str, object],
) -> LibraryRulesPayload:
    return {
        "limite_emprestimos_ativos": _integer(
            rules,
            "limite_emprestimos_ativos",
            1,
            20,
        ),
        "limite_pedidos_em_aberto": _integer(
            rules,
            "limite_pedidos_em_aberto",
            1,
            20,
        ),
        "permitir_pedido_com_reserva_ativa": _boolean(
            rules,
            "permitir_pedido_com_reserva_ativa",
        ),
        "bloquear_com_atraso": _boolean(rules, "bloquear_com_atraso"),
        "exigir_autorizacao_bibliotecaria": _boolean(
            rules,
            "exigir_autorizacao_bibliotecaria",
        ),
        "prazo_emprestimo_dias": _integer(
            rules,
            "prazo_emprestimo_dias",
            1,
            60,
        ),
        "prazo_retirada_horas": _integer(
            rules,
            "prazo_retirada_horas",
            1,
            168,
        ),
    }


def _parse_library_rules(value: object) -> LibraryRules:
    if not isinstance(value, dict):
        raise XanoInvalidResponseError(
            field="resposta",
            reason="esperado objeto com as regras da biblioteca",
        )
    try:
        payload = validate_library_rules(value)
    except LibraryRulesValidationError as error:
        raise XanoInvalidResponseError(
            field=error.field,
            reason=str(error),
        ) from None

    result: LibraryRules = {
        "limite_emprestimos_ativos": payload["limite_emprestimos_ativos"],
        "limite_pedidos_em_aberto": payload["limite_pedidos_em_aberto"],
        "permitir_pedido_com_reserva_ativa": payload[
            "permitir_pedido_com_reserva_ativa"
        ],
        "bloquear_com_atraso": payload["bloquear_com_atraso"],
        "exigir_autorizacao_bibliotecaria": payload[
            "exigir_autorizacao_bibliotecaria"
        ],
        "prazo_emprestimo_dias": payload["prazo_emprestimo_dias"],
        "prazo_retirada_horas": payload["prazo_retirada_horas"],
    }
    for field in ("atualizado_em", "atualizado_por"):
        metadata = value.get(field)
        if metadata is not None and not isinstance(metadata, str):
            raise XanoInvalidResponseError(
                field=field,
                reason="esperado texto ou null",
            )
        if field in value:
            result[field] = metadata
    return result


async def get_library_rules(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> LibraryRules:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "GET",
        "/configuracoes",
        token=token,
    )
    return _parse_library_rules(parse_xano_response_json(response))


async def update_library_rules(
    rules: Mapping[str, object],
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> LibraryRules:
    payload = validate_library_rules(rules)
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "PUT",
        "/admin/configuracoes",
        token=token,
        json=payload,
    )
    return parse_xano_write_response(response, _parse_library_rules)

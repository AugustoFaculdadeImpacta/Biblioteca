"""Normalização compartilhada de respostas de listas do Xano."""

import re
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from typing import Generic, TypeVar

from biblioteca_mais_nova.xano_client import XanoInvalidResponseError
from biblioteca_mais_nova.xano_client import (
    adiar_log_falha_xano,
    registrar_falha_parse_xano,
)


_ENVELOPE_KEYS = ("items", "result", "data", "results", "records")
_Record = TypeVar("_Record")


class ParsedRecords(list[_Record], Generic[_Record]):
    def __init__(
        self,
        records: Iterable[_Record] = (),
        *,
        skipped_count: int = 0,
    ) -> None:
        super().__init__(records)
        self.skipped_count = skipped_count


def parse_xano_id(value: object) -> int:
    if type(value) is int and value > 0:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value.strip()):
        parsed = int(value.strip())
        if parsed > 0:
            return parsed
    raise XanoInvalidResponseError()


def parse_optional_xano_id(value: object) -> int | None:
    if value is None or type(value) is int and value == 0:
        return None
    if isinstance(value, str) and value.strip() == "0":
        return None
    return parse_xano_id(value)


def parse_xano_timestamp(value: object) -> str | None:
    if value is None or (type(value) in {int, float} and value == 0):
        return None
    if type(value) in {int, float}:
        timestamp = value / 1000 if abs(value) >= 100_000_000_000 else value
        try:
            return datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            ).isoformat()
        except (OverflowError, OSError, ValueError):
            raise XanoInvalidResponseError() from None
    if isinstance(value, str) and value:
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise XanoInvalidResponseError() from None
        return value
    raise XanoInvalidResponseError()


def parse_xano_bool(value: object) -> bool:
    if type(value) is bool:
        return value
    if type(value) is int and value in {0, 1}:
        return value == 1
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "false"}:
            return normalized == "true"
    raise XanoInvalidResponseError()


def parse_optional_xano_text(value: object) -> str | None:
    if value is None or isinstance(value, str):
        return value
    raise XanoInvalidResponseError()


def parse_xano_records(
    payload: object,
    parser: Callable[[object], _Record],
    *,
    identifier: Callable[[dict[str, object]], object] | None = None,
) -> ParsedRecords[_Record]:
    records = _list_payload(payload)
    parsed: list[_Record] = []
    skipped_count = 0
    first_failure: tuple[int, XanoInvalidResponseError] | None = None

    for index, record in enumerate(records):
        error: XanoInvalidResponseError | None = None
        fatal = False
        with adiar_log_falha_xano():
            if not isinstance(record, dict):
                error = XanoInvalidResponseError(
                    field="registro",
                    reason="o valor precisa ser um objeto",
                )
                fatal = True
            elif identifier is None and "id" not in record:
                error = XanoInvalidResponseError(
                    field="id",
                    reason="identificador obrigatório ausente",
                )
                fatal = True
            else:
                record_identifier = (
                    record.get("id")
                    if identifier is None
                    else identifier(record)
                )
                try:
                    parse_xano_id(record_identifier)
                except XanoInvalidResponseError:
                    field = "id"
                    if identifier is not None and record_identifier is None:
                        error = XanoInvalidResponseError(
                            field=field,
                            reason="identificador obrigatório ausente",
                        )
                        fatal = True
                    else:
                        error = XanoInvalidResponseError(
                            field=field,
                            reason="o identificador precisa ser inteiro positivo",
                        )
                if error is None:
                    try:
                        parsed.append(parser(record))
                    except XanoInvalidResponseError as parser_error:
                        error = parser_error

        if error is not None:
            if first_failure is None:
                first_failure = (index, error)
            if fatal:
                error.reference = registrar_falha_parse_xano(error, index)
                raise error
            skipped_count += 1

    if first_failure is not None:
        registrar_falha_parse_xano(
            first_failure[1],
            first_failure[0],
        )

    return ParsedRecords(parsed, skipped_count=skipped_count)


def extract_xano_list(payload: object) -> list[object]:
    return _list_payload(payload)


def _list_payload(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in _ENVELOPE_KEYS:
            records = payload.get(key)
            if isinstance(records, list):
                return records
    raise XanoInvalidResponseError()

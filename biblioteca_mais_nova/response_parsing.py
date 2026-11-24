"""Normalização compartilhada de respostas de listas do Xano."""

import re
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from typing import Generic, TypeVar

from biblioteca_mais_nova.xano_client import XanoInvalidResponseError


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
    return None if value is None else parse_xano_id(value)


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

    for record in records:
        if not isinstance(record, dict):
            raise XanoInvalidResponseError()
        if identifier is None and "id" not in record:
            raise XanoInvalidResponseError()
        record_identifier = (
            record.get("id") if identifier is None else identifier(record)
        )
        try:
            parse_xano_id(record_identifier)
        except XanoInvalidResponseError:
            if record_identifier is None and identifier is not None:
                raise
            skipped_count += 1
            continue
        try:
            parsed.append(parser(record))
        except XanoInvalidResponseError:
            skipped_count += 1

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

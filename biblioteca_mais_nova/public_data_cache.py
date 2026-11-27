"""Cópias temporárias de dados públicos para uso durante falhas de rede."""

import copy
import json
import logging
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_LOGGER = logging.getLogger("biblioteca.cache_publico")
_VERSION = 1
_MAX_AGE_SECONDS = 24 * 60 * 60
_LOCK = threading.RLock()
_MEMORY: dict[tuple[str, str], tuple[float, Any]] = {}
_clock = time.time


@dataclass(frozen=True)
class PublicSnapshot:
    data: Any
    updated_at: float


def public_snapshot_path() -> Path:
    return Path(tempfile.gettempdir()) / "biblioteca-public-cache-v1.json"


def _path_key(path: Path) -> str:
    return str(path.resolve())


def _read_document(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"version": _VERSION, "entries": {}}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        _LOGGER.warning("Não foi possível ler a cópia temporária pública.")
        return {"version": _VERSION, "entries": {}}
    if (
        not isinstance(document, dict)
        or document.get("version") != _VERSION
        or not isinstance(document.get("entries"), dict)
    ):
        _LOGGER.warning("A cópia temporária pública tem formato inválido.")
        return {"version": _VERSION, "entries": {}}
    return document


def load_public_snapshot(
    key: str,
    *,
    now: float | None = None,
    path: Path | None = None,
) -> PublicSnapshot | None:
    target = path or public_snapshot_path()
    current_time = _clock() if now is None else now
    cache_key = (_path_key(target), key)
    with _LOCK:
        memory_value = _MEMORY.get(cache_key)
        if memory_value is not None:
            updated_at, data = memory_value
            age = current_time - updated_at
            if 0 <= age <= _MAX_AGE_SECONDS:
                return PublicSnapshot(copy.deepcopy(data), updated_at)
            _MEMORY.pop(cache_key, None)

        entry = _read_document(target)["entries"].get(key)
        if not isinstance(entry, dict):
            return None
        updated_at = entry.get("updated_at")
        data = entry.get("data")
        if (
            type(updated_at) not in {int, float}
            or current_time - updated_at < 0
            or current_time - updated_at > _MAX_AGE_SECONDS
            or "data" not in entry
        ):
            return None
        _MEMORY[cache_key] = (float(updated_at), copy.deepcopy(data))
        return PublicSnapshot(copy.deepcopy(data), float(updated_at))


def save_public_snapshot(
    key: str,
    data: Any,
    *,
    now: float | None = None,
    path: Path | None = None,
) -> PublicSnapshot:
    target = path or public_snapshot_path()
    current_time = _clock() if now is None else now
    encoded_data = json.dumps(data, ensure_ascii=False)
    cache_key = (_path_key(target), key)
    with _LOCK:
        document = _read_document(target)
        document["entries"][key] = {
            "updated_at": current_time,
            "data": json.loads(encoded_data),
        }
        temporary = target.with_name(f"{target.name}.tmp")
        try:
            temporary.write_text(
                json.dumps(document, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            temporary.replace(target)
        except OSError:
            _LOGGER.warning("Não foi possível persistir a cópia temporária pública.")
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                _LOGGER.warning("Não foi possível limpar o arquivo temporário da cópia.")
        _MEMORY[cache_key] = (current_time, json.loads(encoded_data))
    return PublicSnapshot(copy.deepcopy(data), current_time)


def clear_public_snapshots_for_tests(path: Path | None = None) -> None:
    with _LOCK:
        if path is None:
            _MEMORY.clear()
            return
        prefix = _path_key(path)
        for key in tuple(_MEMORY):
            if key[0] == prefix:
                del _MEMORY[key]

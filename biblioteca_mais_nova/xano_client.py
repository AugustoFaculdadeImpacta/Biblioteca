"""Cliente HTTP do Xano executado exclusivamente no backend."""

import asyncio
import concurrent.futures
import contextvars
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import threading
import time
import traceback
import unicodedata
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar
from urllib.parse import urlsplit
from weakref import WeakKeyDictionary

import httpx
from dotenv import load_dotenv


_LOGGER = logging.getLogger("biblioteca.xano")
_MAX_RETRIES = 3
_RETRY_DELAYS = (0.5, 1.5, 3.0)
_RETRYABLE_STATUSES = {429, 502, 503, 504}
_AUTHENTICATED_LIST_PATHS = frozenset(
    {
        "/minhas/emprestimos",
        "/minhas/solicitacoes",
        "/minhas/reservas",
    }
)
_AUTHENTICATED_GET_CACHE_TTL_SECONDS = 20.0
_AUTHENTICATED_CACHE_SECRET = os.urandom(32)
_AUTHENTICATED_CACHE_LOCK = threading.RLock()
_AUTHENTICATED_GET_CACHE: dict[
    tuple[str, str, str, int, int],
    tuple[float, httpx.Response, httpx.AsyncBaseTransport | None],
] = {}
_AUTHENTICATED_GET_INFLIGHT: dict[
    tuple[str, str, str, int, int],
    concurrent.futures.Future[httpx.Response],
] = {}
_AUTHENTICATED_CACHE_GENERATIONS: dict[tuple[str, str], int] = {}
_cache_clock = time.monotonic
_sleep = asyncio.sleep
_PAGE_DIAGNOSTICS: contextvars.ContextVar["_PageDiagnostics | None"] = (
    contextvars.ContextVar("xano_page_diagnostics", default=None)
)
_LAST_RESPONSE: contextvars.ContextVar[httpx.Response | None] = contextvars.ContextVar(
    "xano_last_response", default=None
)
_EVENT_CONTEXT: contextvars.ContextVar[tuple[str, str] | None] = contextvars.ContextVar(
    "xano_event_context", default=None
)
_DEFER_FAILURE_LOG: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "xano_defer_failure_log",
    default=False,
)
_SEMAPHORES: WeakKeyDictionary[
    asyncio.AbstractEventLoop, asyncio.Semaphore
] = WeakKeyDictionary()
_SEMAPHORES_LOCK = threading.Lock()
_P = ParamSpec("_P")
_R = TypeVar("_R")


def _authenticated_cache_scope(
    base_url: httpx.URL,
    token: str,
) -> tuple[str, str]:
    host = f"{base_url.scheme}://{base_url.host}:{base_url.port or ''}"
    token_key = hmac.new(
        _AUTHENTICATED_CACHE_SECRET,
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return host, token_key


def _invalidate_authenticated_get_cache(scope: tuple[str, str]) -> None:
    with _AUTHENTICATED_CACHE_LOCK:
        _AUTHENTICATED_CACHE_GENERATIONS[scope] = (
            _AUTHENTICATED_CACHE_GENERATIONS.get(scope, 0) + 1
        )
        for key in tuple(_AUTHENTICATED_GET_CACHE):
            if key[:2] == scope:
                del _AUTHENTICATED_GET_CACHE[key]


def limpar_cache_autenticado() -> None:
    """Limpa o cache pessoal de teste ou encerramento de sessão."""
    with _AUTHENTICATED_CACHE_LOCK:
        _AUTHENTICATED_GET_CACHE.clear()
        _AUTHENTICATED_GET_INFLIGHT.clear()
        _AUTHENTICATED_CACHE_GENERATIONS.clear()


_xano_limiter_clock = time.monotonic
_XANO_LIMIT_LOCK = threading.RLock()
_XANO_REQUEST_TIMES: dict[str, list[float]] = {}
_XANO_PAUSE_UNTIL: dict[str, float] = {}
_XANO_WAITERS: dict[str, list[tuple[int, int, asyncio.Future[None]]]] = {}
_XANO_WAITER_SEQUENCE = 0


def _xano_limit_config() -> tuple[int, float]:
    try:
        limit = int(os.environ.get("BIBLIOTECA_XANO_LIMITE_REQ", "8"))
    except ValueError:
        limit = 8
    try:
        window = float(os.environ.get("BIBLIOTECA_XANO_JANELA_S", "20"))
    except ValueError:
        window = 20.0
    return max(limit, 1), max(window, 0.1)


def _limpar_limitador_xano() -> None:
    with _XANO_LIMIT_LOCK:
        _XANO_REQUEST_TIMES.clear()
        _XANO_PAUSE_UNTIL.clear()
        _XANO_WAITERS.clear()


def _xano_host(base_url: httpx.URL) -> str:
    return f"{base_url.host}:{base_url.port or (443 if base_url.scheme == 'https' else 80)}"


def _xano_priority(method: str, path: str) -> int:
    if method.upper() in {"POST", "PATCH", "DELETE"}:
        return 300
    event_context = _EVENT_CONTEXT.get()
    if event_context is not None:
        return 200
    if path.startswith("/catalogo/capa") or "/resumo" in path:
        return 100
    return 150


def _drain_xano_waiters(host: str) -> None:
    now = _xano_limiter_clock()
    limit, window = _xano_limit_config()
    with _XANO_LIMIT_LOCK:
        times = _XANO_REQUEST_TIMES.setdefault(host, [])
        cutoff = now - window
        while times and times[0] <= cutoff:
            times.pop(0)
        pause_until = _XANO_PAUSE_UNTIL.get(host, 0.0)
        if pause_until > now:
            return
        waiters = _XANO_WAITERS.setdefault(host, [])
        waiters[:] = [
            waiter for waiter in waiters
            if not waiter[2].done()
        ]
        waiters.sort(key=lambda waiter: (-waiter[0], waiter[1]))
        while len(times) < limit and waiters:
            _, _, future = waiters.pop(0)
            times.append(now)
            if not future.done():
                future.set_result(None)


def _pausar_xano(host: str, seconds: float) -> None:
    until = _xano_limiter_clock() + max(seconds, 0.0) + 1.0
    with _XANO_LIMIT_LOCK:
        current = _XANO_PAUSE_UNTIL.get(host, 0.0)
        _XANO_PAUSE_UNTIL[host] = max(current, until)


async def _adquirir_slot_xano(
    host: str,
    priority: int,
) -> bool:
    global _XANO_WAITER_SEQUENCE
    loop = asyncio.get_running_loop()
    future: asyncio.Future[None] = loop.create_future()
    started = _xano_limiter_clock()
    with _XANO_LIMIT_LOCK:
        _XANO_WAITER_SEQUENCE += 1
        sequence = _XANO_WAITER_SEQUENCE
        _XANO_WAITERS.setdefault(host, []).append(
            (priority, sequence, future)
        )
    _drain_xano_waiters(host)
    await asyncio.sleep(0)
    try:
        while not future.done():
            await _sleep(0.05)
            _drain_xano_waiters(host)
            if not future.done() and _xano_limiter_clock() - started >= 25.0:
                return False
    except asyncio.TimeoutError:
        _drain_xano_waiters(host)
        if _xano_limiter_clock() - started >= 25.0:
            with _XANO_LIMIT_LOCK:
                waiters = _XANO_WAITERS.get(host, [])
                waiters[:] = [
                    waiter for waiter in waiters
                    if waiter[2] is not future
                ]
            return False
    return True


async def _cached_authenticated_get(
    scope: tuple[str, str],
    path: str,
    transport_id: int,
    transport: httpx.AsyncBaseTransport | None,
    request: Callable[[], Awaitable[httpx.Response]],
) -> httpx.Response:
    with _AUTHENTICATED_CACHE_LOCK:
        generation = _AUTHENTICATED_CACHE_GENERATIONS.get(scope, 0)
        key = (*scope, path, transport_id, generation)
        now = _cache_clock()
        for expired_key, value in tuple(_AUTHENTICATED_GET_CACHE.items()):
            if value[0] <= now:
                del _AUTHENTICATED_GET_CACHE[expired_key]
        cached = _AUTHENTICATED_GET_CACHE.get(key)
        if cached is not None:
            if cached[0] > now:
                return cached[1]
            del _AUTHENTICATED_GET_CACHE[key]

        shared = _AUTHENTICATED_GET_INFLIGHT.get(key)
        is_leader = shared is None
        if shared is None:
            shared = concurrent.futures.Future()
            _AUTHENTICATED_GET_INFLIGHT[key] = shared

    if not is_leader:
        return await asyncio.shield(asyncio.wrap_future(shared))

    try:
        response = await request()
    except BaseException as error:
        with _AUTHENTICATED_CACHE_LOCK:
            if _AUTHENTICATED_GET_INFLIGHT.get(key) is shared:
                del _AUTHENTICATED_GET_INFLIGHT[key]
            shared.set_exception(error)
        raise

    with _AUTHENTICATED_CACHE_LOCK:
        if _AUTHENTICATED_GET_INFLIGHT.get(key) is shared:
            del _AUTHENTICATED_GET_INFLIGHT[key]
        if (
            _AUTHENTICATED_CACHE_GENERATIONS.get(scope, 0) == generation
            and response.is_success
        ):
            _AUTHENTICATED_GET_CACHE[key] = (
                _cache_clock() + _AUTHENTICATED_GET_CACHE_TTL_SECONDS,
                response,
                transport,
            )
        shared.set_result(response)
    return response


SAFE_ERROR_MESSAGES = {
    "Este e-mail já está cadastrado.": (
        "Este e-mail já está cadastrado. Tente entrar com sua conta."
    ),
    "Solicitacao duplicada. Consulte Minha biblioteca.": (
        "Você já tem uma solicitação ou reserva ativa para este título. "
        "Consulte Minha biblioteca."
    ),
    "Já existe solicitação ativa para este título.": (
        "Você já tem uma solicitação ativa para este título. "
        "Consulte Minha biblioteca."
    ),
    "Já existe reserva ativa para este título.": (
        "Você já tem uma reserva ativa para este título. "
        "Consulte Minha biblioteca."
    ),
    "Titulo nao encontrado.": "Este título não foi encontrado no catálogo.",
    "Conta desativada.": (
        "A conta está desativada. Procure a administração da biblioteca."
    ),
    "A desativacao foi recusada: ha emprestimo ativo.": (
        "O título não pode ser desativado enquanto houver empréstimo ativo."
    ),
    "A desativacao foi recusada: ha reserva ativa.": (
        "O título não pode ser desativado enquanto houver reserva ativa."
    ),
    "Estudante possui emprestimo atrasado.": (
        "A reserva foi recusada porque o estudante possui empréstimo atrasado."
    ),
    "Estudante ja possui o titulo emprestado.": (
        "A reserva foi recusada porque o estudante já está com esse título."
    ),
    "Estudante ja possui reserva ativa para este titulo.": (
        "O estudante já possui uma reserva ativa para esse título."
    ),
    "Titulo inativo nao aceita novas reservas.": (
        "Não é possível reservar um título desativado."
    ),
    "Estudante nao encontrado ou inativo.": (
        "Estudante não encontrado ou com conta desativada."
    ),
}


class XanoConfigurationError(ValueError):
    """Configuração ausente ou inválida para acessar o Xano."""

    def __init__(self, message: str) -> None:
        self.reference = _emit_failure(
            method="CONFIG",
            path="(configuração Xano)",
            status="sem_resposta",
            duration_ms=0,
            response=None,
            request=None,
            result="configuração indisponível",
        )
        super().__init__(message)


class XanoRequestError(RuntimeError):
    """Falha sanitizada ao acessar o Xano."""

    def __init__(self, message: str, *, reference: str | None = None) -> None:
        self.reference = reference
        super().__init__(message)


class XanoTimeoutError(XanoRequestError):
    """Tempo limite excedido ao acessar o Xano."""


class XanoInvalidResponseError(XanoRequestError):
    """Resposta inválida retornada pelo Xano."""

    def __init__(
        self,
        message: str = "O Xano respondeu em formato inesperado.",
        *,
        reference: str | None = None,
        field: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.field = field
        self.reason = reason or message
        if not _DEFER_FAILURE_LOG.get():
            _record_failure()
        response = _LAST_RESPONSE.get()
        if (
            reference is None
            and response is not None
            and not _DEFER_FAILURE_LOG.get()
        ):
            reference = _log_response_failure(
                response,
                _invalid_response_result(self, 0),
            )
        super().__init__(message, reference=reference)


class XanoWriteSucceededWithUnreadableResponse(Exception):
    """Escrita 2xx concluída cujo corpo não pôde ser interpretado."""

    def __init__(self, *, reference: str | None = None) -> None:
        self.reference = reference
        super().__init__()


class XanoNonJsonResponseError(XanoInvalidResponseError):
    """Resposta que não contém JSON quando o contrato exige JSON."""

    def __init__(
        self,
        status_code: int,
        *,
        reference: str | None = None,
    ) -> None:
        self.status_code = status_code
        super().__init__(
            "O Xano devolveu uma página de erro.",
            reference=reference,
        )


class XanoResponseError(XanoRequestError):
    """Resposta HTTP de erro retornada pelo Xano."""

    def __init__(
        self,
        status_code: int,
        public_detail: str | None = None,
        *,
        non_json_response: bool = False,
        reference: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.public_detail = public_detail
        self.non_json_response = non_json_response
        super().__init__(
            f"O serviço Xano retornou um erro HTTP {status_code}.",
            reference=reference,
        )


@contextmanager
def contexto_evento_xano(action: str, profile: str) -> Generator[None, None, None]:
    token = _EVENT_CONTEXT.set((action, profile))
    try:
        yield
    finally:
        _EVENT_CONTEXT.reset(token)


@contextmanager
def adiar_log_falha_xano() -> Generator[None, None, None]:
    token = _DEFER_FAILURE_LOG.set(True)
    try:
        yield
    finally:
        _DEFER_FAILURE_LOG.reset(token)


def _new_reference() -> str:
    return os.urandom(4).hex()[:5].upper()


def _sanitize_diagnostic(value: str) -> str:
    value = re.sub(r"https?://[^\s\"'<>]+", "[URL omitida]", value)
    value = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [omitido]", value)
    value = re.sub(
        r"(?i)(authorization\s*[:=]\s*)[^\s,;\"']+",
        r"\1[omitido]",
        value,
    )
    value = re.sub(
        r"(?i)([\"']?(?:access_token|refresh_token|token|password|senha|"
        r"password_hash|authorization)[\"']?\s*[:=]\s*[\"']?)[^\"'\s,}]+",
        r"\1[omitido]",
        value,
    )
    value = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[e-mail omitido]",
        value,
    )
    return value


def _request_action_profile(
    method: str,
    path: str,
    request: httpx.Request | None = None,
) -> tuple[str, str]:
    context = _EVENT_CONTEXT.get()
    if context is not None:
        return context

    sent = _request_json(request)
    if method == "POST" and path == "/solicitacoes-emprestimo":
        return "reservar_livro", "estudante"
    if method == "PATCH" and re.fullmatch(r"/catalogo/titulos/\d+", path):
        if sent.get("ativo") is False:
            return "desativar_titulo", "bibliotecario"
        return "atualizar_titulo", "bibliotecario"
    if path.startswith("/minhas/") or path == "/solicitacoes-emprestimo":
        return f"ler_{path.rsplit('/', 1)[-1]}", "estudante"
    if path.startswith("/admin/"):
        return f"{method.lower()}_{path.strip('/').replace('/', '_')}", "bibliotecario/admin"
    return f"{method.lower()}_{path.strip('/').replace('/', '_') or 'xano'}", "não identificado"


def _request_json(request: httpx.Request | None) -> dict[str, object]:
    if request is None:
        return {}
    try:
        data = json.loads(request.content)
    except (UnicodeDecodeError, json.JSONDecodeError, RuntimeError):
        return {}
    return data if isinstance(data, dict) else {}


def _sent_keys(request: httpx.Request | None) -> str:
    payload = _request_json(request)
    if not payload:
        return "nenhum"
    keys = sorted(str(key) for key in payload)
    if type(payload.get("ativo")) is bool:
        keys = [key for key in keys if key != "ativo"]
        keys.append(f"ativo={str(payload['ativo']).lower()}")
    return ", ".join(keys)


def _response_details(response: httpx.Response | None) -> tuple[str, str, str, str]:
    if response is None:
        return "", "nenhum", "nenhuma", ""
    raw = response.content.decode("utf-8", errors="replace")
    try:
        body = json.loads(raw) if raw else None
    except (json.JSONDecodeError, UnicodeDecodeError):
        body = None

    if isinstance(body, list):
        top = "lista"
        keys: list[str] = []
    elif isinstance(body, dict):
        top = "objeto"
        keys = [str(key) for key in list(body)[:20]]
    else:
        top = "nenhum"
        keys = []

    xano_message = ""
    if isinstance(body, dict) and "code" in body and "message" in body:
        xano_message = (
            "Xano disse: code="
            + _sanitize_diagnostic(str(body["code"]))[:80]
            + " message="
            + _sanitize_diagnostic(str(body["message"]))[:140]
        )

    safe_raw = _sanitize_diagnostic(raw)
    return safe_raw[:300], top, ", ".join(keys) or "nenhuma", xano_message


def _emit_failure(
    *,
    method: str,
    path: str,
    status: int | str,
    duration_ms: int,
    response: httpx.Response | None,
    request: httpx.Request | None,
    result: str,
    reference: str | None = None,
    traceback_text: str | None = None,
    active_diagnostics: tuple[bool, bool | None, bool | None] | None = None,
    sent_keys: tuple[str, ...] | None = None,
) -> str:
    reference = reference or _new_reference()
    if os.environ.get("BIBLIOTECA_LOG_ERROS") == "0":
        return reference

    action, profile = _request_action_profile(method, path, request)
    content_type = _content_type(response) if response is not None else "-"
    response_size = len(response.content) if response is not None else 0
    snippet, top, keys, xano_message = _response_details(response)
    block = [
        f"[ERRO xano] ref={reference} {datetime.now().astimezone():%Y-%m-%d %H:%M:%S}",
        f"  ação: {_sanitize_diagnostic(action)} | perfil: {_sanitize_diagnostic(profile)}",
        (
            f"  chamada: {method} {path} -> {status} em {duration_ms} ms | "
            f"content-type: {content_type or '-'} | tamanho: {response_size}"
        ),
        (
            "  enviado (chaves): "
            + (
                ", ".join(_sanitize_diagnostic(key) for key in sent_keys)
                if sent_keys is not None
                else _sent_keys(request)
            )
        ),
        f"  recebido: {snippet or '[vazio]'} | topo JSON: {top} | chaves: {keys}",
    ]
    if xano_message:
        block.append(f"  {xano_message}")
    block.append(f"  resultado: {_sanitize_diagnostic(result)}")
    if active_diagnostics is not None:
        active_sent, active_response, active_reloaded = active_diagnostics
        values = (
            str(active_sent).lower(),
            (
                str(active_response).lower()
                if active_response is not None
                else "nenhum"
            ),
            (
                str(active_reloaded).lower()
                if active_reloaded is not None
                else "nenhum"
            ),
        )
        block.append(
            "  ativo: enviado="
            + values[0]
            + " | resposta="
            + values[1]
            + " | releitura="
            + values[2]
        )
    if traceback_text:
        block.extend(
            "  " + line
            for line in _sanitize_diagnostic(traceback_text).rstrip().splitlines()
        )
    block.append("  dica: no painel do Xano, abra o Request History desta chamada")
    print("\n".join(block), file=sys.stderr, flush=True)
    return reference


def _log_response_failure(response: httpx.Response, result: str) -> str:
    try:
        request = response.request
    except RuntimeError:
        request = None
    method = request.method if request is not None else "RESPOSTA"
    path = request.url.path if request is not None else "(resposta sem chamada)"
    return _emit_failure(
        method=method,
        path=path,
        status=response.status_code,
        duration_ms=int(response.extensions.get("xano_duration_ms", 0)),
        response=response,
        request=request,
        result=result,
    )


def _invalid_response_result(
    error: XanoInvalidResponseError,
    record_index: int,
) -> str:
    field = error.field or "estrutura"
    reason = (
        error.reason
        if error.field is not None
        else "formato incompatível"
    )
    return f"registro {record_index}, campo {field}: {reason}"


def registrar_falha_parse_xano(
    error: XanoInvalidResponseError,
    record_index: int,
) -> str | None:
    _record_failure()
    response = _LAST_RESPONSE.get()
    if response is None:
        return error.reference
    return _log_response_failure(
        response,
        _invalid_response_result(error, record_index),
    )


def registrar_excecao_backend(exception: Exception) -> str:
    details = "".join(
        traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__,
        )
    )
    return _emit_failure(
        method="EVENTO",
        path="(backend Reflex)",
        status="exceção",
        duration_ms=0,
        response=None,
        request=None,
        result=f"exceção inesperada: {type(exception).__name__}",
        traceback_text=details,
    )


def registrar_resultado_xano(
    *,
    action: str,
    profile: str,
    method: str,
    path: str,
    status: int | str,
    result: str,
    reference: str | None = None,
    duration_ms: int = 0,
    active_diagnostics: tuple[bool, bool | None, bool | None] | None = None,
    sent_keys: tuple[str, ...] | None = None,
) -> str:
    with contexto_evento_xano(action, profile):
        return _emit_failure(
            method=method,
            path=path,
            status=status,
            duration_ms=duration_ms,
            response=None,
            request=None,
            result=result,
            reference=reference,
            active_diagnostics=active_diagnostics,
            sent_keys=sent_keys,
        )


@dataclass(slots=True)
class _PageDiagnostics:
    route: str
    calls: int = 0
    failures: int = 0


@contextmanager
def _diagnostic_page(route: str) -> Generator[None, None, None]:
    parent = _PAGE_DIAGNOSTICS.get()
    diagnostics = parent or _PageDiagnostics(route=route)
    token = _PAGE_DIAGNOSTICS.set(diagnostics)
    try:
        yield
    finally:
        _PAGE_DIAGNOSTICS.reset(token)
        if parent is None and _diagnostics_enabled():
            _LOGGER.info(
                "xano_pagina rota=%s chamadas=%d falhas=%d",
                route,
                diagnostics.calls,
                diagnostics.failures,
            )


def diagnosticar_pagina_xano(
    route: str,
) -> Callable[[Callable[_P, Awaitable[_R]]], Callable[_P, Awaitable[_R]]]:
    """Registra no diagnóstico as chamadas feitas durante um carregamento."""

    def decorate(
        handler: Callable[_P, Awaitable[_R]],
    ) -> Callable[_P, Awaitable[_R]]:
        @wraps(handler)
        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            with _diagnostic_page(route):
                return await handler(*args, **kwargs)

        return wrapper

    return decorate


def parse_xano_response_json(response: httpx.Response) -> object:
    """Interpreta JSON do Xano sem expor o corpo de uma resposta inválida."""
    content_type = _content_type(response)
    if content_type and not _is_json_content_type(content_type):
        reference = _log_response_failure(
            response,
            "resposta 2xx ilegível: content-type não JSON",
        )
        raise XanoNonJsonResponseError(
            response.status_code,
            reference=reference,
        ) from None
    try:
        return response.json()
    except ValueError:
        reference = _log_response_failure(
            response,
            "resposta 2xx ilegível: JSON ausente ou inválido",
        )
        raise XanoInvalidResponseError(reference=reference) from None


def parse_xano_write_response(
    response: httpx.Response,
    parser: Callable[[object], _R],
) -> _R:
    """Interpreta a resposta de uma escrita sem converter 2xx em falha."""
    try:
        payload = parse_xano_response_json(response)
        with adiar_log_falha_xano():
            return parser(payload)
    except XanoInvalidResponseError as error:
        if error.reference is None:
            error.reference = registrar_falha_parse_xano(error, 0)
        raise XanoWriteSucceededWithUnreadableResponse(
            reference=error.reference,
        ) from None


def xano_message_with_reference(message: str, error: Exception) -> str:
    reference = getattr(error, "reference", None)
    if not isinstance(reference, str) or not reference:
        return message
    suffix = f"(ref. {reference})"
    if message.endswith(suffix):
        return message
    return f"{message} {suffix}"


def xano_public_error_message(error: Exception) -> str | None:
    """Retorna mensagens públicas comuns sem substituir erros de domínio."""
    if isinstance(error, XanoResponseError):
        if error.status_code == 429:
            _, window = _xano_limit_config()
            wait_seconds = max(1, round(window))
            message = (
                "O Xano permite só 10 chamadas a cada 20 segundos no plano atual. "
                f"Aguarde cerca de {wait_seconds} s e tente de novo."
            )
            return xano_message_with_reference(
                message,
                error,
            )
        if error.non_json_response:
            return xano_message_with_reference(
                "O Xano devolveu uma página de erro "
                f"(código {error.status_code}).",
                error,
            )
        if error.public_detail == "O Xano respondeu em formato inesperado.":
            return xano_message_with_reference(error.public_detail, error)
        return None
    if isinstance(error, XanoNonJsonResponseError):
        return xano_message_with_reference(
            "O Xano devolveu uma página de erro "
            f"(código {error.status_code}).",
            error,
        )
    if isinstance(error, XanoInvalidResponseError):
        return xano_message_with_reference(
            "O Xano respondeu em formato inesperado.",
            error,
        )
    if isinstance(error, XanoTimeoutError):
        return xano_message_with_reference(
            "O Xano demorou para responder. Tente novamente.",
            error,
        )
    if isinstance(error, XanoRequestError):
        return xano_message_with_reference(
            "Não foi possível conectar ao Xano. Verifique a conexão e tente novamente.",
            error,
        )
    return None


def _diagnostics_enabled() -> bool:
    if os.environ.get("BIBLIOTECA_DIAGNOSTICO") != "1":
        return False
    _LOGGER.setLevel(logging.INFO)
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)
    return True


def _get_semaphore() -> asyncio.Semaphore:
    loop = asyncio.get_running_loop()
    with _SEMAPHORES_LOCK:
        semaphore = _SEMAPHORES.get(loop)
        if semaphore is None:
            semaphore = asyncio.Semaphore(3)
            _SEMAPHORES[loop] = semaphore
        return semaphore


def _content_type(response: httpx.Response) -> str:
    value = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if not value:
        return ""
    if any(character not in "abcdefghijklmnopqrstuvwxyz0123456789/+-." for character in value):
        return ""
    return value[:80]


def _is_json_content_type(content_type: str) -> bool:
    return content_type == "application/json" or content_type.endswith("+json")


def _retry_after_seconds(headers: httpx.Headers, fallback: float) -> float:
    value = headers.get("Retry-After")
    if value is None:
        return fallback
    try:
        seconds = float(value)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            seconds = (retry_at - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return fallback
    if not float("-inf") < seconds < float("inf"):
        return fallback
    return min(max(seconds, 0.0), 10.0)


def _record_attempt() -> None:
    diagnostics = _PAGE_DIAGNOSTICS.get()
    if diagnostics is not None:
        diagnostics.calls += 1


def _log_request(
    *,
    method: str,
    path: str,
    status: int | str,
    duration_ms: int,
    response: httpx.Response | None,
    attempt: int,
    cause: str = "-",
) -> None:
    if not _diagnostics_enabled():
        return
    content_type = _content_type(response) if response is not None else "-"
    response_size = len(response.content) if response is not None else 0
    _LOGGER.info(
        "xano_chamada metodo=%s caminho=%s status=%s duracao_ms=%d "
        "content_type=%s tamanho_resposta=%d tentativa=%d causa=%s",
        method,
        path,
        status,
        duration_ms,
        content_type or "-",
        response_size,
        attempt,
        cause,
    )


def _error_detail(
    response: httpx.Response,
) -> tuple[str | None, bool, str | None]:
    content_type = _content_type(response)
    if content_type and not _is_json_content_type(content_type):
        return None, True, None
    try:
        body = response.json()
    except ValueError:
        if _is_json_content_type(content_type):
            return "O Xano respondeu em formato inesperado.", False, None
        return None, True, None
    if not isinstance(body, dict):
        return "O Xano respondeu em formato inesperado.", False, None
    raw_message = body.get("message")
    if not isinstance(raw_message, str):
        raw_message = None
    for key in ("message", "error", "detail"):
        detail = body.get(key)
        if not isinstance(detail, str):
            continue
        if detail in SAFE_ERROR_MESSAGES:
            return SAFE_ERROR_MESSAGES[detail], False, raw_message
        folded = unicodedata.normalize("NFKD", detail)
        words = re.findall(
            r"[a-z]+",
            folded.encode("ascii", errors="ignore").decode("ascii").lower(),
        )
        portuguese_markers = {
            "acesso",
            "ativo",
            "biblioteca",
            "campo",
            "conta",
            "credenciais",
            "dados",
            "duplicada",
            "duplicado",
            "encontrado",
            "erro",
            "estudante",
            "limite",
            "nao",
            "invalida",
            "invalidas",
            "invalido",
            "pedido",
            "pedidos",
            "perfil",
            "recurso",
            "reserva",
            "reservas",
            "titulo",
            "usuario",
        }
        if (
            len(detail) <= 140
            and not re.search(r"(?i)\b\S+@\S+\b", detail)
            and not re.search(r"\d{5,}", detail)
            and any(word in portuguese_markers for word in words)
        ):
            return _sanitize_diagnostic(detail), False, raw_message
    return None, False, raw_message


@dataclass(slots=True)
class XanoClient:
    _base_url: httpx.URL = field(repr=False)
    _transport: httpx.AsyncBaseTransport | None = field(default=None, repr=False)
    _timeout: float = 10.0

    @classmethod
    def from_environment(
        cls,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 10.0,
    ) -> "XanoClient":
        load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
        raw_url = os.environ.get("XANO_API_BASE_URL", "").strip()
        if not raw_url:
            raise XanoConfigurationError(
                "Configure XANO_API_BASE_URL no ambiente do backend."
            )

        try:
            parsed = urlsplit(raw_url)
            hostname = parsed.hostname
            port = parsed.port
            url = httpx.URL(raw_url)
        except ValueError:
            raise XanoConfigurationError(
                "XANO_API_BASE_URL deve ser uma URL HTTP(S) válida."
            ) from None

        if (
            parsed.scheme not in {"http", "https"}
            or not hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or url.username
            or url.password
        ):
            raise XanoConfigurationError(
                "XANO_API_BASE_URL deve conter somente uma origem HTTP(S) e um caminho."
            )

        if parsed.scheme != "https" and hostname.lower() not in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            raise XanoConfigurationError(
                "XANO_API_BASE_URL deve usar HTTPS fora do ambiente local."
            )

        normalized_url = url.copy_with(path=f"{url.path.rstrip('/')}/")
        if port is not None and not 0 < port < 65536:
            raise XanoConfigurationError(
                "XANO_API_BASE_URL deve conter uma porta válida."
            )
        return cls(
            _base_url=normalized_url,
            _transport=transport,
            _timeout=timeout,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        request_method = method.upper()
        endpoint = urlsplit(path)
        if token is not None:
            scope = _authenticated_cache_scope(self._base_url, token)
            if (
                request_method == "GET"
                and endpoint.path in _AUTHENTICATED_LIST_PATHS
                and not endpoint.query
            ):
                response = await _cached_authenticated_get(
                    scope,
                    endpoint.path,
                    id(self._transport) if self._transport is not None else 0,
                    self._transport,
                    lambda: self._request_uncached(
                        method,
                        path,
                        token=token,
                        json=json,
                    ),
                )
                _LAST_RESPONSE.set(response)
                return response
            if request_method != "GET":
                _invalidate_authenticated_get_cache(scope)
        return await self._request_uncached(
            method,
            path,
            token=token,
            json=json,
        )

    async def _request_uncached(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        endpoint = urlsplit(path)
        if (
            not endpoint.path
            or endpoint.scheme
            or endpoint.netloc
            or endpoint.fragment
            or endpoint.path.startswith("//")
            or any(part in {".", ".."} for part in endpoint.path.split("/"))
        ):
            raise ValueError("O caminho da requisição Xano deve ser relativo à API.")

        url = self._base_url.join(endpoint.path.lstrip("/"))
        if endpoint.query:
            url = url.copy_with(query=endpoint.query.encode())
        _LAST_RESPONSE.set(None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        request_method = method.upper()

        host = _xano_host(self._base_url)
        priority = _xano_priority(request_method, endpoint.path)
        retried_429 = False
        for attempt in range(1, _MAX_RETRIES + 2):
            started_at = time.perf_counter()
            _record_attempt()
            if not await _adquirir_slot_xano(host, priority):
                raise XanoTimeoutError(
                    "O limite de espera do Xano foi excedido.",
                    reference=_emit_failure(
                        method=request_method,
                        path=endpoint.path,
                        status="sem_resposta",
                        duration_ms=round(
                            (time.perf_counter() - started_at) * 1000
                        ),
                        response=None,
                        request=None,
                        result="espera máxima de 25 s excedida",
                    ),
                )
            try:
                async with _get_semaphore():
                    async with httpx.AsyncClient(
                        timeout=self._timeout,
                        transport=self._transport,
                    ) as client:
                        response = await client.request(
                            request_method,
                            url,
                            headers=headers,
                            json=json,
                        )
            except httpx.TimeoutException as error:
                duration_ms = round((time.perf_counter() - started_at) * 1000)
                _record_failure()
                request = getattr(error, "request", None)
                reference = _emit_failure(
                    method=request_method,
                    path=endpoint.path,
                    status="sem_resposta",
                    duration_ms=duration_ms,
                    response=None,
                    request=request,
                    result=f"tempo esgotado: {type(error).__name__}",
                )
                if request_method == "GET" and attempt <= _MAX_RETRIES:
                    await _sleep(_RETRY_DELAYS[attempt - 1])
                    continue
                raise XanoTimeoutError(
                    "O serviço Xano excedeu o tempo limite.",
                    reference=reference,
                ) from None
            except httpx.RequestError as error:
                duration_ms = round((time.perf_counter() - started_at) * 1000)
                _record_failure()
                request = getattr(error, "request", None)
                reference = _emit_failure(
                    method=request_method,
                    path=endpoint.path,
                    status="sem_resposta",
                    duration_ms=duration_ms,
                    response=None,
                    request=request,
                    result=f"falha de conexão: {type(error).__name__}",
                )
                if request_method == "GET" and attempt <= _MAX_RETRIES:
                    await _sleep(_RETRY_DELAYS[attempt - 1])
                    continue
                raise XanoRequestError(
                    "Não foi possível se comunicar com o serviço Xano.",
                    reference=reference,
                ) from None

            duration_ms = round((time.perf_counter() - started_at) * 1000)
            response.extensions["xano_duration_ms"] = duration_ms
            if response.is_error:
                _record_failure()
                public_detail, non_json_response, _ = _error_detail(response)
                reference = _emit_failure(
                    method=request_method,
                    path=endpoint.path,
                    status=response.status_code,
                    duration_ms=duration_ms,
                    response=response,
                    request=response.request,
                    result=f"resposta HTTP {response.status_code}",
                )
                if response.status_code == 429:
                    _, window = _xano_limit_config()
                    _pausar_xano(host, window)
                    if (
                        request_method == "GET"
                        and not retried_429
                    ):
                        retried_429 = True
                        continue
                if (
                    request_method == "GET"
                    and response.status_code in _RETRYABLE_STATUSES
                    and attempt <= _MAX_RETRIES
                ):
                    delay = _retry_after_seconds(
                        response.headers,
                        _RETRY_DELAYS[attempt - 1],
                    )
                    await _sleep(delay)
                    continue
                raise XanoResponseError(
                    response.status_code,
                    public_detail,
                    non_json_response=non_json_response,
                    reference=reference,
                )

            _LAST_RESPONSE.set(response)
            _log_request(
                method=request_method,
                path=endpoint.path,
                status=response.status_code,
                duration_ms=duration_ms,
                response=response,
                attempt=attempt,
            )
            return response

        raise XanoRequestError(
            "Não foi possível concluir a chamada ao Xano.",
            reference=_emit_failure(
                method=request_method,
                path=endpoint.path,
                status="sem_resposta",
                duration_ms=0,
                response=None,
                request=None,
                result="tentativas esgotadas",
            ),
        )


def _record_failure() -> None:
    diagnostics = _PAGE_DIAGNOSTICS.get()
    if diagnostics is not None:
        diagnostics.failures += 1

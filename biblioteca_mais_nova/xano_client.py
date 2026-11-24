"""Cliente HTTP do Xano executado exclusivamente no backend."""

import asyncio
import contextvars
import logging
import os
import threading
import time
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
_sleep = asyncio.sleep
_PAGE_DIAGNOSTICS: contextvars.ContextVar["_PageDiagnostics | None"] = (
    contextvars.ContextVar("xano_page_diagnostics", default=None)
)
_SEMAPHORES: WeakKeyDictionary[
    asyncio.AbstractEventLoop, asyncio.Semaphore
] = WeakKeyDictionary()
_SEMAPHORES_LOCK = threading.Lock()
_P = ParamSpec("_P")
_R = TypeVar("_R")


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


class XanoRequestError(RuntimeError):
    """Falha sanitizada ao acessar o Xano."""


class XanoTimeoutError(XanoRequestError):
    """Tempo limite excedido ao acessar o Xano."""


class XanoInvalidResponseError(XanoRequestError):
    """Resposta inválida retornada pelo Xano."""

    def __init__(
        self,
        message: str = "O Xano respondeu em formato inesperado.",
    ) -> None:
        _record_failure()
        super().__init__(message)


class XanoNonJsonResponseError(XanoInvalidResponseError):
    """Resposta que não contém JSON quando o contrato exige JSON."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__("O Xano devolveu uma página de erro.")


class XanoResponseError(XanoRequestError):
    """Resposta HTTP de erro retornada pelo Xano."""

    def __init__(
        self,
        status_code: int,
        public_detail: str | None = None,
        *,
        non_json_response: bool = False,
    ) -> None:
        self.status_code = status_code
        self.public_detail = public_detail
        self.non_json_response = non_json_response
        super().__init__(f"O serviço Xano retornou um erro HTTP {status_code}.")


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
        raise XanoNonJsonResponseError(response.status_code) from None
    try:
        return response.json()
    except ValueError:
        raise XanoInvalidResponseError() from None


def xano_public_error_message(error: Exception) -> str | None:
    """Retorna mensagens públicas comuns sem substituir erros de domínio."""
    if isinstance(error, XanoResponseError):
        if error.status_code == 429:
            return (
                "O Xano limitou as requisições por alguns segundos. "
                "Aguarde um pouco e tente de novo."
            )
        if error.non_json_response:
            return (
                "O Xano devolveu uma página de erro "
                f"(código {error.status_code})."
            )
        if error.public_detail == "O Xano respondeu em formato inesperado.":
            return error.public_detail
        return None
    if isinstance(error, XanoNonJsonResponseError):
        return (
            "O Xano devolveu uma página de erro "
            f"(código {error.status_code})."
        )
    if isinstance(error, XanoInvalidResponseError):
        return "O Xano respondeu em formato inesperado."
    if isinstance(error, XanoTimeoutError):
        return "O Xano demorou para responder. Tente novamente."
    if isinstance(error, XanoRequestError):
        return "Não foi possível conectar ao Xano. Verifique a conexão e tente novamente."
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


def _error_detail(response: httpx.Response) -> tuple[str | None, bool]:
    content_type = _content_type(response)
    if content_type and not _is_json_content_type(content_type):
        return None, True
    try:
        body = response.json()
    except ValueError:
        if _is_json_content_type(content_type):
            return "O Xano respondeu em formato inesperado.", False
        return None, True
    if not isinstance(body, dict):
        return "O Xano respondeu em formato inesperado.", False
    for key in ("message", "error", "detail"):
        detail = body.get(key)
        if isinstance(detail, str) and detail in SAFE_ERROR_MESSAGES:
            return SAFE_ERROR_MESSAGES[detail], False
    return None, False


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
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        request_method = method.upper()

        for attempt in range(1, _MAX_RETRIES + 2):
            started_at = time.perf_counter()
            _record_attempt()
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
                _log_request(
                    method=request_method,
                    path=endpoint.path,
                    status="sem_resposta",
                    duration_ms=duration_ms,
                    response=None,
                    attempt=attempt,
                    cause=type(error).__name__,
                )
                if request_method == "GET" and attempt <= _MAX_RETRIES:
                    await _sleep(_RETRY_DELAYS[attempt - 1])
                    continue
                raise XanoTimeoutError(
                    "O serviço Xano excedeu o tempo limite."
                ) from None
            except httpx.RequestError as error:
                duration_ms = round((time.perf_counter() - started_at) * 1000)
                _record_failure()
                _log_request(
                    method=request_method,
                    path=endpoint.path,
                    status="sem_resposta",
                    duration_ms=duration_ms,
                    response=None,
                    attempt=attempt,
                    cause=type(error).__name__,
                )
                if request_method == "GET" and attempt <= _MAX_RETRIES:
                    await _sleep(_RETRY_DELAYS[attempt - 1])
                    continue
                raise XanoRequestError(
                    "Não foi possível se comunicar com o serviço Xano."
                ) from None

            duration_ms = round((time.perf_counter() - started_at) * 1000)
            if response.is_error:
                _record_failure()
                _log_request(
                    method=request_method,
                    path=endpoint.path,
                    status=response.status_code,
                    duration_ms=duration_ms,
                    response=response,
                    attempt=attempt,
                )
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
                public_detail, non_json_response = _error_detail(response)
                raise XanoResponseError(
                    response.status_code,
                    public_detail,
                    non_json_response=non_json_response,
                )

            _log_request(
                method=request_method,
                path=endpoint.path,
                status=response.status_code,
                duration_ms=duration_ms,
                response=response,
                attempt=attempt,
            )
            return response

        raise XanoRequestError("Não foi possível concluir a chamada ao Xano.")


def _record_failure() -> None:
    diagnostics = _PAGE_DIAGNOSTICS.get()
    if diagnostics is not None:
        diagnostics.failures += 1

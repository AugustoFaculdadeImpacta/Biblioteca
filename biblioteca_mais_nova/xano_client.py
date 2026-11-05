"""Cliente HTTP do Xano executado exclusivamente no backend."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import load_dotenv


class XanoConfigurationError(ValueError):
    """Configuração ausente ou inválida para acessar o Xano."""


class XanoRequestError(RuntimeError):
    """Falha sanitizada ao acessar o Xano."""


class XanoResponseError(XanoRequestError):
    """Resposta HTTP de erro retornada pelo Xano."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"O serviço Xano retornou um erro HTTP {status_code}.")


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

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                )
        except httpx.RequestError:
            raise XanoRequestError(
                "Não foi possível se comunicar com o serviço Xano."
            ) from None

        if response.is_error:
            raise XanoResponseError(response.status_code)
        return response

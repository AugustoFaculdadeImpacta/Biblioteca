"""Operações de catálogo conforme os endpoints locais do Xano."""

import copy
import time
from typing import NotRequired, TypedDict
from urllib.parse import urlsplit

import httpx

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    parse_xano_response_json,
    xano_public_error_message,
)


class Category(TypedDict):
    id: int
    nome: str


class PublicTitleFields(TypedDict):
    id: int
    titulo: str
    autores: str
    created_at: NotRequired[str | int | float | None]
    ativo: NotRequired[bool | None]
    isbn: NotRequired[str | None]
    editora: NotRequired[str | None]
    edicao: NotRequired[str | None]
    ano_publicacao: NotRequired[int | None]
    descricao: NotRequired[str | None]
    capa_url: NotRequired[str | None]


class PublicCatalogEntry(TypedDict):
    titulo: PublicTitleFields
    categorias: list["TitleCategory"]
    exemplares_disponiveis: int


class TitlePayload(TypedDict, total=False):
    titulo: str
    autores: str
    isbn: str
    editora: str
    edicao: str
    ano_publicacao: int
    descricao: str
    capa_url: str


class Title(TypedDict):
    id: int


class TitleCategory(TypedDict):
    id: int
    titulo_id: int
    categoria_id: int


class Copy(TypedDict):
    id: int
    titulo_id: int
    estado: str
    codigo_tombo: str


class AdminCatalogCopy(TypedDict):
    id: int
    titulo_id: int
    estado: str
    codigo_tombo: str | None


class AdminCatalogEntry(TypedDict):
    titulo: PublicTitleFields
    categorias: list["TitleCategory"]
    exemplares: list[AdminCatalogCopy]
    exemplares_disponiveis: int


class AdminCatalogDisplayCopy(TypedDict):
    codigo_tombo: str
    estado: str


class AdminCatalogDisplayEntry(TypedDict):
    id: int
    titulo: str
    autores: str
    isbn: str
    editora: str
    edicao: str
    ano_publicacao: str
    descricao: str
    capa_url: str
    capa_real: NotRequired[str]
    capa_gerada: NotRequired[str]
    ativo: bool
    categorias: str
    exemplares_disponiveis: int
    exemplares: list[AdminCatalogDisplayCopy]


class CatalogValidationError(ValueError):
    """Entrada de catálogo inválida para exibição."""


_PUBLIC_CACHE_TTL_SECONDS = 60.0
_PUBLIC_CACHE: dict[str, tuple[float, object]] = {}


def invalidar_cache_catalogo_publico() -> None:
    """Remove catálogo e categorias públicas após uma escrita administrativa."""
    _PUBLIC_CACHE.clear()


def limpar_cache_catalogo_publico() -> None:
    """Uso exclusivo em testes para isolar o estado em memória."""
    invalidar_cache_catalogo_publico()


def _cache_read(key: str) -> object | None:
    cached = _PUBLIC_CACHE.get(key)
    if cached is None:
        return None
    expires_at, value = cached
    if expires_at <= time.monotonic():
        _PUBLIC_CACHE.pop(key, None)
        return None
    return copy.deepcopy(value)


def _cache_write(key: str, value: object) -> None:
    _PUBLIC_CACHE[key] = (
        time.monotonic() + _PUBLIC_CACHE_TTL_SECONDS,
        copy.deepcopy(value),
    )


def _validate_cover_url(value: str) -> None:
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
    except ValueError:
        parsed = None
        hostname = None

    if (
        parsed is None
        or parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise CatalogValidationError(
            "O link da imagem da capa deve usar HTTPS e ter um endereço válido."
        )


def build_title_payload(form_data: dict[str, str]) -> TitlePayload:
    titulo = form_data.get("titulo", "").strip()
    autores = form_data.get("autores", "").strip()
    if not titulo:
        raise CatalogValidationError("Informe o título.")
    if not autores:
        raise CatalogValidationError("Informe os autores.")

    payload: TitlePayload = {"titulo": titulo, "autores": autores}
    for field in ("isbn", "editora", "edicao", "descricao"):
        value = form_data.get(field, "").strip()
        if value:
            payload[field] = value

    cover_url = form_data.get("capa_url", "").strip()
    if cover_url:
        _validate_cover_url(cover_url)
        payload["capa_url"] = cover_url

    year = form_data.get("ano_publicacao", "").strip()
    if year:
        try:
            payload["ano_publicacao"] = int(year)
        except ValueError:
            raise CatalogValidationError(
                "O ano de publicação deve ser um número inteiro."
            ) from None
    return payload


def _response_json(response: httpx.Response) -> object:
    return parse_xano_response_json(response)


def _response_error() -> XanoRequestError:
    return XanoInvalidResponseError()


async def list_categories(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[Category]:
    cached = _cache_read("categorias") if transport is None else None
    if isinstance(cached, list):
        return copy.deepcopy(cached)
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", "/catalogo/categorias")
    categories = _response_json(response)
    if not isinstance(categories, list):
        raise _response_error()

    parsed: list[Category] = []
    for category in categories:
        if (
            not isinstance(category, dict)
            or type(category.get("id")) is not int
            or not isinstance(category.get("nome"), str)
        ):
            raise _response_error()
        parsed.append({"id": category["id"], "nome": category["nome"]})
    if transport is None:
        _cache_write("categorias", parsed)
    return parsed


def _parse_public_catalog_entry(value: object) -> PublicCatalogEntry:
    if not isinstance(value, dict):
        raise _response_error()

    title = value.get("titulo")
    categories = value.get("categorias")
    available = value.get("exemplares_disponiveis")
    if (
        not isinstance(title, dict)
        or type(title.get("id")) is not int
        or not isinstance(title.get("titulo"), str)
        or not isinstance(title.get("autores"), str)
        or not isinstance(categories, list)
        or type(available) is not int
        or available < 0
    ):
        raise _response_error()

    parsed_title: PublicTitleFields = {
        "id": title["id"],
        "titulo": title["titulo"],
        "autores": title["autores"],
    }
    created_at = title.get("created_at")
    if created_at is not None and type(created_at) not in {str, int, float}:
        raise _response_error()
    if "created_at" in title:
        parsed_title["created_at"] = created_at

    active = title.get("ativo")
    if active is not None and type(active) is not bool:
        raise _response_error()
    if "ativo" in title:
        parsed_title["ativo"] = active
    for field in ("isbn", "editora", "edicao", "descricao"):
        field_value = title.get(field)
        if field_value is not None and not isinstance(field_value, str):
            raise _response_error()
        if field in title:
            parsed_title[field] = field_value
    cover_url = title.get("capa_url")
    if cover_url is not None and not isinstance(cover_url, str):
        raise _response_error()
    if cover_url:
        try:
            _validate_cover_url(cover_url)
        except CatalogValidationError:
            raise _response_error() from None
        parsed_title["capa_url"] = cover_url
    elif "capa_url" in title:
        parsed_title["capa_url"] = None

    year = title.get("ano_publicacao")
    if year is not None and type(year) is not int:
        raise _response_error()
    if "ano_publicacao" in title:
        parsed_title["ano_publicacao"] = year

    parsed_categories: list[TitleCategory] = []
    for category in categories:
        if (
            not isinstance(category, dict)
            or type(category.get("id")) is not int
            or category.get("titulo_id") != title["id"]
            or type(category.get("titulo_id")) is not int
            or type(category.get("categoria_id")) is not int
        ):
            raise _response_error()
        parsed_categories.append(
            {
                "id": category["id"],
                "titulo_id": category["titulo_id"],
                "categoria_id": category["categoria_id"],
            }
        )

    return {
        "titulo": parsed_title,
        "categorias": parsed_categories,
        "exemplares_disponiveis": available,
    }


async def list_public_titles(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[PublicCatalogEntry]:
    cached = _cache_read("titulos_publicos") if transport is None else None
    if isinstance(cached, list):
        return copy.deepcopy(cached)
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", "/catalogo/titulos")
    titles = _response_json(response)
    if not isinstance(titles, list):
        raise _response_error()
    public_titles: list[PublicCatalogEntry] = []
    for title in titles:
        if isinstance(title, dict):
            title_fields = title.get("titulo")
            active = (
                title_fields.get("ativo")
                if isinstance(title_fields, dict)
                else None
            )
            if active is False:
                continue
        public_titles.append(_parse_public_catalog_entry(title))
    if transport is None:
        _cache_write("titulos_publicos", public_titles)
    return public_titles


async def get_public_title(
    title_id: int,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> PublicCatalogEntry:
    if type(title_id) is not int or title_id < 1:
        raise _response_error()
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", f"/catalogo/titulos/{title_id}")
    value = _response_json(response)
    if (
        isinstance(value, dict)
        and isinstance(value.get("titulo"), dict)
        and value["titulo"].get("ativo") is False
    ):
        raise XanoResponseError(404)
    return _parse_public_catalog_entry(value)


def _parse_admin_catalog_entry(value: object) -> AdminCatalogEntry:
    if not isinstance(value, dict):
        raise _response_error()
    public_entry = _parse_public_catalog_entry(value)
    copies = value.get("exemplares")
    if not isinstance(copies, list):
        raise _response_error()

    parsed_copies: list[AdminCatalogCopy] = []
    for copy in copies:
        if (
            not isinstance(copy, dict)
            or type(copy.get("id")) is not int
            or copy.get("titulo_id") != public_entry["titulo"]["id"]
            or type(copy.get("titulo_id")) is not int
            or not isinstance(copy.get("estado"), str)
            or copy["estado"]
            not in {"disponivel", "reservado", "emprestado", "indisponivel"}
        ):
            raise _response_error()
        code = copy.get("codigo_tombo")
        if code is not None and not isinstance(code, str):
            raise _response_error()
        parsed_copies.append(
            {
                "id": copy["id"],
                "titulo_id": copy["titulo_id"],
                "estado": copy["estado"],
                "codigo_tombo": code,
            }
        )

    return {
        "titulo": public_entry["titulo"],
        "categorias": public_entry["categorias"],
        "exemplares": parsed_copies,
        "exemplares_disponiveis": public_entry["exemplares_disponiveis"],
    }


async def list_admin_catalog(
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[AdminCatalogEntry]:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", "/admin/acervo", token=token)
    entries = _response_json(response)
    if not isinstance(entries, list):
        raise _response_error()
    return [_parse_admin_catalog_entry(entry) for entry in entries]


async def update_title(
    title_id: int,
    payload: TitlePayload,
    token: str,
    *,
    active: bool | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Title:
    if type(title_id) is not int or title_id < 1:
        raise _response_error()
    request_payload: dict[str, object] = dict(payload)
    if active is not None:
        request_payload["ativo"] = active

    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "PATCH",
        f"/catalogo/titulos/{title_id}",
        token=token,
        json=request_payload,
    )
    title = _response_json(response)
    if (
        not isinstance(title, dict)
        or type(title.get("id")) is not int
        or title["id"] != title_id
    ):
        raise _response_error()
    invalidar_cache_catalogo_publico()
    return {"id": title_id}


async def create_title(
    payload: TitlePayload,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Title:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "POST",
        "/catalogo/titulos",
        token=token,
        json=payload,
    )
    title = _response_json(response)
    if not isinstance(title, dict) or type(title.get("id")) is not int:
        raise _response_error()
    invalidar_cache_catalogo_publico()
    return {"id": title["id"]}


async def associate_category(
    title_id: int,
    category_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> TitleCategory:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "POST",
        f"/admin/titulos/{title_id}/categorias",
        token=token,
        json={"categoria_id": category_id},
    )
    association = _response_json(response)
    if (
        not isinstance(association, dict)
        or type(association.get("id")) is not int
        or type(association.get("titulo_id")) is not int
        or association.get("titulo_id") != title_id
        or type(association.get("categoria_id")) is not int
        or association.get("categoria_id") != category_id
    ):
        raise _response_error()
    invalidar_cache_catalogo_publico()
    return {
        "id": association["id"],
        "titulo_id": title_id,
        "categoria_id": category_id,
    }


async def category_contains_title(
    category_id: int,
    title_id: int,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> bool:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "GET",
        f"/catalogo/categorias/{category_id}/titulos",
    )
    titles = _response_json(response)
    if not isinstance(titles, list):
        raise _response_error()
    for title in titles:
        if not isinstance(title, dict) or type(title.get("id")) is not int:
            raise _response_error()
        if title["id"] == title_id:
            return True
    return False


async def create_copy(
    title_id: int,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Copy:
    client = XanoClient.from_environment(transport=transport)
    response = await client.request(
        "POST",
        "/admin/exemplares",
        token=token,
        json={"titulo_id": title_id},
    )
    copy = _response_json(response)
    if (
        not isinstance(copy, dict)
        or type(copy.get("id")) is not int
        or type(copy.get("titulo_id")) is not int
        or copy.get("titulo_id") != title_id
        or not isinstance(copy.get("estado"), str)
        or not isinstance(copy.get("codigo_tombo"), str)
        or not copy["codigo_tombo"]
    ):
        raise _response_error()
    invalidar_cache_catalogo_publico()
    return {
        "id": copy["id"],
        "titulo_id": title_id,
        "estado": copy["estado"],
        "codigo_tombo": copy["codigo_tombo"],
    }


def catalog_error_message(error: Exception) -> str:
    if isinstance(error, CatalogValidationError):
        return str(error)
    common_message = xano_public_error_message(error)
    if common_message is not None:
        return common_message
    if isinstance(error, XanoConfigurationError):
        return "O acervo está temporariamente indisponível. Tente novamente mais tarde."
    if isinstance(error, XanoResponseError):
        if error.public_detail:
            return error.public_detail
        if error.status_code == 401:
            return "Sua sessão expirou ou não é mais válida. Entre novamente para continuar."
        if error.status_code == 403:
            return "Sua conta não tem permissão para acessar este recurso."
        if error.status_code == 404:
            return "O recurso não foi encontrado ou a rota ainda não está disponível."
        if error.status_code >= 500:
            return "O serviço Xano está temporariamente indisponível. Tente novamente mais tarde."
    return "Ocorreu um erro inesperado. Tente novamente mais tarde."

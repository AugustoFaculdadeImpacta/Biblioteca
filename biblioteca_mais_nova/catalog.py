"""Operações de catálogo conforme os endpoints locais do Xano."""

import json
from typing import NotRequired, TypedDict

import httpx

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoRequestError,
)


class Category(TypedDict):
    id: int
    nome: str


class PublicTitleFields(TypedDict):
    id: int
    titulo: str
    autores: str
    isbn: NotRequired[str | None]
    editora: NotRequired[str | None]
    edicao: NotRequired[str | None]
    ano_publicacao: NotRequired[int | None]
    descricao: NotRequired[str | None]


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


class CatalogValidationError(ValueError):
    """Entrada de catálogo inválida para exibição."""


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
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        raise XanoRequestError(
            "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
        ) from None


def _response_error() -> XanoRequestError:
    return XanoRequestError(
        "O serviço não retornou uma resposta válida. Tente novamente mais tarde."
    )


async def list_categories(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[Category]:
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
    for field in ("isbn", "editora", "edicao", "descricao"):
        field_value = title.get(field)
        if field_value is not None and not isinstance(field_value, str):
            raise _response_error()
        if field in title:
            parsed_title[field] = field_value

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
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", "/catalogo/titulos")
    titles = _response_json(response)
    if not isinstance(titles, list):
        raise _response_error()
    return [_parse_public_catalog_entry(title) for title in titles]


async def get_public_title(
    title_id: int,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> PublicCatalogEntry:
    if type(title_id) is not int or title_id < 1:
        raise _response_error()
    client = XanoClient.from_environment(transport=transport)
    response = await client.request("GET", f"/catalogo/titulos/{title_id}")
    return _parse_public_catalog_entry(_response_json(response))


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
    return {
        "id": copy["id"],
        "titulo_id": title_id,
        "estado": copy["estado"],
        "codigo_tombo": copy["codigo_tombo"],
    }


def catalog_error_message(error: Exception) -> str:
    if isinstance(error, CatalogValidationError):
        return str(error)
    if isinstance(error, XanoConfigurationError):
        return "O acervo está temporariamente indisponível. Tente novamente mais tarde."
    if isinstance(error, XanoRequestError):
        return "Não foi possível concluir a operação no acervo. Confira a situação antes de tentar novamente."
    return "Ocorreu um erro inesperado. Tente novamente mais tarde."

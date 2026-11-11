"""Prepara o catálogo de demonstração no Xano; não executa sem --apply."""

from __future__ import annotations

import argparse
import json
import os
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

if __package__:
    from .demo_seed_data import CATEGORY_NAMES, SEED_TITLES
else:
    from demo_seed_data import CATEGORY_NAMES, SEED_TITLES


class SeedError(Exception):
    pass


JsonRequester = Callable[[str, str, str, str, dict[str, object] | None], object]


def request_json(
    method: str,
    path: str,
    base_url: str,
    token: str,
    body: dict[str, object] | None = None,
) -> object:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise SeedError(f"O Xano respondeu HTTP {error.code} ao seed.") from None
    except (TimeoutError, URLError):
        raise SeedError("Não foi possível se comunicar com o Xano.") from None
    except OSError:
        raise SeedError("Não foi possível se comunicar com o Xano.") from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise SeedError("O Xano retornou uma resposta inválida.") from None


def _list_response(value: object, resource: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not all(
        isinstance(item, dict) for item in value
    ):
        raise SeedError(f"A resposta de {resource} não corresponde ao contrato.")
    return value


def _record_id(value: object, resource: str) -> int:
    if not isinstance(value, dict) or type(value.get("id")) is not int:
        raise SeedError(f"A resposta de {resource} não contém um identificador.")
    return int(value["id"])


def _normalize(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _title_identity(entry: dict[str, object]) -> tuple[str, str]:
    title = entry.get("titulo")
    if not isinstance(title, dict):
        raise SeedError("A listagem do acervo retornou título inválido.")
    name = title.get("titulo")
    author = title.get("autores")
    if not isinstance(name, str) or not isinstance(author, str):
        raise SeedError("A listagem do acervo não contém título e autor.")
    return _normalize(name), _normalize(author)


def _relations(entry: dict[str, object]) -> set[int]:
    categories = entry.get("categorias", [])
    if not isinstance(categories, list) or not all(
        isinstance(item, dict) and type(item.get("categoria_id")) is int
        for item in categories
    ):
        raise SeedError("A listagem do acervo retornou categorias inválidas.")
    return {int(item["categoria_id"]) for item in categories}


def _copies(entry: dict[str, object]) -> list[dict[str, object]]:
    copies = entry.get("exemplares", [])
    if not isinstance(copies, list) or not all(
        isinstance(item, dict) and type(item.get("id")) is int for item in copies
    ):
        raise SeedError("A listagem do acervo retornou exemplares inválidos.")
    return copies


def seed_catalog(
    base_url: str,
    token: str,
    requester: JsonRequester = request_json,
) -> dict[str, int]:
    categories = _list_response(
        requester("GET", "/catalogo/categorias", base_url, token, None),
        "categorias",
    )
    category_map: dict[str, int] = {}
    for category in categories:
        name = category.get("nome")
        if not isinstance(name, str):
            raise SeedError("A listagem de categorias retornou dados inválidos.")
        key = _normalize(name)
        if key in category_map:
            raise SeedError("Há categorias duplicadas; revise o acervo antes do seed.")
        category_map[key] = _record_id(category, "categorias")

    counts = {"categorias": 0, "titulos": 0, "associacoes": 0, "exemplares": 0}
    for name in CATEGORY_NAMES:
        key = _normalize(name)
        if key not in category_map:
            created = requester(
                "POST",
                "/catalogo/categorias",
                base_url,
                token,
                {"nome": name},
            )
            category_map[key] = _record_id(created, "criação de categoria")
            counts["categorias"] += 1

    catalog = _list_response(
        requester("GET", "/admin/acervo", base_url, token, None),
        "acervo administrativo",
    )
    title_map: dict[tuple[str, str], dict[str, object]] = {}
    for entry in catalog:
        identity = _title_identity(entry)
        if identity in title_map:
            raise SeedError("Há títulos de seed duplicados; revise o acervo.")
        title_map[identity] = entry

    for seed in SEED_TITLES:
        identity = (_normalize(seed.title), _normalize(seed.author))
        entry = title_map.get(identity)
        if entry is None:
            created_title = requester(
                "POST",
                "/catalogo/titulos",
                base_url,
                token,
                {"titulo": seed.title, "autores": seed.author},
            )
            title_id = _record_id(created_title, "criação de título")
            entry = {
                "titulo": created_title,
                "categorias": [],
                "exemplares": [],
            }
            title_map[identity] = entry
            counts["titulos"] += 1
        else:
            title_id = _record_id(entry.get("titulo"), "listagem do acervo")

        relations = _relations(entry)
        for category_name in seed.categories:
            category_id = category_map[_normalize(category_name)]
            if category_id not in relations:
                requester(
                    "POST",
                    f"/admin/titulos/{title_id}/categorias",
                    base_url,
                    token,
                    {"categoria_id": category_id},
                )
                relations.add(category_id)
                counts["associacoes"] += 1

        copies = _copies(entry)
        for _ in range(max(0, seed.copies - len(copies))):
            created_copy = requester(
                "POST",
                "/admin/exemplares",
                base_url,
                token,
                {"titulo_id": title_id},
            )
            _record_id(created_copy, "criação de exemplar")
            counts["exemplares"] += 1

    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="executa as escritas no destino Xano informado pelo ambiente",
    )
    parser.add_argument(
        "--confirm-destination",
        action="store_true",
        help="confirma que workspace, branch e ambiente foram identificados",
    )
    args = parser.parse_args(argv)
    if not args.apply:
        print(
            f"Prévia: {len(CATEGORY_NAMES)} categorias e "
            f"{len(SEED_TITLES)} títulos; nenhuma chamada foi realizada. "
            "Revise o destino e use --apply somente após autorização."
        )
        return 0
    if not args.confirm_destination:
        parser.error(
            "Antes de --apply, identifique e confirme workspace, branch e ambiente."
        )

    base_url = os.environ.get("XANO_BASE_URL", "").strip()
    token = os.environ.get("XANO_ADMIN_TOKEN", "")
    parsed_url = urlsplit(base_url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        parser.error("Defina XANO_BASE_URL com um endereço HTTPS válido.")
    if not token:
        parser.error("Defina XANO_ADMIN_TOKEN no ambiente de execução.")

    counts = seed_catalog(base_url, token)
    print(
        "Seed concluído: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
        + "."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

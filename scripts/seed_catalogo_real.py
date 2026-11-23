"""Prepara e, opcionalmente, aplica um catálogo real ao Xano."""

from __future__ import annotations
import argparse
import asyncio
import os
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import httpx

from biblioteca_mais_nova.catalog import (
    associate_category,
    build_title_payload,
    create_copy,
    create_title,
    list_categories,
    list_public_titles,
    update_title,
)
from biblioteca_mais_nova.login import build_login_payload, submit_login
from biblioteca_mais_nova.seed_data import TITULOS


TITULOS_TESTE = ("Jack Sparrow", "Something")


def normalizar(texto: object) -> str:
    valor = unicodedata.normalize("NFKD", str(texto or "").strip().casefold())
    return "".join(char for char in valor if not unicodedata.combining(char))


def preparar_plano(categorias: list[dict], existentes: list[dict], titulos: list[dict] | None = None) -> dict:
    escolhidos = titulos or TITULOS
    mapa_categorias = {normalizar(item["nome"]): item["id"] for item in categorias}
    existentes_normalizados = {
        normalizar(
            item["titulo"]["titulo"]
            if isinstance(item.get("titulo"), dict)
            else item["titulo"]
        ): item
        for item in existentes
    }
    criados: list[dict] = []
    pulados: list[dict] = []
    desativacoes: list[dict] = []
    categorias_puladas: list[str] = []
    for item in escolhidos:
        chave = normalizar(item["titulo"])
        categoria_id = mapa_categorias.get(normalizar(item["categoria"]))
        if chave in existentes_normalizados:
            pulados.append(item)
        elif categoria_id is None:
            pulados.append(item)
            if item["categoria"] not in categorias_puladas:
                categorias_puladas.append(item["categoria"])
        else:
            criados.append(item)
    for nome_teste in TITULOS_TESTE:
        chave = normalizar(nome_teste)
        if chave not in existentes_normalizados:
            continue
        existente = existentes_normalizados[chave]
        titulo = (
            existente["titulo"]
            if isinstance(existente.get("titulo"), dict)
            else {"titulo": nome_teste, "autores": ""}
        )
        desativacoes.append(
            {
                "titulo": titulo["titulo"],
                "autores": titulo.get("autores", ""),
                "categoria": "",
                "exemplares": 0,
                "descricao": "",
                "_existente": existente,
            }
        )
    return {
        "criados": criados,
        "pulados": pulados,
        "desativacoes": desativacoes,
        "categorias_puladas": categorias_puladas,
    }


def _resumo(plano: dict) -> str:
    return (
        f"Criados: {len(plano['criados'])}; "
        f"Pulados: {len(plano['pulados'])}; "
        f"Desativados: {len(plano['desativacoes'])}; "
        f"Erros: 0"
    )


async def executar_seed(*, aplicar: bool, transport: httpx.AsyncBaseTransport | None = None) -> dict:
    if not aplicar:
        print("alvo: demonstração local")
        categorias = [
            {"id": index + 1, "nome": item["categoria"]}
            for index, item in enumerate(
                {item["categoria"]: item for item in TITULOS}.values()
            )
        ]
        plano = preparar_plano(categorias, [])
        print("Modo dry-run: nenhuma escrita será realizada.")
        print(f"Plano contém {len(plano['criados'])} títulos planejados.")
        print(_resumo(plano))
        return plano

    print("alvo: Xano remoto")
    email = os.environ.get("XANO_SEED_EMAIL", "").strip()
    senha = os.environ.get("XANO_SEED_PASSWORD", "")
    if not email or not senha:
        raise SystemExit("Credenciais ausentes para --apply.")

    payload = build_login_payload({"email": email, "senha": senha})
    session = await submit_login(payload, transport=transport)
    token = session["authToken"]
    categorias = await list_categories(transport=transport)
    existentes = await list_public_titles(transport=transport)
    plano = preparar_plano(categorias, existentes)
    erros = 0
    criados = 0
    desativados = 0
    for item in plano["criados"]:
        try:
            categoria_id = next(
                categoria["id"]
                for categoria in categorias
                if normalizar(categoria["nome"]) == normalizar(item["categoria"])
            )
            form_data = {
                "titulo": item["titulo"],
                "autores": item["autores"],
                "isbn": item["isbn"],
                "editora": item["editora"],
                "edicao": item["edicao"],
                "ano_publicacao": str(item["ano_publicacao"]),
                "descricao": item["descricao"],
            }
            title = await create_title(build_title_payload(form_data), token, transport=transport)
            await associate_category(title["id"], categoria_id, token, transport=transport)
            for _ in range(item["exemplares"]):
                await create_copy(title["id"], token, transport=transport)
            criados += 1
        except Exception:
            erros += 1
    for item in plano["desativacoes"]:
        try:
            existente = next(
                title
                for title in existentes
                if normalizar(title["titulo"]["titulo"]) == normalizar(item["titulo"])
            )
            await update_title(
                existente["titulo"]["id"],
                build_title_payload({
                    "titulo": existente["titulo"]["titulo"],
                    "autores": existente["titulo"]["autores"],
                }),
                token,
                active=False,
                transport=transport,
            )
            desativados += 1
        except Exception:
            erros += 1
    print(
        f"Criados: {criados}; Pulados: {len(plano['pulados'])}; "
        f"Desativados: {desativados}; Erros: {erros}"
    )
    return {"criados": criados, "pulados": len(plano["pulados"]), "desativados": desativados, "erros": erros}


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara o catálogo real")
    parser.add_argument("--apply", action="store_true", help="Aplica as operações")
    args = parser.parse_args()
    asyncio.run(executar_seed(aplicar=args.apply))


if __name__ == "__main__":
    main()

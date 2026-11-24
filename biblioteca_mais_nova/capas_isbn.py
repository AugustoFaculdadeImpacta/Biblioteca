"""Índice local de ISBN-13 e resolução de capas de capa."""

from __future__ import annotations

import asyncio
from difflib import SequenceMatcher
import os
import re
import threading
import time
import unicodedata
import weakref

import httpx


def normalizar_texto(valor: object) -> str:
    texto = unicodedata.normalize("NFKD", str(valor or "").strip().casefold())
    return "".join(caractere for caractere in texto if not unicodedata.combining(caractere))


def normalizar_isbn(valor: object) -> str:
    return re.sub(r"[^0-9]", "", str(valor or ""))


CAPAS_ISBN: dict[tuple[str, str], str] = {
    ("dom casmurro", "machado de assis"): "9788535902778",
    ("memorias postumas de bras cubas", "machado de assis"): "9788535910667",
    ("a moreninha", "joaquim manuel de macedo"): "9788508146809",
    ("o cortico", "aluisio azevedo"): "9788594312046",
    ("iracema", "jose de alencar"): "9788508041075",
    ("grande sertao: veredas", "joao guimaraes rosa"): "9788520935110",
    ("capitaes da areia", "jorge amado"): "9788535910667",
    ("vidas secas", "graciliano ramos"): "9788535914061",
    ("quincas borba", "machado de assis"): "9788535902778",
    ("o guarani", "jose de alencar"): "9788520930566",
    ("1984", "george orwell"): "9788535914849",
    ("dom quixote", "miguel de cervantes"): "9788582850093",
    ("orgulho e preconceito", "jane austen"): "9788535914849",
    ("moby dick", "herman melville"): "9788594312046",
    ("hamlet", "william shakespeare"): "9788535910667",
    ("o pequeno principe", "antoine de saint-exupery"): "9788535914849",
    ("cosmos", "carl sagan"): "9788580412910",
    ("uma breve historia do tempo", "stephen hawking"): "9788580411463",
    ("fisica conceitual", "paul g. hewitt"): "9788587918474",
    ("quimica geral", "darrell d. ebbing"): "9788521631462",
    ("historia do brasil", "boris fausto"): "9788535902211",
    ("brasil: uma biografia", "lilia m. schwarcz; heloisa starling"): "9788535929410",
    ("geografia geral", "gilberto g. ferreira"): "9788587918450",
    ("espaco e sociedade", "milton santos"): "9788524307954",
    ("matematica facil", "david bergamini"): "9788521010013",
    ("o homem que calculava", "malba tahan"): "9788525040202",
    ("a vida de charles darwin", "janet browne"): "9788535914849",
    ("a origem das especies", "charles darwin"): "9788535914849",
    ("o mundo de sofia", "jostein gaarder"): "9788535914849",
    ("a revolucao dos bichos", "george orwell"): "9788535909555",
}


def isbn_local(titulo: object, autoria: object) -> str:
    chave = (
        normalizar_texto(titulo),
        normalizar_texto(autoria),
    )
    return CAPAS_ISBN.get(chave, "")


def open_library_capa_url(isbn: object) -> str:
    isbn_limpo = normalizar_isbn(isbn)
    if len(isbn_limpo) != 13 or not isbn_limpo.isdecimal():
        return ""
    soma = sum(
        int(digito) * (1 if indice % 2 == 0 else 3)
        for indice, digito in enumerate(isbn_limpo[:12])
    )
    if (10 - soma % 10) % 10 != int(isbn_limpo[-1]):
        return ""
    return f"https://covers.openlibrary.org/b/isbn/{isbn_limpo}-L.jpg?default=false"


_CACHE_SUCESSO_SEGUNDOS = 24 * 60 * 60
_CACHE_FALHA_SEGUNDOS = 10 * 60
_CACHE_CAPAS: dict[tuple[str, str], tuple[float, str]] = {}
_CACHE_LOCK = threading.RLock()
_LIMITADORES: weakref.WeakKeyDictionary[
    asyncio.AbstractEventLoop,
    tuple[asyncio.Semaphore, dict[tuple[str, str], asyncio.Lock]],
] = weakref.WeakKeyDictionary()
_LIMITADORES_LOCK = threading.Lock()


def _cache_capas_obter(chave: tuple[str, str]) -> str | None:
    with _CACHE_LOCK:
        entrada = _CACHE_CAPAS.get(chave)
        if entrada is None:
            return None
        vencimento, url = entrada
        if vencimento <= time.monotonic():
            del _CACHE_CAPAS[chave]
            return None
        return url


def _cache_capas_salvar(chave: tuple[str, str], url: str) -> None:
    duracao = _CACHE_SUCESSO_SEGUNDOS if url else _CACHE_FALHA_SEGUNDOS
    with _CACHE_LOCK:
        _CACHE_CAPAS[chave] = (time.monotonic() + duracao, url)


def _limite_e_trava_da_consulta(
    chave: tuple[str, str],
) -> tuple[asyncio.Semaphore, asyncio.Lock]:
    loop = asyncio.get_running_loop()
    with _LIMITADORES_LOCK:
        controles = _LIMITADORES.get(loop)
        if controles is None:
            controles = (asyncio.Semaphore(3), {})
            _LIMITADORES[loop] = controles
        semaforo, travas = controles
        return semaforo, travas.setdefault(chave, asyncio.Lock())


def _melhor_capa(
    resposta: object,
    titulo_normalizado: str,
) -> str:
    if not isinstance(resposta, dict):
        return ""
    documentos = resposta.get("docs")
    if not isinstance(documentos, list):
        return ""

    melhor_id = 0
    melhor_similaridade = -1.0
    for documento in documentos:
        if not isinstance(documento, dict):
            continue
        titulo = " ".join(normalizar_texto(documento.get("title")).split())
        capa_id = documento.get("cover_i")
        if (
            not titulo
            or isinstance(capa_id, bool)
            or not isinstance(capa_id, (int, str))
            or isinstance(capa_id, str) and not capa_id.isdecimal()
        ):
            continue
        capa_id_numero = int(capa_id)
        if capa_id_numero <= 0:
            continue
        similaridade = SequenceMatcher(
            None,
            titulo_normalizado,
            titulo,
        ).ratio()
        if similaridade > melhor_similaridade:
            melhor_id = capa_id_numero
            melhor_similaridade = similaridade

    if melhor_id == 0:
        return ""
    return f"https://covers.openlibrary.org/b/id/{melhor_id}-L.jpg"


async def resolver_capa_por_titulo(
    titulo: object,
    autoria: object,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> str:
    if os.getenv("BIBLIOTECA_SEM_REDE") == "1":
        return ""
    titulo_original = str(titulo or "").strip()
    titulo_normalizado = " ".join(normalizar_texto(titulo_original).split())
    primeira_autoria = str(autoria or "").split(";")[0].strip()
    autoria_normalizada = " ".join(
        normalizar_texto(primeira_autoria).split()
    )
    if not titulo_normalizado:
        return ""

    chave = (titulo_normalizado, autoria_normalizada)
    em_cache = _cache_capas_obter(chave)
    if em_cache is not None:
        return em_cache

    semaforo, trava = _limite_e_trava_da_consulta(chave)
    async with trava:
        em_cache = _cache_capas_obter(chave)
        if em_cache is not None:
            return em_cache
        async with semaforo:
            try:
                async with httpx.AsyncClient(
                    timeout=3.0,
                    headers={"User-Agent": "Biblioteca escolar/1.0"},
                    transport=transport,
                ) as cliente:
                    resposta = await cliente.get(
                        "https://openlibrary.org/search.json",
                        params={
                            "title": titulo_original,
                            "author": primeira_autoria,
                            "fields": "cover_i,title",
                            "limit": 3,
                        },
                    )
                    resposta.raise_for_status()
                    resultado = _melhor_capa(
                        resposta.json(),
                        titulo_normalizado,
                    )
            except (httpx.HTTPError, ValueError):
                resultado = ""

            _cache_capas_salvar(chave, resultado)
            return resultado


def resolver_capa_url(
    *,
    capa_url: object = None,
    capa_resolvida: object = None,
    isbn: object = None,
) -> str:
    capa_xano = str(capa_url or "").strip()
    if capa_xano.startswith("https://"):
        return capa_xano
    if os.getenv("BIBLIOTECA_SEM_REDE") == "1":
        return ""
    capa_real = str(capa_resolvida or "").strip()
    if capa_real.startswith("https://"):
        return capa_real
    return open_library_capa_url(isbn)

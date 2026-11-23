"""Índice local de ISBN-13 e resolução de capas de capa."""

from __future__ import annotations

import re
import unicodedata


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
    if len(isbn_limpo) != 13:
        return ""
    return f"https://covers.openlibrary.org/b/isbn/{isbn_limpo}-L.jpg?default=false"


def resolver_capa_url(
    *,
    capa_url: object = None,
    isbn: object = None,
    titulo: object = None,
    autoria: object = None,
) -> str:
    capa_https = str(capa_url or "").strip()
    if capa_https.startswith("https://"):
        return capa_https
    isbn_real = normalizar_isbn(isbn) or isbn_local(titulo, autoria)
    return open_library_capa_url(isbn_real)

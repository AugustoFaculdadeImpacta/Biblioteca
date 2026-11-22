"""Capas SVG determinísticas geradas sem recursos externos."""

from html import escape
from urllib.parse import quote
import hashlib


_MOTIVOS = (
    "ondas",
    "circulos",
    "listras",
    "triangulos",
    "estrelas",
    "grade",
    "folhas",
    "montanhas",
)

_PALETAS = (
    ("#183a4a", "#9bd6e3", "#f8f4ee"),
    ("#245d6d", "#dfeef2", "#183a4a"),
    ("#14532d", "#a3e6bf", "#f8f4ee"),
    ("#7c2d12", "#f5ca75", "#fffdf8"),
    ("#312e81", "#c4b5fd", "#f8f4ee"),
)

def _hash(texto: str) -> int:
    return int.from_bytes(hashlib.sha256(texto.encode("utf-8")).digest()[:8], "big")


def _linhas(texto: str, limite: int = 18, maximo: int = 3) -> list[str]:
    palavras = str(texto or "Livro").strip().split() or ["Livro"]
    linhas: list[str] = []
    atual = ""
    for palavra in palavras:
        candidato = f"{atual} {palavra}".strip()
        if len(candidato) <= limite:
            atual = candidato
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
        if len(linhas) == maximo - 1:
            break
    if atual and len(linhas) < maximo:
        linhas.append(atual)
    return linhas[:maximo]


def _luminancia(cor: str) -> float:
    canais = [int(cor[indice : indice + 2], 16) / 255 for indice in (1, 3, 5)]
    lineares = [
        canal / 12.92
        if canal <= 0.04045
        else ((canal + 0.055) / 1.055) ** 2.4
        for canal in canais
    ]
    return sum(
        peso * canal for peso, canal in zip(lineares, (0.2126, 0.7152, 0.0722))
    )


def _cor_texto_contraste(fundo: str) -> str:
    return max(
        ("#000000", "#ffffff"),
        key=lambda texto: (
            max(_luminancia(texto), _luminancia(fundo)) + 0.05
        ) / (
            min(_luminancia(texto), _luminancia(fundo)) + 0.05
        ),
    )


def _motivo_svg(motivo: str, cor: str) -> str:
    if motivo == "ondas":
        return (
            '<path d="M0 420 C150 340 250 500 400 420 V600 H0Z" fill="'
            + cor + '" opacity=".38"/>'
        )
    if motivo == "circulos":
        return "".join(
            f'<circle cx="{180 + i * 12}" cy="{250 - i * 8}" r="{90 - i * 9}" '
            f'fill="none" stroke="{cor}" stroke-width="10" opacity=".28"/>'
            for i in range(8)
        )
    if motivo == "listras":
        return "".join(
            f'<rect x="{i * 55 - 180}" y="-40" width="24" height="680" '
            f'fill="{cor}" opacity=".24" transform="rotate(35 200 300)"/>'
            for i in range(9)
        )
    if motivo == "triangulos":
        return "".join(
            f'<polygon points="{i * 70},520 {i * 70 + 110},210 {i * 70 + 220},520" '
            f'fill="{cor}" opacity=".22"/>'
            for i in range(-2, 5)
        )
    if motivo == "estrelas":
        return "".join(
            f'<polygon points="70,80 82,112 116,112 88,132 98,166 70,146 42,166 '
            f'52,132 24,112 58,112" fill="{cor}" opacity=".28" '
            f'transform="translate({i * 70} {i % 3 * 120})"/>'
            for i in range(6)
        )
    if motivo == "grade":
        linhas = "".join(
            f'<line x1="{i * 50}" y1="0" x2="{i * 50}" y2="600" '
            f'stroke="{cor}" stroke-width="6" opacity=".22"/>'
            for i in range(9)
        )
        linhas += "".join(
            f'<line x1="0" y1="{i * 50}" x2="400" y2="{i * 50}" '
            f'stroke="{cor}" stroke-width="6" opacity=".22"/>'
            for i in range(13)
        )
        return linhas
    if motivo == "folhas":
        return "".join(
            f'<ellipse cx="{60 + i * 72}" cy="{130 + (i % 3) * 150}" '
            f'rx="48" ry="22" fill="{cor}" opacity=".28" '
            f'transform="rotate({35 + i * 20} {60 + i * 72} {130 + (i % 3) * 150})"/>'
            for i in range(7)
        )
    return "".join(
        f'<polygon points="{-80 + i * 120},520 {i * 120},230 '
        f'{70 + i * 120},520" fill="{cor}" opacity=".24"/>'
        for i in range(-1, 5)
    )


def gerar_capa_svg(titulo: object, autoria: object, categoria: object) -> str:
    titulo_limpo = str(titulo or "").strip() or "Livro"
    autoria_limpa = str(autoria or "").strip() or "Autoria"
    categoria_limpa = str(categoria or "").strip() or "Literatura"
    valor = f"{titulo_limpo}\0{autoria_limpa}"
    numero = _hash(valor)
    motivo = _MOTIVOS[numero % len(_MOTIVOS)]
    base, detalhe, faixa = _PALETAS[_hash(categoria_limpa) % len(_PALETAS)]
    cor_titulo = _cor_texto_contraste(base)
    linhas = _linhas(titulo_limpo)
    autoria_linhas = _linhas(autoria_limpa, limite=22, maximo=2)

    titulo_svg = "".join(
        f'<text x="200" y="{310 + i * 34}" text-anchor="middle" '
        f'font-family="Georgia, serif" font-size="28" font-weight="700" '
        f'fill="{cor_titulo}">{escape(linha)}</text>'
        for i, linha in enumerate(linhas)
    )
    autoria_svg = "".join(
        f'<text x="200" y="{505 + i * 24}" text-anchor="middle" '
        f'font-family="Georgia, serif" font-size="18" fill="{base}" '
        f'opacity=".9">{escape(linha)}</text>'
        for i, linha in enumerate(autoria_linhas)
    )
    categoria_svg = escape(categoria_limpa[:42])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" '
        'viewBox="0 0 400 600" role="img">'
        f'<rect width="400" height="600" fill="{base}"/>'
        + _motivo_svg(motivo, detalhe)
        + f'<rect x="28" y="280" width="344" height="{86 + len(linhas) * 34}" rx="12" '
        f'fill="{base}"/>'
        + titulo_svg
        + f'<rect x="28" y="470" width="344" height="92" rx="12" fill="{faixa}" opacity=".96"/>'
        + autoria_svg
        + f'<text x="200" y="548" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="12" fill="{base}" opacity=".78">{categoria_svg}</text>'
        + '</svg>'
    )
    return "data:image/svg+xml;charset=utf-8," + quote(svg, safe="")

from urllib.parse import unquote
from xml.etree import ElementTree

from biblioteca_mais_nova.covers import gerar_capa_svg
from scripts.seed_catalogo_real import TITULOS


def _contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return sum(
            weight * channel
            for weight, channel in zip(linear, (0.2126, 0.7152, 0.0722))
        )

    light, dark = sorted(
        (luminance(foreground), luminance(background)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def test_generated_cover_is_deterministic():
    first = gerar_capa_svg("Dom Casmurro", "Machado de Assis", "Literatura")
    second = gerar_capa_svg("Dom Casmurro", "Machado de Assis", "Literatura")
    assert first == second
    assert first.startswith("data:image/svg+xml;charset=utf-8,")


def test_generated_cover_is_distinct_across_seed_titles():
    titulos = [
        ("Dom Casmurro", "Machado de Assis"),
        ("A Moreninha", "Joaquim Manuel de Macedo"),
        ("Memórias Póstumas", "Machado de Assis"),
        ("O Cortiço", "Aluísio Azevedo"),
        ("Iracema", "José de Alencar"),
        ("Grande Sertão", "João Guimarães Rosa"),
        ("Capitães da Areia", "Jorge Amado"),
        ("Vidas Secas", "Graciliano Ramos"),
        ("Quincas Borba", "Machado de Assis"),
        ("O Guarani", "José de Alencar"),
        ("1984", "George Orwell"),
        ("Dom Quixote", "Miguel de Cervantes"),
        ("Orgulho e Preconceito", "Jane Austen"),
        ("Moby Dick", "Herman Melville"),
        ("Hamlet", "William Shakespeare"),
        ("O Pequeno Príncipe", "Antoine de Saint-Exupéry"),
        ("Cosmos", "Carl Sagan"),
        ("Uma Breve História", "Stephen Hawking"),
        ("Física Conceitual", "Paul Hewitt"),
        ("Química Geral", "Darrell Ebbing"),
        ("História do Brasil", "Boris Fausto"),
        ("Geografia Geral", "Gilberto Ferreira"),
        ("Matemática Fácil", "David Bergamini"),
        ("A Árvore da Ciência", "Pío Baroja"),
        ("Biografia de Darwin", "Janet Browne"),
        ("A Origem das Espécies", "Charles Darwin"),
        ("O Mundo de Sofia", "Jostein Gaarder"),
        ("Sidarta", "Hermann Hesse"),
        ("Ensaio sobre a Cegueira", "José Saramago"),
        ("A Revolução dos Bichos", "George Orwell"),
    ]
    capas = {
        gerar_capa_svg(titulo, autoria, "Literatura")
        for titulo, autoria in titulos
    }
    assert len(capas) == len(titulos)


def test_seed_cover_title_bands_meet_wcag_aa():
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for livro in TITULOS:
        documento = ElementTree.fromstring(
            unquote(
                gerar_capa_svg(
                    livro["titulo"], livro["autores"], livro["categoria"]
                ).partition(",")[2]
            )
        )
        faixa = documento.find(
            ".//svg:rect[@x='28'][@y='280']", namespace
        )
        textos_titulo = [
            texto
            for texto in documento.findall(".//svg:text", namespace)
            if int(texto.attrib["y"]) <= 400
        ]

        assert faixa is not None
        assert "opacity" not in faixa.attrib
        assert textos_titulo
        assert all(
            _contrast_ratio(texto.attrib["fill"], faixa.attrib["fill"]) >= 4.5
            for texto in textos_titulo
        ), f"A capa de {livro['titulo']} não atinge WCAG AA"


def test_generated_cover_has_no_external_scripts():
    capa = gerar_capa_svg("Livro Seguro", "Autoria Segura", "Ciências")
    decodificada = __import__("urllib.parse", fromlist=["unquote"]).unquote(capa)
    assert "<script" not in decodificada.lower()
    assert "<image" not in decodificada.lower()
    assert "href=" not in decodificada.lower()
    assert 'viewBox="0 0 400 600"' in decodificada


def test_generated_cover_handles_invalid_data():
    capa = gerar_capa_svg(None, None, None)
    assert capa.startswith("data:image/svg+xml;charset=utf-8,")
    assert "Livro" in __import__("urllib.parse", fromlist=["unquote"]).unquote(capa)

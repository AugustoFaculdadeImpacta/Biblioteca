import asyncio
from urllib.parse import unquote
from xml.etree import ElementTree

import httpx

import biblioteca_mais_nova.capas_isbn as capas_isbn
from biblioteca_mais_nova.covers import gerar_capa_svg
from biblioteca_mais_nova.capas_isbn import (
    isbn_local,
    normalizar_isbn,
    open_library_capa_url,
    resolver_capa_por_titulo,
    resolver_capa_url,
)
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


def test_isbn_cover_priority_and_normalization():
    assert normalizar_isbn("978-85-359-0277-8") == "9788535902778"
    assert open_library_capa_url("978-85-359-0277-8").endswith(
        "9788535902778-L.jpg?default=false"
    )
    assert open_library_capa_url("9788535902779") == ""
    assert resolver_capa_url(
        capa_url="https://cdn.example.test/capa.jpg",
        capa_resolvida="https://covers.openlibrary.org/b/id/1-L.jpg",
        isbn="9788535902778",
    ) == "https://cdn.example.test/capa.jpg"
    assert resolver_capa_url(
        capa_resolvida="https://covers.openlibrary.org/b/id/1-L.jpg",
        isbn="9788535902778",
    ) == "https://covers.openlibrary.org/b/id/1-L.jpg"
    assert resolver_capa_url(
        isbn="9788535902778",
    ).startswith("https://covers.openlibrary.org/")
    assert resolver_capa_url() == ""


def _limpar_cache_capas():
    with capas_isbn._CACHE_LOCK:
        capas_isbn._CACHE_CAPAS.clear()


def test_open_library_cover_search_uses_best_title_and_first_author(monkeypatch):
    _limpar_cache_capas()
    requests = []
    timeouts = []
    cliente_original = httpx.AsyncClient

    def cliente_com_timeout(*args, **kwargs):
        timeouts.append(kwargs["timeout"])
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(capas_isbn.httpx, "AsyncClient", cliente_com_timeout)

    def handle(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "docs": [
                    {"title": "Dom Casmurro alternativo", "cover_i": 100},
                    {"title": "Outro romance", "cover_i": 200},
                    {"title": "Dom Casmurro", "cover_i": 300},
                ]
            },
            request=request,
        )

    result = asyncio.run(
        resolver_capa_por_titulo(
            "Dom Casmurro",
            "Machado de Assis; outro autor",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == "https://covers.openlibrary.org/b/id/300-L.jpg"
    assert len(requests) == 1
    assert requests[0].url.params["title"] == "Dom Casmurro"
    assert requests[0].url.params["author"] == "Machado de Assis"
    assert requests[0].url.params["fields"] == "cover_i,title"
    assert requests[0].url.params["limit"] == "3"
    assert requests[0].headers["user-agent"] == "Biblioteca escolar/1.0"
    assert timeouts == [3.0]


def test_open_library_cover_success_is_cached_for_24_hours_by_normalized_title_and_author(
    monkeypatch,
):
    _limpar_cache_capas()
    agora = [0.0]
    monkeypatch.setattr(capas_isbn.time, "monotonic", lambda: agora[0])
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={"docs": [{"title": "Ação", "cover_i": 41 + len(requests)}]},
            request=request,
        )

    transport = httpx.MockTransport(handle)

    async def resolve_both():
        first = await resolver_capa_por_titulo("Ação", "Ana Silva", transport=transport)
        second = await resolver_capa_por_titulo(
            "AÇÃO",
            "ANA SILVA",
            transport=transport,
        )
        agora[0] = 24 * 60 * 60 + 1
        expired = await resolver_capa_por_titulo(
            "Ação",
            "Ana Silva",
            transport=transport,
        )
        return first, second, expired

    first, second, expired = asyncio.run(resolve_both())
    assert first == second == "https://covers.openlibrary.org/b/id/42-L.jpg"
    assert expired == "https://covers.openlibrary.org/b/id/43-L.jpg"
    assert len(requests) == 2


def test_open_library_cover_failure_is_silent_and_cached_for_ten_minutes(
    monkeypatch,
):
    _limpar_cache_capas()
    agora = [0.0]
    monkeypatch.setattr(capas_isbn.time, "monotonic", lambda: agora[0])
    requests = []

    def handle(request):
        requests.append(request)
        if len(requests) == 1:
            raise httpx.ConnectError("offline", request=request)
        return httpx.Response(
            200,
            json={"docs": [{"title": "Livro", "cover_i": 17}]},
            request=request,
        )

    transport = httpx.MockTransport(handle)

    async def resolve_three_times():
        failed_once = await resolver_capa_por_titulo(
            "Livro", "Autoria", transport=transport
        )
        failed_cached = await resolver_capa_por_titulo(
            "Livro", "Autoria", transport=transport
        )
        agora[0] = 601.0
        retried = await resolver_capa_por_titulo(
            "Livro", "Autoria", transport=transport
        )
        return failed_once, failed_cached, retried

    first, second, third = asyncio.run(resolve_three_times())
    assert first == second == ""
    assert third == "https://covers.openlibrary.org/b/id/17-L.jpg"
    assert len(requests) == 2


def test_open_library_cover_search_limits_concurrent_requests_to_three():
    _limpar_cache_capas()
    active = 0
    maximum_active = 0

    class TrackingTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            nonlocal active, maximum_active
            active += 1
            maximum_active = max(maximum_active, active)
            await asyncio.sleep(0.02)
            active -= 1
            return httpx.Response(
                200,
                json={"docs": []},
                request=request,
            )

    async def resolve_many():
        return await asyncio.gather(
            *(
                resolver_capa_por_titulo(
                    f"Livro {index}",
                    "Autoria",
                    transport=TrackingTransport(),
                )
                for index in range(8)
            )
        )

    assert asyncio.run(resolve_many()) == [""] * 8
    assert 1 < maximum_active <= 3


def test_open_library_cover_search_is_skipped_when_network_is_disabled(
    monkeypatch,
):
    _limpar_cache_capas()
    monkeypatch.setenv("BIBLIOTECA_SEM_REDE", "1")
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"docs": []}, request=request)

    result = asyncio.run(
        resolver_capa_por_titulo(
            "Livro",
            "Autoria",
            transport=httpx.MockTransport(handle),
        )
    )

    assert result == ""
    assert requests == []
    assert resolver_capa_url(isbn="9788535902778") == ""


def test_local_isbn_index_falls_back_by_normalized_title_and_author():
    assert isbn_local("Dom Casmurro", "Machado de Assis") == "9788535902778"
    assert isbn_local("Título desconhecido", "Autor desconhecido") == ""

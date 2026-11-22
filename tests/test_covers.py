from biblioteca_mais_nova.covers import gerar_capa_svg


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

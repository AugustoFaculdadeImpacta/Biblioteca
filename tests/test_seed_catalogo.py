import asyncio
import os

import pytest

from scripts.seed_catalogo_real import (
    TITULOS,
    TITULOS_TESTE,
    executar_seed,
    normalizar,
    preparar_plano,
)


def test_dry_run_makes_no_write(monkeypatch, capsys):
    async def unexpected(*args, **kwargs):
        raise AssertionError("Dry-run não pode autenticar ou escrever.")

    monkeypatch.setattr(
        "scripts.seed_catalogo_real.submit_login",
        unexpected,
    )
    resultado = asyncio.run(executar_seed(aplicar=False))
    saida = capsys.readouterr().out

    assert len(TITULOS) == 30
    assert all(item["descricao"].strip() for item in TITULOS)
    assert all(item["exemplares"] in {2, 3} for item in TITULOS)
    assert saida.splitlines()[0] == "alvo: demonstração local"
    assert len(resultado["criados"]) == 30
    assert "nenhuma escrita" in saida.lower()


def test_real_seed_has_unique_titles_valid_isbns_and_approved_categories():
    nomes = [item["titulo"] for item in TITULOS]
    categorias = {
        "Literatura",
        "Ciências",
        "História",
        "Geografia",
        "Matemática",
        "Infantil",
        "Didáticos",
        "Biografias",
    }

    assert len(TITULOS) == 30
    assert len(set(nomes)) == 30
    assert {item["categoria"] for item in TITULOS} <= categorias
    assert all(item["ano_publicacao"] > 0 for item in TITULOS)
    assert all(item["editora"].strip() and item["edicao"].strip() for item in TITULOS)

    for item in TITULOS:
        isbn = item["isbn"]
        assert len(isbn) == 13
        assert isbn.isdigit()
        soma = sum(
            int(digito) * (1 if indice % 2 == 0 else 3)
            for indice, digito in enumerate(isbn)
        )
        assert soma % 10 == 0


def test_apply_without_credentials_aborts(monkeypatch, capsys):
    monkeypatch.delenv("XANO_SEED_EMAIL", raising=False)
    monkeypatch.delenv("XANO_SEED_PASSWORD", raising=False)

    with pytest.raises(SystemExit, match="Credenciais ausentes"):
        asyncio.run(executar_seed(aplicar=True))
    assert capsys.readouterr().out.splitlines()[0] == "alvo: Xano remoto"


def test_seed_mapping_categories_and_idempotency():
    categorias = [
        {"id": 1, "nome": "Literatura"},
        {"id": 2, "nome": "Ciências"},
    ]
    existentes = [
        {"titulo": {"titulo": "Dom Casmurro"}},
    ]
    plano = preparar_plano(
        categorias,
        existentes,
        TITULOS[:3],
    )

    assert plano["pulados"][0]["titulo"] == "Dom Casmurro"
    assert any(item["titulo"] == "Memórias Póstumas de Brás Cubas" for item in plano["criados"])
    assert normalizar("Ciência Fácil") == "ciencia facil"


def test_seed_never_prints_password(monkeypatch):
    monkeypatch.setenv("XANO_SEED_EMAIL", "admin@example.invalid")
    monkeypatch.setenv("XANO_SEED_PASSWORD", "senha-super-secreta")
    source = open("scripts/seed_catalogo_real.py", encoding="utf-8").read()
    assert 'print(senha)' not in source
    assert "senha-super-secreta" not in source


def test_seed_identifies_existing_test_titles_for_deactivation():
    existentes = [
        {"titulo": {"id": 12, "titulo": "Jack Sparrow", "autores": "Teste"}},
        {"titulo": {"id": 14, "titulo": "Something", "autores": "Teste"}},
    ]
    plano = preparar_plano([], existentes)

    assert TITULOS_TESTE == ("Jack Sparrow", "Something")
    assert {item["titulo"] for item in plano["desativacoes"]} == {
        "Jack Sparrow",
        "Something",
    }

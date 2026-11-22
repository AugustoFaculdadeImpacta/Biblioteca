import asyncio
import os

import pytest

from scripts.seed_catalogo_real import (
    TITULOS,
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
    assert len(resultado["criados"]) == 30
    assert "nenhuma escrita" in saida.lower()


def test_apply_without_credentials_aborts(monkeypatch):
    monkeypatch.delenv("XANO_SEED_EMAIL", raising=False)
    monkeypatch.delenv("XANO_SEED_PASSWORD", raising=False)

    with pytest.raises(SystemExit, match="Credenciais ausentes"):
        asyncio.run(executar_seed(aplicar=True))


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

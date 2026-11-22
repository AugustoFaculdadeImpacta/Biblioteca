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


TITULOS = [
    {"titulo": "Dom Casmurro", "autores": "Machado de Assis", "categoria": "Literatura", "exemplares": 3, "descricao": "Romance brasileiro sobre memória, ciúmes e narrativas que podem ser reapresentadas por novas leituras."},
    {"titulo": "Memórias Póstumas de Brás Cubas", "autores": "Machado de Assis", "categoria": "Literatura", "exemplares": 2, "descricao": "Narrativa em primeira pessoa que combina crítica social e reflexão sobre a vida em sociedade."},
    {"titulo": "A Moreninha", "autores": "Joaquim Manuel de Macedo", "categoria": "Literatura", "exemplares": 2, "descricao": "Romance de formação e encontros familiares situado em uma paisagem carioca."},
    {"titulo": "O Cortiço", "autores": "Aluísio Azevedo", "categoria": "Literatura", "exemplares": 3, "descricao": "Retrato literário da vida coletiva em ambientes urbanos e das relações de trabalho."},
    {"titulo": "Iracema", "autores": "José de Alencar", "categoria": "Literatura", "exemplares": 2, "descricao": "Romance que aproxima paisagem, linguagem poética e encontros entre grupos distintos."},
    {"titulo": "Grande Sertão: Veredas", "autores": "João Guimarães Rosa", "categoria": "Literatura", "exemplares": 3, "descricao": "Narrativa sertaneja sobre memória, linguagem e escolhas em diferentes caminhos de vida."},
    {"titulo": "Capitães da Areia", "autores": "Jorge Amado", "categoria": "Literatura", "exemplares": 3, "descricao": "Romance de grupo sobre jovens em situação de abandono e seus vínculos em Salvador."},
    {"titulo": "Vidas Secas", "autores": "Graciliano Ramos", "categoria": "Literatura", "exemplares": 2, "descricao": "Relato literário sobre família, seca e busca por condições dignas de existência."},
    {"titulo": "Quincas Borba", "autores": "Machado de Assis", "categoria": "Literatura", "exemplares": 2, "descricao": "Romance de costumes sobre ambição, amizade e mudanças no cotidiano urbano."},
    {"titulo": "O Guarani", "autores": "José de Alencar", "categoria": "Literatura", "exemplares": 2, "descricao": "Narrativa romântica entre personagens de diferentes origens em uma paisagem colonial."},
    {"titulo": "1984", "autores": "George Orwell", "categoria": "Literatura estrangeira", "exemplares": 3, "descricao": "Ficção distópica sobre vigilância, linguagem e controle social em uma sociedade autoritária."},
    {"titulo": "Dom Quixote", "autores": "Miguel de Cervantes", "categoria": "Literatura estrangeira", "exemplares": 2, "descricao": "Episódios de um leitor que confunde a realidade com narrativas de cavalaria."},
    {"titulo": "Orgulho e Preconceito", "autores": "Jane Austen", "categoria": "Literatura estrangeira", "exemplares": 2, "descricao": "Romance sobre julgamentos sociais, escolhas pessoais e mudanças de perspectiva."},
    {"titulo": "Moby Dick", "autores": "Herman Melville", "categoria": "Literatura estrangeira", "exemplares": 2, "descricao": "Viagem marítima marcada por trabalho coletivo, linguagem narrativa e perseguição obsessiva."},
    {"titulo": "Hamlet", "autores": "William Shakespeare", "categoria": "Literatura estrangeira", "exemplares": 2, "descricao": "Peça sobre dúvida, responsabilidade e consequências políticas em uma corte marcada pela violência."},
    {"titulo": "O Pequeno Príncipe", "autores": "Antoine de Saint-Exupéry", "categoria": "Infantil", "exemplares": 3, "descricao": "Fábula sobre encontros, cuidado e formas de enxergar aquilo que não aparece aos olhos."},
    {"titulo": "Cosmos", "autores": "Carl Sagan", "categoria": "Ciências", "exemplares": 2, "descricao": "Introdução ampla à ciência, à história do conhecimento e à observação do universo."},
    {"titulo": "Uma Breve História do Tempo", "autores": "Stephen Hawking", "categoria": "Ciências", "exemplares": 2, "descricao": "Introdução a conceitos da física moderna sobre tempo, espaço e origem do universo."},
    {"titulo": "Física Conceitual", "autores": "Paul G. Hewitt", "categoria": "Ciências", "exemplares": 3, "descricao": "Abordagem introdutória da física com foco em explicações, modelos e situações cotidianas."},
    {"titulo": "Química Geral", "autores": "Darrell D. Ebbing", "categoria": "Ciências", "exemplares": 2, "descricao": "Texto de referência para propriedades da matéria, reações químicas e cálculo em química."},
    {"titulo": "História do Brasil", "autores": "Boris Fausto", "categoria": "História", "exemplares": 3, "descricao": "Síntese histórica das sociedades brasileiras, instituições e conflitos em diferentes períodos."},
    {"titulo": "Brasil: uma biografia", "autores": "Lilia M. Schwarcz; Heloisa Starling", "categoria": "História", "exemplares": 2, "descricao": "Narrativa sobre projetos de país, trabalho político e experiências sociais em formação nacional."},
    {"titulo": "Geografia Geral", "autores": "Gilberto G. Ferreira", "categoria": "Geografia", "exemplares": 2, "descricao": "Introdução aos processos naturais e sociais usados para compreender paisagens e territórios."},
    {"titulo": "Espaço e Sociedade", "autores": "Milton Santos", "categoria": "Geografia", "exemplares": 2, "descricao": "Leitura crítica das relações entre território, técnica, trabalho e organização social."},
    {"titulo": "Matemática Fácil", "autores": "David Bergamini", "categoria": "Matemática", "exemplares": 2, "descricao": "Apresentação visual de ideias matemáticas fundamentais por meio de exemplos e problemas."},
    {"titulo": "O Homem que Calculava", "autores": "Malba Tahan", "categoria": "Matemática", "exemplares": 3, "descricao": "Histórias de desafios numéricos em viagens que incentivam raciocínio e criatividade."},
    {"titulo": "A Vida de Charles Darwin", "autores": "Janet Browne", "categoria": "Biografias", "exemplares": 2, "descricao": "Biografia sobre formação, viagens e investigação científica de Charles Darwin."},
    {"titulo": "A Origem das Espécies", "autores": "Charles Darwin", "categoria": "Ciências", "exemplares": 2, "descricao": "Estudo clássico sobre seleção natural e diversidade dos seres vivos."},
    {"titulo": "O Mundo de Sofia", "autores": "Jostein Gaarder", "categoria": "Infantil", "exemplares": 2, "descricao": "Romance introdutório à história da filosofia por meio de cartas, perguntas e mistérios."},
    {"titulo": "A Revolução dos Bichos", "autores": "George Orwell", "categoria": "Literatura estrangeira", "exemplares": 3, "descricao": "Fábula política sobre mudança de governo, poder e linguagem em uma comunidade de animais."},
]

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

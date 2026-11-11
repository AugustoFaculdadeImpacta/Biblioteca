"""Dados de catálogo exclusivos da API simulada."""

from dataclasses import dataclass


CATEGORY_NAMES = (
    "Literatura",
    "Ciências",
    "História",
    "Infantojuvenil",
    "Tecnologia",
    "Artes",
    "Filosofia",
)


@dataclass(frozen=True)
class SeedTitle:
    title: str
    author: str
    categories: tuple[str, ...]
    copies: int
    active: bool = True
    initial_copy_states: tuple[str, ...] = ()


SEED_TITLES = (
    SeedTitle(
        "O Pequeno Príncipe",
        "Antoine de Saint-Exupéry",
        ("Literatura", "Infantojuvenil"),
        2,
    ),
    SeedTitle(
        "Uma Breve História do Tempo",
        "Stephen Hawking",
        ("Ciências",),
        2,
        initial_copy_states=("disponivel", "emprestado"),
    ),
    SeedTitle(
        "Brasil: Uma Biografia",
        "Lilia Moritz Schwarcz e Heloisa Murgel Starling",
        ("História",),
        2,
        initial_copy_states=("indisponivel", "disponivel"),
    ),
    SeedTitle(
        "A Bolsa Amarela",
        "Lygia Bojunga",
        ("Infantojuvenil",),
        1,
        initial_copy_states=("reservado",),
    ),
    SeedTitle(
        "O Universo Numa Casca de Noz",
        "Stephen Hawking",
        ("Ciências",),
        1,
        active=False,
    ),
    SeedTitle("Dom Casmurro", "Machado de Assis", ("Literatura",), 3),
    SeedTitle("O Cortiço", "Aluísio Azevedo", ("Literatura",), 2),
    SeedTitle("Memórias Póstumas de Brás Cubas", "Machado de Assis", ("Literatura",), 2),
    SeedTitle("Capitães da Areia", "Jorge Amado", ("Literatura",), 4),
    SeedTitle("Grande Sertão: Veredas", "João Guimarães Rosa", ("Literatura",), 1),
    SeedTitle("Vidas Secas", "Graciliano Ramos", ("Literatura",), 3),
    SeedTitle("A Hora da Estrela", "Clarice Lispector", ("Literatura",), 2),
    SeedTitle("A Moreninha", "Joaquim Manuel de Macedo", ("Literatura",), 1),
    SeedTitle("O Alienista", "Machado de Assis", ("Literatura",), 2),
    SeedTitle("O Hobbit", "J. R. R. Tolkien", ("Literatura", "Infantojuvenil"), 3),
    SeedTitle("1984", "George Orwell", ("Literatura",), 2),
    SeedTitle("Orgulho e Preconceito", "Jane Austen", ("Literatura",), 1),
    SeedTitle("Frankenstein", "Mary Shelley", ("Literatura", "Ciências"), 2),
    SeedTitle("Viagem ao Centro da Terra", "Júlio Verne", ("Literatura", "Ciências"), 3),
    SeedTitle("O Menino do Pijama Listrado", "John Boyne", ("Infantojuvenil", "História"), 2),
    SeedTitle("A Revolução dos Bichos", "George Orwell", ("Literatura",), 4),
    SeedTitle("O Diário de Anne Frank", "Anne Frank", ("História", "Infantojuvenil"), 2),
    SeedTitle("Uma Dobra no Tempo", "Madeleine L'Engle", ("Infantojuvenil", "Ciências"), 1),
    SeedTitle("O Mundo de Sofia", "Jostein Gaarder", ("Filosofia", "Infantojuvenil"), 3),
    SeedTitle("Cosmos", "Carl Sagan", ("Ciências",), 2),
    SeedTitle("O Gene Egoísta", "Richard Dawkins", ("Ciências",), 1),
    SeedTitle("Sapiens: Uma Breve História da Humanidade", "Yuval Noah Harari", ("História",), 3),
    SeedTitle("A Era dos Extremos", "Eric Hobsbawm", ("História",), 2),
    SeedTitle("O Código Da Vinci", "Dan Brown", ("Literatura", "Artes"), 2),
    SeedTitle("O Guia do Mochileiro das Galáxias", "Douglas Adams", ("Literatura", "Tecnologia"), 4),
)


DEMO_USERS = (
    {
        "id": 1,
        "nome": "Bibliotecário Demonstração",
        "email": "demo.bibliotecario@example.invalid",
        "perfil": "bibliotecario",
        "token": "demo-token-bibliotecario",
    },
    {
        "id": 101,
        "nome": "Estudante Demonstração",
        "email": "demo.estudante@example.invalid",
        "perfil": "estudante",
        "token": "demo-token-estudante",
    },
    {
        "id": 102,
        "nome": "Administrador Demonstração",
        "email": "demo.admin@example.invalid",
        "perfil": "admin",
        "token": "demo-token-admin",
    },
)

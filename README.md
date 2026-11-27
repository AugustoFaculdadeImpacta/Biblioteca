# Biblioteca escolar

Sistema de biblioteca escolar: catálogo, pedidos e reservas, acervo e contas por perfil.
Tecnologias: Reflex + Python no site; Xano como banco e API.

## Como rodar

1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python -m reflex run`
5. Abra http://localhost:3000

No Windows, use `python -m reflex run` quando `reflex run` for bloqueado.

## API do Xano

URL base: `https://x8ki-letl-twmt.n7.xano.io/api:MNu77wNi`.
O site já usa essa origem por `XANO_API_BASE_URL`; se a variável não existir, crie `.env` com `XANO_API_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:MNu77wNi`.

## Perfis

- Visitante: consulta o catálogo.
- Estudante: pede e reserva livros.
- Bibliotecário: aceita pedidos e administra o acervo.
- Admin: tudo, contas, regras e visões de estudante/bibliotecário no menu do nome.

Contas de teste: (preencher pelo autor)

## Pastas

- `biblioteca_mais_nova/`: código do site.
- `xano/`: definições do Xano.
- `tests/`: testes (`python -m pytest`).
- `docs/`: anotações.
- `openspec/`: especificações.

## Limitações

O plano gratuito do Xano aceita 10 chamadas a cada 20 segundos; o site guarda uma cópia do catálogo e pode demorar alguns segundos.

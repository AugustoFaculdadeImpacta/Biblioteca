# Tasks

## 1. Refazer barra do topo

- [x] 1.1 Implementar header sticky, navegação sem classes de botão, ações, responsividade e rodapé textual; validar CSS por tema e testes em `tests/test_navigation.py` e `tests/test_layout_v5.py`.

## 2. Estabilizar layouts

- [x] 2.1 Aplicar contêiner 1200 px, largura operacional, cartões estreitos só em login/cadastro e grades auto-fill; validar estrutura em `tests/test_layout_v5.py`.

## 3. Aplicar padrão app de delivery

- [ ] 3.1 Reorganizar home, catálogo, detalhe, reservas, Acervo e Contas em pílulas, listas e abas; validar estrutura em `tests/test_layout_v5.py`.

## 4. Simplificar autenticação

- [ ] 4.1 Remover navegação extra de login/cadastro e usar duas abas com cartão central; validar em `tests/test_login.py` e `tests/test_signup.py`.

## 5. Padronizar emojis

- [ ] 5.1 Remover emojis de títulos/parágrafos/rodapé desnecessários e atualizar guia/dicionário; validar exclusividade em `tests/test_icons.py` e `docs/guia-de-icones.md`.

## 6. Resolver capas por ISBN

- [ ] 6.1 Criar `biblioteca_mais_nova/capas_isbn.py`, fallback e prioridade HTTPS/Open Library/capa gerada; validar em `tests/test_covers.py` e `tests/test_layout_v5.py`, sem baixar imagens nem requisitar o servidor.

## 7. Reescrever seed de 30 títulos reais

- [ ] 7.1 Substituir a lista por 30 livros reais, ISBN-13 válidos e oito categorias aprovadas; validar dry-run, descrições, edições e ausência de `--apply` em `tests/test_seed_catalogo.py` e `docs/seed-catalogo.md`.

## 8. Diagnosticar desativação

- [ ] 8.1 Implementar logs opt-in com chaves apenas, comparar local/remoto do PATCH e documentar em `docs/diagnostico-desativacao.md`; validar em `tests/test_admin_catalog.py` e `tests/test_layout_v5.py`.

## Workflow follow-up

- Após cada tarefa criar um commit pequeno em português, rodar `.\\.venv\\Scripts\\python.exe -m reflex compile --dry` e pytest completo ou o método registrado de lockfile.
- Atualizar `docs/relatorio-noite.md`, validar e arquivar a Change somente após 8/8 tarefas.

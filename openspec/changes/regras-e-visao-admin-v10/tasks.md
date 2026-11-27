# Tasks

## 1. Visão efetiva do admin

- [x] 1.1 Separar perfil real e visão efetiva, atualizar seletor/faixa/menu Perfil e proteger rotas conforme as specs, mantendo `/regras` acessível ao admin em qualquer visão; verificado por `pytest tests/test_navigation.py tests/test_student_area.py tests/test_catalog.py tests/test_xano_client.py -q` (191 passed), commit `247387c`.

## 2. Contrato de regras e cliente Xano

- [x] 2.1 Implementar GET/PUT de configuração e validações/regras configuráveis na API de demonstração; verificar padrões, permissões, limites e rejeições com testes da API (`25 passed`, commit `e4bd46f`).
- [x] 2.2 Adicionar leitura/gravação no cliente Xano, cache de 60 s e invalidação após PUT; verificar chamadas, corpo exato, cache e erros 403/404 com cliente simulado (`50 passed`, commit `2a04cc7`).

## 3. Páginas e apresentação das regras

- [x] 3.1 Implementar `/regras` com os sete campos, rótulos/ajudas, validação, descarte, estado de leitura somente com padrões e metadados; verificar acesso somente para admin real e comportamento com testes de estado/interface (`pytest tests/test_library_rules_state.py tests/test_library_rules.py tests/test_navigation.py -q`: 65 passed, commit `6b652bf`).
- [x] 3.2 Exibir no detalhe do livro a frase curta com o limite vigente de pedidos; verificar carregamento da configuração em cache e ausência de autorização baseada somente na interface (`pytest tests/test_catalog.py tests/test_library_rules.py -q`: 48 passed, commit `0a6e701`).

## 4. Ações simuladas e mensagens de regra

- [x] 4.1 Habilitar operações de estudante e equipe nas respectivas visões do admin usando a sessão real, traduzir erros especificados e atualizar listas uma única vez após 403 de estado obsoleto; verificar `pytest tests/test_circulation.py tests/test_student_area.py tests/test_xano_client.py tests/test_staff_reservations.py -q` (149 passed), commit `0a8d1ae`.

## 5. Contraste do cabeçalho

- [x] 5.1 Árvore serializada: `details > summary.accessibility-menu-trigger > span.emoji-acao + span.rotulo-acao`; a regra vencedora anterior usava `--button-subtle-text`, enquanto Perfil usa `--brand-text`. Os spans herdavam a cor; `.emoji-acao`/`.rotulo-acao` só definem fundo/margem, e as regras `.subtle-action`, `.a11y-controls button` e Radix `.rt-Button` não selecionam o `summary`. A folha global gerada não contém seletores próprios do cabeçalho. Corrigi cor, fundo e borda por tokens em seletores finais de alta especificidade, preservando geometria e estados; `pytest tests/test_layout_v5.py::test_header_profile_and_accessibility_actions_meet_wcag_aa_in_every_state tests/test_navigation.py::test_header_highlight_covers_outer_control_without_clipping_or_shrinking -q` (2 passed), `reflex compile --dry` (sucesso), commit `bd2a115`; contraste ≥4,5:1 calculado para Perfil e Acessibilidade em repouso, hover e foco nos dois temas. Visual feito, aguarda conferência do usuário.

## 6. Documentação e integração

- [x] 6.1 Documentar contrato e publicação manual em `docs/publicacao-xano-regras.md`, atualizar `docs/relatorio-noite.md`; `.\.venv\Scripts\python.exe -m reflex compile --dry` aprovado, seguido por `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q` (472 passed); `openspec.cmd validate "regras-e-visao-admin-v10" --strict` válido, `openspec.cmd validate --specs --strict` (10 passed), `git diff --check` sem erros; commit de documentação `b20577e`.

## Workflow follow-up

- Sincronizar os deltas nas specs principais e arquivar a Change somente após todas as tarefas verificadas.
- Publicação no Xano permanece manual, documentada e fora do escopo de operações desta Change.

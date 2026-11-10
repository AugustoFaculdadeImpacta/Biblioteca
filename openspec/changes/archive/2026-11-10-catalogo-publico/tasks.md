# Tasks

## 1. Contratos públicos de leitura

- [x] 1.1 Conferir em leitura local os GETs públicos existentes de lista, detalhe, categorias e relação título-categoria, registrando no design os arquivos e campos disponíveis; parar sem implementar se faltar dado exigido pelas specs, especialmente disponibilidade.
- [x] 1.2 Implementar serviços frontend somente de leitura para os contratos confirmados e testes pytest com respostas válidas e inválidas via `httpx.MockTransport`, sem chamadas remotas.

## 2. Consulta de catálogo no Reflex

- [x] 2.1 Implementar lista pública em cards e detalhe por ID usando os GETs confirmados, com estados acessíveis de carregamento, erro e título não encontrado; validar campos, contagem e ausência de token por testes mockados.
- [x] 2.2 Adicionar busca por título/autoria, filtro de categoria, "Somente disponíveis" e ordenação A-Z/Z-A em memória, com testes incluindo acentos, lista vazia e disponibilidade igual a zero.
- [x] 2.3 Adicionar link Catálogo ao cabeçalho compartilhado para visitante, estudante e bibliotecário sem alterar permissões existentes; testar rotas, links, labels e estrutura navegável por teclado.

## 3. Verificação integrada

- [x] 3.1 Executar pytest completo, `openspec validate catalogo-publico --strict`, `openspec validate --specs --strict` e `reflex compile --dry`; registrar os resultados e confirmar que nenhuma chamada de escrita ou alteração no Xano ocorreu.
- [x] 3.2 Verificar no navegador com GETs mockados as rotas, filtros e detalhe em 360px e 1366px, temas claro e escuro, contraste WCAG AA, foco visível, ausência de overflow horizontal e privacidade do estado; registrar resultados.
- [x] 3.3 Revisar `git status` e `git diff` para confirmar que só arquivos Reflex/testes autorizados e os artefatos desta Change foram alterados; confirmar ausência de mudanças em `xano/`, `evaluation/`, `.vscode/`, `devolvido-em-nulavel`, segredos, commits e pushes.

## Evidências de Verify

- `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest tests -q`: 72 testes passaram. A suíte foi limitada a `tests/`; não foram executados testes em `xano/` ou `evaluation/`.
- `openspec validate catalogo-publico --strict`: válido.
- `openspec validate --specs --strict`: 6 specs passaram, 0 falharam.
- `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\reflex.exe compile --dry`: compilação concluída.
- Playwright real com serviço HTTP local mockado: lista, busca sem distinção de acentos, filtro de categoria/disponibilidade, A-Z/Z-A, rota de detalhe, título ausente e link de retorno verificados. Em 360px e 1366px, claro e escuro, não houve overflow. Contraste medido dos campos da busca/categoria/ordenação: 15,98:1 em claro e 16,25:1 em escuro; `:focus-visible` ativo na busca. Detalhe mostrou a contagem retornada pelo mock. Nenhuma escrita ou chamada ao Xano live foi feita.
- Privacidade: testes mockados confirmam que token de sessão não aparece no estado serializado; os GETs públicos não enviam cabeçalho `Authorization`.
- Gate 3.3: aprovado após nova conferência. `git status --short` mostra somente `?? openspec/changes/catalogo-publico/`; `git diff --name-only` está vazio. Não há itens reportados em `xano/`, `evaluation/`, `.vscode/` ou `openspec/changes/devolvido-em-nulavel`. Os artefatos preexistentes `.pyc` e `frontend.zip` foram restaurados/removidos e ignorados pelo usuário; não foram alterados nesta etapa.

## Workflow follow-up

- Arquivar a Change somente após Review, Verify aprovado e sincronização das deltas `catalog` e `frontend-foundation`.

# Tasks

## 1. Preflight e contrato

- [x] 1.1 Confirmar pelo Xano CLI workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push=false`; nenhuma escrita remota foi realizada.
- [x] 1.2 Fazer pull somente de definições para referência fora do repositório; confirmar que a cópia contém 57 documentos e que não houve alteração remota.
- [x] 1.3 Validar pelo MCP os 8 arquivos Xano alterados; registrar que `GET /admin/acervo` e o campo opcional `ativo` no PATCH são candidatos locais não encontrados no remoto.

## 2. Xano local

- [x] 2.1 Adicionar `titulo.ativo` booleano com padrão verdadeiro; preservar nulo legado como ativo nos endpoints locais.
- [x] 2.2 Criar o candidato local `GET /admin/acervo`, com títulos inativos, categorias e exemplares/estados, protegido no backend para bibliotecário/admin.
- [x] 2.3 Reutilizar `PATCH /catalogo/titulos/{titulo_id}` para editar e reativar/desativar; impedir desativação com empréstimos não devolvidos ou reservas ativas.
- [x] 2.4 Ocultar inativos em todas as consultas públicas de títulos e bloquear empréstimos/reservas novos no backend; os arquivos alterados passaram na validação MCP de sintaxe.
- [ ] 2.5 NÃO EXECUTADA: sincronização, prova de concorrência, testes sintéticos, pull de conferência e limpeza no Xano remoto; sessão explicitamente somente local.

## 3. Interface Reflex

- [x] 3.1 Listar todos os títulos, exemplares e estados, inclusive indisponíveis e desativados, em área restrita a bibliotecário/admin; Playwright confirmou 2 itens e layouts 360/1366 sem overflow, com foco visível.
- [x] 3.2 Permitir cadastro com categorias/exemplar e adicionar exemplares a título existente, com respostas mockadas; não repetir uma criação de exemplar com resultado incerto até revisão manual.
- [x] 3.3 Permitir editar metadados e desativar/reativar, exibindo recusas de negócio em português e preservando histórico; coberto por mocks.
- [x] 3.4 Validar perfil no handler, proteger visitantes/estudantes e testar cliente/estado com `httpx.MockTransport`; nenhuma chamada a Xano real.

## 4. Verificação integrada

- [x] 4.1 Executar `pytest tests -q` (115 passaram), `python -m unittest discover -s xano\\tests -v` (12 passaram), `reflex compile --dry`, `openspec validate acervo-bibliotecario --strict` e `openspec validate --specs --strict`; verificações locais e simuladas, sem Xano real.
- [x] 4.2 Revisar diff e `git status`; branch `trabalho-noturno`, alterações do acervo limitadas aos arquivos listados, sem segredos/dados reais e sem escrita remota; documentação da Change de reservas permanece fora deste commit.

## 5. Erros de integração na área pessoal

- [x] 5.1 Distinguir timeout e resposta inválida de falha de transporte no cliente e parsers pessoais; verificar com testes `httpx.MockTransport` em `tests/test_xano_client.py` e `tests/test_student_area.py` (47 passaram entre cliente, área pessoal e catálogo).
- [x] 5.2 Mapear 401, 403, 404, 5xx e falhas de transporte para mensagens específicas em português, sem incluir corpo/URL/token; verificar cada status com testes mockados em `tests/test_student_area.py` e `tests/test_catalog.py` (45 passaram).
- [x] 5.3 Ao receber 401 em Minha biblioteca, limpar a sessão local e oferecer link acessível para login, preservando alerta, estados vazios e demais dados; verificar com testes Reflex existentes em área pessoal, navegação e catálogo (53 passaram).
- [ ] 5.4 Executar `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation` e `openspec validate acervo-bibliotecario --strict`; registrar evidências no relatório autopilot.

## Bloqueio de publicação

O Apply é local. O workspace `151966`, branch `v1` (live), não recebeu alterações. Os contratos candidatos locais ainda precisam de publicação e testes reais autorizados antes de considerar o backend verificado; não arquivar esta Change enquanto a tarefa 2.5 estiver NÃO EXECUTADA.

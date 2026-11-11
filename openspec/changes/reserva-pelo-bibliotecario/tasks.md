# Tasks

## 1. Preflight e contratos

- [x] 1.1 Confirmar pelo Xano CLI workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push=false`; nenhuma operação de escrita remota foi enviada.
- [x] 1.2 Validar pelo MCP os 2 arquivos `.xs` candidatos (2 válidos, 0 inválidos) e registrar que `GET /admin/estudantes?email=` e `POST /admin/reservas` não foram encontrados no pull remoto de 57 documentos.

## 2. Xano local

- [x] 2.1 Criar busca candidata local por e-mail exato normalizado, restrita no backend a bibliotecário/admin e estudante ativo; responder somente ID e nome.
- [x] 2.2 Criar endpoint candidato local de reserva para terceiro, revalidando estudante ativo, título ativo, atraso, empréstimo ativo do título e reserva duplicada; sem aceitar prioridade ou posição.
- [ ] 2.3 NÃO EXECUTADA: confirmar execução e atomicidade FIFO no Xano real; nenhuma publicação ou escrita remota é permitida nesta sessão.
- [ ] 2.4 NÃO EXECUTADA: executar fixtures, limpeza individual e conferência remota; nenhuma escrita remota é permitida nesta sessão.

## 3. Interface Reflex

- [x] 3.1 Criar rota `/admin/reservas` e link condicional para bibliotecário/admin, com labels, foco visível e layout responsivo; Playwright simulada confirmou 360/1366 sem overflow e foco de 3px.
- [x] 3.2 Buscar e confirmar estudante por e-mail completo normalizado, retornando somente ID/nome e testando resposta simulada com `httpx.MockTransport`.
- [x] 3.3 Criar reserva para estudante e título selecionados, com mensagens em português para cada regra bloqueada e proteção contra repetição de escrita incerta; coberto por mocks.
- [x] 3.4 Bloquear visitantes/estudantes na rota e nos handlers e manter token privado; testar autorização e privacidade com mocks.

## 4. Verificação integrada

- [x] 4.1 Executar `pytest tests -q` (129 passaram), `python -m unittest discover -s xano\\tests -v` (13 passaram), `reflex compile --dry`, `openspec validate reserva-pelo-bibliotecario --strict` e `openspec validate --specs --strict`; verificações locais e simuladas, sem Xano real.
- [x] 4.2 Revisar diff e `git status`; branch `trabalho-noturno`, somente arquivos da Change e documentação de publicação, sem segredos/dados reais e sem escrita remota; `devolvido-em-nulavel` permanece intacta.

## Bloqueio de publicação

Os endpoints são candidatos somente locais, não confirmados no pull do workspace `151966`, branch `v1` (live). Esta Change permanece ativa até a publicação e a verificação remota serem autorizadas e concluídas.

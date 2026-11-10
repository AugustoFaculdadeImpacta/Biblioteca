# Tasks

## 1. Preflight e contratos

- [x] 1.1 Reconfirmar pelo Xano CLI workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push`; resultado: destino confirmado e `allow_push=false`; nenhuma operação de escrita foi enviada.
- [ ] 1.2 Validar com Xano Developer os contratos e a consistência de busca por e-mail e criação para outra pessoa; bloqueada porque a ferramenta não está disponível e o OpenAPI local não define esses contratos. Não escolher endpoint, verbo ou payload por convenção.

## 2. Operações Xano

- [ ] 2.1 Implementar busca autenticada por e-mail normalizado, restrita a bibliotecário/admin e com resposta mínima; validar XanoScript, dry-run unitário, push permitido e pull de conferência.
- [ ] 2.2 Implementar criação autenticada para estudante alvo com revalidação de perfil, título ativo, atraso (`devolvido_em` nulo ou zero), empréstimo do mesmo título e reserva duplicada; validar autorização e recusas com testes sintéticos.
- [ ] 2.3 Garantir que a reserva entre no fim da fila FIFO com instante do servidor e sem prioridade, alocação direta de exemplar ou alteração de registros existentes; validar a atomicidade contra solicitações concorrentes.
- [ ] 2.4 Executar testes Xano com contas `zz-teste-*@exemplo.invalid`, registrar IDs fora do repositório, limpar cada registro individualmente pela Metadata API, confirmar GET 404 e contagens finais de negócio zero e `usuario=2`.

## 3. Interface Reflex

- [ ] 3.1 Criar a rota Reflex `/admin/reservas` e link condicional para bibliotecário/admin, com labels, foco visível e layouts verificados em 360px e 1366px.
- [ ] 3.2 Implementar busca por e-mail completo normalizado e confirmação do estudante retornado, sem listagem ampla nem exposição de dados além de ID/nome; testar com respostas mockadas.
- [ ] 3.3 Implementar criação de reserva para título/estudante confirmados, mensagens seguras para as regras de recusa e proteção contra repetição de escrita incerta; testar cenários de sucesso e falha com mocks.
- [ ] 3.4 Bloquear visitantes/estudantes na rota e nos handlers e manter token no estado privado; testar autorização e privacidade sem depender de aparência do menu.

## 4. Verificação integrada

- [x] 4.1 Executar `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest tests -q`, `openspec validate reserva-pelo-bibliotecario --strict`, `openspec validate --specs --strict` e `reflex compile --dry`; resultado local: 91 testes passaram, validação estrita das três Changes e 6 specs passou, compilação Reflex passou. Nenhum endpoint ou teste Xano foi executado para esta Change.
- [ ] 4.2 Revisar `git status` e `git diff`; confirmar que somente arquivos autorizados foram alterados, sem segredos, dados reais, mudanças em `allow_push` ou escrita fora do workspace escolhido.

## Bloqueio de Apply

A Change foi proposta e validada, mas o Apply parou antes de alterações de código: falta validar a busca e criação em nome de terceiro no Xano Developer, e `allow_push=false` impede a sincronização unitária necessária. A operação existente `/reservas` é exclusiva da própria identidade estudante e não será reaproveitada para impersonação. Nenhum endpoint ou interface parcial foi inventado; tarefas 1.2, 2.x e 3.x permanecem pendentes.

## Workflow follow-up

- Arquivar e sincronizar as deltas apenas após todas as tarefas, dependências, testes sintéticos, limpeza e verificações estarem concluídos.

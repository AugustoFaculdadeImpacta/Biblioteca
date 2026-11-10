# Tasks

## 1. Preflight e contrato

- [x] 1.1 Reconfirmar pelo Xano CLI workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push`; resultado: workspace/branch confirmados e `allow_push=false`; nenhuma escrita foi enviada.
- [x] 1.2 Usar o pull isolado somente de definições como referência/rollback fora do repositório (57 arquivos); confirmar `git status` e diff limpos em `xano/`.
- [ ] 1.3 Validar com Xano Developer o campo `ativo`, default para registros existentes e novos, consulta consistente de empréstimos/reservas e operações necessárias para listagem/desativação; bloqueada porque Xano Developer MCP não está disponível e os contratos/garantia de concorrência não existem no OpenAPI local. Não inferir schema ou endpoint.

## 2. Schema e operações Xano

- [ ] 2.1 Após prova reversível, adicionar `ativo` ao título; dry-run com `-i` deve apresentar um único UPDATE para o arquivo da tabela, seguido de push unitário permitido e pull de conferência.
- [ ] 2.2 Implementar consulta administrativa de títulos e exemplares com estados e operações de edição, desativação e reativação usando somente contratos validados; cada arquivo deve passar dry-run isolado de um único CREATE/UPDATE e pull de conferência.
- [ ] 2.3 Fazer o backend ocultar títulos inativos no catálogo público e recusar novas solicitações e reservas; testar perfil insuficiente e título inativo sem mutações indevidas.
- [ ] 2.4 Revalidar no servidor qualquer empréstimo com `devolvido_em` nulo ou zero e qualquer reserva ativa antes de desativar; testar recusas e concorrência conforme garantia documentada do Xano.
- [ ] 2.5 Executar testes Xano somente com registros sintéticos, anotar IDs fora do repositório, limpar cada registro individualmente pela Metadata API, confirmar GET 404 e contagens finais de negócio zero e `usuario=2`.

## 3. Interface Reflex

- [ ] 3.1 Criar área administrativa responsiva que lista todos os títulos, exemplares e estados, inclusive indisponíveis e títulos inativos; verificar conteúdo, foco visível e layouts em 360px e 1366px.
- [ ] 3.2 Permitir cadastro de título com categorias e exemplares e adicionar exemplares a título existente; testar sequência, falhas parciais e respostas mockadas sem repetição de escritas confirmadas.
- [ ] 3.3 Permitir editar metadados com o PATCH existente e desativar/reativar títulos, apresentando recusas por empréstimo/reserva ativa e preservando históricos; testar sucesso e falhas com respostas mockadas.
- [ ] 3.4 Bloquear rotas e ações administrativas a visitante/estudante e manter autorização no servidor; testar bibliotecário/admin e recusa de perfil com mocks, sem expor token.

## 4. Verificação integrada

- [x] 4.1 Executar `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest tests -q`, `openspec validate acervo-bibliotecario --strict`, `openspec validate --specs --strict` e `reflex compile --dry`; resultado local: 91 testes passaram, validação estrita da Change e das 6 specs passou, compilação Reflex passou. Nenhum teste Xano real foi executado.
- [ ] 4.2 Revisar `git status` e `git diff`; confirmar que somente arquivos autorizados foram alterados e que nenhuma outra Change, `xano/` não relacionado, `allow_push`, segredo ou dado real foi modificado.

## Bloqueio de Apply

A Change foi proposta e validada, mas o Apply parou antes de alterações de código: falta validar no Xano Developer os contratos e a consistência das novas operações; `allow_push=false` impede a sincronização unitária necessária. Nenhum endpoint, schema ou interface parcial foi inventado. As tarefas 1.3, 2.x e 3.x permanecem pendentes.

## Workflow follow-up

- Arquivar e sincronizar as deltas somente quando todas as tarefas, incluindo as operações e testes reais do Xano, estiverem concluídas e verificadas.

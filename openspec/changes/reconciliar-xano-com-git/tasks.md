# Tasks

## 1. Capturar e inventariar o estado remoto

- [ ] 1.1 Confirmar pelo CLI que o destino continua sendo o workspace `151966`, branch `v1` live; executar pull somente de definições para pasta temporária fora do repositório e registrar a confirmação sem expor credenciais.
- [ ] 1.2 Comparar o pull com `xano/` por recurso e produzir uma lista revisável de divergências: 9 definições comuns, recursos somente remotos e recursos somente locais; verificar os totais por tabela e endpoint sem alterar arquivos versionados.
- [ ] 1.3 Inspecionar os diffs remotos para garantir que apenas definições publicadas serão consideradas e que nenhum registro, variável, draft, token ou segredo será copiado; pausar e registrar o motivo se algum conteúdo não puder ser versionado com segurança.

## 2. Reconciliar as definições aprovadas no Git

- [ ] 2.1 Para cada recurso divergente ou somente remoto, preservar o conteúdo local original e incorporar ao Git apenas a definição cuja mudança tenha sido revisada; verificar por diff que nenhum recurso local foi sobrescrito sem revisão e nenhum conteúdo sensível foi adicionado.
- [ ] 2.2 Atualizar `xano/README.md` e/ou documentação relacionada com o destino, escopo do pull, recursos reconciliados e exceções; verificar que não há segredos nem afirmações sem evidência.
- [ ] 2.3 Executar as verificações locais disponíveis para os arquivos Xano e revisar `git diff -- xano/` e `git status --short -- xano/`; confirmar que a mudança foi somente local e que nenhum push ou alteração remota ocorreu.

## 3. Verificar a reconciliação

- [ ] 3.1 Comparar novamente os arquivos reconciliados com o snapshot remoto salvo, conferir que cada diferença remanescente está documentada e executar `openspec validate "reconciliar-xano-com-git" --strict --json`.
- [ ] 3.2 Revisar `git diff` completo da Change e confirmar que a cópia temporária do pull e quaisquer artefatos auxiliares estão fora do repositório; registrar evidências sanitizadas para Verify.

## Workflow follow-up

- Depois da aprovação humana do Apply e de Verify, arquivar a Change. Não enviar arquivos ao Xano como parte desta reconciliação local.

# Tasks

## 1. Confirmar destino, autenticação e baseline

- [x] 1.1 Antes de qualquer operação remota, verificar `git status --short`, confirmar pelo Xano CLI e por consulta somente de leitura que o destino é o workspace `151966` da biblioteca e identificar branch/ambiente; confirmar que `~/.xano/credentials.yaml` está fora do projeto e não exibir nem registrar credenciais.
- [x] 1.2 Consultar documentação oficial da Metadata API/CLI para exportação/pull, importação delimitada e exclusão individual; identificar um modo comprovadamente pontual de limpeza antes da criação remota e parar se ele não existir, sem usar `push --delete --sync`.
- [x] 1.3 Fazer pull/export somente de definições, sem registros ou variáveis, guardar a referência fora de `xano/` e comparar com o Git usando `git diff`; relatar divergências antes do primeiro push e documentar em `docs/xano-workflow.md` a versão CLI 1.3.4, as ajudas reais, opções de pull/push e o limite destrutivo de `--sync --delete`.

## 2. Criar e alterar tabela descartável

- [x] 2.1 Adicionar `xano/table/zz_teste_nota.xs` com `id`, `texto` e `criado_em`; revisar dry-run que listou somente CREATE dessa tabela e confirmar criação delimitada, sem recursos fora de `zz_teste_*`.
- [x] 2.2 Confirmar a tabela ID `912722` e os campos iniciais por GET; adicionar `prioridade`, revisar dry-run limitado a UPDATE/ADD_FIELD da mesma tabela e confirmar alteração por pull/GET.
- [ ] 2.3 Documentar em `docs/xano-workflow.md` os comandos/requests confirmados para criar, revisar a prévia e alterar a tabela, sem registrar token ou resposta que contenha segredo.

## 3. Provar endpoints temporários

- [ ] 3.1 Criar endpoints públicos GET e POST no grupo `zz_teste_*`, ambos limitados exclusivamente à tabela `zz_teste_nota`; antes de cada push, revisar `--dry-run` com `-i` somente para os arquivos temporários e usar `--force` somente se a prévia listar recursos `zz_teste_*`; chamar os endpoints por HTTP real e confirmar respostas.
- [ ] 3.2 Alterar a validação do POST para rejeitar texto vazio após normalização; revisar outra prévia delimitada antes do push e confirmar por chamadas reais que texto válido é aceito e texto vazio falha sem criar registro.
- [ ] 3.3 Documentar as rotas e chamadas reproduzíveis de GET/POST em `docs/xano-workflow.md`, incluindo a alteração e o resultado observado, sem incluir token nem dados sensíveis.

## 4. Conectar o cliente de teste Reflex

- [ ] 4.1 Adicionar um teste pytest de leitura do endpoint de prova com `httpx.MockTransport`, seguindo `biblioteca_mais_nova/xano_client.py` e verificando método, caminho e resposta sem abrir conexão real.
- [ ] 4.2 Executar o teste novo e os testes diretamente relacionados; confirmar que o transporte mockado não envia escrita real e registrar somente resultados sanitizados.
- [ ] 4.3 Completar em `docs/xano-workflow.md` o passo a passo para adicionar uma tabela/endpoint e consumi-lo pelo cliente Reflex, diferenciando a chamada real de prova do teste mockado do app.

## 5. Remover recursos e verificar conclusão

- [ ] 5.1 Obter IDs atuais por GET e remover individualmente os endpoints, o grupo `zz_teste_*` e a tabela ID `912722` pela Metadata API oficial; não usar exclusão global nem apagar recursos fora do prefixo.
- [ ] 5.2 Confirmar por consulta/GET que cada endpoint e tabela foi removido (404 ou ausência inequívoca), apagar somente os arquivos temporários `zz_teste_*` locais e verificar `git status --short -- xano/` limpo e `git diff` sem alteração nos recursos originais.
- [ ] 5.3 Registrar no documento apenas evidências sanitizadas de pull/diff, chamadas, alterações e limpeza; executar `openspec validate` e comparar cada tarefa com a evidência antes de encerrar Verify.

## Workflow follow-up

- Após Review humano e Apply, somente arquivar a Change depois de todas as tarefas e Verify aprovados, com a ausência remota dos recursos descartáveis e `xano/` limpo confirmadas.

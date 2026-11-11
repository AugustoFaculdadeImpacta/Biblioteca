# Tasks

## 1. Confirmar destino, autenticação e baseline

- [x] 1.1 Antes de qualquer operação remota, verificar `git status --short`, confirmar pelo Xano CLI e por consulta somente de leitura que o destino é o workspace `151966` da biblioteca e identificar branch/ambiente; confirmar que `~/.xano/credentials.yaml` está fora do projeto e não exibir nem registrar credenciais.
- [x] 1.2 Consultar documentação oficial da Metadata API/CLI para exportação/pull, importação delimitada e exclusão individual; identificar um modo comprovadamente pontual de limpeza antes da criação remota e parar se ele não existir, sem usar `push --delete --sync`.
- [x] 1.3 Fazer pull/export somente de definições, sem registros ou variáveis, guardar a referência fora de `xano/` e comparar com o Git usando `git diff`; relatar divergências antes do primeiro push e documentar em `docs/xano-workflow.md` a versão CLI 1.3.4, as ajudas reais, opções de pull/push e o limite destrutivo de `--sync --delete`.

## 2. Criar e alterar tabela descartável

- [x] 2.1 Adicionar `xano/table/zz_teste_nota.xs` com `id`, `texto` e `criado_em`; revisar dry-run que listou somente CREATE dessa tabela e confirmar criação delimitada, sem recursos fora de `zz_teste_*`.
- [x] 2.2 Confirmar a tabela ID `912722` e os campos iniciais por GET; adicionar `prioridade`, revisar dry-run limitado a UPDATE/ADD_FIELD da mesma tabela e confirmar alteração por pull/GET.
- [x] 2.3 Documentar em `docs/xano-workflow.md` os comandos/requests confirmados para criar, revisar a prévia e alterar a tabela, sem registrar token ou resposta que contenha segredo.

## 3. Endpoints temporários — fora do escopo

- [x] 3.1 Fora do escopo por decisão aprovada: não criar nem chamar endpoints públicos; `allow_push = false` foi confirmado e não foi alterado.
- [x] 3.2 Fora do escopo por decisão aprovada: não alterar validação de POST nem testar a rejeição de texto vazio, pois o endpoint de prova não foi criado.
- [x] 3.3 Fora do escopo por decisão aprovada: documentar como limitação que rotas GET/POST temporárias e chamadas HTTP reais não foram executadas.

## 4. Cliente de teste Reflex — fora do escopo

- [x] 4.1 Fora do escopo por decisão aprovada: não adicionar teste pytest de leitura com `httpx.MockTransport`.
- [x] 4.2 Fora do escopo por decisão aprovada: nenhum teste de cliente foi executado; portanto, não há resultado de transporte mockado a registrar.
- [x] 4.3 Fora do escopo por decisão aprovada: registrar em `docs/xano-workflow.md` que o consumo pelo cliente Reflex e o teste mockado não foram implementados nesta Change.

## 5. Remover recursos e verificar conclusão

- [x] 5.1 Obter IDs por GET; confirmar que não havia grupo/endpoints `zz_teste_*` e remover individualmente a tabela ID `912722` pela Metadata API oficial; não usar exclusão global nem apagar recursos fora do prefixo.
- [x] 5.2 Confirmar por GET a ausência da tabela `912722` (404), confirmar que nenhum grupo/arquivo `zz_teste_*` restou no GET/pull, apagar o arquivo local temporário e aceitar `D xano/table/zz_teste_nota.xs` em `git status` por ser arquivo rastreado antes da prova; confirmar que não houve outras alterações em `xano/`.
- [x] 5.3 Registrar em `docs/xano-workflow.md` evidências sanitizadas de criação, alteração, remoção, pull e diff; executar `openspec validate --strict` e comparar as tarefas com as evidências antes de arquivar.

## Workflow follow-up

- Arquivar a Change somente depois da validação estrita e da confirmação de que o único estado Xano local remanescente é a exclusão intencional do arquivo temporário rastreado.

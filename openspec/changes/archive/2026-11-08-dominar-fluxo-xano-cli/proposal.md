# Proposal

## Why

Precisamos comprovar um fluxo seguro e reproduzível para inspecionar, criar, alterar e remover uma tabela descartável no Xano sem afetar as nove tabelas e os 28 endpoints já versionados. A prova documenta o destino confirmado, os comandos de CLI e as operações pontuais da Metadata API, sem registrar credenciais.

## What Changes

- Documentar em `docs/xano-workflow.md` a ajuda real da CLI, pull somente de definições, comparação com Git, criação/alteração delimitada de tabela e remoção individual.
- Confirmar o workspace `151966`, branch `v1` live e ambiente antes das operações remotas; não importar registros, variáveis ou segredos.
- Criar, alterar e remover somente a tabela descartável `zz_teste_nota`; nunca usar `push --delete --sync` nem tocar nos recursos existentes.
- Registrar a limitação observada: `allow_push = false` impediu prosseguir com endpoints de prova. O ciclo de endpoints públicos e o teste de cliente Reflex com `httpx.MockTransport` foram retirados do escopo; a preferência não foi alterada e essas verificações não foram executadas.
- Manter as credenciais em `~/.xano/credentials.yaml`, fora do repositório, e não exibi-las nem copiá-las para arquivos ou logs.
- Não fazer commit ou deploy. A exclusão local de `xano/table/zz_teste_nota.xs` é intencional e aparece como `D` no Git porque o arquivo já era rastreado.
- Tratar divergências preexistentes entre Xano e Git em Change separada, com revisão própria antes de sincronizar.

## Capabilities

### New Capabilities

Nenhuma. A Change documenta e verifica um fluxo de desenvolvimento descartável, sem introduzir comportamento durável no produto. `skip_specs: true` está declarado em `.openspec.yaml`.

### Modified Capabilities

Nenhuma.

## Impact

- Xano live: tabela `zz_teste_nota` no workspace `151966`; criação e alteração confirmadas anteriormente, remoção confirmada por GET 404.
- Repositório: `docs/xano-workflow.md`, artefatos desta Change e exclusão local intencional de `xano/table/zz_teste_nota.xs`.
- Limitação: nenhum grupo ou endpoint `zz_teste_*` foi criado ou chamado; nenhum teste Reflex/pytest com `httpx.MockTransport` foi adicionado ou executado.
- Segurança: nenhum token, registro ou dado sensível é documentado.

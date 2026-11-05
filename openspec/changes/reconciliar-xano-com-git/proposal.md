# Proposal

## Why

O workspace Xano `151966`, branch live `v1`, diverge do Git: o pull de definições mostrou 11 tabelas e 36 endpoints remotos, enquanto o repositório contém 9 tabelas e 28 endpoints; as nove tabelas correspondentes também diferem. Precisamos reconciliar essa referência remota com os arquivos versionados sem sobrescrever diferenças locais sem revisão nem alterar recursos no Xano.

## What Changes

- Fazer um novo pull somente de definições do workspace `151966`, branch `v1`, para uma pasta temporária fora de `xano/`, e confirmar o destino antes de qualquer operação remota.
- Comparar cada definição remota com a versão local correspondente, identificar recursos remotos adicionais (`Authentication` e `Event Logs`) e preparar um diff revisável por recurso.
- Incorporar ao Git as definições aprovadas após revisão das diferenças, sem enviar alterações ao Xano, importar registros ou variáveis, ou incluir segredos.
- Preservar as versões locais originais e parar para decisão humana quando houver conflito sem decisão documentada; não resolver divergências por sobrescrita automática.
- Registrar no `xano/` e na documentação o resultado da reconciliação e a origem/escopo do pull, sem commit automático.

## Capabilities

### New Capabilities

Nenhuma. Esta Change reconcilia arquivos de infraestrutura versionados e não altera comportamento do produto. `.openspec.yaml` declara `skip_specs: true`.

### Modified Capabilities

Nenhuma.

## Impact

- Workspace Xano `151966`, branch live `v1`: somente leitura durante esta Change; nenhuma alteração remota ou operação de push.
- Repositório: definições Xano em `xano/` e documentação relacionada, conforme cada diff aprovado.
- Segurança: pull apenas de definições publicadas; não exportar registros, variáveis de ambiente, drafts ou credenciais. A credencial padrão permanece fora do repositório.

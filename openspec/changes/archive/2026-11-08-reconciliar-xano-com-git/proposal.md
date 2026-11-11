# Proposal

## Why

O workspace Xano `151966`, branch live `v1`, diverge do Git: o pull de definições mostrou 11 tabelas e 36 endpoints remotos, enquanto o repositório contém 9 tabelas e 28 endpoints; as nove tabelas correspondentes também diferem. Precisamos reconciliar essa referência remota com os arquivos versionados sem sobrescrever diferenças locais sem revisão nem alterar recursos no Xano.

## What Changes

- Registrar o inventário do pull somente de definições do workspace `151966`, branch live `v1`, e compará-lo com `xano/`.
- Incorporar somente quatro declarações explícitas de retorno em lista nos endpoints GET públicos de catálogo, compatíveis com os contratos locais.
- Documentar em `design.md`, `xano/README.md` e `docs/xano-workflow.md` as contagens, recursos fora do escopo e divergências classificadas.
- Manter sem alteração local as divergências de segurança, FIFO e demais comportamentos cuja equivalência com as specs não foi comprovada.
- Fazer somente leitura no Xano; não alterar `allow_push`, não fazer push e não criar commit.

## Capabilities

### New Capabilities

Nenhuma. Esta Change reconcilia arquivos de infraestrutura versionados e não altera comportamento do produto. `.openspec.yaml` declara `skip_specs: true`.

### Modified Capabilities

Nenhuma.

## Impact

- Workspace Xano `151966`, branch live `v1`: somente leitura durante esta Change; nenhuma alteração remota ou operação de push.
- Repositório: quatro arquivos GET de catálogo em `xano/`, os relatórios `xano/README.md` e `docs/xano-workflow.md`, e os artefatos desta Change.
- Segurança: pull apenas de definições publicadas; não exportar registros, variáveis de ambiente ou drafts. Campos de credencial encontrados na cópia temporária foram sanitizados; nenhum valor foi incorporado ao repositório.

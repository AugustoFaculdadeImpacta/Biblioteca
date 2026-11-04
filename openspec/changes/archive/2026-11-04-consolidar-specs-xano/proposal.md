# Proposal

## Why

As cinco capabilities comportamentais da biblioteca já possuem requisitos em deltas arquivadas, mas `openspec/specs/` está vazio. Consolidar cópias fiéis desses requisitos cria a fonte principal de consulta sem reinterpretar regras nem alterar a implementação.

## What Changes

- Criar cinco specs principais a partir dos requisitos ADDED das deltas arquivadas `2026-11-03-estrutura-inicial-xano-biblioteca`.
- Preservar literalmente os 18 blocos de requisitos e seus cenários, sem reescrever, resumir ou aprimorar o conteúdo.
- Registrar no design as divergências e pendências conhecidas, sem corrigi-las nesta Change.

## Capabilities

### New Capabilities

- `catalog`: consulta pública e administração autorizada do acervo.
- `copy-condition`: registro e consulta do histórico de condições de exemplares.
- `identity-session`: cadastro, autenticação e perfil confiável.
- `loan-circulation`: solicitação, retirada e devolução de empréstimos.
- `reservations`: fila FIFO e oportunidades de retirada por reserva.

### Modified Capabilities

Nenhuma. As specs principais correspondentes ainda não existem.

## Impact

- Criação de cinco arquivos em `openspec/specs/`, exclusivamente durante o Archive, por sincronização dos deltas desta Change.
- Nenhuma alteração em `docs/`, `xano/` ou na Change ativa `verificacao-avancada-circulacao`.
- Nenhuma operação remota no Xano.

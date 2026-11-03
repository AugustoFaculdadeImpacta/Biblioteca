# Proposal

## Why

O backend Xano foi aplicado e os fluxos seguros de identidade, empréstimo, fila FIFO, oferta, autorização e condição foram verificados no workspace live. Restam regras que exigem manipulação temporal, disparo de processamento global ou disputa concorrente; elas precisam de um plano de teste isolado para não afetar registros fora dos fixtures.

## What Changes

- Planejar e executar, somente em ambiente isolado e descartável, a verificação de atraso, limite simultâneo de empréstimos, expiração e reoferta de reserva, concorrência e geração de código de tombo.
- Não alterar requisitos de produto, tabelas, endpoints ou o frontend nesta Change.
- Registrar evidência reproduzível e limites de cada cenário antes de consolidar o resultado.

## Capabilities

Nenhuma alteração de requisito de produto. Esta Change é exclusivamente de verificação; `skip_specs: true` está declarado em `.openspec.yaml`.

## Impact

- Xano: requer um ambiente isolado que possa receber e remover fixtures sem risco para dados live.
- OpenSpec: a Change anterior permanece como fonte da implementação Xano; esta Change concentra somente provas avançadas ainda pendentes.

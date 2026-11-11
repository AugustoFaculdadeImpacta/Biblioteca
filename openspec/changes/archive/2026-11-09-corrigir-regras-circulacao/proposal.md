# Proposal

## Why

A verificação no workspace `151966/v1` encontrou três divergências entre o comportamento do backend e os requisitos já aprovados: solicitação aceita apesar de atraso, duas retiradas concorrentes aceitas para o mesmo estudante e falha HTTP 500 ao ofertar a próxima reserva FIFO. Os cenários e a limpeza foram concluídos; esta Change trata somente as correções do backend.

## What Changes

- Corrigir e verificar no servidor o bloqueio de novas solicitações de estudante com empréstimo vencido.
- Corrigir a definição de empréstimo ativo para tratar `devolvido_em = null` ou `0` como não devolvido e revalidar o limite após essa correção.
- Se o teste de limite ainda aceitar duas retiradas após o primeiro lote, interromper a execução e solicitar decisão sobre o mecanismo atômico, com índices únicos como opção a validar por teste.
- Corrigir o erro da oferta da próxima reserva e garantir seleção determinística da primeira reserva elegível em FIFO.
- Adicionar ou ajustar somente validações e operações Xano necessárias às regras aprovadas; não alterar a interface Reflex nem o schema nesta etapa.
- Validar as correções com cenários controlados e fixtures rastreáveis, incluindo duas chamadas concorrentes e confirmação da ordem FIFO.
- Revalidar o workspace/branch antes de qualquer Apply remoto. Para cada endpoint corrigido, comparar um pull remoto isolado com o arquivo Git correspondente e relatar a divergência; fazer dry-run e push sempre delimitados por `-i` ao endpoint, prosseguindo somente se o dry-run listar exclusivamente esse recurso como `UPDATE`. No plano Free, o push é sempre habilitado; não alterar a preferência `allow_push`.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma alteração de requisito. `loan-circulation` e `reservations` já definem o bloqueio por atraso, o limite concorrente de empréstimos ativos e o atendimento FIFO. Esta Change corrige a implementação para cumprir esses contratos; por isso, `.openspec.yaml` declara `skip_specs: true`.

## Impact

- Xano: rotas de solicitação, retirada, devolução e elegibilidade de reserva, além de oferta/consulta FIFO; nenhuma mudança de schema ou mecanismo atômico sem nova decisão após o teste do primeiro lote.
- Verificação: cenários de atraso, limite concorrente e FIFO, com limpeza confirmada de fixtures.
- Sem alterações em `biblioteca_mais_nova/`, `tests/` ou interface Reflex.
- Nenhuma operação remota faz parte desta proposta. Qualquer Apply depende de revisão e aprovação explícitas, confirmação do destino e inspeção do pull, diff e dry-run delimitados antes de sincronizar cada definição.

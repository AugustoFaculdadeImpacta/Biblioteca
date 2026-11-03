# Design

## Context

Veja `proposal.md` para a motivação. A Change `estrutura-inicial-xano-biblioteca` já comprovou em `151966/v1` os fluxos seguros com fixtures e limpeza por ID. A branch é live e não oferece isolamento para disparar um processador global de expiração, alterar datas de registros ou provocar disputas sem risco de afetar recursos fora das fixtures.

## Goals / Non-Goals

**Goals:**

- Executar cenários avançados somente quando existir ambiente isolado, descartável e com escrita autorizada.
- Garantir que cada fixture, mutação temporal e exclusão seja rastreável por ID e reversível pela limpeza.

**Non-Goals:**

- Alterar regras de produto, tabelas, endpoints, grupo de API ou a aplicação Reflex.
- Executar testes globais de expiração, atraso ou concorrência na branch live atual.

## Decisions

### Exigir ambiente isolado antes dos testes avançados

Os testes de expiração chamam um endpoint que pode processar qualquer oferta vencida; os testes de atraso exigem alterar vencimentos; e os de concorrência criam disputas deliberadas. A Change só prossegue se houver ambiente descartável confirmado. A alternativa de executar na live foi rejeitada porque não permite provar que somente fixtures seriam afetadas.

### Usar fixtures rastreadas e limpeza confirmada

Toda fixture deve ser criada por API, ter ID/tabela registrados imediatamente e ser removida em ordem de dependência. A limpeza é aprovada somente após consulta individual retornar 404. A alternativa de truncar tabelas ou listar registros é proibida.

## Risks / Trade-offs

- [Não há ambiente isolado disponível] → a Change permanece pendente; não substituir a evidência por alegação de comportamento não testado.
- [Falha de limpeza] → interromper os próximos cenários, registrar os IDs e não arquivar a Change.
- [Concorrência não reproduzível] → registrar comandos, paralelismo e respostas para permitir repetição, sem declarar atomicidade sem evidência.

# Design

## Context

Veja `proposal.md` para a motivação. As cinco specs principais ainda não existem; os textos de origem são as cinco deltas arquivadas em `2026-11-03-estrutura-inicial-xano-biblioteca`. A Change é documental: a consolidação das specs principais será feita pelo Archive, com sincronização selecionada.

## Goals / Non-Goals

**Goals:**

- Preservar literalmente cada um dos 18 blocos `Requirement` e seus cenários das deltas de origem.
- Criar uma capability principal por arquivo, mantendo os caminhos `catalog`, `copy-condition`, `identity-session`, `loan-circulation` e `reservations`.
- Deixar divergências documentadas para Changes futuras, sem escolher ou aplicar correções nesta Change.

**Non-Goals:**

- Alterar requisitos, documentação do produto, XS, tabelas, endpoints ou qualquer estado no Xano.
- Modificar `docs/`, `xano/` ou a Change ativa `verificacao-avancada-circulacao`.
- Verificar comportamento remoto ou declarar resolvidas as limitações conhecidas.

## Decisions

### Usar as deltas arquivadas como única fonte normativa

Cada arquivo em `specs/<capability>/spec.md` é uma cópia integral da delta correspondente, sem reescrita, resumo ou melhoria de requisitos. A sincronização do Archive deve criar as specs principais a partir desses requisitos ADDED; a verificação comparará todos os blocos de requisito e cenários com a origem.

Alternativa considerada: editar os requisitos para alinhá-los aos XS ou à documentação conceitual. Rejeitada porque a solicitação limita esta Change à consolidação fiel e não autoriza resolver divergências.

### Manter uma spec por capability

As cinco capabilities permanecem separadas, conforme os caminhos e limites das deltas de origem. Não há capability principal pré-existente em `openspec/specs/` para modificar.

Alternativa considerada: agrupar todas as regras em uma spec ampla de biblioteca. Rejeitada por perder a divisão de domínio que já existe nas deltas.

## Riscos / Divergências conhecidas

- **Apresentação dos timestamps em `America/Sao_Paulo`:** a delta de reservas exige apresentação dos timestamps da oferta; a definição local consultada de `GET /minhas/reservas` adiciona formatação para `expira_em`, mas não para `ofertada_em`. Investigar e decidir em Change futura; não alterar XS nesta Change.
- **Concorrência:** os requisitos descrevem exclusão mútua e unicidade sob operações concorrentes, mas a evidência local registra que essas garantias não foram verificadas em runtime. Verificar em ambiente isolado numa Change futura.
- **README do Xano:** `xano/README.md` relata verificações autenticadas como ainda necessárias, enquanto `RESULTS.md` arquivado registra uma execução segura posterior. Harmonizar os registros numa Change documental futura, sem mudar os fatos ou a implementação.
- **Decisões abertas na visão geral:** `docs/project-overview.md` ainda apresenta algumas decisões como abertas (incluindo pedido sem exemplar, provisionamento de bibliotecário e detalhes da janela de retirada) embora as deltas arquivadas estabeleçam comportamentos relacionados. Revisar a coerência documental em Change futura; não editar `docs/` aqui.

## Risks / Trade-offs

- [O Archive pode criar conteúdo principal diferente da cópia literal pretendida] → comparar cada um dos 18 blocos e seus cenários com as deltas de origem antes de aprovar a verificação.
- [Divergências conhecidas podem ser interpretadas como resolvidas por estarem em specs principais] → mantê-las explicitamente registradas acima como itens pendentes, sem alterar os requisitos nesta Change.

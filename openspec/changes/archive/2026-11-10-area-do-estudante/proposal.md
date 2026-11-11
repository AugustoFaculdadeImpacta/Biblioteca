# Proposal

## Why

Após consultar o catálogo, estudantes ainda não conseguem solicitar empréstimos nem acompanhar sua situação em um só lugar. A área do estudante conectará a consulta pública aos endpoints autenticados existentes, deixando elegibilidade e alocação sob validação do backend.

## What Changes

- Permitir que estudante autenticado solicite empréstimo a partir do catálogo; quando não houver exemplar imediatamente disponível, apresentar a ação como entrada na fila de reserva.
- Usar o endpoint existente `POST /solicitacoes-emprestimo`, que revalida disponibilidade e elegibilidade no servidor; não chamar `POST /reservas` diretamente, pois esse endpoint não exige indisponibilidade.
- Criar uma página autenticada “Minha biblioteca” com empréstimos, solicitações, reservas, prazos e oferta de retirada.
- Apresentar aviso claro quando houver empréstimo em atraso e explicar que novas solicitações e reservas podem ser bloqueadas.
- Mostrar no cabeçalho um acesso à página do estudante autenticado.
- Manter a Change frontend-only: nenhuma edição, push ou escrita remota no Xano; testes de escrita usam mocks.
- Documentar a divergência observada entre o POST local de solicitação e a spec de circulação, sem alterar a spec consolidada ou o backend neste bloco.

## Capabilities

### New Capabilities

### Modified Capabilities

- `catalog`: permitir que estudantes iniciem solicitação de empréstimo ou sejam encaminhados à fila quando o catálogo indicar indisponibilidade.
- `loan-circulation`: definir a experiência do estudante para solicitar e acompanhar empréstimos e avisos de atraso.
- `reservations`: definir a consulta do estudante a reservas e ofertas de retirada.
- `frontend-foundation`: adicionar acesso à área pessoal na navegação do estudante autenticado.

## Impact

- Frontend Reflex, estado privado da sessão e cliente HTTP Xano executado no backend.
- Endpoints existentes no OpenAPI do grupo Biblioteca: `POST /solicitacoes-emprestimo`, `GET /minhas/emprestimos`, `GET /minhas/solicitacoes` e `GET /minhas/reservas`; o catálogo fornece metadados para resolver `titulo_id`.
- Testes pytest com mocks; nenhum endpoint, tabela, contrato Xano ou dado remoto será alterado nesta Change.

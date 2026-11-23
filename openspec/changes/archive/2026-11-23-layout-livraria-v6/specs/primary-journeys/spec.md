# primary-journeys Delta

## ADDED Requirements

### Requirement: Jornadas da livraria v6 usam navegação estável
A interface MUST manter busca, reserva e navegação por perfil consistentes em todas as larguras verificadas.

A busca global e a reserva devem respeitar o estado de autenticação do usuário.

#### Scenario: Visitante escolhe reservar
- **WHEN** o visitante clica em reservar em um detalhe
- **THEN** é direcionado à página de login

#### Scenario: Estudante autenticado
- **WHEN** o estudante reserva um título disponível
- **THEN** o pedido aparece em Reservas aguardando

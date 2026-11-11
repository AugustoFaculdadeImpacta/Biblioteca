# Spec Delta

## ADDED Requirements

### Requirement: Estudante acompanha reservas e ofertas próprias
A interface MUST permitir que estudante autenticado consulte suas reservas, estados e prazos de oferta, sem revelar dados pessoais ou reservas de outros estudantes.

#### Scenario: Consultar reservas pessoais
- **WHEN** estudante autenticado abre sua área pessoal
- **THEN** a interface lista somente suas reservas e apresenta o estado e o prazo de retirada retornados pelo serviço

#### Scenario: Reserva aguardando atendimento
- **WHEN** estudante possui reserva em espera na fila
- **THEN** a interface informa que a reserva aguarda atendimento sem inventar posição numérica não fornecida pelo serviço

#### Scenario: Reserva ofertada
- **WHEN** reserva possui oferta de retirada válida
- **THEN** a interface apresenta o prazo convertido para `America/Sao_Paulo` conforme retornado pelo serviço

#### Scenario: Nenhuma reserva pessoal
- **WHEN** estudante autenticado não possui reservas
- **THEN** a interface informa que não há reservas e oferece retorno ao catálogo

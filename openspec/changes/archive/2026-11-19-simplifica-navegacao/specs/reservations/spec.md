# Spec Delta

## MODIFIED Requirements

### Requirement: Estudante acompanha reservas e ofertas próprias
A interface MUST permitir que estudante autenticado consulte em `/reservas` somente suas reservas, estados e prazos de oferta retornados pelo serviço.

#### Scenario: Consultar reservas pessoais
- **WHEN** estudante autenticado abre `/reservas`
- **THEN** a interface lista somente suas reservas e apresenta estado e prazo de retirada retornados pelo serviço

#### Scenario: Reserva aguardando atendimento
- **WHEN** estudante possui reserva em espera na fila
- **THEN** a interface informa que a reserva aguarda atendimento sem inventar posição numérica não fornecida pelo serviço

#### Scenario: Reserva ofertada
- **WHEN** reserva possui oferta de retirada válida
- **THEN** a interface apresenta o prazo convertido para `America/Sao_Paulo` conforme retornado pelo serviço

#### Scenario: Nenhuma reserva pessoal
- **WHEN** estudante autenticado não possui reservas
- **THEN** a interface informa no bloco correspondente que não há reservas e oferece retorno ao catálogo, mantendo os demais estados pessoais visíveis

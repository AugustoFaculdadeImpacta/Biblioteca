# Spec Delta

## MODIFIED Requirements

### Requirement: Elegibilidade da reserva é revalidada no backend
O sistema MUST verificar autenticação, perfil estudante, situação ativa do título e bloqueios vigentes antes de criar ou atender uma reserva.

#### Scenario: Estudante com empréstimo atrasado
- **WHEN** estudante com empréstimo vencido e não devolvido solicita reserva de título ativo
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Visitante ou bibliotecário sem contexto de estudante tenta reservar
- **WHEN** perfil não estudante envia uma solicitação de reserva
- **THEN** o backend recusa a operação

#### Scenario: Título desativado
- **WHEN** estudante tenta criar reserva para título inativo
- **THEN** o backend recusa a operação sem adicionar ou alterar itens da fila

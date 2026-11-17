# Spec Delta

## MODIFIED Requirements

### Requirement: Estado de fila e oportunidade é visível conforme autorização
O sistema MUST permitir ao estudante consultar suas reservas e oportunidades e ao bibliotecário ou admin consultar e operar filas, sem expor dados pessoais de outros estudantes ao público.

#### Scenario: Estudante consulta própria fila
- **WHEN** estudante autenticado consulta suas reservas
- **THEN** recebe somente suas reservas e oportunidades, com estado e prazo definidos

#### Scenario: Bibliotecário consulta fila
- **WHEN** bibliotecário autenticado consulta fila de um título
- **THEN** recebe a ordem e o estado operacional necessários para atender a próxima reserva

#### Scenario: Admin consulta e opera fila
- **WHEN** admin autenticado consulta ou opera a fila de reservas
- **THEN** recebe os mesmos dados operacionais e pode executar as mesmas operações permitidas ao bibliotecário

#### Scenario: Perfil sem privilégio tenta operar fila
- **WHEN** estudante ou visitante tenta consultar ou operar uma fila administrativa
- **THEN** o backend recusa a operação e não expõe dados pessoais de outros estudantes

# Spec Delta

## MODIFIED Requirements

### Requirement: Bibliotecário confirma retirada física
O sistema MUST criar o empréstimo de um exemplar físico somente quando bibliotecário ou admin autenticado confirmar a retirada e o backend revalidar elegibilidade e disponibilidade.

#### Scenario: Retirada confirmada
- **WHEN** bibliotecário ou admin confirma a retirada de exemplar elegível para estudante elegível
- **THEN** o sistema registra a retirada, define vencimento para 14 dias corridos depois e marca o empréstimo como ativo

#### Scenario: Retirada concorrente ou inelegível
- **WHEN** duas confirmações concorrem pelo mesmo exemplar ou a elegibilidade mudou
- **THEN** o backend permite no máximo uma confirmação válida e recusa a operação conflitante sem criar empréstimo duplicado

#### Scenario: Estudante tenta confirmar retirada
- **WHEN** estudante tenta executar a confirmação física
- **THEN** o backend recusa a operação sem criar empréstimo

### Requirement: Bibliotecário confirma devolução
O sistema MUST registrar a devolução física de empréstimo ativo somente por bibliotecário ou admin autenticado.

#### Scenario: Devolução registrada
- **WHEN** bibliotecário ou admin confirma a devolução do exemplar
- **THEN** o sistema registra o instante de devolução e encerra o empréstimo ativo

#### Scenario: Devolução inválida
- **WHEN** pedido referencia empréstimo inexistente, já encerrado ou usuário sem perfil bibliotecário ou admin
- **THEN** o backend recusa a operação sem alterar o histórico

## ADDED Requirements

### Requirement: Consulta administrativa de solicitações exige perfil privilegiado
O sistema MUST permitir que bibliotecário ou admin autenticado consulte solicitações pendentes de circulação, sem expor operações administrativas a estudantes ou visitantes.

#### Scenario: Bibliotecário consulta solicitações pendentes
- **WHEN** bibliotecário autenticado consulta a fila administrativa
- **THEN** o sistema retorna somente solicitações pendentes necessárias à operação da biblioteca

#### Scenario: Admin consulta solicitações pendentes
- **WHEN** admin autenticado consulta a fila administrativa
- **THEN** o sistema retorna as mesmas solicitações pendentes que ao bibliotecário

#### Scenario: Perfil não privilegiado consulta a fila
- **WHEN** estudante ou visitante tenta consultar solicitações administrativas
- **THEN** o backend recusa a operação sem revelar dados pessoais ou alterar registros

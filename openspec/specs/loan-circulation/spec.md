# loan-circulation Specification

## Purpose

Definir solicitação, retirada física e devolução de exemplares, com prazos e elegibilidade verificados no backend da biblioteca.

## Requirements

### Requirement: Estudante solicita empréstimo sem concluir retirada
O sistema MUST separar o pedido do estudante da confirmação física do empréstimo; registrar ou recusar o pedido conforme elegibilidade validada no servidor, sem iniciar prazo de empréstimo antes da retirada.

#### Scenario: Pedido de estudante elegível
- **WHEN** estudante autenticado solicita empréstimo
- **THEN** o backend valida identidade e elegibilidade e registra o pedido sem tratá-lo como retirada concluída

#### Scenario: Estudante inelegível
- **WHEN** estudante possui empréstimo ativo vencido ou não atende a outra regra aprovada
- **THEN** o backend recusa o pedido e não altera empréstimos nem disponibilidade

#### Scenario: Sem exemplar disponível
- **WHEN** estudante elegível solicita empréstimo e não há exemplar imediatamente disponível
- **THEN** o pedido entra na fila FIFO de reservas do título e não cria um empréstimo nem uma fila separada de solicitações

#### Scenario: Exemplar atribuído à reserva
- **WHEN** um exemplar fica disponível e a reserva do estudante chega à sua vez na fila FIFO
- **THEN** o backend associa o exemplar à reserva e registra oferta de retirada válida por 48 horas corridas, com timestamps armazenados em UTC e apresentados no fuso `America/Sao_Paulo`; essa regra não altera o prazo de empréstimo de 14 dias corridos

### Requirement: Bibliotecário confirma retirada física
O sistema MUST criar o empréstimo de um exemplar físico somente quando bibliotecário autenticado confirmar a retirada e o backend revalidar elegibilidade e disponibilidade.

#### Scenario: Retirada confirmada
- **WHEN** bibliotecário confirma a retirada de exemplar elegível para estudante elegível
- **THEN** o sistema registra a retirada, define vencimento para 14 dias corridos depois e marca o empréstimo como ativo

#### Scenario: Retirada concorrente ou inelegível
- **WHEN** duas confirmações concorrem pelo mesmo exemplar ou a elegibilidade mudou
- **THEN** o backend permite no máximo uma confirmação válida e recusa a operação conflitante sem criar empréstimo duplicado

#### Scenario: Estudante tenta confirmar retirada
- **WHEN** estudante tenta executar a confirmação física
- **THEN** o backend recusa a operação sem criar empréstimo

### Requirement: Existe no máximo um empréstimo ativo por estudante e exemplar
O sistema MUST impedir mais de um empréstimo ativo por estudante e mais de um empréstimo ativo por exemplar, inclusive em operações concorrentes.

#### Scenario: Limite ativo do estudante
- **WHEN** estudante já possui empréstimo ativo e tenta obter outro
- **THEN** o backend recusa a nova confirmação de retirada

#### Scenario: Exemplar já emprestado
- **WHEN** bibliotecário tenta emprestar exemplar com empréstimo ativo
- **THEN** o backend recusa a operação e mantém o empréstimo existente

### Requirement: Bibliotecário confirma devolução
O sistema MUST registrar a devolução física de empréstimo ativo somente por bibliotecário autenticado.

#### Scenario: Devolução registrada
- **WHEN** bibliotecário confirma a devolução do exemplar
- **THEN** o sistema registra o instante de devolução e encerra o empréstimo ativo

#### Scenario: Devolução inválida
- **WHEN** pedido referencia empréstimo inexistente, já encerrado ou usuário sem perfil bibliotecário
- **THEN** o backend recusa a operação sem alterar o histórico

### Requirement: Atraso bloqueia novas operações do estudante
O sistema MUST considerar atrasado empréstimo ativo cujo vencimento passou e bloquear novos pedidos de empréstimo e reservas desse estudante.

#### Scenario: Empréstimo vencido
- **WHEN** estudante tem empréstimo ativo com vencimento anterior ao instante atual
- **THEN** o backend recusa novos pedidos de empréstimo e comunica a restrição

#### Scenario: Empréstimo não vencido
- **WHEN** estudante tem empréstimo ativo ainda dentro do prazo
- **THEN** a regra de atraso não o bloqueia por vencimento, sem remover os demais limites aprovados

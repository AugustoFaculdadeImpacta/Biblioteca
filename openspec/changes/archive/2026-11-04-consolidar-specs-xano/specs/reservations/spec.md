# Spec Delta

## Purpose

Definir reservas de títulos em fila FIFO e a oportunidade limitada de retirada quando a reserva é atendida por exemplar disponível.

## ADDED Requirements

### Requirement: Reserva pertence a título e entra em fila FIFO
O sistema MUST registrar reservas por título em ordem de solicitação e permitir no máximo uma reserva ativa por estudante e título.

#### Scenario: Nova reserva
- **WHEN** estudante autenticado reserva um título elegível
- **THEN** a reserva é registrada na fila do título com posição relativa determinada pela ordem de solicitação

#### Scenario: Reserva ativa duplicada
- **WHEN** estudante tenta criar outra reserva ativa para o mesmo título
- **THEN** o backend recusa duplicidade e preserva a reserva existente

#### Scenario: Título já emprestado ao estudante
- **WHEN** estudante tem empréstimo ativo não atrasado de exemplar daquele título
- **THEN** o backend recusa a reserva

### Requirement: Elegibilidade da reserva é revalidada no backend
O sistema MUST verificar autenticação, perfil estudante e bloqueios vigentes antes de criar ou atender uma reserva.

#### Scenario: Estudante com empréstimo atrasado
- **WHEN** estudante com empréstimo vencido e não devolvido solicita reserva
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Visitante ou bibliotecário sem contexto de estudante tenta reservar
- **WHEN** perfil não estudante envia uma solicitação de reserva
- **THEN** o backend recusa a operação

### Requirement: Atendimento segue a ordem e não duplica exemplar
O sistema MUST oferecer exemplar disponível à próxima reserva elegível na ordem FIFO e impedir que o mesmo exemplar seja prometido simultaneamente a reservas ou empréstimos incompatíveis.

#### Scenario: Próxima reserva atendida
- **WHEN** um exemplar se torna disponível para atender uma fila não vazia
- **THEN** o sistema seleciona a primeira reserva elegível e registra a oportunidade de retirada associada ao exemplar

#### Scenario: Disputa concorrente pelo exemplar
- **WHEN** operações concorrentes tentam alocar o mesmo exemplar
- **THEN** no máximo uma alocação é confirmada e as demais não alteram a reserva ou empréstimo existente

### Requirement: Oportunidade de retirada dura dois dias
O sistema MUST associar o exemplar disponível à próxima reserva elegível na fila FIFO e registrar uma oportunidade de retirada válida por 48 horas corridas a partir do instante em que o sistema associa o exemplar e registra a oferta. Os timestamps MUST ser armazenados em UTC e apresentados no fuso `America/Sao_Paulo`.

#### Scenario: Exemplar associado à reserva atendida
- **WHEN** um exemplar fica disponível e a reserva chega à vez do estudante na fila
- **THEN** o backend associa o exemplar à reserva, registra a oferta no instante dessa associação e define a expiração para 48 horas corridas depois, armazenando os timestamps em UTC

#### Scenario: Janela expirada
- **WHEN** o timestamp de expiração da oportunidade passou sem retirada
- **THEN** a reserva é marcada como expirada, o exemplar é liberado e ofertado à próxima reserva elegível na ordem FIFO; a oportunidade expirada deixa de permitir retirada

#### Scenario: Próxima reserva inelegível
- **WHEN** a reserva mais antiga na fila não é mais elegível, por exemplo porque o estudante tem empréstimo atrasado
- **THEN** o backend não oferece exemplar a essa reserva e continua pela ordem FIFO até encontrar a próxima reserva elegível

#### Scenario: Prazo apresentado ao estudante
- **WHEN** estudante consulta sua oportunidade de retirada
- **THEN** o sistema apresenta os timestamps convertidos para o fuso `America/Sao_Paulo`

### Requirement: Estado de fila e oportunidade é visível conforme autorização
O sistema MUST permitir ao estudante consultar suas reservas e oportunidades e ao bibliotecário consultar e operar filas, sem expor dados pessoais de outros estudantes ao público.

#### Scenario: Estudante consulta própria fila
- **WHEN** estudante autenticado consulta suas reservas
- **THEN** recebe somente suas reservas e oportunidades, com estado e prazo definidos

#### Scenario: Bibliotecário consulta fila
- **WHEN** bibliotecário autenticado consulta fila de um título
- **THEN** recebe a ordem e o estado operacional necessários para atender a próxima reserva

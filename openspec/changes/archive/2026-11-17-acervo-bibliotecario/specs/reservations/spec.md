# Spec Delta

## MODIFIED Requirements

### Requirement: Elegibilidade da reserva é revalidada no backend
O sistema MUST verificar autenticação, perfil estudante, situação ativa do título, atraso, o limite de três empréstimos ativos e empréstimo ativo do mesmo título antes de criar ou atender uma reserva.

#### Scenario: Estudante com empréstimo atrasado
- **WHEN** estudante com empréstimo vencido e não devolvido solicita reserva de título ativo
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Empréstimo ativo de outro título
- **WHEN** estudante possui menos de três empréstimos ativos de outros títulos e solicita reserva elegível
- **THEN** o backend não bloqueia a reserva por causa desses empréstimos

#### Scenario: Limite de empréstimos atingido
- **WHEN** estudante possui três empréstimos ativos e solicita reserva
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Título já emprestado ao estudante
- **WHEN** estudante possui empréstimo ativo de exemplar do título solicitado
- **THEN** o backend recusa a reserva sem alterar a fila

#### Scenario: Visitante ou bibliotecário sem contexto de estudante tenta reservar
- **WHEN** perfil não estudante envia uma solicitação de reserva
- **THEN** o backend recusa a operação

#### Scenario: Título desativado
- **WHEN** estudante tenta criar reserva para título inativo
- **THEN** o backend recusa a operação sem adicionar ou alterar itens da fila

## ADDED Requirements

### Requirement: Estudante abre detalhes do título reservado
A área pessoal MUST permitir que estudante abra os detalhes públicos do título associado à própria solicitação ou reserva, sem alterar o estado ou o prazo.

#### Scenario: Abrir detalhes de uma solicitação ou reserva
- **WHEN** estudante seleciona o título exibido em uma solicitação ou reserva própria
- **THEN** a interface abre a rota pública de detalhes do mesmo `titulo_id` e preserva o estado e o prazo apresentados na área pessoal

### Requirement: Equipe decide reservas respeitando a fila
O sistema MUST permitir a bibliotecários e admins consultar reservas ativas, recusar reserva somente enquanto aguarda na fila e oferecer exemplar disponível à próxima reserva elegível em FIFO.

#### Scenario: Oferecer exemplar à próxima reserva
- **WHEN** bibliotecário/admin solicita oferta e há exemplar disponível
- **THEN** o backend oferece o exemplar somente à próxima reserva elegível, registra prazo de 48 horas e não permite escolher prioridade ou posição

#### Scenario: Recusar reserva aguardando
- **WHEN** bibliotecário/admin recusa reserva em estado `aguardando`
- **THEN** o backend marca a reserva e sua solicitação vinculada como `recusada`, sem alterar exemplares nem outras reservas

#### Scenario: Recusar reserva já ofertada
- **WHEN** bibliotecário/admin tenta recusar reserva em estado `ofertada`
- **THEN** o backend recusa a operação e mantém o exemplar associado até retirada ou expiração

#### Scenario: Perfil sem privilégio tenta decidir reserva
- **WHEN** visitante ou estudante tenta listar, oferecer ou recusar reserva administrativa
- **THEN** o backend recusa a operação sem alterar a fila ou a disponibilidade

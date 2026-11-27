# Spec Delta

## MODIFIED Requirements

### Requirement: Reserva pertence a título e entra em fila FIFO
O sistema MUST registrar reservas por título em ordem de solicitação e respeitar `permitir_pedido_com_reserva_ativa` ao receber nova solicitação do mesmo estudante e título.

#### Scenario: Nova reserva
- **WHEN** estudante autenticado reserva um título elegível
- **THEN** a reserva é registrada na fila do título com posição relativa determinada pela ordem de solicitação

#### Scenario: Reserva ativa duplicada
- **WHEN** estudante tenta criar outra reserva ativa para o mesmo título e `permitir_pedido_com_reserva_ativa` é falso
- **THEN** o backend recusa duplicidade e preserva a reserva existente

#### Scenario: Novo pedido permitido apesar de reserva ativa
- **WHEN** estudante solicita título com reserva ativa e `permitir_pedido_com_reserva_ativa` é verdadeiro
- **THEN** o backend permite o pedido se elegível sem criar uma segunda reserva ativa duplicada

#### Scenario: Título já emprestado ao estudante
- **WHEN** estudante tem empréstimo ativo não atrasado de exemplar daquele título
- **THEN** o backend recusa a reserva

### Requirement: Elegibilidade da reserva é revalidada no backend

O sistema MUST verificar autenticação, perfil ou visão efetiva de estudante, situação ativa do título, regras configuradas de atraso e limites de empréstimos e pedidos, e empréstimo ativo do mesmo título antes de criar ou atender uma reserva.

#### Scenario: Estudante com empréstimo atrasado
- **WHEN** estudante com empréstimo vencido e não devolvido solicita reserva de título ativo enquanto `bloquear_com_atraso` é verdadeiro
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Empréstimo ativo de outro título
- **WHEN** estudante possui quantidade de empréstimos ativos inferior a `limite_emprestimos_ativos` e solicita uma reserva elegível
- **THEN** o backend não bloqueia a reserva por causa desses empréstimos

#### Scenario: Limite de empréstimos atingido
- **WHEN** estudante possui quantidade de empréstimos ativos igual a `limite_emprestimos_ativos` e solicita reserva
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Limite de pedidos em aberto atingido
- **WHEN** estudante possui quantidade de pedidos em aberto igual a `limite_pedidos_em_aberto`
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Título já emprestado ao estudante
- **WHEN** estudante possui empréstimo ativo de exemplar do título solicitado
- **THEN** o backend recusa a reserva sem alterar a fila

#### Scenario: Visitante ou bibliotecário sem contexto de estudante tenta reservar
- **WHEN** visitante ou bibliotecário sem visão de estudante envia solicitação de reserva
- **THEN** o backend recusa a operação

#### Scenario: Admin atua como estudante
- **WHEN** admin seleciona a visão Estudante e solicita reserva
- **THEN** o endpoint autoriza a sessão admin conforme o contrato publicado e registra o pedido no nome do admin

#### Scenario: Título desativado
- **WHEN** estudante tenta criar reserva para título inativo
- **THEN** o backend recusa a operação sem adicionar ou alterar itens da fila

### Requirement: Oportunidade de retirada dura dois dias
O sistema MUST associar o exemplar disponível à próxima reserva elegível na fila FIFO e registrar uma oportunidade de retirada pelo valor `prazo_retirada_horas` a partir do instante da oferta, armazenando timestamps em UTC e apresentando-os no fuso `America/Sao_Paulo`.

#### Scenario: Exemplar associado à reserva atendida
- **WHEN** um exemplar fica disponível e a reserva chega à vez do estudante na fila
- **THEN** o backend associa o exemplar à reserva e define a expiração para `prazo_retirada_horas` depois, armazenando os timestamps em UTC

#### Scenario: Janela expirada
- **WHEN** o timestamp de expiração da oportunidade passou sem retirada
- **THEN** a reserva é marcada como expirada, o exemplar é liberado e ofertado à próxima reserva elegível na ordem FIFO; a oportunidade expirada deixa de permitir retirada

#### Scenario: Próxima reserva inelegível
- **WHEN** a reserva mais antiga na fila não é mais elegível, por exemplo porque o estudante tem empréstimo atrasado enquanto `bloquear_com_atraso` está ativo
- **THEN** o backend não oferece exemplar a essa reserva e continua pela ordem FIFO até encontrar a próxima reserva elegível

#### Scenario: Prazo apresentado ao estudante
- **WHEN** estudante consulta sua oportunidade de retirada
- **THEN** o sistema apresenta os timestamps convertidos para `America/Sao_Paulo`

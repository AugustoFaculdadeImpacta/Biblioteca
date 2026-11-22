# reservations Specification

## Purpose

Definir reservas de títulos em fila FIFO e a oportunidade limitada de retirada quando a reserva é atendida por exemplar disponível.

## Requirements

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
### Requirement: Estudante acompanha reservas e ofertas próprias
A interface MUST permitir que estudante autenticado consulte em `/reservas` somente suas reservas, estados e prazos de oferta retornados pelo serviço.

#### Scenario: Consultar reservas pessoais
- **WHEN** estudante autenticado abre `/reservas`
- **THEN** a interface lista somente suas reservas e apresenta o estado e o prazo de retirada retornados pelo serviço

#### Scenario: Reserva aguardando atendimento
- **WHEN** estudante possui reserva em espera na fila
- **THEN** a interface informa que a reserva aguarda atendimento sem inventar posição numérica não fornecida pelo serviço

#### Scenario: Reserva ofertada
- **WHEN** reserva possui oferta de retirada válida
- **THEN** a interface apresenta o prazo convertido para `America/Sao_Paulo` conforme retornado pelo serviço

#### Scenario: Nenhuma reserva pessoal
- **WHEN** estudante autenticado não possui reservas
- **THEN** a interface informa no bloco correspondente que não há reservas e oferece retorno ao catálogo, mantendo os demais estados pessoais visíveis
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
### Requirement: Funcionário encontra estudante por e-mail para reserva

O sistema MUST permitir a bibliotecários e admins autenticados localizar uma conta estudante por e-mail completo normalizado e retornar somente a identidade mínima necessária para confirmar o alvo da reserva.

#### Scenario: Estudante localizado
- **WHEN** bibliotecário ou admin busca e-mail completo válido associado a estudante
- **THEN** o backend retorna somente o identificador e o nome necessários para confirmar a pessoa

#### Scenario: E-mail sem estudante correspondente
- **WHEN** bibliotecário ou admin busca e-mail válido sem conta estudante correspondente
- **THEN** a interface informa que não encontrou estudante e não inicia criação de reserva

#### Scenario: Perfil sem privilégio tenta buscar estudante
- **WHEN** visitante ou estudante tenta consultar estudante para uma reserva administrativa
- **THEN** o backend recusa a consulta sem revelar a existência de contas
### Requirement: Bibliotecário cria reserva em nome de estudante com elegibilidade revalidada

O sistema MUST permitir que bibliotecário ou admin autenticado crie reserva para uma conta de estudante existente somente após o backend revalidar perfil do alvo, situação do título e todas as regras de elegibilidade existentes.

#### Scenario: Reserva criada para estudante elegível
- **WHEN** bibliotecário ou admin solicita reserva para estudante elegível e título ativo
- **THEN** o backend cria uma reserva associada ao estudante e título informados, sem criar empréstimo ou sessão de estudante

#### Scenario: Estudante alvo tem empréstimo atrasado
- **WHEN** estudante alvo tem empréstimo vencido e não devolvido, com `devolvido_em` nulo ou zero
- **THEN** o backend recusa a reserva sem alterar a fila

#### Scenario: Estudante alvo tem empréstimo ativo de outro título
- **WHEN** estudante alvo tem até dois empréstimos ativos de outros títulos e solicita uma reserva elegível
- **THEN** o backend não recusa a reserva apenas pela existência desses empréstimos

#### Scenario: Estudante alvo atingiu o limite de empréstimos
- **WHEN** estudante alvo tem três empréstimos ativos
- **THEN** o backend recusa a reserva sem alterar a fila

#### Scenario: Estudante alvo já tem o título emprestado
- **WHEN** estudante alvo já possui empréstimo ativo não atrasado de exemplar daquele título
- **THEN** o backend recusa a reserva sem alterar a fila

#### Scenario: Reserva ativa duplicada
- **WHEN** estudante alvo já possui reserva ativa para o título
- **THEN** o backend recusa a duplicata e preserva a reserva existente

#### Scenario: Alvo não é estudante ou não existe
- **WHEN** identificador informado não corresponde a conta estudante existente
- **THEN** o backend recusa a operação sem criar reserva

#### Scenario: Título inativo
- **WHEN** bibliotecário ou admin tenta criar reserva para título inativo
- **THEN** o backend recusa a operação sem alterar a fila

#### Scenario: Perfil sem privilégio tenta criar para outra pessoa
- **WHEN** visitante ou estudante tenta criar reserva administrativa para outra conta
- **THEN** o backend recusa a operação sem criar reserva
### Requirement: Reserva administrativa respeita integralmente FIFO

O sistema MUST inserir uma reserva criada em nome de estudante na ordem normal da fila e não permitir que a função administrativa altere posições ou atribua prioridade.

#### Scenario: Reserva adicionada após a fila existente
- **WHEN** bibliotecário ou admin cria reserva para estudante elegível enquanto há reservas aguardando
- **THEN** a nova reserva é posicionada depois das reservas existentes conforme a ordem de criação registrada pelo servidor

#### Scenario: Tentativa de informar prioridade ou posição
- **WHEN** cliente inclui posição, prioridade ou horário de criação na solicitação administrativa
- **THEN** o backend ignora ou recusa esses valores e preserva a ordem FIFO determinada pelo servidor

### Requirement: Falhas ao solicitar reserva têm mensagens específicas
A interface MUST traduzir falhas conhecidas ao solicitar reserva em mensagens curtas em português com código identificador, sem revelar detalhes internos ou credenciais.

#### Scenario: Sessão expirada
- **WHEN** serviço recusa a reserva com HTTP 401
- **THEN** a interface mostra `[RES-401] Sua sessão expirou, entre de novo`

#### Scenario: Perfil sem permissão
- **WHEN** serviço recusa a reserva com HTTP 403
- **THEN** a interface mostra `[RES-403] Seu perfil não pode reservar`

#### Scenario: Recurso ou endpoint indisponível
- **WHEN** serviço responde HTTP 404 à solicitação
- **THEN** a interface mostra `[RES-404] Este recurso ainda não está disponível no servidor`

#### Scenario: Regra de negócio conflita com a reserva
- **WHEN** serviço responde HTTP 409 por limite ou duplicidade
- **THEN** a interface mostra `[RES-409]` e a mensagem de negócio segura correspondente ao limite ou à reserva já existente

#### Scenario: Erro do servidor
- **WHEN** serviço responde com código HTTP entre 500 e 599
- **THEN** a interface mostra `[RES-5XX] O servidor teve um problema (código 5xx)`

#### Scenario: Tempo esgotado
- **WHEN** a solicitação de reserva termina por timeout
- **THEN** a interface mostra `[RES-TIMEOUT] Sem resposta do servidor. Confira Minhas reservas antes de tentar de novo`

#### Scenario: Outros erros de comunicação
- **WHEN** ocorre falha diferente de status conhecido ou timeout
- **THEN** a interface mostra código curto e mensagem genérica segura, sem resposta bruta do serviço

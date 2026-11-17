# Spec Delta

## MODIFIED Requirements

### Requirement: Estudante solicita empréstimo sem concluir retirada
O sistema MUST separar o pedido do estudante da confirmação física do empréstimo; registrar ou recusar o pedido conforme elegibilidade validada no servidor e situação ativa do título, sem iniciar prazo de empréstimo antes da retirada.

#### Scenario: Pedido de estudante elegível
- **WHEN** estudante autenticado solicita empréstimo de título ativo
- **THEN** o backend valida identidade e elegibilidade e registra o pedido sem tratá-lo como retirada concluída

#### Scenario: Estudante inelegível
- **WHEN** estudante possui empréstimo ativo vencido ou não atende a outra regra aprovada
- **THEN** o backend recusa o pedido e não altera empréstimos nem disponibilidade

#### Scenario: Empréstimos ativos de outros títulos abaixo do limite
- **WHEN** estudante possui até dois empréstimos ativos de outros títulos e solicita um título elegível
- **THEN** o backend permite a solicitação se não houver atraso nem empréstimo ativo do mesmo título

#### Scenario: Limite de três empréstimos ativos
- **WHEN** estudante já possui três empréstimos ativos
- **THEN** o backend recusa nova solicitação ou retirada sem alterar empréstimos nem disponibilidade

#### Scenario: Estudante já possui exemplar do mesmo título
- **WHEN** estudante tenta solicitar ou retirar outro exemplar de título que já possui ativo
- **THEN** o backend recusa a operação sem alterar empréstimos nem disponibilidade

#### Scenario: Sem exemplar disponível
- **WHEN** estudante elegível solicita empréstimo de título ativo e não há exemplar imediatamente disponível
- **THEN** o pedido entra na fila FIFO de reservas do título e não cria um empréstimo nem uma fila separada de solicitações

#### Scenario: Exemplar atribuído à reserva
- **WHEN** um exemplar fica disponível e a reserva do estudante chega à sua vez na fila FIFO
- **THEN** o backend associa o exemplar à reserva e registra oferta de retirada válida por 48 horas corridas, com timestamps armazenados em UTC e apresentados no fuso `America/Sao_Paulo`; essa regra não altera o prazo de empréstimo de 14 dias corridos

#### Scenario: Solicitação para título desativado
- **WHEN** estudante autenticado solicita empréstimo ou reserva de título inativo
- **THEN** o backend recusa a solicitação sem criar pedido, reserva ou empréstimo

## ADDED Requirements

### Requirement: Minha biblioteca explica falhas de carregamento
A área pessoal MUST informar falhas de integração com mensagens específicas e sem expor detalhes internos, oferecendo nova autenticação quando a sessão não for aceita.

#### Scenario: Sessão inválida ou expirada
- **WHEN** uma chamada pessoal retorna HTTP 401
- **THEN** a interface informa que a sessão expirou ou não é válida, encerra a sessão local e oferece um link acessível para entrar novamente

#### Scenario: Perfil sem permissão
- **WHEN** uma chamada pessoal retorna HTTP 403
- **THEN** a interface informa que a conta não tem permissão para consultar o recurso

#### Scenario: Recurso ou rota indisponível
- **WHEN** uma chamada pessoal retorna HTTP 404
- **THEN** a interface informa que o recurso não foi encontrado ou que a rota não está disponível

#### Scenario: Serviço indisponível ou timeout
- **WHEN** o serviço retorna HTTP 5xx ou a chamada excede o tempo limite
- **THEN** a interface informa que o serviço está temporariamente indisponível e orienta tentar novamente mais tarde

#### Scenario: Resposta inválida
- **WHEN** o serviço retorna JSON inválido ou dados incompatíveis com o contrato pessoal
- **THEN** a interface informa que a resposta do serviço é inválida sem exibir conteúdo interno

#### Scenario: Estado de erro acessível
- **WHEN** uma falha impede carregar os registros pessoais
- **THEN** a mensagem é anunciada como alerta acessível e os estados vazios existentes não são apresentados como se a consulta tivesse sido bem-sucedida

### Requirement: Equipe administra retiradas e empréstimos ativos
O sistema MUST permitir a bibliotecários e admins consultar solicitações pendentes e empréstimos ativos, registrar retirada/devolução física e recusar somente solicitações ainda pendentes, validando autorização e elegibilidade no backend.

#### Scenario: Confirmar retirada elegível
- **WHEN** bibliotecário/admin confirma a retirada de solicitação elegível
- **THEN** o backend revalida FIFO, disponibilidade, limite e atraso, cria o empréstimo por 14 dias e marca a solicitação como atendida

#### Scenario: Recusar solicitação pendente
- **WHEN** bibliotecário/admin recusa solicitação em estado `pendente`
- **THEN** o backend marca somente a solicitação como `recusada` sem alterar exemplares ou empréstimos

#### Scenario: Recusar solicitação já atendida ou em reserva
- **WHEN** bibliotecário/admin tenta recusar solicitação que não está `pendente`
- **THEN** o backend recusa a operação sem alterar solicitação, reserva ou empréstimo

#### Scenario: Consultar empréstimos ativos e atrasos
- **WHEN** bibliotecário/admin abre o painel de circulação
- **THEN** recebe empréstimos não devolvidos com estudante, título e vencimento suficientes para identificar atrasos e registrar devolução

#### Scenario: Registrar devolução
- **WHEN** bibliotecário/admin confirma devolução de empréstimo ativo
- **THEN** o backend registra a devolução e disponibiliza o exemplar conforme condições e fila FIFO

#### Scenario: Perfil sem privilégio tenta operar circulação
- **WHEN** visitante ou estudante consulta ou altera filas administrativas
- **THEN** o backend recusa a operação sem expor dados de terceiros ou alterar registros

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

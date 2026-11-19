# loan-circulation Specification

## Purpose

Definir solicitação, retirada física e devolução de exemplares, com prazos e elegibilidade verificados no backend da biblioteca.

## Requirements

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

#### Scenario: Empréstimos ativos de outros títulos abaixo do limite
- **WHEN** estudante possui até dois empréstimos ativos de outros títulos e solicita um título elegível
- **THEN** o backend permite a solicitação se não houver atraso nem empréstimo ativo do mesmo título

#### Scenario: Limite de três empréstimos ativos
- **WHEN** estudante já possui três empréstimos ativos
- **THEN** o backend recusa nova solicitação ou retirada sem alterar empréstimos nem disponibilidade

#### Scenario: Estudante já possui exemplar do mesmo título
- **WHEN** estudante tenta solicitar ou retirar outro exemplar de título que já possui ativo
- **THEN** o backend recusa a operação sem alterar empréstimos nem disponibilidade

#### Scenario: Solicitação para título desativado
- **WHEN** estudante autenticado solicita empréstimo ou reserva de título inativo
- **THEN** o backend recusa a solicitação sem criar pedido, reserva ou empréstimo
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
### Requirement: Limite de empréstimos ativos por estudante e exemplar
O sistema MUST permitir até três empréstimos ativos por estudante, impedir um quarto empréstimo ativo e impedir mais de um empréstimo ativo por exemplar, inclusive em operações concorrentes.

#### Scenario: Estudante abaixo do limite
- **WHEN** estudante possui até dois empréstimos ativos de outros títulos e solicita outro título elegível
- **THEN** o backend permite a operação se não houver atraso nem empréstimo ativo do mesmo título

#### Scenario: Limite ativo do estudante
- **WHEN** estudante já possui três empréstimos ativos e tenta obter outro
- **THEN** o backend recusa a nova confirmação de retirada

#### Scenario: Mesmo título já emprestado
- **WHEN** estudante possui exemplar ativo de um título e tenta obter outro exemplar do mesmo título
- **THEN** o backend recusa a operação sem afetar empréstimos existentes

#### Scenario: Exemplar já emprestado
- **WHEN** bibliotecário tenta emprestar exemplar com empréstimo ativo
- **THEN** o backend recusa a operação e mantém o empréstimo existente
### Requirement: Bibliotecário confirma devolução

O sistema MUST registrar a devolução física de empréstimo ativo somente por bibliotecário ou admin autenticado.

#### Scenario: Devolução registrada
- **WHEN** bibliotecário ou admin confirma a devolução do exemplar
- **THEN** o sistema registra o instante de devolução e encerra o empréstimo ativo

#### Scenario: Devolução inválida
- **WHEN** pedido referencia empréstimo inexistente, já encerrado ou usuário sem perfil bibliotecário ou admin
- **THEN** o backend recusa a operação sem alterar o histórico
### Requirement: Atraso bloqueia novas operações do estudante
O sistema MUST considerar atrasado empréstimo ativo cujo vencimento passou e bloquear novos pedidos de empréstimo e reservas desse estudante.

#### Scenario: Empréstimo vencido
- **WHEN** estudante tem empréstimo ativo com vencimento anterior ao instante atual
- **THEN** o backend recusa novos pedidos de empréstimo e comunica a restrição

#### Scenario: Empréstimo não vencido
- **WHEN** estudante tem empréstimo ativo ainda dentro do prazo
- **THEN** a regra de atraso não o bloqueia por vencimento, sem remover os demais limites aprovados
### Requirement: Estudante acompanha empréstimos e solicitações próprios
A interface MUST permitir que estudante autenticado consulte somente seus empréstimos, solicitações e reservas na rota `/reservas`, com estados e prazos retornados pelo serviço.

#### Scenario: Consultar situação pessoal
- **WHEN** estudante autenticado abre `/reservas`
- **THEN** a interface organiza pedidos, ofertas de reserva e empréstimos em quatro blocos com contadores: “Aguardando aprovação”, “Aprovadas”, “Emprestados” e “Em atraso”

#### Scenario: Não há registros pessoais
- **WHEN** estudante autenticado não possui itens em um ou mais estados
- **THEN** cada bloco vazio apresenta contador zero e orientação amigável sem ocultar os demais blocos

#### Scenario: Sessão sem perfil estudante
- **WHEN** visitante ou bibliotecário tenta abrir a área pessoal de estudante
- **THEN** a interface bloqueia ou redireciona o acesso e não consulta dados pessoais de estudante

#### Scenario: Aguardando aprovação
- **WHEN** estudante possui pedido pendente
- **THEN** o bloco apresenta o título e a data de solicitação quando retornados pelo serviço, sem inventar data ausente

#### Scenario: Reserva aprovada
- **WHEN** estudante possui reserva ofertada
- **THEN** o bloco apresenta o título e o prazo de retirada retornado pelo serviço

#### Scenario: Empréstimo ativo em dia
- **WHEN** estudante possui empréstimo não devolvido e ainda dentro do prazo
- **THEN** o bloco apresenta a data de devolução e os dias restantes calculados a partir do vencimento retornado

#### Scenario: Empréstimo atrasado
- **WHEN** estudante possui empréstimo ativo vencido
- **THEN** a página destaca um alerta no topo, e o bloco Em atraso apresenta o contador, os dias de atraso e orientação para procurar a biblioteca

#### Scenario: Dados insuficientes para identificar título
- **WHEN** o registro de empréstimo não permite associar um título com os dados existentes
- **THEN** a interface não inventa o título e a necessidade de identificador/nome do título é registrada como dependência do contrato Xano

#### Scenario: Admin em visão de estudante
- **WHEN** admin em visão simulada abre `/reservas`
- **THEN** a interface usa somente a própria sessão admin e apresenta a recusa do backend sem consultar ou simular dados pessoais de estudante

### Requirement: Rota antiga da área pessoal redireciona para Reservas
A rota `/minha-biblioteca` MUST permanecer compatível e redirecionar para `/reservas` sem consultar dados pessoais antes do redirecionamento.

#### Scenario: Abrir a rota antiga
- **WHEN** estudante autenticado abre `/minha-biblioteca`
- **THEN** a aplicação redireciona para `/reservas`

#### Scenario: Visitante abre a rota antiga
- **WHEN** visitante abre `/minha-biblioteca`
- **THEN** a aplicação redireciona para `/login` sem enviar consulta de dados pessoais
### Requirement: Estudante recebe aviso de empréstimo atrasado
A interface MUST destacar quando estudante possui empréstimo ativo vencido e informar que o backend pode bloquear novas solicitações e reservas.

#### Scenario: Empréstimo vencido e não devolvido
- **WHEN** estudante consulta um empréstimo cujo vencimento passou e `devolvido_em` é nulo ou zero
- **THEN** a interface exibe um aviso de atraso e orienta a procurar a biblioteca

#### Scenario: Empréstimo devolvido ou ainda no prazo
- **WHEN** empréstimo foi devolvido ou seu vencimento ainda não passou
- **THEN** a interface não classifica esse empréstimo como atraso ativo

#### Scenario: Backend bloqueia nova solicitação
- **WHEN** backend recusa uma solicitação por atraso ou outra regra de elegibilidade
- **THEN** a interface apresenta uma mensagem de recusa e não indica que a solicitação foi criada
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

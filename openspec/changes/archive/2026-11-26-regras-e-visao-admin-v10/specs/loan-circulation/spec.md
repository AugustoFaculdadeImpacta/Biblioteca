# Spec Delta

## MODIFIED Requirements

### Requirement: Estudante solicita empréstimo sem concluir retirada
O sistema MUST separar o pedido do estudante da confirmação física do empréstimo; registrar ou recusar o pedido conforme elegibilidade validada no servidor e situação ativa do título, sem iniciar prazo de empréstimo antes da retirada.

#### Scenario: Pedido de estudante elegível
- **WHEN** estudante autenticado solicita empréstimo de título ativo
- **THEN** o backend valida identidade e elegibilidade e registra o pedido sem tratá-lo como retirada concluída

#### Scenario: Estudante inelegível
- **WHEN** estudante não atende a uma regra configurada de elegibilidade
- **THEN** o backend recusa o pedido e não altera empréstimos nem disponibilidade

#### Scenario: Sem exemplar disponível
- **WHEN** estudante elegível solicita empréstimo de título ativo e não há exemplar imediatamente disponível
- **THEN** o pedido entra na fila FIFO de reservas do título e não cria um empréstimo nem uma fila separada de solicitações

#### Scenario: Exemplar atribuído à reserva
- **WHEN** um exemplar fica disponível e a reserva do estudante chega à sua vez na fila FIFO
- **THEN** o backend associa o exemplar à reserva e registra oferta de retirada válida pelo número de horas configurado, com timestamps armazenados em UTC e apresentados no fuso `America/Sao_Paulo`; essa regra não altera o prazo de empréstimo configurado

#### Scenario: Empréstimos ativos de outros títulos abaixo do limite
- **WHEN** estudante possui menos empréstimos ativos que `limite_emprestimos_ativos` em outros títulos e solicita um título elegível
- **THEN** o backend permite a solicitação se não houver bloqueio por atraso ou empréstimo ativo do mesmo título

#### Scenario: Limite de três empréstimos ativos
- **WHEN** estudante possui quantidade de empréstimos ativos igual a `limite_emprestimos_ativos`
- **THEN** o backend recusa nova solicitação ou retirada sem alterar empréstimos nem disponibilidade

#### Scenario: Estudante já possui exemplar do mesmo título
- **WHEN** estudante tenta solicitar ou retirar outro exemplar de título que já possui ativo
- **THEN** o backend recusa a operação sem alterar empréstimos nem disponibilidade

#### Scenario: Solicitação para título desativado
- **WHEN** estudante autenticado solicita empréstimo ou reserva de título inativo
- **THEN** o backend recusa a solicitação sem criar pedido, reserva ou empréstimo

#### Scenario: Limite de pedidos em aberto atingido
- **WHEN** estudante possui quantidade de pedidos em aberto igual a `limite_pedidos_em_aberto`
- **THEN** o backend recusa novo pedido sem alterar pedidos, reservas ou empréstimos

#### Scenario: Reserva ativa existente
- **WHEN** estudante solicita título que já possui reserva ativa e `permitir_pedido_com_reserva_ativa` é falso
- **THEN** o backend recusa o novo pedido e preserva a reserva existente

#### Scenario: Reserva ativa permitida
- **WHEN** estudante solicita título que já possui reserva ativa e `permitir_pedido_com_reserva_ativa` é verdadeiro
- **THEN** o backend aplica as demais regras configuradas e não cria duplicidade de reserva ativa

### Requirement: Bibliotecário confirma retirada física
O sistema MUST criar o empréstimo de um exemplar físico somente quando bibliotecário ou admin autenticado confirmar a retirada e o backend revalidar elegibilidade e disponibilidade.

#### Scenario: Retirada confirmada
- **WHEN** bibliotecário ou admin confirma a retirada de exemplar elegível para estudante elegível
- **THEN** o sistema registra a retirada, define vencimento para `prazo_emprestimo_dias` depois e marca o empréstimo como ativo

#### Scenario: Retirada concorrente ou inelegível
- **WHEN** duas confirmações concorrem pelo mesmo exemplar ou a elegibilidade mudou
- **THEN** o backend permite no máximo uma confirmação válida e recusa a operação conflitante sem criar empréstimo duplicado

#### Scenario: Estudante tenta confirmar retirada
- **WHEN** estudante tenta executar a confirmação física
- **THEN** o backend recusa a operação sem criar empréstimo

### Requirement: Limite de empréstimos ativos por estudante e exemplar
O sistema MUST permitir até `limite_emprestimos_ativos` empréstimos ativos por estudante e impedir mais de um empréstimo ativo por exemplar, inclusive em operações concorrentes.

#### Scenario: Estudante abaixo do limite
- **WHEN** estudante possui quantidade de empréstimos ativos inferior ao limite configurado e solicita outro título elegível
- **THEN** o backend permite a operação se não houver bloqueio por atraso nem empréstimo ativo do mesmo título

#### Scenario: Limite ativo do estudante
- **WHEN** estudante já possui `limite_emprestimos_ativos` empréstimos ativos e tenta obter outro
- **THEN** o backend recusa a nova confirmação de retirada

#### Scenario: Mesmo título já emprestado
- **WHEN** estudante possui exemplar ativo de um título e tenta obter outro exemplar do mesmo título
- **THEN** o backend recusa a operação sem afetar empréstimos existentes

#### Scenario: Exemplar já emprestado
- **WHEN** bibliotecário tenta emprestar exemplar com empréstimo ativo
- **THEN** o backend recusa a operação e mantém o empréstimo existente

### Requirement: Atraso bloqueia novas operações do estudante
O sistema MUST aplicar a regra `bloquear_com_atraso` aos novos pedidos de empréstimo e reservas do estudante.

#### Scenario: Empréstimo vencido
- **WHEN** estudante tem empréstimo ativo com vencimento anterior ao instante atual e `bloquear_com_atraso` é verdadeiro
- **THEN** o backend recusa novos pedidos de empréstimo e comunica a restrição

#### Scenario: Empréstimo vencido com bloqueio desativado
- **WHEN** estudante tem empréstimo ativo vencido e `bloquear_com_atraso` é falso
- **THEN** o atraso não bloqueia a operação, sem remover os demais limites e regras aprovados

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
- **WHEN** admin em visão de estudante abre `/reservas`
- **THEN** a interface usa a sessão admin, apresenta somente os registros próprios do admin e executa as ações de estudante permitidas pelo endpoint; não consulta nem simula dados de terceiros

### Requirement: Equipe administra retiradas e empréstimos ativos
O sistema MUST permitir a bibliotecários e admins consultar solicitações pendentes e empréstimos ativos, registrar retirada/devolução física e recusar somente solicitações ainda pendentes, validando autorização e elegibilidade no backend.

#### Scenario: Confirmar retirada elegível
- **WHEN** bibliotecário/admin confirma a retirada de solicitação elegível
- **THEN** o backend revalida FIFO, disponibilidade, `limite_emprestimos_ativos` e `bloquear_com_atraso`, cria o empréstimo pelo prazo configurado e marca a solicitação como atendida

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

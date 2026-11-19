# Spec Delta

## MODIFIED Requirements

### Requirement: Estudante acompanha empréstimos e solicitações próprios
A interface MUST permitir que estudante autenticado consulte somente seus empréstimos, solicitações e reservas na rota `/reservas`, com estados e prazos retornados pelo serviço.

#### Scenario: Consultar situação pessoal
- **WHEN** estudante autenticado abre `/reservas`
- **THEN** a interface organiza pedidos, ofertas de reserva e empréstimos em quatro blocos com contadores: “Aguardando aprovação”, “Aprovadas”, “Emprestados” e “Em atraso”

#### Scenario: Não há registros pessoais
- **WHEN** estudante autenticado não possui itens em um ou mais estados
- **THEN** cada bloco vazio apresenta contador zero e orientação amigável sem ocultar os demais blocos

#### Scenario: Sessão sem perfil estudante
- **WHEN** visitante ou bibliotecário tenta abrir a área pessoal
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

## ADDED Requirements

### Requirement: Rota antiga da área pessoal redireciona para Reservas
A rota `/minha-biblioteca` MUST permanecer compatível e redirecionar para `/reservas` sem consultar dados pessoais antes do redirecionamento.

#### Scenario: Abrir a rota antiga
- **WHEN** estudante autenticado abre `/minha-biblioteca`
- **THEN** a aplicação redireciona para `/reservas`

#### Scenario: Visitante abre a rota antiga
- **WHEN** visitante abre `/minha-biblioteca`
- **THEN** a aplicação redireciona para `/login` sem enviar consulta de dados pessoais

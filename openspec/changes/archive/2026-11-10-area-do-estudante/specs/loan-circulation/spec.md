# Spec Delta

## ADDED Requirements

### Requirement: Estudante acompanha empréstimos e solicitações próprios
A interface MUST permitir que estudante autenticado consulte seus empréstimos e solicitações com seus estados e prazos, sem expor registros de outras pessoas.

#### Scenario: Consultar situação pessoal
- **WHEN** estudante autenticado abre sua área pessoal
- **THEN** a interface apresenta somente os empréstimos e solicitações associados à sessão, incluindo seus estados e vencimentos definidos pelo serviço

#### Scenario: Não há registros pessoais
- **WHEN** estudante autenticado ainda não possui empréstimos ou solicitações
- **THEN** a interface informa que não há registros e oferece retorno ao catálogo

#### Scenario: Sessão sem perfil estudante
- **WHEN** visitante ou bibliotecário tenta abrir a área pessoal de estudante
- **THEN** a interface bloqueia ou redireciona o acesso e não consulta dados pessoais de estudante

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

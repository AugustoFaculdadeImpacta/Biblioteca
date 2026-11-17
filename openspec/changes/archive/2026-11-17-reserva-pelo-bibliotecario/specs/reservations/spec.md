# Spec Delta

## ADDED Requirements

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

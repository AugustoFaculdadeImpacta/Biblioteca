# Spec Delta

## MODIFIED Requirements

### Requirement: Cadastro de título usa somente os campos definidos
A interface MUST enviar somente os campos aceitos pelo endpoint local de criação de título e usar o registro retornado para obter seu identificador.

#### Scenario: Metadados do título no formulário
- **WHEN** bibliotecário autenticado preenche o cadastro ou edição de um título
- **THEN** título e autores são obrigatórios, e ISBN, editora, edição, ano de publicação, descrição e link HTTPS da capa são opcionais

#### Scenario: Envio do título
- **WHEN** bibliotecário confirma cadastro ou edição com dados válidos
- **THEN** a interface envia somente campos opcionais preenchidos entre `titulo`, `autores`, `isbn`, `editora`, `edicao`, `ano_publicacao`, `descricao` e `capa_url`, obtendo o identificador retornado na criação

#### Scenario: URL de capa inválida
- **WHEN** bibliotecário informa um link de capa que não usa HTTPS ou não é uma URL válida
- **THEN** a interface informa a validação e não envia a operação

### Requirement: Interface pública apresenta títulos e disponibilidade
A interface MUST permitir que visitantes e estudantes consultem o catálogo público por lista e detalhe, sem autenticação, exibindo a disponibilidade informada pelo serviço e os metadados opcionais disponíveis.

#### Scenario: Consultar títulos públicos
- **WHEN** visitante ou estudante abre o catálogo
- **THEN** a interface apresenta títulos ativos em cartões com capa disponível ou capa CSS de fallback e permite abrir o detalhe

#### Scenario: Consultar disponibilidade no detalhe
- **WHEN** visitante ou estudante abre o detalhe de um título
- **THEN** a interface apresenta capa disponível ou fallback, título, autoria, categorias, descrição e exemplares disponíveis sem expor dados pessoais

#### Scenario: Descrição ausente
- **WHEN** o título não tem descrição preenchida
- **THEN** o detalhe apresenta “Sem descrição cadastrada.”

#### Scenario: Campo de capa ausente no contrato
- **WHEN** uma resposta não inclui `capa_url` ou contém seu valor nulo/vazio
- **THEN** a interface continua exibindo o título com a capa CSS de fallback e não trata a ausência do campo como erro

## ADDED Requirements

### Requirement: Cartão de catálogo evita metadado repetido
Cada cartão MUST apresentar a categoria uma única vez como etiqueta e manter capa, título, autoria, disponibilidade e ação de detalhe legíveis.

#### Scenario: Categorias exibidas no cartão
- **WHEN** cartão de título possui uma ou mais categorias
- **THEN** as categorias aparecem na etiqueta sem uma segunda linha repetindo “Categorias:”

#### Scenario: Capa remota disponível ou ausente
- **WHEN** cartão possui `capa_url` HTTPS ou não possui capa
- **THEN** a imagem usa texto alternativo acessível quando presente e, na ausência, é exibida a capa CSS derivada de categoria e título

### Requirement: Ação no detalhe respeita o perfil efetivo
O detalhe MUST oferecer a ação de reserva ao estudante autenticado, orientar visitantes ao login e ocultar a ação de estudante para bibliotecário e admin.

#### Scenario: Estudante autenticado abre o detalhe
- **WHEN** estudante autenticado consulta um título
- **THEN** vê “Reservar” e a operação usa o fluxo autenticado existente, que deixa elegibilidade e resultado final sob validação do backend

#### Scenario: Visitante abre o detalhe
- **WHEN** visitante consulta um título
- **THEN** vê “Entrar para reservar” com destino de login

#### Scenario: Perfil não estudante abre o detalhe
- **WHEN** bibliotecário, admin ou admin em visão simulada consulta um título
- **THEN** não vê nem pode acionar a ação exclusiva de estudante

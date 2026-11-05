# Spec Delta

## ADDED Requirements

### Requirement: Interface administrativa do acervo é exclusiva de bibliotecários
A interface MUST permitir acesso às ações administrativas somente após autenticação com perfil `bibliotecario`; a autorização do backend permanece obrigatória para toda escrita.

#### Scenario: Bibliotecário autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `bibliotecario` abre a área de administração
- **THEN** a interface permite acessar os formulários administrativos e envia as operações com a sessão autenticada em cada chamada

#### Scenario: Estudante ou visitante tenta acessar a administração
- **WHEN** estudante autenticado ou visitante abre uma rota ou tenta uma ação administrativa
- **THEN** a interface bloqueia ou redireciona o acesso e não envia requisição de escrita

#### Scenario: Backend recusa operação administrativa
- **WHEN** o backend recusa a operação por perfil insuficiente
- **THEN** a interface não indica sucesso e informa a recusa sem expor detalhes internos

### Requirement: Cadastro de título usa somente os campos definidos
A interface MUST enviar somente os campos aceitos pelo endpoint local de criação de título e usar o registro retornado para obter seu identificador.

#### Scenario: Metadados do título no formulário
- **WHEN** bibliotecário autenticado preenche o cadastro de um título
- **THEN** título e autores são obrigatórios, e ISBN, editora, edição, ano de publicação e descrição são opcionais

#### Scenario: Envio do título
- **WHEN** bibliotecário confirma o cadastro com os dados válidos do formulário
- **THEN** a interface envia somente `titulo`, `autores`, `isbn`, `editora`, `edicao`, `ano_publicacao` e `descricao` para `POST /catalogo/titulos` e obtém `id` do registro retornado

### Requirement: Título pode ser associado a categorias existentes
A interface MUST permitir selecionar categorias obtidas da listagem pública e associá-las ao título recém-criado usando os identificadores retornados pelos endpoints.

#### Scenario: Carregar categorias para seleção
- **WHEN** bibliotecário autenticado abre o cadastro de título
- **THEN** a interface lista as categorias retornadas por `GET /catalogo/categorias` usando os campos `id` e `nome`

#### Scenario: Associar categorias selecionadas
- **WHEN** bibliotecário seleciona uma ou mais categorias para um título criado
- **THEN** a interface envia uma associação para cada seleção usando `titulo_id` como identificador de rota e `categoria_id` como entrada e apresenta sucesso somente para associações confirmadas

#### Scenario: Título já associado à categoria ou referência inválida
- **WHEN** a associação é recusada por duplicidade ou referência inexistente
- **THEN** a interface informa a falha sem indicar associação inexistente como concluída e permite retomar sem recriar o título

### Requirement: Bibliotecário pode criar exemplares físicos do título
A interface MUST permitir criar uma quantidade solicitada de exemplares para um título existente, enviando somente seu `titulo_id` e exibindo o código de tombo gerado pelo servidor para cada exemplar criado.

#### Scenario: Criar exemplares
- **WHEN** bibliotecário solicita um ou mais exemplares para um título criado
- **THEN** a interface repete `POST /admin/exemplares` com `titulo_id` para cada unidade e apresenta os registros e códigos de tombo retornados

#### Scenario: Falha parcial ao criar exemplares
- **WHEN** uma das chamadas sequenciais de criação falha após outras terem sido confirmadas
- **THEN** a interface distingue as unidades criadas das pendentes e não repete automaticamente escritas já confirmadas

#### Scenario: Resposta não contém identificador ou código esperado
- **WHEN** uma resposta bem-sucedida de criação não contém os campos necessários definidos pela implementação local
- **THEN** a interface informa que o resultado precisa ser conferido, não presume sucesso completo e não repete automaticamente a escrita

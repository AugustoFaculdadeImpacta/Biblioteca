# catalog Specification

## Purpose

Define consulta pública e administração autorizada do acervo, preservando a distinção entre obra bibliográfica, categorias e exemplares físicos.

## Requirements

### Requirement: Catálogo é consultável publicamente
O sistema MUST permitir a visitantes consultar títulos e disponibilidade agregada sem autenticação, derivando disponibilidade dos exemplares elegíveis.

#### Scenario: Consulta pública
- **WHEN** visitante solicita o catálogo ou um título
- **THEN** o sistema retorna metadados bibliográficos publicados e disponibilidade agregada, sem dados pessoais de estudantes

#### Scenario: Disponibilidade por exemplares
- **WHEN** o sistema informa disponibilidade de um título
- **THEN** o resultado deriva dos exemplares físicos elegíveis e não de uma quantidade independente mantida no título

### Requirement: Título pode relacionar múltiplas categorias e exemplares
O sistema MUST representar uma obra bibliográfica separada de suas categorias e unidades físicas, permitindo relação muitos-para-muitos entre títulos e categorias e um-para-muitos entre título e exemplar.

#### Scenario: Metadados bibliográficos
- **WHEN** bibliotecário cria ou atualiza um título
- **THEN** título e autor(es) são obrigatórios; ISBN, editora, edição, ano de publicação e descrição são opcionais

#### Scenario: Título em várias categorias
- **WHEN** título é associado a mais de uma categoria
- **THEN** consulta do título e consultas por categoria refletem todas as associações

#### Scenario: Múltiplas unidades físicas
- **WHEN** um título possui vários exemplares
- **THEN** cada exemplar mantém identidade e condição próprias sob o título correspondente

#### Scenario: Código de tombo do exemplar
- **WHEN** bibliotecário cria uma unidade física
- **THEN** o sistema atribui ao exemplar um código de tombo único e imutável, no formato exemplificado por `EX-000001`; cada exemplar recebe código diferente e o código não é o ISBN

#### Scenario: Código de tombo não é informado pelo cliente
- **WHEN** cliente tenta definir ou alterar o código de tombo em uma operação de exemplar
- **THEN** o backend gera e preserva o código, sem aceitar valor fornecido ou alteração pelo cliente

### Requirement: Administração do acervo exige perfil bibliotecário
O sistema MUST autorizar no backend a criação/atualização de títulos, categorias e associações e a criação de exemplares somente para bibliotecários autenticados. Estados operacionais de exemplares são alterados somente pelos fluxos de empréstimo, reserva e condição.

#### Scenario: Bibliotecário mantém metadados do acervo
- **WHEN** bibliotecário autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Estudante ou visitante tenta administrar acervo
- **WHEN** estudante autenticado ou visitante tenta criar ou atualizar metadados, associar categorias ou criar exemplar
- **THEN** o backend recusa a operação sem alterar dados

#### Scenario: Remoção sem política aprovada
- **WHEN** uma operação tenta remover título, categoria, associação ou exemplar sem política de exclusão/arquivamento aprovada
- **THEN** o contrato não oferece a remoção e o estado persistido permanece inalterado

### Requirement: API de catálogo valida relações
O sistema MUST validar existência e compatibilidade das relações de título, categoria e exemplar antes de persistir alterações administrativas.

#### Scenario: Referência inválida
- **WHEN** pedido administrativo referencia título, categoria ou exemplar inexistente ou incompatível
- **THEN** o sistema recusa a alteração e preserva o estado anterior

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

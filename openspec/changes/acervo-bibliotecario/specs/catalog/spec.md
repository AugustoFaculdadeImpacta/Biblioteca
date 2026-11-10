# Spec Delta

## MODIFIED Requirements

### Requirement: Catálogo é consultável publicamente
O sistema MUST permitir a visitantes consultar títulos ativos e disponibilidade agregada sem autenticação, derivando disponibilidade dos exemplares elegíveis.

#### Scenario: Consulta pública
- **WHEN** visitante solicita o catálogo ou um título
- **THEN** o sistema retorna metadados bibliográficos publicados e disponibilidade agregada de títulos ativos, sem dados pessoais de estudantes

#### Scenario: Disponibilidade por exemplares
- **WHEN** o sistema informa disponibilidade de um título ativo
- **THEN** o resultado deriva dos exemplares físicos elegíveis e não de uma quantidade independente mantida no título

#### Scenario: Título desativado não aparece publicamente
- **WHEN** visitante solicita catálogo ou detalhe de título desativado
- **THEN** o título não é incluído no catálogo público e seu detalhe não é exposto

### Requirement: Administração do acervo exige perfil bibliotecário
O sistema MUST autorizar no backend a bibliotecários e admins autenticados a consultar e manter metadados e exemplares do acervo. Estados operacionais de exemplares são alterados somente pelos fluxos de empréstimo, reserva e condição.

#### Scenario: Bibliotecário mantém metadados do acervo
- **WHEN** bibliotecário autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Admin mantém metadados do acervo
- **WHEN** admin autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Estudante ou visitante tenta administrar acervo
- **WHEN** estudante autenticado ou visitante tenta consultar dados administrativos ou alterar metadados, associações ou exemplares
- **THEN** o backend recusa a operação sem revelar dados administrativos nem alterar dados

#### Scenario: Remoção sem política aprovada
- **WHEN** usuário tenta remover fisicamente título, exemplar, empréstimo ou reserva
- **THEN** o backend recusa a operação e preserva o registro e seu histórico

### Requirement: Interface administrativa do acervo é exclusiva de bibliotecários
A interface MUST permitir acesso às ações administrativas somente após autenticação com perfil `bibliotecario` ou `admin`; a autorização do backend permanece obrigatória para toda leitura administrativa e escrita.

#### Scenario: Bibliotecário autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `bibliotecario` abre a área de administração
- **THEN** a interface permite acessar os formulários administrativos e envia as operações com a sessão autenticada em cada chamada

#### Scenario: Admin autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `admin` abre a área de administração
- **THEN** a interface permite as mesmas ações administrativas disponíveis ao bibliotecário e envia as operações com a sessão autenticada em cada chamada

#### Scenario: Estudante ou visitante tenta acessar a administração
- **WHEN** estudante ou visitante abre uma rota ou tenta uma ação administrativa
- **THEN** a interface bloqueia ou redireciona o acesso e não envia requisição administrativa

#### Scenario: Backend recusa operação administrativa
- **WHEN** o backend recusa a operação por perfil insuficiente
- **THEN** a interface não indica sucesso e informa a recusa sem expor detalhes internos

### Requirement: Bibliotecário pode criar exemplares físicos do título
A interface MUST permitir criar exemplares para título novo ou existente, enviando somente o identificador do título e exibindo o código de tombo gerado pelo servidor para cada unidade.

#### Scenario: Criar exemplares
- **WHEN** bibliotecário ou admin conclui o cadastro de um título e solicita exemplares
- **THEN** a interface cria cada unidade para o título e apresenta os registros e códigos de tombo retornados

#### Scenario: Adicionar exemplares a título existente
- **WHEN** bibliotecário ou admin seleciona título existente e solicita um ou mais exemplares
- **THEN** a interface cria as unidades para o identificador selecionado e apresenta os registros e códigos de tombo retornados

#### Scenario: Falha parcial ao criar exemplares
- **WHEN** uma chamada sequencial de criação falha após outras terem sido confirmadas
- **THEN** a interface distingue as unidades criadas das pendentes e não repete automaticamente escritas já confirmadas

#### Scenario: Resposta não contém identificador ou código esperado
- **WHEN** uma resposta bem-sucedida de criação não contém os campos necessários definidos pela implementação local
- **THEN** a interface informa que o resultado precisa ser conferido, não presume sucesso completo e não repete automaticamente a escrita

## ADDED Requirements

### Requirement: Bibliotecário consulta o acervo administrativo completo
O sistema MUST permitir a bibliotecários e admins autenticados consultar todos os títulos, exemplares e estados operacionais, inclusive itens indisponíveis e títulos desativados.

#### Scenario: Consultar acervo completo
- **WHEN** bibliotecário ou admin abre a área administrativa do acervo
- **THEN** recebe todos os títulos e seus exemplares com os estados necessários à gestão, sem expor dados pessoais de estudantes

#### Scenario: Consultar título desativado
- **WHEN** bibliotecário ou admin consulta o acervo que contém título desativado
- **THEN** o título permanece visível e identificado como desativado, com seu histórico preservado

#### Scenario: Perfil sem privilégio tenta consultar acervo completo
- **WHEN** visitante ou estudante tenta consultar a listagem administrativa
- **THEN** o backend recusa a consulta e não revela os dados administrativos

### Requirement: Bibliotecário edita metadados de título existente
O sistema MUST permitir a bibliotecários e admins autenticados editar os metadados permitidos de um título existente sem alterar seu identificador, exemplares ou histórico.

#### Scenario: Atualização válida
- **WHEN** bibliotecário ou admin envia metadados válidos para título existente
- **THEN** os metadados são atualizados e o identificador e os registros relacionados permanecem preservados

#### Scenario: Título inexistente
- **WHEN** operação de edição referencia título inexistente
- **THEN** o backend recusa a atualização sem criar outro título

#### Scenario: Perfil sem privilégio tenta editar título
- **WHEN** estudante ou visitante tenta editar metadados de título
- **THEN** o backend recusa a alteração sem modificar o acervo

### Requirement: Título é desativado logicamente e reativado com histórico preservado
O sistema MUST usar o estado `ativo` do título para remoção lógica e reativação, sem excluir fisicamente título ou histórico, e deve revalidar empréstimos e reservas no backend antes da desativação.

#### Scenario: Desativar título sem empréstimo ou reserva ativa
- **WHEN** bibliotecário ou admin solicita desativar título sem empréstimo ativo e sem reserva ativa associada ao título ou a seus exemplares
- **THEN** o backend marca o título como inativo, preserva os registros relacionados e remove o título do catálogo público

#### Scenario: Bloquear desativação com empréstimo ativo
- **WHEN** título ou exemplar associado possui empréstimo não devolvido, considerando `devolvido_em` nulo ou zero como não devolvido
- **THEN** o backend recusa a desativação e mantém o título ativo e os registros inalterados

#### Scenario: Bloquear desativação com reserva ativa
- **WHEN** título ou exemplar associado possui reserva ativa segundo os estados definidos pelo contrato de reservas
- **THEN** o backend recusa a desativação e mantém o título ativo e a fila inalterada

#### Scenario: Reativar título
- **WHEN** bibliotecário ou admin reativa título desativado
- **THEN** o título volta a ser elegível para consulta pública, sem recriar o registro nem alterar o histórico existente

#### Scenario: Perfil sem privilégio tenta desativar ou reativar
- **WHEN** estudante ou visitante solicita desativação ou reativação
- **THEN** o backend recusa a operação sem alterar o título

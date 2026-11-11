# Spec Delta

## MODIFIED Requirements

### Requirement: Administração do acervo exige perfil bibliotecário
O sistema MUST autorizar no backend a criação/atualização de títulos, categorias e associações e a criação de exemplares somente para bibliotecários ou admins autenticados. Estados operacionais de exemplares são alterados somente pelos fluxos de empréstimo, reserva e condição.

#### Scenario: Bibliotecário mantém metadados do acervo
- **WHEN** bibliotecário autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Admin mantém metadados do acervo
- **WHEN** admin autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Estudante ou visitante tenta administrar acervo
- **WHEN** estudante autenticado ou visitante tenta criar ou atualizar metadados, associar categorias ou criar exemplar
- **THEN** o backend recusa a operação sem alterar dados

#### Scenario: Remoção sem política aprovada
- **WHEN** uma operação tenta remover título, categoria, associação ou exemplar sem política de exclusão/arquivamento aprovada
- **THEN** o contrato não oferece a remoção e o estado persistido permanece inalterado

### Requirement: Interface administrativa do acervo é exclusiva de bibliotecários
A interface MUST permitir acesso às ações administrativas somente após autenticação com perfil `bibliotecario` ou `admin`; a autorização do backend permanece obrigatória para toda escrita.

#### Scenario: Bibliotecário autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `bibliotecario` abre a área de administração
- **THEN** a interface permite acessar os formulários administrativos e envia as operações com a sessão autenticada em cada chamada

#### Scenario: Admin autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `admin` abre a área de administração
- **THEN** a interface permite as mesmas ações administrativas disponíveis ao bibliotecário e envia as operações com a sessão autenticada em cada chamada

#### Scenario: Estudante ou visitante tenta acessar a administração
- **WHEN** estudante autenticado ou visitante abre uma rota ou tenta uma ação administrativa
- **THEN** a interface bloqueia ou redireciona o acesso e não envia requisição de escrita

#### Scenario: Backend recusa operação administrativa
- **WHEN** o backend recusa a operação por perfil insuficiente
- **THEN** a interface não indica sucesso e informa a recusa sem expor detalhes internos

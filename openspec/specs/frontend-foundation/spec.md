# frontend-foundation Specification

## Purpose

Estabelecer a base acessível e segura do frontend da biblioteca para que capacidades futuras possam ser implementadas sem expor credenciais ou antecipar regras de negócio.

## Requirements

### Requirement: Aplicação apresenta estrutura base navegável
O sistema MUST apresentar uma estrutura comum de aplicação com navegação simples entre áreas, sem executar operações de negócio nesta capability.

#### Scenario: Abertura da aplicação
- **WHEN** visitante abre a aplicação
- **THEN** o sistema apresenta o layout base e controles de navegação disponíveis sem exigir autenticação

#### Scenario: Navegação por teclado
- **WHEN** visitante percorre a estrutura base usando teclado
- **THEN** os controles de navegação podem ser alcançados e ativados sem uso de ponteiro

### Requirement: Controles interativos exibem foco visível
O sistema MUST apresentar um indicador visual distinguível de foco `:focus-visible` em campos e botões quando alcançados por navegação de teclado.

#### Scenario: Foco por teclado em campo
- **WHEN** visitante move o foco para um campo usando teclado
- **THEN** o campo apresenta um indicador visual de foco perceptível

#### Scenario: Foco por teclado em botão
- **WHEN** visitante move o foco para um botão usando teclado
- **THEN** o botão apresenta um indicador visual de foco perceptível

### Requirement: Cliente Xano usa configuração de ambiente no backend
O sistema MUST enviar requisições ao Xano a partir do backend Reflex e obter a URL base de uma variável de ambiente, sem embutir a URL no código cliente ou no bundle público.

#### Scenario: URL base configurada
- **WHEN** o backend Reflex prepara uma requisição ao Xano
- **THEN** o cliente usa a URL base definida em `XANO_API_BASE_URL`

#### Scenario: URL base ausente ou inválida
- **WHEN** o cliente precisa enviar uma requisição e `XANO_API_BASE_URL` está ausente ou inválida
- **THEN** o backend informa um erro de configuração sem realizar a requisição

### Requirement: Token de sessão permanece privado no backend Reflex
O sistema MUST manter o token de sessão somente em estado isolado por sessão no backend Reflex e impedir que ele seja exposto ao navegador, ao bundle público ou aos logs da aplicação.

#### Scenario: Requisição autenticada pelo backend
- **WHEN** uma requisição ao Xano necessita de autenticação
- **THEN** o backend usa o token associado à sessão sem enviá-lo como estado ou conteúdo acessível ao navegador

#### Scenario: Sessões de usuários diferentes
- **WHEN** duas sessões Reflex distintas mantêm tokens diferentes
- **THEN** uma sessão não pode usar nem observar o token da outra

#### Scenario: Registro de erros de rede
- **WHEN** uma requisição autenticada falha
- **THEN** o erro apresentado e os logs não contêm o token nem o cabeçalho de autorização

### Requirement: Navegação compartilhada apresenta opções adequadas à sessão
A aplicação MUST exibir em todas as telas um cabeçalho navegável com opções coerentes com a sessão e o perfil autenticado e acesso ao catálogo público.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece links para Início, Catálogo, Entrar e Cadastrar-se, além de navegação por teclado com foco visível

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Minha biblioteca e Sair e não exibe Entrar, Cadastrar-se ou acesso administrativo

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Cadastrar livro em `/admin/acervo` e Sair

#### Scenario: Usuário encerra a sessão
- **WHEN** usuário autenticado ativa Sair
- **THEN** a sessão privada é removida e a aplicação retorna à página inicial com navegação de visitante

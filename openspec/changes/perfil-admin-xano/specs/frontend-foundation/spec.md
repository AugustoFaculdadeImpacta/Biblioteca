# Spec Delta

## MODIFIED Requirements

### Requirement: Navegação compartilhada apresenta opções adequadas à sessão
A aplicação MUST exibir em todas as telas um cabeçalho navegável com opções coerentes com a sessão e o perfil autenticado e acesso ao catálogo público.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece links para Início, Catálogo, Entrar e Cadastrar-se, além de navegação por teclado com foco visível

#### Scenario: Usuário autenticado navega na aplicação
- **WHEN** usuário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho apresenta “Olá, <nome>” com o nome recebido na sessão, sem exibir e-mail, senha ou token, e oferece Catálogo e Sair

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Minha biblioteca e Sair e não exibe Entrar, Cadastrar-se ou acesso administrativo

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Cadastrar livro em `/admin/acervo` e Sair

#### Scenario: Admin autenticado navega na aplicação
- **WHEN** admin autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece as mesmas opções administrativas que ao bibliotecário, acesso à gestão de bibliotecários e não oferece ações exclusivas de estudante

#### Scenario: Administrador autenticado navega na aplicação
- **WHEN** administrador autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece as opções de bibliotecário e o acesso à gestão de bibliotecários

#### Scenario: Bibliotecário tenta abrir gestão de bibliotecários
- **WHEN** bibliotecário autenticado abre a rota de gestão de bibliotecários
- **THEN** a interface nega o acesso e não envia operações de gestão de contas

#### Scenario: Usuário encerra a sessão
- **WHEN** usuário autenticado ativa Sair
- **THEN** a sessão privada é removida e a aplicação retorna à página inicial com navegação de visitante

# Spec Delta

## MODIFIED Requirements

### Requirement: Navegação compartilhada apresenta opções adequadas à sessão
A aplicação MUST exibir em todas as telas um cabeçalho navegável com opções coerentes com a sessão e o perfil autenticado e acesso ao catálogo público.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece links para Início, Catálogo, Entrar e Cadastrar-se, além de navegação por teclado com foco visível

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo e Sair e não exibe Entrar, Cadastrar-se ou acesso administrativo

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Cadastrar livro em `/admin/acervo` e Sair

#### Scenario: Usuário encerra a sessão
- **WHEN** usuário autenticado ativa Sair
- **THEN** a sessão privada é removida e a aplicação retorna à página inicial com navegação de visitante

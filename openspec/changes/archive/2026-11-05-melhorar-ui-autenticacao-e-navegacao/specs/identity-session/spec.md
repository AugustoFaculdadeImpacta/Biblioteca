# Spec Delta

## ADDED Requirements

### Requirement: Redirecionamento após autenticação
A interface MUST encaminhar usuários após autenticação bem-sucedida ao destino inicial correspondente e confirmar o autocadastro sem expor dados privados da sessão.

#### Scenario: Login bem-sucedido de estudante
- **WHEN** a API autentica um estudante
- **THEN** a interface mantém a sessão de forma privada e redireciona para a página inicial

#### Scenario: Login bem-sucedido de bibliotecário
- **WHEN** a API autentica um bibliotecário
- **THEN** a interface mantém a sessão de forma privada e redireciona para `/admin/acervo`

#### Scenario: Autocadastro bem-sucedido
- **WHEN** a API conclui o cadastro e inicia a sessão do estudante
- **THEN** a interface mantém a sessão de forma privada, redireciona para a página inicial e apresenta uma confirmação de sucesso

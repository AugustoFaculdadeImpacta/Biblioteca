# Spec Delta

## MODIFIED Requirements

### Requirement: Login e perfil usam identidade confiável
O sistema MUST autenticar por e-mail e senha e obter o perfil armazenado (`estudante`, `bibliotecario` ou `admin`), sem aceitar papel do cliente. Admin MUST ter permissões administrativas de bibliotecário e, quando a visão efetiva for Estudante ou Bibliotecário, poder acionar os fluxos correspondentes usando a própria sessão admin e conforme autorização do backend. O login MUST recusar contas com `ativo=false` usando mensagem genérica em português e normalizar o e-mail como no cadastro (remover espaços externos, converter para minúsculas e rejeitar espaços internos), sem alterar a senha.

#### Scenario: Login válido
- **WHEN** uma conta existente apresenta a senha correta
- **THEN** o sistema autentica a conta e retorna nome, identidade pública e perfil confiável conforme o contrato aprovado

#### Scenario: Login inválido
- **WHEN** o e-mail ou senha não corresponde a uma conta
- **THEN** o sistema recusa o login sem revelar qual credencial falhou

#### Scenario: E-mail de login com espaço interno
- **WHEN** o e-mail enviado para login contém espaço interno
- **THEN** o sistema recusa a entrada sem alterar a senha ou consultar conta por uma chave não normalizada

#### Scenario: Perfil da conta autenticada
- **WHEN** uma conta autenticada consulta sua identidade
- **THEN** o sistema retorna o papel armazenado na conta; a primeira conta bibliotecária ou admin é provisionada manualmente por operador autorizado no Xano, sem endpoint público de promoção nem credenciais embutidas nos arquivos do projeto

#### Scenario: Conta desativada tenta fazer login
- **WHEN** uma conta possui `ativo=false` e apresenta credenciais corretas
- **THEN** o sistema recusa o login com a mesma mensagem genérica usada para credenciais inválidas

#### Scenario: Permissões administrativas de admin
- **WHEN** uma conta autenticada possui perfil `admin`
- **THEN** ela pode executar operações autorizadas ao bibliotecário e, na visão Estudante, operações de estudante permitidas ao admin pelo backend, mantendo sua identidade, token e titularidade reais de admin

#### Scenario: Perfil real não é substituído pela visão
- **WHEN** admin seleciona a visão Estudante ou Bibliotecário
- **THEN** o cliente mantém `admin` como perfil real, envia a sessão original e não emite token nem identidade falsificados

#### Scenario: Xano ainda não publicou permissão para admin
- **WHEN** endpoint recusa com HTTP 403 por perfil uma ação de admin na visão simulada
- **THEN** a interface informa que a permissão precisa ser publicada no Xano e não apresenta a ação como concluída

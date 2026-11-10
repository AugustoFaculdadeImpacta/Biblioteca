# Spec Delta

## MODIFIED Requirements

### Requirement: Login e perfil usam identidade confiável
O sistema MUST autenticar por e-mail e senha e obter o perfil confiável da conta autenticada entre `estudante`, `bibliotecario` e `admin`, sem aceitar papel declarado pelo cliente. Admin MUST ter as permissões administrativas de bibliotecário. O e-mail do login MUST seguir a mesma normalização do cadastro: remover espaços externos, converter para minúsculas e rejeitar espaços internos; a senha permanece inalterada.

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

#### Scenario: Permissões administrativas de admin
- **WHEN** uma conta autenticada possui perfil `admin`
- **THEN** ela pode executar as operações autorizadas ao bibliotecário, sem obter permissões de estudante que dependam de perfil estudante

## ADDED Requirements

### Requirement: Admin provisiona contas privilegiadas
O sistema MUST permitir que somente admin autenticado crie contas com perfil bibliotecário ou admin, sem revelar senha ou emitir sessão para a conta criada.

#### Scenario: Admin cria conta bibliotecária
- **WHEN** admin autenticado envia nome, e-mail, senha e perfil `bibliotecario`
- **THEN** o backend cria a conta com e-mail normalizado e único e retorna somente a identidade pública e o perfil

#### Scenario: Admin cria outra conta admin
- **WHEN** admin autenticado envia nome, e-mail, senha e perfil `admin`
- **THEN** o backend cria a conta e retorna somente a identidade pública e o perfil

#### Scenario: Perfil solicitado não é privilegiado
- **WHEN** admin tenta criar conta com perfil diferente de `bibliotecario` ou `admin`
- **THEN** o backend recusa a operação sem criar conta

#### Scenario: Usuário sem perfil admin tenta provisionar conta
- **WHEN** visitante, estudante ou bibliotecário tenta criar conta privilegiada
- **THEN** o backend recusa a operação sem criar conta

#### Scenario: E-mail privilegiado já existe
- **WHEN** admin tenta criar conta com e-mail já associado a outra conta após normalização
- **THEN** o backend recusa a operação sem criar uma conta duplicada

#### Scenario: Autocadastro público permanece restrito
- **WHEN** visitante usa o cadastro público ou inclui nele um perfil privilegiado
- **THEN** o backend cria somente estudante ou recusa o campo de perfil e nunca cria conta bibliotecária ou admin

### Requirement: Gestão de bibliotecários é exclusiva de admin
O sistema MUST permitir a admin autenticado criar e desativar contas de bibliotecário, preservando a conta e seu histórico. A operação deve ser autorizada no backend; não se presume um campo ou endpoint que ainda não esteja definido no contrato Xano.

#### Scenario: Admin cria bibliotecário
- **WHEN** admin autenticado cria uma conta de bibliotecário com os dados válidos exigidos pelo contrato aprovado
- **THEN** o backend cria a conta com perfil bibliotecário e retorna somente dados públicos

#### Scenario: Admin desativa bibliotecário
- **WHEN** admin autenticado desativa uma conta de bibliotecário
- **THEN** a conta deixa de poder autenticar ou executar operações privilegiadas, sem ser removida fisicamente nem perder seu histórico

#### Scenario: Bibliotecário, estudante ou visitante tenta gerir bibliotecários
- **WHEN** usuário que não é admin tenta criar ou desativar conta de bibliotecário
- **THEN** o backend recusa a operação sem alterar contas

#### Scenario: Cadastro público solicita perfil privilegiado
- **WHEN** pessoa visitante tenta usar o cadastro público para criar bibliotecário ou admin
- **THEN** o backend cria somente estudante ou recusa o pedido

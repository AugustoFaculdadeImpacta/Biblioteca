# Spec Delta

## MODIFIED Requirements

### Requirement: Cadastro cria uma conta de estudante
O sistema MUST aceitar nome, e-mail único e senha sem confirmação de e-mail e permitir acesso imediato após sucesso. Antes de validar, salvar ou verificar duplicidade, deve remover espaços no início e no fim do e-mail e convertê-lo integralmente para minúsculas; deve rejeitar espaços internos. A unicidade MUST ser aplicada ao e-mail normalizado. A senha não deve ser normalizada nem alterada.

#### Scenario: Cadastro válido
- **WHEN** a pessoa envia nome, e-mail ainda não cadastrado e senha
- **THEN** o sistema cria uma conta de estudante e retorna o resultado de autenticação necessário ao acesso imediato

#### Scenario: E-mail já cadastrado após normalização
- **WHEN** a pessoa envia um e-mail que, após remoção de espaços externos e conversão para minúsculas, já está associado a uma conta, inclusive em cadastros concorrentes
- **THEN** o cadastro é recusado e nenhuma segunda conta com esse e-mail é criada

#### Scenario: E-mail contém espaço interno
- **WHEN** a pessoa envia um endereço de e-mail que contém espaço interno
- **THEN** o cadastro é recusado e nenhuma conta é criada

#### Scenario: Entrada de e-mail e senha
- **WHEN** o sistema processa e-mail e senha para cadastro ou login
- **THEN** aplica a normalização aprovada somente ao e-mail e preserva a senha exatamente como enviada

#### Scenario: Tentativa de escolher perfil
- **WHEN** o cliente inclui um papel bibliotecário ou outro perfil no cadastro
- **THEN** o backend ignora o campo ou recusa o pedido e nunca concede esse papel por autocadastro

#### Scenario: Formulário de autocadastro
- **WHEN** visitante abre a tela de cadastro de estudante
- **THEN** a interface solicita somente nome, e-mail e senha e não oferece campo para escolher perfil

#### Scenario: Validação do formulário antes do envio
- **WHEN** a pessoa envia o formulário com campo obrigatório vazio, e-mail fora do formato esperado ou e-mail com espaço interno após a normalização
- **THEN** a interface informa o campo inválido em português e não envia a requisição de cadastro

#### Scenario: E-mail já cadastrado informado pela API
- **WHEN** a API recusa o cadastro por conflito de e-mail duplicado
- **THEN** a interface informa claramente que o e-mail já está cadastrado e não autentica uma nova sessão

#### Scenario: Erro de validação ou comunicação no cadastro
- **WHEN** a API retorna erro de entrada ou ocorre falha de comunicação durante o cadastro
- **THEN** a interface apresenta uma mensagem segura em português, sem expor token, cabeçalho de autorização, URL interna ou detalhes técnicos

#### Scenario: Cadastro concluído pela interface
- **WHEN** a API retorna sucesso com sessão e identidade pública
- **THEN** a interface confirma o cadastro e permite acesso imediato como estudante, mantendo o token inacessível ao navegador e aos logs

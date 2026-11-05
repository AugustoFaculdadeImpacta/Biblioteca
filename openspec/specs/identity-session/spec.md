# identity-session Specification

## Purpose

Definir identidade, autenticação e perfil confiável no Xano para estudantes e bibliotecários, incluindo os contratos necessários a futuros clientes da API.

## Requirements

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

### Requirement: Login e perfil usam identidade confiável
O sistema MUST autenticar por e-mail e senha e obter o perfil da conta autenticada, sem aceitar papel declarado pelo cliente. O e-mail do login MUST seguir a mesma normalização do cadastro: remover espaços externos, converter para minúsculas e rejeitar espaços internos; a senha permanece inalterada.

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
- **THEN** o sistema retorna o papel armazenado na conta; o primeiro bibliotecário é provisionado manualmente por operador autorizado no Xano, sem endpoint público de promoção nem credenciais embutidas nos arquivos do projeto

### Requirement: Login pela interface mantém sessão privada
A interface MUST permitir autenticação por e-mail e senha conforme o contrato, informar falhas sem expor detalhes técnicos e manter token e perfil inacessíveis ao navegador.

#### Scenario: Formulário de login
- **WHEN** visitante abre a tela de login
- **THEN** a interface solicita somente e-mail e senha e não permite escolher perfil

#### Scenario: Normalização de e-mail no login
- **WHEN** a pessoa envia e-mail com espaços externos ou letras maiúsculas
- **THEN** o sistema remove espaços externos e converte o e-mail para minúsculas, preservando a senha exatamente como foi digitada

#### Scenario: E-mail inválido no login
- **WHEN** a pessoa envia e-mail vazio, fora do formato esperado ou com espaço interno
- **THEN** a interface informa o erro em português e não envia a requisição

#### Scenario: Login com sucesso
- **WHEN** a API retorna `200` com token e identidade pública válida
- **THEN** a interface inicia sessão usando o perfil retornado pela API e apresenta navegação correspondente, sem permitir que o cliente escolha ou altere o perfil

#### Scenario: Credenciais recusadas
- **WHEN** a API retorna erro de entrada ou autenticação recusada
- **THEN** a interface mostra mensagem segura em português sem revelar qual credencial falhou nem detalhes internos

#### Scenario: Privacidade da sessão autenticada
- **WHEN** a interface processa token ou perfil retornados pela API
- **THEN** nenhum desses valores aparece em estado enviado ao cliente, persistência de navegador ou logs

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

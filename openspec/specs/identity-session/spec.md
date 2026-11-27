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

O sistema MUST autenticar por e-mail e senha usando o perfil armazenado (`estudante`, `bibliotecario` ou `admin`), nunca um papel enviado pelo cliente. Admin MUST ter permissões de bibliotecário e poder acionar operações de estudante ou equipe na visão efetiva correspondente, com a sessão admin original e autorização do backend. Login MUST recusar contas `ativo=false` com mensagem genérica em português e normalizar e-mail como no cadastro, sem alterar a senha.

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
### Requirement: Admin provisiona contas privilegiadas

O sistema MUST permitir que somente admin autenticado crie contas de bibliotecário, definindo esse perfil no servidor, sem revelar senha, hash ou token de sessão.

#### Scenario: Admin cria conta bibliotecária
- **WHEN** admin autenticado envia nome, e-mail e senha
- **THEN** o backend cria uma conta ativa com perfil `bibliotecario`, e-mail normalizado e único, e retorna somente identidade pública e situação

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

O sistema MUST permitir que admin autenticado liste, crie, desative e reative contas de bibliotecário, preservando a conta e seu histórico. A tabela de usuário possui campo booleano `ativo` com padrão verdadeiro; login e operações administrativas devem recusar contas explicitamente desativadas. A autorização deve ser validada no backend.

#### Scenario: Admin cria bibliotecário
- **WHEN** admin autenticado cria uma conta de bibliotecário com os dados válidos exigidos pelo contrato aprovado
- **THEN** o backend cria a conta com perfil bibliotecário e retorna somente dados públicos

#### Scenario: Conta bibliotecária desativada usa token existente
- **WHEN** uma conta bibliotecária possui `ativo=false` e apresenta um token anteriormente emitido para uma operação administrativa
- **THEN** o backend recusa a operação sem alterar dados

#### Scenario: Admin desativa bibliotecário
- **WHEN** admin autenticado desativa uma conta de bibliotecário
- **THEN** a conta deixa de poder autenticar ou executar operações privilegiadas, sem ser removida fisicamente nem perder seu histórico

#### Scenario: Admin reativa bibliotecário
- **WHEN** admin autenticado reativa uma conta de bibliotecário desativada
- **THEN** `ativo` volta a verdadeiro e a conta pode autenticar e executar operações bibliotecárias

#### Scenario: Admin tenta desativar a si mesmo ou outro admin
- **WHEN** admin tenta alterar a própria conta ou uma conta com perfil `admin`
- **THEN** o backend recusa a operação sem alterar a conta

#### Scenario: Resposta de gestão não contém credenciais
- **WHEN** admin lista, cria, desativa ou reativa bibliotecários
- **THEN** nenhuma resposta inclui senha, hash de senha ou token

#### Scenario: Bibliotecário, estudante ou visitante tenta gerir bibliotecários
- **WHEN** usuário que não é admin tenta criar ou desativar conta de bibliotecário
- **THEN** o backend recusa a operação sem alterar contas

#### Scenario: Cadastro público solicita perfil privilegiado
- **WHEN** pessoa visitante tenta usar o cadastro público para criar bibliotecário ou admin
- **THEN** o backend cria somente estudante ou recusa o pedido

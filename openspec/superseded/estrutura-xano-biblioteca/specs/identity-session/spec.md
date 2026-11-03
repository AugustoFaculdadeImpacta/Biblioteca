# Spec Delta

## Purpose

Define identidade e sessão da biblioteca escolar, com Xano como autoridade de credenciais e perfil e Reflex como intermediário seguro para as interações do estudante e do bibliotecário.

## ADDED Requirements

### Requirement: Cadastro cria uma conta de estudante
O sistema MUST aceitar cadastro com e-mail e senha, rejeitar endereço já cadastrado e iniciar uma sessão de estudante após sucesso, sem exigir confirmação de e-mail.

#### Scenario: Cadastro válido
- **WHEN** uma pessoa envia e-mail e senha ainda não cadastrados
- **THEN** o sistema cria uma conta com perfil `estudante` e inicia a sessão sem confirmação de e-mail

#### Scenario: E-mail já cadastrado
- **WHEN** uma pessoa tenta cadastrar um endereço já associado a uma conta
- **THEN** o sistema recusa o cadastro e não cria uma segunda conta

#### Scenario: Tentativa de definir outro perfil no cadastro
- **WHEN** o cliente inclui `perfil=bibliotecario` ou outro papel no pedido de cadastro
- **THEN** o sistema ignora esse valor ou recusa o pedido e não cria uma conta com privilégios escolhidos pelo cliente

### Requirement: Login valida credenciais e revela somente a identidade segura
O sistema MUST autenticar por e-mail e senha e disponibilizar somente os dados públicos de identidade e o perfil confiável à interface.

#### Scenario: Login com credenciais válidas
- **WHEN** uma conta existente apresenta a senha correta
- **THEN** o sistema inicia a sessão e retorna à interface a identidade pública e o perfil confiável

#### Scenario: Login com credenciais inválidas
- **WHEN** o e-mail não existe ou a senha não corresponde
- **THEN** o sistema recusa a autenticação sem revelar qual credencial falhou

### Requirement: Perfil vem da conta autenticada
O sistema MUST determinar o perfil a partir da conta autenticada e MUST NOT permitir que o cliente escolha ou altere o próprio papel.

#### Scenario: Estudante consulta a própria identidade
- **WHEN** uma sessão de estudante válida consulta seu perfil
- **THEN** o sistema retorna o perfil `estudante` associado à identidade autenticada

#### Scenario: Conta de bibliotecário provisionada manualmente
- **WHEN** uma conta de bibliotecário provisionada por operador após confirmação do destino autorizado autentica
- **THEN** o sistema retorna o perfil `bibliotecario` armazenado na conta, sem oferecer promoção pública

### Requirement: Sessão é mediada pelo backend Reflex
O sistema MUST manter a credencial de sessão Xano apenas em estado privado e isolado da sessão do usuário no backend Reflex, sem expô-la ao navegador.

#### Scenario: Chamadas autenticadas
- **WHEN** uma pessoa autenticada consulta sua identidade ou executa uma chamada protegida incluída em Changes futuras
- **THEN** o backend Reflex encaminha a chamada usando a credencial privada e a interface recebe somente a resposta autorizada

#### Scenario: Sessão ausente ou inválida
- **WHEN** não há credencial válida no contexto privado do usuário
- **THEN** o backend recusa a chamada autenticada e não reutiliza credencial de outra sessão

#### Scenario: Isolamento entre usuários
- **WHEN** duas sessões Reflex autenticam contas diferentes e fazem chamadas simultâneas
- **THEN** cada chamada usa somente a credencial e o perfil da sessão correspondente

### Requirement: Logout encerra o contexto local autenticado
O sistema MUST limpar a credencial e os dados de identidade do contexto privado Reflex no logout e bloquear chamadas autenticadas subsequentes daquele contexto.

#### Scenario: Logout local
- **WHEN** a pessoa encerra a sessão
- **THEN** o contexto privado é limpo e uma chamada autenticada subsequente é recusada

### Requirement: Fluxos de identidade não expõem credenciais ao cliente
O sistema MUST NOT incluir senha ou token Xano em respostas, eventos, estado serializado, bundle, armazenamento ou tráfego acessível ao navegador.

#### Scenario: Inspeção do lado do cliente
- **WHEN** a interface executa cadastro, login, consulta de perfil ou logout
- **THEN** respostas e estado observáveis no navegador contêm apenas dados públicos e mensagens necessárias à interface, nunca senha ou token Xano

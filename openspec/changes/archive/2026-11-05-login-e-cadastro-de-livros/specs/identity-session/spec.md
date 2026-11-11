# Spec Delta

## ADDED Requirements

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

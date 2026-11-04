# Spec Delta

## Purpose

Define identidade, autenticação e perfil confiável no Xano para estudantes e bibliotecários, incluindo os contratos necessários a futuros clientes da API.

## ADDED Requirements

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

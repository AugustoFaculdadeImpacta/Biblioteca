# Proposal

## Why

A aplicação ainda não permite que estudantes criem uma conta pela interface. Uma tela de autocadastro ligada ao contrato OpenAPI permite que a pessoa envie os dados exigidos, receba retorno claro e obtenha acesso imediato sem expor o token de sessão.

## What Changes

- Adicionar a tela de cadastro de estudante em Reflex, com nome, e-mail e senha, validação de entrada conforme `identity-session` e mensagens de erro em português.
- Integrar a submissão somente ao `POST /auth/signup`, usando o cliente Xano server-side e o formato de sessão definido no OpenAPI.
- Manter o token retornado exclusivamente no estado privado da sessão Reflex; não persistir a senha nem enviar perfil escolhido pelo cliente.
- Testar sucesso e falhas com transporte HTTP mockado, sem chamadas de escrita ao Xano live.
- Incluir um roteiro manual para teste futuro pelo usuário em ambiente acadêmico escolhido e não produtivo, sem credenciais versionadas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `identity-session`: especificar a interação observável da tela de autocadastro, validação dos campos, tratamento de conflitos/erros da API e acesso imediato após sucesso.

## Impact

- Frontend Reflex e estado privado de sessão já existentes.
- Integração backend com `POST /auth/signup` conforme `xano/openapi.json`; nenhuma alteração de contrato Xano nesta Change.
- Testes pytest com `httpx.MockTransport` e documentação do roteiro manual.

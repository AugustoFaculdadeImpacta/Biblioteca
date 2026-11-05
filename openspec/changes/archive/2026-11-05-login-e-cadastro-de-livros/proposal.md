# Proposal

## Why

Estudantes e bibliotecários precisam entrar na aplicação, e bibliotecários precisam de uma interface para manter o acervo sem expor credenciais ou permitir que perfis não autorizados iniciem operações administrativas. A interface deve seguir exclusivamente os campos e operações definidos nas specs e no contrato OpenAPI.

## What Changes

- Adicionar tela Reflex de login usando e-mail normalizado e senha preservada, com mensagens seguras para erros do contrato.
- Manter token e perfil somente no estado backend da sessão; liberar a interface administrativa apenas para perfil bibliotecário, sem substituir a autorização obrigatória do Xano.
- Corrigir o cliente backend para enviar o token de sessão no cabeçalho de autorização das requisições autenticadas, sem registrá-lo nem expô-lo ao navegador.
- Adicionar a interface de cadastro de título com os campos obrigatórios e opcionais definidos em `titulos_POST.xs`.
- Completar o fluxo sequencial de cadastro, selecionando categorias a partir da listagem pública, associando-as ao título retornado e criando a quantidade solicitada de exemplares; usar somente IDs retornados pelos endpoints e exibir os códigos de tombo retornados pelo servidor.
- Usar somente transporte HTTP simulado nos testes automatizados; não enviar operações de escrita ao Xano live.
- Registrar a origem de cada campo e resposta nos arquivos `.xs` locais; o OpenAPI não descreve todos os schemas de resposta, então esta Change seguirá a implementação local sem alterar `xano/` nem inventar atributos.
- Incluir roteiro manual para execução futura em ambiente acadêmico não produtivo, validando o destino antes de qualquer escrita real.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `identity-session`: documentar o formulário e o comportamento observável do login Reflex, inclusive privacidade de sessão e tratamento de erro.
- `catalog`: documentar o fluxo administrativo completo de título, categorias e exemplares, a restrição de perfil na interface e o uso de IDs/código de tombo retornados pelos endpoints.

## Impact

- Frontend Reflex, estado privado de sessão, cliente Xano backend e testes com `httpx.MockTransport`.
- Endpoints existentes `POST /auth/login`, `GET /auth/me`, `POST /catalogo/titulos`, `POST /catalogo/categorias`, `POST /admin/titulos/{tituloId}/categorias` e `POST /admin/exemplares`; nenhum endpoint ou schema Xano será alterado nesta Change.
- A implementação local dos endpoints Xano nos arquivos `.xs` é a fonte de campos e respostas para esta Change; a diferença de nome entre o parâmetro de rota `titulo_id` local e `tituloId` no OpenAPI será documentada, mantendo a semântica da rota e sem alterar `xano/`.

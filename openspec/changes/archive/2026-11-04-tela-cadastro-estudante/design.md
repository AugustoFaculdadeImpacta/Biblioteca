# Design

## Context

Consulte [proposal.md](./proposal.md) e a delta [identity-session](./specs/identity-session/spec.md). A fundação já fornece Reflex, cliente HTTP server-side, normalização básica e estado de sessão com `_session_token` privado; o contrato em `xano/openapi.json` define `POST /auth/signup`, campos `nome`, `email`, `senha` e uma resposta `Sessao` com `authToken` e `usuario`.

## Goals / Non-Goals

**Goals:**

- Fazer a validação de formulário antes de qualquer chamada e integrar o contrato de cadastro sem enviar campos extras.
- Tratar status de erro de forma previsível e segura, sem imprimir corpos de resposta nem dados de credencial.
- Manter os limites de acessibilidade e privacidade já verificados na fundação.

**Non-Goals:**

- Definir políticas adicionais de senha, confirmação de e-mail, recuperação de senha ou campos escolares que não constam no contrato.
- Alterar endpoints, tabelas ou regras Xano.
- Implementar login, manutenção de catálogo ou navegação autenticada além da confirmação de acesso imediato.

## Decisions

### Integrar pelo cliente Xano já existente

O evento de submissão chama somente `POST /auth/signup`, com as chaves exatas do schema `Cadastro`. O e-mail é removido de espaços externos e convertido para minúsculas antes da validação; espaços internos e formato inválido impedem a chamada. A senha é transmitida sem normalização e não é guardada em estado Reflex, persistência local ou logs. Nenhum campo de perfil é incluído.

Alternativa considerada: chamar o Xano diretamente pelo navegador. Rejeitada porque exporia configuração, credenciais e resposta de autenticação no cliente, contrariando `frontend-foundation`.

### Manter a resposta de autenticação no backend

Após `200`, validar a presença de `authToken` e `usuario` antes de atualizar a sessão. Armazenar `authToken` pelo helper privado da substate Reflex existente, que também atualiza somente o indicador público não sensível `is_authenticated`. A resposta bruta não é colocada em variáveis públicas, retornada ao navegador nem registrada. A interface mostra apenas confirmação de cadastro/acesso imediato.

Alternativa considerada: manter o token em estado público ou armazenamento do navegador. Rejeitada pela garantia de privacidade da capability `frontend-foundation`.

### Mapear erros do endpoint para mensagens seguras

O cliente HTTP expõe status sanitizado, sem corpo da API, URL ou cabeçalhos. Para `409` no signup, a interface informa que o e-mail já está cadastrado. Para `400`, falha de configuração e erro de transporte, mostra mensagens distintas mas sem detalhes técnicos ou credenciais. A validação local mantém os campos para correção, sem enviar a requisição inválida. A senha nunca é escrita em logs.

Alternativa considerada: exibir diretamente `message` do servidor. Rejeitada porque o texto não é estável no contrato e pode conter detalhes internos.

### Testar com transporte simulado

Os testes chamam os handlers com transporte `httpx.MockTransport`, verificando método, caminho e payload, respostas de sucesso e erros, estado/delta e ausência de dados sensíveis nos logs. Nenhum teste usa URL Xano real ou envia signup live. Um roteiro manual documenta execução futura pelo usuário num ambiente acadêmico não produtivo, com e-mail de teste controlado pelo operador.

## Risks / Trade-offs

- [O contrato atual deixa regras de complexidade e comprimento da senha indefinidas] → não inventar restrições; enviar a senha exatamente como recebida e validar apenas presença.
- [A API pode mudar o formato de mensagens de conflito/validação] → mapear status conhecido para texto controlado pela interface e manter o contrato OpenAPI como referência.
- [Falha após o servidor criar conta, antes de a sessão ser atualizada] → validar a resposta antes de alterar o estado e reportar erro de forma segura; não repetir automaticamente uma escrita potencialmente concluída.
- [Teste manual cria uma conta persistente no ambiente selecionado] → o roteiro exige ambiente acadêmico não produtivo e identidade de teste exclusiva, sem assumir endpoint de exclusão que não está no OpenAPI.

## Migration Plan

Não há migração nesta Change. A integração depende da URL configurada localmente no backend; verificações automatizadas usam apenas transporte mockado. Antes de qualquer teste manual, o operador confirma que `XANO_API_BASE_URL` aponta para ambiente acadêmico não produtivo.

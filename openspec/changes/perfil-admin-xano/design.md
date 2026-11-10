# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [identity-session](./specs/identity-session/spec.md), [frontend-foundation](./specs/frontend-foundation/spec.md), [catalog](./specs/catalog/spec.md), [copy-condition](./specs/copy-condition/spec.md), [loan-circulation](./specs/loan-circulation/spec.md) e [reservations](./specs/reservations/spec.md).

O enum local de `usuario.perfil` contém estudante e bibliotecário; 14 endpoints locais com operações administrativas exigem literalmente bibliotecário. O autocadastro Xano atribui estudante no servidor e a tabela tem índice único de e-mail normalizado. O login Reflex aceita atualmente apenas estudante e bibliotecário.

## Goals / Non-Goals

**Goals:**
- Adicionar admin como terceiro perfil confiável, com a mesma autorização bibliotecária no backend e no estado de sessão Reflex.
- Limitar criação de contas privilegiadas a uma conta admin autenticada e preservar o autocadastro público de estudante.
- Fazer a mudança de schema em uma única atualização delimitada, sem mudar os outros fluxos de autorização ou dados.

**Non-Goals:**
- Criar ou provisionar a primeira conta admin durante esta Change; o operador fará isso manualmente usando o roteiro sem segredos.
- Alterar permissões de estudante, acesso público, `auth=false`, FIFO, elegibilidade, estado de empréstimos ou a interpretação de `devolvido_em` (nulo ou zero).
- Permitir push de múltiplos arquivos, habilitar `allow_push`, apagar dados ou sincronizar `xano/` inteiro.

## Decisions

### Autoridade do perfil e permissões herdadas

O valor `admin` é armazenado no Xano e retornado pelo login; não é aceito como papel enviado por autocadastro. Nos endpoints que atualmente exigem bibliotecário, a checagem de servidor passa a aceitar exatamente `bibliotecario` ou `admin`. Endpoints pessoais de estudante continuam exigindo somente estudante. No Reflex, o tipo de sessão aceita admin e a verificação de permissões administrativas trata admin como bibliotecário, mantendo token e perfil privados.

**Alternativa considerada:** permitir admin em qualquer endpoint autenticado; rejeitada porque incluiria operações exclusivas de estudante sem necessidade.

### Provisionamento de contas privilegiadas

Adicionar `POST /admin/usuarios` no grupo Biblioteca, exigindo autenticação e perfil admin no servidor. Os únicos campos derivados da tabela local `usuario` são `nome`, `email`, `senha` e `perfil`; o perfil de destino aceita somente `bibliotecario` ou `admin`. Reutilizar normalização e índice único existentes para o e-mail. A resposta inclui somente identidade pública e perfil, nunca senha nem token de sessão.

A rota segue a convenção observada em `/admin/titulos` e `/admin/exemplares`; confirmar a forma final com a documentação do Xano Developer antes de criar o endpoint. Se essa documentação exigir outro contrato, interromper e atualizar esta Change antes de qualquer escrita.

**Alternativa considerada:** estender `POST /auth/signup` com um campo de perfil; rejeitada porque tornaria o autocadastro uma superfície de elevação de privilégios.

### Sequência e limites operacionais Xano

Antes de qualquer alteração remota, usar somente Xano CLI para confirmar workspace `151966`, branch e ambiente, obter pull isolado de definições sem registros/ambiente e salvar rollback fora do repositório. Verificar `git status` e diff antes de sincronizar. A alteração do enum só pode prosseguir após prova em tabela de teste reversível. Depois, o dry-run de `usuario.xs` deve mostrar exatamente um UPDATE; cada arquivo seguinte de endpoint também é isolado e revisado. Push, se permitido, é unitário e seguido por pull de conferência.

A documentação local registra branch `v1` como live e `allow_push=false`, e que sandbox push não aceita `-i`. Se o CLI confirmar essa limitação ou não houver destino isolado compatível com filtro unitário, parar antes de mudar/pushar qualquer arquivo Xano e manter as tarefas remanescentes pendentes. Não alterar `allow_push` nem contornar a limitação com push mais amplo.

**Alternativa considerada:** usar sandbox sem filtro de arquivo para contornar `allow_push`; rejeitada porque viola a exigência de push delimitado.

### Teste e primeiro administrador

Testes automatizados do cliente e do frontend usam mocks. Testes Xano reais, se todos os gates operacionais permitirem, usam apenas contas sintéticas `zz-teste-*@exemplo.invalid`, registram IDs localmente fora do relatório público e removem recursos individualmente pela Metadata API, verificando GET 404 e contagens finais (tabelas de negócio zero; `usuario=2`). O roteiro de primeiro admin explica o provisionamento manual pelo operador, mas não contém senha, token nem e-mail real.

## Risks / Trade-offs

- [O workspace pode impedir o push unitário] → confirmar destino e `allow_push` no início de Apply; interromper sem contornar ou modificar preferências.
- [Enum e endpoints podem ficar parcialmente sincronizados] → atualizar e conferir cada arquivo individualmente; não avançar ao próximo push se o pull de conferência divergir.
- [Conta admin passa a ter poder de criar outras contas privilegiadas] → validação obrigatória no backend, lista fechada de perfis de destino, e-mail único e teste de recusa de perfis não autorizados.
- [Sessão admin pode vazar token ou obter ações de estudante] → testes de estado privado/logs e verificações de perfil positivas e negativas em cada evento; autorização Xano continua sendo a autoridade.

## Migration Plan

Sem migração de dados ou exclusão. Após preflight e prova em tabela de teste, atualizar primeiro a enum `usuario` com dry-run que apresente somente um UPDATE. Em seguida atualizar um arquivo de endpoint por vez, revisar e sincronizar individualmente, incluir OpenAPI e integração mínima de sessão, testar com mocks e só então executar testes sintéticos autorizados. Rollback restaura os arquivos de referência salvos fora do repositório e reverte o schema pela cópia isolada; se qualquer etapa falhar, parar novos pushes e preservar IDs/estado para investigação.

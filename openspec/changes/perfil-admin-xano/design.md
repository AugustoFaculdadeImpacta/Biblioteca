# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [identity-session](./specs/identity-session/spec.md), [frontend-foundation](./specs/frontend-foundation/spec.md), [catalog](./specs/catalog/spec.md), [copy-condition](./specs/copy-condition/spec.md), [loan-circulation](./specs/loan-circulation/spec.md) e [reservations](./specs/reservations/spec.md).

O enum local de `usuario.perfil` contém estudante e bibliotecário; 14 endpoints locais com operações administrativas exigem literalmente bibliotecário. O autocadastro Xano atribui estudante no servidor e a tabela tem índice único de e-mail normalizado. A tabela não possui campo de situação/ativo e o contrato OpenAPI local não define operação de listagem ou desativação de usuários.

## Goals / Non-Goals

**Goals:**
- Adicionar admin como terceiro perfil confiável, com a mesma autorização bibliotecária no backend e no estado de sessão Reflex.
- Limitar criação e desativação de bibliotecários a uma conta admin autenticada e preservar o autocadastro público de estudante.
- Disponibilizar gestão de bibliotecários somente a admin quando os contratos de backend para listagem e desativação estiverem definidos.
- Fazer a mudança de schema em uma única atualização delimitada, sem mudar os outros fluxos de autorização ou dados.

**Non-Goals:**
- Criar ou provisionar a primeira conta admin durante esta Change; o operador fará isso manualmente usando o roteiro sem segredos.
- Alterar permissões de estudante, acesso público, `auth=false`, FIFO, elegibilidade, estado de empréstimos ou a interpretação de `devolvido_em` (nulo ou zero).
- Permitir push de múltiplos arquivos, habilitar `allow_push`, apagar dados ou sincronizar `xano/` inteiro.

## Decisions

### Autoridade do perfil e permissões herdadas

O valor `admin` é armazenado no Xano e retornado pelo login; não é aceito como papel enviado por autocadastro. Nos endpoints que atualmente exigem bibliotecário, a checagem de servidor passa a aceitar exatamente `bibliotecario` ou `admin`. Endpoints pessoais de estudante continuam exigindo somente estudante. No Reflex, o tipo de sessão aceita admin e a verificação de permissões administrativas trata admin como bibliotecário, mantendo token e perfil privados.

**Alternativa considerada:** permitir admin em qualquer endpoint autenticado; rejeitada porque incluiria operações exclusivas de estudante sem necessidade.

### Criação e desativação de contas privilegiadas

O contrato atual da Change previa `POST /admin/usuarios` para criar contas, exigindo autenticação e perfil admin no servidor. Os únicos campos existentes em `usuario` são `nome`, `email`, `senha` e `perfil`; o perfil de destino aceita somente `bibliotecario` ou `admin`. Reutilizar normalização e índice único existentes para o e-mail. A resposta deve incluir somente identidade pública e perfil, nunca senha nem token de sessão.

O usuário também exige desativação lógica de bibliotecários, mas o schema local não possui campo de situação/ativo e o OpenAPI não define operações de consulta ou desativação de usuários. Não criar campos, rotas ou comportamentos inferidos. A tela de gestão e a desativação ficam pendentes até existir contrato aprovado e verificável para esses comportamentos.

**Alternativas consideradas:** usar `perfil=estudante` como desativação ou apagar a conta; rejeitadas porque não impedem login/uso como estudante, ou destroem identidade e histórico. Estender `POST /auth/signup` com um campo de perfil também foi rejeitado por expor elevação de privilégios no cadastro público.

### Sequência e limites operacionais Xano

Antes de qualquer alteração remota, usar somente Xano CLI para confirmar workspace `151966`, branch e ambiente, obter pull isolado de definições sem registros/ambiente e salvar rollback fora do repositório. Verificar `git status` e diff antes de sincronizar. A alteração do enum só pode prosseguir após prova em tabela de teste reversível. Depois, o dry-run de `usuario.xs` deve mostrar exatamente um UPDATE; cada arquivo seguinte de endpoint também é isolado e revisado. Push, se permitido, é unitário e seguido por pull de conferência.

A CLI confirmou workspace `151966`, branch `v1` live e `allow_push=false`; sandbox push não aceita `-i`. Como o push Git/Xano não foi autorizado nesta execução e a operação delimitada não está disponível, nenhum arquivo Xano será alterado ou sincronizado. As tarefas de schema, endpoints e testes remotos permanecem pendentes.

**Alternativa considerada:** usar sandbox sem filtro de arquivo para contornar `allow_push`; rejeitada porque viola a exigência de push delimitado.

### Teste e primeiro administrador

O primeiro admin deve ser criado manualmente pelo dono do workspace, usando os campos existentes e os mecanismos de senha suportados pelo Xano; nenhum segredo será escrito em arquivos ou logs. Testes automatizados do cliente e do frontend usam mocks. Testes Xano reais, quando autorizados e com os gates operacionais atendidos, usam apenas contas sintéticas `zz-teste-*@exemplo.invalid`, registram IDs localmente fora do relatório público e removem recursos individualmente pela Metadata API, verificando GET 404 e contagens finais (tabelas de negócio zero; `usuario=2`).

## Decisões tomadas por delegação (revisar)

- Admin herda permissões administrativas do bibliotecário; operações exclusivas de estudante continuam restritas a `estudante`.
- Cadastro público continua criando somente estudantes; a primeira conta admin é criada pelo dono do workspace no Xano, sem senha documentada.
- Desativação é lógica, não exclui registros e deve impedir acesso administrativo; não será simulada por mudança para estudante.
- Não inventar campo, rota ou contrato para listar/desativar contas. Como `usuario` não tem campo de situação e o OpenAPI local não oferece essas operações, a tela e a desativação permanecem pendentes.
- O destino Xano é workspace `151966`, branch `v1` live, grupo Biblioteca. `allow_push=false`; não alterar essa configuração nem contornar a ausência de push unitário.

## Risks / Trade-offs

- [O workspace pode impedir o push unitário] → confirmar destino e `allow_push` no início de Apply; interromper sem contornar ou modificar preferências.
- [Enum e endpoints podem ficar parcialmente sincronizados] → atualizar e conferir cada arquivo individualmente; não avançar ao próximo push se o pull de conferência divergir.
- [Conta admin passa a ter poder de criar outras contas privilegiadas] → validação obrigatória no backend, lista fechada de perfis de destino, e-mail único e teste de recusa de perfis não autorizados.
- [Sessão admin pode vazar token ou obter ações de estudante] → testes de estado privado/logs e verificações de perfil positivas e negativas em cada evento; autorização Xano continua sendo a autoridade.

## Migration Plan

Sem migração de dados ou exclusão. Após preflight e prova em tabela de teste, atualizar primeiro a enum `usuario` com dry-run que apresente somente um UPDATE. Em seguida atualizar um arquivo de endpoint por vez, revisar e sincronizar individualmente, incluir OpenAPI e integração mínima de sessão, testar com mocks e só então executar testes sintéticos autorizados. Rollback restaura os arquivos de referência salvos fora do repositório e reverte o schema pela cópia isolada; se qualquer etapa falhar, parar novos pushes e preservar IDs/estado para investigação.

# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [identity-session](./specs/identity-session/spec.md), [frontend-foundation](./specs/frontend-foundation/spec.md), [catalog](./specs/catalog/spec.md), [copy-condition](./specs/copy-condition/spec.md), [loan-circulation](./specs/loan-circulation/spec.md) e [reservations](./specs/reservations/spec.md).

O enum local de `usuario.perfil` contém estudante e bibliotecário; 15 endpoints locais com operações administrativas exigem literalmente bibliotecário. O autocadastro Xano atribui estudante no servidor e a tabela tem índice único de e-mail normalizado. A tabela não possui campo de situação/ativo e o contrato OpenAPI local não define operações de gestão de bibliotecários.

## Goals / Non-Goals

**Goals:**
- Adicionar admin como terceiro perfil confiável, com a mesma autorização bibliotecária no backend e no estado de sessão Reflex.
- Limitar listagem, criação, desativação e reativação de bibliotecários a uma conta admin autenticada e preservar o autocadastro público de estudante.
- Impedir que contas desativadas façam login ou executem operações administrativas, inclusive por tokens já emitidos.
- Oferecer a admin uma alternância de visualização entre bibliotecário e estudante sem substituir sua identidade nem alterar autorização no backend.
- Fazer a mudança de schema em uma única atualização delimitada, sem mudar os outros fluxos de autorização ou dados.

**Non-Goals:**
- Criar ou provisionar a primeira conta admin durante esta Change; o operador fará isso manualmente usando o roteiro sem segredos.
- Alterar permissões de estudante, acesso público, `auth=false`, FIFO, elegibilidade, estado de empréstimos ou a interpretação de `devolvido_em` (nulo ou zero).
- Permitir push de múltiplos arquivos, habilitar `allow_push`, apagar dados ou sincronizar `xano/` inteiro.

## Decisions

### Autoridade do perfil e permissões herdadas

O valor `admin` é armazenado no Xano e retornado pelo login; não é aceito como papel enviado por autocadastro. Nos endpoints que atualmente exigem bibliotecário, a checagem de servidor passa a aceitar exatamente `bibliotecario` ou `admin`. Endpoints pessoais de estudante continuam exigindo somente estudante. No Reflex, o tipo de sessão aceita admin e a verificação de permissões administrativas trata admin como bibliotecário, mantendo token e perfil privados.

**Alternativa considerada:** permitir admin em qualquer endpoint autenticado; rejeitada porque incluiria operações exclusivas de estudante sem necessidade.

### Ativação de conta e gestão de bibliotecários

Adicionar `usuario.ativo` como booleano com padrão verdadeiro. O login deve recusar `ativo=false` usando a mesma mensagem genérica para credenciais inválidas. Valores nulos de registros legados não são tratados como desativação. Os endpoints administrativos existentes também conferem `ativo != false`, para que um token já emitido não preserve acesso privilegiado após a desativação.

Somente admin pode listar bibliotecários, criar bibliotecário e alterar sua situação. A criação usa `POST /admin/usuarios`, e-mail normalizado/único, senha recebida sem normalização e perfil fixo `bibliotecario`; a entrada não escolhe perfil. A listagem retorna somente `id`, `nome`, `email` e `ativo`. A atualização usa `PATCH /admin/usuarios/{usuario_id}` com o único campo `ativo`, aceitando `false` para desativar e `true` para reativar. Não pode alterar a própria conta nem uma conta que não seja bibliotecária. Nenhuma resposta administrativa pode incluir senha, hash ou token.

O pedido indicava que `POST /admin/usuarios` já existia, mas a leitura somente de definições da branch `v1` trouxe 57 documentos e não encontrou essa rota nem endpoints administrativos de usuários. Assim, os três endpoints acima são candidatos locais definidos para implementar o contrato aprovado; sua existência/comportamento no workspace remoto não foi confirmado e não haverá publicação nesta execução.

**Alternativas consideradas:** usar `perfil=estudante` como desativação ou apagar a conta; rejeitadas porque mudam o papel histórico ou destroem identidade. Permitir que o cliente escolha perfil na criação também foi rejeitado por ampliar a operação privilegiada.

### Sequência e limites operacionais Xano

Antes de qualquer alteração remota, usar somente Xano CLI para confirmar workspace `151966`, branch e ambiente, obter pull isolado de definições sem registros/ambiente e salvar rollback fora do repositório. Verificar `git status` e diff antes de sincronizar. A alteração do enum só pode prosseguir após prova em tabela de teste reversível. Depois, o dry-run de `usuario.xs` deve mostrar exatamente um UPDATE; cada arquivo seguinte de endpoint também é isolado e revisado. Push, se permitido, é unitário e seguido por pull de conferência.

A CLI confirmou workspace `151966`, branch `v1` live e `allow_push=false`; sandbox push não aceita `-i`. Nesta execução somente os arquivos locais serão preparados e validados; não haverá push, sandbox nem alteração de `allow_push`. As provas do enum, publicação e testes remotos permanecem pendentes.

**Alternativa considerada:** usar sandbox sem filtro de arquivo para contornar `allow_push`; rejeitada porque viola a exigência de push delimitado.

### Teste e primeiro administrador

O primeiro admin deve ser criado manualmente pelo dono do workspace, usando os campos existentes e os mecanismos de senha suportados pelo Xano; nenhum segredo será escrito em arquivos ou logs. Testes automatizados do cliente e do frontend usam mocks. Testes Xano reais, quando autorizados e com os gates operacionais atendidos, usam apenas contas sintéticas `zz-teste-*@exemplo.invalid`, registram IDs localmente fora do relatório público e removem recursos individualmente pela Metadata API, verificando GET 404 e contagens finais (tabelas de negócio zero; `usuario=2`).

## Decisões tomadas por delegação (revisar)

- Admin herda permissões administrativas do bibliotecário; operações exclusivas de estudante continuam restritas a `estudante`.
- Cadastro público continua criando somente estudantes; a primeira conta admin é criada pelo dono do workspace no Xano, sem senha documentada.
- Contrato aprovado nesta etapa: `usuario.ativo` é booleano com padrão verdadeiro; `ativo=false` impede login com mensagem genérica. Os guards administrativos também recusam a conta desativada para invalidar privilégios de tokens já emitidos.
- A gestão cobre bibliotecários, não administradores. Admin cria bibliotecário com perfil fixo; não pode desativar a si mesmo ou outra conta admin. Respostas administrativas nunca expõem senha, hash ou token.
- Caminhos locais candidatos: `GET /admin/usuarios`, `POST /admin/usuarios` e `PATCH /admin/usuarios/{usuario_id}` com entrada `ativo`. O pull somente de definições da branch `v1` trouxe 57 documentos e não encontrou endpoint de usuários; portanto, não há contrato Xano remoto confirmado.
- O repositório contém 15 guards administrativos de perfil bibliotecário, embora as tarefas originais mencionassem 14; todos os 15 serão cobertos.
- O destino Xano é workspace `151966`, branch `v1` live, grupo Biblioteca. `allow_push=false`; não alterar essa configuração nem contornar a ausência de push unitário.

## Risks / Trade-offs

- [O workspace pode impedir o push unitário] → manter publicação pendente até autorização operacional separada; não contornar nem modificar preferências.
- [Enum e endpoints podem ficar parcialmente sincronizados] → atualizar e conferir cada arquivo individualmente; não avançar ao próximo push se o pull de conferência divergir.
- [Uma conta desativada mantém token válido] → verificar `ativo != false` nas rotas administrativas além de bloquear o login.
- [Sessão admin pode vazar token ou obter ações de estudante] → testes de estado privado/logs e verificações de perfil positivas e negativas em cada evento; autorização Xano continua sendo a autoridade.
- [Visualização de estudante pode ser confundida com impersonação] → manter o perfil e token admin, enviar somente esse token às rotas pessoais existentes e mostrar a recusa do backend sem fabricar dados quando admin não for elegível.

## Migration Plan

Sem migração de dados ou exclusão. Após preflight e prova em tabela de teste, atualizar primeiro a enum `usuario` com dry-run que apresente somente um UPDATE. Em seguida atualizar um arquivo de endpoint por vez, revisar e sincronizar individualmente, incluir OpenAPI e integração mínima de sessão, testar com mocks e só então executar testes sintéticos autorizados. Rollback restaura os arquivos de referência salvos fora do repositório e reverte o schema pela cópia isolada; se qualquer etapa falhar, parar novos pushes e preservar IDs/estado para investigação.

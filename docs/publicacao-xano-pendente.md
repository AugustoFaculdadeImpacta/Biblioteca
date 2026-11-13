# Publicação Xano pendente

Este arquivo registra trabalho local que poderá exigir publicação ou execução
futura no Xano real. **Nada foi publicado, executado, excluído ou alterado
remotamente nesta sessão.**

## Gate obrigatório antes de qualquer operação

Identificar e confirmar, com o responsável pelo ambiente, o workspace, a branch,
o ambiente e o grupo de API da biblioteca escolar. Não assumir que um destino
registrado anteriormente continua correto. Se houver mais de um destino
plausível, não operar. Antes de qualquer sincronização futura, revisar backup,
permissões e diff unitário. Este documento não autoriza operações remotas.

## Ordem pendente

1. **Confirmar o destino e a autorização operacional.** Workspace, branch,
   ambiente e grupo devem ser identificados e confirmados antes de qualquer
   operação remota.
2. **Conferir schema e autenticação locais pendentes.** Revisar, em conjunto,
   `xano/table/usuario.xs`, `xano/table/titulo.xs` e
   `xano/api/default/auth/login_POST.xs`, incluindo enum de perfil, estado ativo
   e compatibilidade de login.
3. **Conferir autorização administrativa.** Revisar os guards e candidatos
   locais de gestão de usuários indicados em
   `docs/publicacao-xano.md`; validar cada rota no destino confirmado antes de
   considerar a permissão operacional.
4. **Conferir e publicar, se aprovado, os contratos locais do acervo.** Inclui
   o estado ativo do título, listagem administrativa, atualização e bloqueios
   de exclusão/desativação. A lista exata de arquivos será atualizada depois
   das Changes locais.
5. **Conferir e publicar, se aprovado, os fluxos de circulação.** Revisar os
   contratos locais e a regra de elegibilidade (até três empréstimos ativos;
   atraso ou empréstimo ativo do mesmo título bloqueia; empréstimos de outros
   títulos não bloqueiam abaixo do limite). Inclui:
   - `POST /solicitacoes-emprestimo`;
   - `POST /reservas`;
   - `POST /admin/reservas`;
   - `POST /admin/solicitacoes/{solicitacaoId}/retirada` e
     `POST /admin/solicitacoes/{solicitacaoId}/recusar`;
   - `POST /admin/reservas/ofertar-proxima`,
     `POST /admin/reservas/{reservaId}/retirada` e
     `POST /admin/reservas/{reservaId}/recusar`;
   - `POST /admin/emprestimos/{emprestimoId}/devolucao` e
     `POST /admin/reservas/processar-expiradas`.
   Validar fila FIFO, disponibilidade, autorização, concorrência e transições
   antes de qualquer publicação. Os arquivos `.xs` locais passaram na validação
   de sintaxe MCP, mas não foram publicados nem testados no workspace.
6. **Revisar e, após autorização, executar o seed do catálogo Xano.** O script
   local `scripts/seed_xano_demo.py` cobre categorias, títulos, vínculos e
   exemplares, obtém endereço/token somente do ambiente de execução, inicia em
   prévia e exige `--apply` mais confirmação do destino. Ele depende de
   `GET /admin/acervo`, contrato candidato ainda não confirmado no Xano remoto.
   O script não provisiona contas: não há contrato aprovado para criar uma
   conta admin de teste. Nenhuma escrita foi executada.
7. **Executar testes remotos somente após autorização e destino confirmado.**
   Inclui testes de autorização, concorrência/FIFO e limpeza individual de
   registros sintéticos `@example.invalid`, sem exclusão global.

## Rotas pessoais

Segundo as evidências fornecidas pelo usuário, `/minhas/emprestimos`,
`/minhas/solicitacoes` e `/minhas/reservas` já estão publicadas. Elas responderam
401 sem token, comportamento esperado de rotas autenticadas. Não há publicação
pendente dessas rotas identificada neste diagnóstico; o erro observado após
login requer tratamento local da sessão e verificação posterior autorizada.

P1 alterou somente o cliente Reflex, parsers e mensagens locais; não adicionou
nem modificou contratos Xano e não requer publicação.

P4.3 adicionou somente alternância visual no frontend Reflex. A identidade,
token e permissões efetivas do admin permanecem inalterados; nenhuma rota,
tabela ou script Xano foi alterado e não há publicação adicional decorrente
dessa funcionalidade.

## Estado da verificação

- Validação local de sintaxe MCP: três rotas pessoais válidas.
- Na auditoria inicial, workspace, branch e tabelas ativos não foram
  consultados; uma consulta posterior está registrada abaixo.
- Na auditoria inicial, publicação, seed e testes autenticados no Xano real
  estavam pendentes. A publicação parcial posterior está registrada abaixo;
  seed e testes autenticados continuam pendentes.
- O seed local foi verificado somente com transporte simulado e modo de prévia;
  não houve chamada ao Xano real. Como o script é Python e não contém
  XanoScript, validação de sintaxe pelo Xano Developer MCP não se aplica.

## Auditoria de pull e dry-run

Esta seção atualiza as observações anteriores sobre o inventário remoto. O
destino observado foi o workspace `151966` (“Augusto's Workspace”), branch
`v1`, única branch listada e marcada como live. Isso coincide com o destino
registrado em `openspec/changes/perfil-admin-xano/tasks.md`. A preferência
atual do workspace é `allow_push=false`.

### Permissão e limites do CLI

A documentação Xano CLI consultada descreve `--allow-push` em `workspace
edit` como “Allow CLI push to the workspace”; portanto, `allow_push` é uma
preferência do workspace, não da branch. Os comandos documentados para
alterá-la são `xano workspace edit -w 151966 --allow-push` e
`xano workspace edit -w 151966 --no-allow-push`. Nenhum deles foi executado.
Pela documentação, a preferência controla o push do CLI; pull e operações de
branch são comandos separados e não são descritos como bloqueados por ela.
O preview abaixo funcionou com `allow_push=false`, o que não autoriza nem
prova que um push real seria aceito.

### Pull e comparação de arquivos

Foi executado `xano workspace pull -d %TEMP%\xano-remoto-151966 -w 151966 -b
v1`, sem `--records`. O CLI informou 57 documentos baixados; os arquivos
ficaram fora do repositório, e registros/contagens de linhas não foram
incluídos nem verificados.

A comparação de tabelas considera campos, tipos, enums e índices. As
diferenças textuais restantes nos schemas correspondem à formatação do pull e
à declaração remota explícita `auth = false`.

| Arquivo/item | Só local | Só remoto | Existe nos dois, mas difere | Igual |
|---|---|---|---|---|
| `table/categoria.xs` | — | — | Texto/formatação e `auth = false`; schema e índices equivalentes | — |
| `table/condicao_exemplar.xs` | — | — | Texto/formatação e `auth = false`; schema e índices equivalentes | — |
| `table/emprestimo.xs` | — | — | Texto/formatação e `auth = false`; schema e índices equivalentes | — |
| `table/event_log.xs` | — | `event_log.xs` | — | — |
| `table/exemplar.xs` | — | — | Texto/formatação e `auth = false`; schema e índices equivalentes | — |
| `table/reserva.xs` | — | — | Local acrescenta `recusada` ao enum `estado` | — |
| `table/solicitacao_emprestimo.xs` | — | — | Texto/formatação e `auth = false`; schema e índices equivalentes | — |
| `table/titulo.xs` | — | — | Local acrescenta o campo opcional `ativo: bool` | — |
| `table/titulo_categoria.xs` | — | — | Texto/formatação e `auth = false`; schema e índices equivalentes | — |
| `table/user.xs` | — | `user.xs` | — | — |
| `table/usuario.xs` | — | — | Local acrescenta `ativo: bool` opcional e o valor `admin` ao enum `perfil` | — |

As diferenças de schema listadas são aditivas: o preview não indicou remoção
ou recriação de tabela, nem mudança de tipo. O pull não trouxe registros, então
não é possível dizer quantos existem ou se são contas/dados reais ou de teste.
Os arquivos remotos `event_log.xs` e `user.xs` não têm correspondente local e
não seriam removidos pelo push parcial usado no preview.

Para as APIs, as rotas foram correlacionadas pela assinatura `verb + path` do
XanoScript, entre `api/default/` local e `api/biblioteca/` remoto. Os caminhos
remotos abaixo são relativos ao pull temporário. “Preview UPDATE” e “Preview
CREATE” vêm do resultado real do dry-run.

| Arquivo/item | Só local | Só remoto | Existe nos dois, mas difere | Igual |
|---|---|---|---|---|
| `api/default/admin/acervo_GET.xs` | Preview CREATE: `GET admin/acervo` | — | — | — |
| `api/default/emprestimos/admin_ativos_GET.xs` | Preview CREATE: `GET admin/emprestimos` | — | — | — |
| `api/default/admin/estudantes_GET.xs` | Preview CREATE: `GET admin/estudantes` | — | — | — |
| `api/default/condicoes/condicoes_GET.xs` ↔ `api/biblioteca/admin/exemplares/exemplar_id/condicoes_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/reservas/admin_GET.xs` | Preview CREATE: `GET admin/reservas` | — | — | — |
| `api/default/emprestimos/admin_solicitacoes_GET.xs` ↔ `api/biblioteca/admin/solicitacoes_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/reservas/fila_GET.xs` ↔ `api/biblioteca/admin/titulos/titulo_id/fila_reservas_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/admin/usuarios_GET.xs` | Preview CREATE: `GET admin/usuarios` | — | — | — |
| `api/default/auth/me_GET.xs` ↔ `api/biblioteca/auth/me_GET.xs` | — | — | Diferença textual, sem operação no preview | — |
| `api/default/catalogo/categorias_GET.xs` ↔ `api/biblioteca/catalogo/categorias_GET.xs` | — | — | — | Igual; sem operação |
| `api/default/catalogo/categorias_id_GET.xs` ↔ `api/biblioteca/catalogo/categorias/categoria_id_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/catalogo/categorias_titulos_GET.xs` ↔ `api/biblioteca/catalogo/categorias/categoria_id/titulos_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/catalogo/titulos_GET.xs` ↔ `api/biblioteca/catalogo/titulos_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/catalogo/titulos_id_GET.xs` ↔ `api/biblioteca/catalogo/titulos/titulo_id_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/emprestimos/minhas_GET.xs` ↔ `api/biblioteca/minhas/emprestimos_GET.xs` | — | — | Diferença textual, sem operação no preview | — |
| `api/default/reservas/minhas_GET.xs` ↔ `api/biblioteca/minhas/reservas_GET.xs` | — | — | Preview UPDATE | — |
| `api/default/emprestimos/minhas_solicitacoes_GET.xs` ↔ `api/biblioteca/minhas/solicitacoes_GET.xs` | — | — | Diferença textual, sem operação no preview | — |
| `api/default/admin/usuarios_id_PATCH.xs` | Preview CREATE: `PATCH admin/usuarios/{usuario_id}` | — | — | — |
| `api/default/catalogo/categorias_id_PATCH.xs` ↔ `api/biblioteca/catalogo/categorias/categoria_id_PATCH.xs` | — | — | Preview UPDATE | — |
| `api/default/catalogo/titulos_id_PATCH.xs` ↔ `api/biblioteca/catalogo/titulos/titulo_id_PATCH.xs` | — | — | Preview UPDATE | — |
| `api/default/emprestimos/devolucao_POST.xs` ↔ `api/biblioteca/admin/emprestimos/emprestimo_id/devolucao_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/admin/exemplares_POST.xs` ↔ `api/biblioteca/admin/exemplares_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/condicoes/condicoes_POST.xs` ↔ `api/biblioteca/admin/exemplares/exemplar_id/condicoes_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/admin/reservas_POST.xs` | Preview CREATE: `POST admin/reservas` | — | — | — |
| `api/default/reservas/ofertar_proxima_POST.xs` ↔ `api/biblioteca/admin/reservas/ofertar_proxima_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/reservas/processar_expiradas_POST.xs` ↔ `api/biblioteca/admin/reservas/processar_expiradas_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/reservas/recusar_POST.xs` | Preview CREATE: `POST admin/reservas/{reserva_id}/recusar` | — | — | — |
| `api/default/reservas/retirada_POST.xs` ↔ `api/biblioteca/admin/reservas/reserva_id/retirada_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/emprestimos/recusar_POST.xs` | Preview CREATE: `POST admin/solicitacoes/{solicitacao_id}/recusar` | — | — | — |
| `api/default/emprestimos/retirada_POST.xs` ↔ `api/biblioteca/admin/solicitacoes/solicitacao_id/retirada_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/admin/titulos_categoria_POST.xs` ↔ `api/biblioteca/admin/titulos/titulo_id/categorias_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/admin/usuarios_POST.xs` | Preview CREATE: `POST admin/usuarios` | — | — | — |
| `api/default/auth/login_POST.xs` ↔ `api/biblioteca/auth/login_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/auth/signup_POST.xs` ↔ `api/biblioteca/auth/signup_POST.xs` | — | — | Diferença textual, sem operação no preview | — |
| `api/default/admin/categorias_POST.xs` ↔ `api/biblioteca/catalogo/categorias_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/admin/titulos_POST.xs` ↔ `api/biblioteca/catalogo/titulos_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/reservas/reservas_POST.xs` ↔ `api/biblioteca/reservas_POST.xs` | — | — | Preview UPDATE | — |
| `api/default/emprestimos/solicitacoes_POST.xs` ↔ `api/biblioteca/solicitacoes_emprestimo_POST.xs` | — | — | Preview UPDATE | — |
| `api/biblioteca/biblioteca.xs` | — | Arquivo de grupo remoto | — | — |
| `api/authentication/authentication.xs` | — | Arquivo de grupo remoto | — | — |
| `api/authentication/auth/login_POST.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/authentication/auth/me_GET.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/authentication/auth/signup_POST.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/authentication/message/send_welcome_email_POST.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/authentication/reset/magic_link_login_POST.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/authentication/reset/request_reset_link_GET.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/authentication/reset/update_password_POST.xs` | — | Endpoint de outro grupo remoto | — | — |
| `api/event_logs/event_logs.xs` | — | Arquivo de grupo remoto | — | — |
| `api/event_logs/logs/user/my_events_GET.xs` | — | Endpoint de outro grupo remoto | — | — |

### Resultado do dry-run e risco de publicação

Foi executado `xano workspace push -d xano -w 151966 -b v1 --dry-run
--no-guids`, sem `--sync`, `--delete` ou `--records`. O preview terminou com
código 0 e informou:

- 3 tabelas atualizadas: `reserva`, `titulo` e `usuario`;
- 10 endpoints criados e 23 atualizados;
- nenhuma remoção, recriação de tabela ou mudança de tipo de campo indicada.

Os 10 endpoints criados são `GET admin/acervo`, `GET admin/emprestimos`,
`GET admin/estudantes`, `GET admin/reservas`, `GET admin/usuarios`,
`PATCH admin/usuarios/{usuario_id}`, `POST admin/reservas`,
`POST admin/reservas/{reserva_id}/recusar`,
`POST admin/solicitacoes/{solicitacao_id}/recusar` e `POST admin/usuarios`.

Os 23 endpoints atualizados são `GET admin/exemplares/{exemplar_id}/condicoes`,
`GET admin/solicitacoes`, `GET admin/titulos/{titulo_id}/fila-reservas`,
`GET catalogo/categorias/{categoria_id}`,
`GET catalogo/categorias/{categoria_id}/titulos`, `GET catalogo/titulos`,
`GET catalogo/titulos/{titulo_id}`, `GET minhas/reservas`,
`PATCH catalogo/categorias/{categoria_id}`,
`PATCH catalogo/titulos/{titulo_id}`,
`POST admin/emprestimos/{emprestimo_id}/devolucao`,
`POST admin/exemplares`, `POST admin/exemplares/{exemplar_id}/condicoes`,
`POST admin/reservas/ofertar-proxima`,
`POST admin/reservas/processar-expiradas`,
`POST admin/reservas/{reserva_id}/retirada`,
`POST admin/solicitacoes/{solicitacao_id}/retirada`,
`POST admin/titulos/{titulo_id}/categorias`, `POST auth/login`,
`POST catalogo/categorias`, `POST catalogo/titulos`, `POST reservas` e
`POST solicitacoes-emprestimo`.

### Branch e plano mínimo

A documentação de branches diz que a branch live atende o tráfego de produção
e é a branch padrão das requisições API. Ela documenta `-b` para selecionar a
branch nos comandos de pull/push, mas não documenta header ou parâmetro HTTP
para um app consumir branch não-live. Portanto, não está confirmado que o app
possa apontar diretamente a uma branch não-live; não se deve presumir esse
comportamento. Nesta consulta, `v1` é a única branch listada e está live.

Para a demonstração dos três perfis, o preview identifica como conjunto
mínimo a publicar as três tabelas aditivas (`table/reserva.xs`,
`table/titulo.xs`, `table/usuario.xs`) e os 33 arquivos locais de API
classificados acima como Preview CREATE/UPDATE. Os quatro endpoints com
diferença textual, mas sem operação no preview, e o endpoint igual
`GET catalogo/categorias` não exigem publicação neste preview. Os grupos e
arquivos remotos extras (`authentication`, `event_logs`, `user.xs` e
`event_log.xs`) podem permanecer; o modo parcial não os remove.

Na auditoria de comparação, nenhum push real, seed, alteração de configuração,
branch ou dado foi executado. A publicação parcial posterior está registrada
na seção seguinte.

## Publicação parcial autorizada — 2026-11-13

### Backup e preferência do CLI

Antes de qualquer push, a cópia `%USERPROFILE%\xano-backup-pre-publicacao`
foi criada fora do repositório a partir do pull sem registros. Foram
verificados 57 documentos e igualdade SHA-256 de todos os arquivos.

O comando `xano workspace edit -w 151966 --allow-push` foi tentado, mas o
workspace respondeu que a opção não está disponível no plano Free e que o
push é sempre habilitado nesse plano. No encerramento,
`xano workspace edit -w 151966 --no-allow-push` terminou com código 0 e a
leitura final confirmou `allow_push=false`. Nenhum outro workspace ou branch
foi alterado.

### Linha de base HTTP

As requisições foram feitas sem token, carregando `XANO_API_BASE_URL` do
ambiente do backend sem exibir seu valor nem corpos de resposta.

| Momento | `GET /catalogo/titulos` | `GET /catalogo/categorias` | `GET /minhas/emprestimos` | `GET /minhas/solicitacoes` | `GET /minhas/reservas` |
|---|---:|---:|---:|---:|---:|
| Antes dos pushes | 200 | 200 | 401 | 401 | 401 |
| Após schemas | 200 | 200 | 401 | 401 | 401 |
| Após endpoints novos | 200 | 200 | 401 | 401 | 401 |

### Schemas publicados

O dry-run filtrado nos três arquivos mostrou exatamente três tabelas
atualizadas e nenhuma criação, remoção, recriação ou alteração de tipo. A
primeira tentativa de push terminou com código 2 após exibir a prévia; o pull
subsequente confirmou que ela não havia aplicado mudanças. Após a prévia ser
revisada, o mesmo push parcial foi executado com `--force` para dispensar a
confirmação interativa e terminou com código 0:

- `xano/table/usuario.xs`;
- `xano/table/titulo.xs`;
- `xano/table/reserva.xs`.

O CLI emitiu um aviso de referências não resolvidas para `reserva`. O pull
posterior trouxe 57 documentos e confirmou `titulo.ativo` opcional,
`usuario.ativo` opcional, `admin` no enum `usuario.perfil` e `recusada` no
enum `reserva.estado`. As outras seis tabelas (`categoria`,
`condicao_exemplar`, `emprestimo`, `exemplar`, `solicitacao_emprestimo` e
`titulo_categoria`) permaneceram idênticas ao backup. Nenhum registro foi
incluído no pull.

### Endpoints novos publicados e verificação sem token

O dry-run mostrou exatamente 10 criações; o push filtrado desses arquivos
terminou com código 0. O CLI emitiu avisos de referências não resolvidas para
as queries. Status observados:

| Rota | Status sem token | Observação |
|---|---:|---|
| `GET /admin/acervo` | 401 | — |
| `GET /admin/emprestimos` | 401 | — |
| `GET /admin/estudantes` | 400; 401 com e-mail falso `@example.invalid` | A primeira sonda omitiu o e-mail obrigatório; a segunda continuou sem token e não altera dados. |
| `GET /admin/reservas` | 401 | — |
| `GET /admin/usuarios` | 401 | — |
| `PATCH /admin/usuarios/{usuario_id}` | 400 sem corpo; 404 com ID `-1` e entrada válida | Não foi obtido 401/403. O dry-run/push e a validação de entrada mostram que a rota foi registrada; o 404 ocorreu com ID inexistente e não prova rejeição por autenticação. Nenhum ID real foi enviado. |
| `POST /admin/reservas` | 400 sem corpo; 401 com IDs inválidos | Nenhuma entrada de usuário/título existente foi enviada. |
| `POST /admin/reservas/{reserva_id}/recusar` | 401 | — |
| `POST /admin/solicitacoes/{solicitacao_id}/recusar` | 401 | — |
| `POST /admin/usuarios` | 400 sem corpo e com nome vazio | Não foi enviada entrada que pudesse criar conta; o status 401/403 não foi comprovado. |

Não houve resposta 500. A linha de base permaneceu 200/200/401/401/401.
Entretanto, os dois casos sem confirmação de 401/403 não foram considerados
aprovados. Não foi possível fazer rollback do lote de criações usando o
backup: nele esses dez endpoints não existem, e removê-los exigiria apagar
endpoints, operação proibida nesta tarefa. Nenhum endpoint foi apagado ou
revertido.

### Lotes de atualização não executados

Os 23 endpoints de atualização e os quatro lotes (login; catálogo/exemplares;
solicitações/empréstimos; reservas) **não foram publicados**, pois a
verificação do lote de criações não satisfez integralmente o requisito de
401/403 e não havia rollback permitido para os endpoints criados.

**Arquivos efetivamente publicados:** os três schemas listados acima e:

- `xano/api/default/admin/acervo_GET.xs`;
- `xano/api/default/emprestimos/admin_ativos_GET.xs`;
- `xano/api/default/admin/estudantes_GET.xs`;
- `xano/api/default/reservas/admin_GET.xs`;
- `xano/api/default/admin/usuarios_GET.xs`;
- `xano/api/default/admin/usuarios_id_PATCH.xs`;
- `xano/api/default/admin/reservas_POST.xs`;
- `xano/api/default/reservas/recusar_POST.xs`;
- `xano/api/default/emprestimos/recusar_POST.xs`;
- `xano/api/default/admin/usuarios_POST.xs`.

Nenhum seed ou criação de conta foi executado. Nenhum push Git foi feito. O
estado final lido para `allow_push` é `false`; no plano Free, a mensagem do
workspace informa que o push permanece habilitado.

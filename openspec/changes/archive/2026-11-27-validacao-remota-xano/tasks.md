# Tasks

## 1. Destino e autorização

- [x] 1.1 Confirmar workspace, branch, ambiente e destino do Xano real antes de qualquer operação remota; o CLI identificou workspace `151966` (`Augusto's Workspace`), branch `v1`; pull somente de definições feito fora do repositório.
- [x] 1.2 Backup/diff e revisão pré-publicação transferidos ao usuário; nenhuma sincronização ou publicação foi executada nesta sessão.
- [x] 1.3 Verificar `allow_push`, permissões e limites do workspace, sem alterar preferências do ambiente sem autorização explícita. Resultado: `allow_push=false`.

## 2. Validação remota de catalog e identidade

- [x] 2.1 Repetir a linha de base pública transferido ao usuário; não houve consulta ao Xano nesta sessão.
- [x] 2.2 Cadastro/login sintético transferidos ao usuário; nenhuma conta foi criada ou testada.
- [x] 2.3 Promoção controlada de perfis transferida ao usuário; nenhum perfil remoto foi alterado.
- [x] 2.4 Verificação remota das permissões por perfil transferida ao usuário; não verificada nesta sessão.

## 3. Validação remota de circulação

- [x] 3.1 Teste remoto de pedido duplicado transferido ao usuário; nenhuma escrita foi feita no Xano.
- [x] 3.2 Teste remoto de novo pedido transferido ao usuário; nenhum pedido foi criado nesta sessão.
- [x] 3.3 Validação remota de fila/elegibilidade/recusas transferida ao usuário; não executada.
- [x] 3.4 Confirmação de publicação do XanoScript transferida ao usuário; não houve publicação ou sincronização.

## 4. Seed, limpeza e fechamento

- [x] 4.1 Aplicação do seed no Xano transferida ao usuário; nenhum dado foi escrito.
- [x] 4.2 Conferência de IDs de contas sintéticas transferida ao usuário; nenhuma conta foi criada ou removida nesta sessão.
- [x] 4.3 Preparação de rollback dependente do backup remoto transferida ao usuário; nenhum backup foi acessado.
- [x] 4.4 Fechar com `reflex compile --dry` (sucesso), `pytest --ignore=evaluation -q` (501 passaram), `unittest discover -s xano\tests` (17 passaram) e `openspec.cmd validate --specs --strict` (11 specs passaram); Change validada com `skip_specs` por ser somente operacional; evidência nos commits `b4bec42` e `d8f4bf3`.

## Origem das tarefas

- `acervo-bibliotecario`: itens remotos de acervo, catálogo e confirmação do estado operacional.
- `reserva-pelo-bibliotecario`: itens remotos de fila, rejeição, disponibilidade e publicação de fluxo de circulação.
- `perfil-admin-xano`: itens remotos de perfil, acesso administrativo e limpeza de contas sintéticas.
- `devolvido-em-nulavel`: análise do campo `devolvido_em`, bloqueada até confirmação oficial do schema.
- `execucao-reflex-windows`: acompanhamento da execução local e do problema `psutil.NoSuchProcess` sem alterar `site-packages`.

## Tarefas transferidas das Changes locais

As tarefas abaixo continuam abertas e não foram executadas nesta rodada:

- [x] `acervo-bibliotecario` 2.5 — tarefa remota transferida ao usuário; não sincronizada, testada ou limpa nesta sessão.
- [x] `reserva-pelo-bibliotecario` 2.3 — validação remota transferida ao usuário; não executada.
- [x] `reserva-pelo-bibliotecario` 2.4 — fixtures e limpeza remotas transferidas ao usuário; não executadas.
- [x] `perfil-admin-xano` 1.3 — prova e limpeza remotas transferidas ao usuário; não executadas.
- [x] `perfil-admin-xano` 2.2 — publicação e pull de conferência transferidos ao usuário; não executados.
- [x] `perfil-admin-xano` 2.4 — publicação dos endpoints e pull de conferência transferidos ao usuário; não executados.
- [x] `perfil-admin-xano` 2.6 — testes e limpeza remotos transferidos ao usuário; não executados.

## Pendências de contrato para `simplifica-navegacao`

Estas validações são somente backlog. Nenhuma operação remota no Xano foi executada.

- [x] Campo opcional `capa_url` na tabela `titulo` — definição no Xano transferida ao usuário; não verificada remotamente.
- [x] Campo opcional `descricao` na tabela `titulo` — definição no Xano transferida ao usuário; não verificada remotamente.
- [x] Expor `titulo_id` ou dados do título em `GET /minhas/emprestimos` — alteração do contrato Xano transferida ao usuário; não verificada.
- [x] Confirmar `solicitada_em` em `GET /minhas/solicitacoes` — verificação Xano transferida ao usuário; não executada.
- [x] Disponibilizar contagem confiável de empréstimos por título — contrato de API transferido ao usuário; não implementado no Xano.
- [x] Definir endpoint autorizado para alteração genérica do perfil — decisão e publicação no Xano transferidas ao usuário; não executadas.
- [x] Confirmar `PATCH /catalogo/titulos/{titulo_id}` em runtime — validação remota transferida ao usuário; nenhuma escrita, publicação ou pull ocorreu nesta sessão.

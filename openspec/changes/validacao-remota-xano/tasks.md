# Tasks

## 1. Destino e autorização

- [x] 1.1 Confirmar workspace, branch, ambiente e destino do Xano real antes de qualquer operação remota; o CLI identificou workspace `151966` (`Augusto's Workspace`), branch `v1`; pull somente de definições feito fora do repositório.
- [ ] 1.2 Fazer backup seguro e revisão do diff antes da publicação parcial; confirmar que o arquivo alvo é o mínimo obrigatório do escopo.
- [x] 1.3 Verificar `allow_push`, permissões e limites do workspace, sem alterar preferências do ambiente sem autorização explícita. Resultado: `allow_push=false`.

## 2. Validação remota de catalog e identidade

- [ ] 2.1 Repetir a linha de base pública: `/catalogo/titulos` 200 com 2 itens, `/catalogo/categorias` 200 com 8 itens e `/minhas/*` sem token 401.
- [ ] 2.2 Verificar cadastro e login de conta sintética nova, com status HTTP registrado para sucesso e falha.
- [ ] 2.3 Validar perfil `bibliotecario` e `admin` por promoção controlada, sem expor senhas, tokens ou URLs.
- [ ] 2.4 Confirmar que a sessão autenticada respeita as regras de cada perfil e não cria comportamento administrativo sem autorização.

## 3. Validação remota de circulação

- [ ] 3.1 Testar o pedido de empréstimo duplicado com a conta sintética existente e confirmar 4xx com mensagem clara em português.
- [ ] 3.2 Validar novo pedido de outro título ou nova solicitação, garantindo que o fluxo continue funcionando após a correção do defeito.
- [ ] 3.3 Verificar fila, elegibilidade e recusas em `POST /admin/...` e rotas de circulação, com registros sintéticos e sem apagar nada.
- [ ] 3.4 Confirmar que a correção local do XanoScript foi publicada com dry-run filtrado e sem `--sync`, `--delete` ou `--records`.

## 4. Seed, limpeza e fechamento

- [ ] 4.1 Executar o seed autorizado somente com o destino confirmado e sem escalonar para dados reais.
- [ ] 4.2 Registrar todos os IDs de contas sintéticas criadas e respeitar o limite e a regra de não apagar registros que não sejam sintéticos.
- [ ] 4.3 Registrar o cenário de rollback imediato se a linha de base piorar, usando o backup em `%USERPROFILE%\xano-backup-pre-publicacao`.
- [ ] 4.4 Validar o fechamento final com `pytest --ignore=evaluation`, `unittest discover -s xano\tests`, `reflex compile --dry` e a validação OpenSpec estrita.

## Origem das tarefas

- `acervo-bibliotecario`: itens remotos de acervo, catálogo e confirmação do estado operacional.
- `reserva-pelo-bibliotecario`: itens remotos de fila, rejeição, disponibilidade e publicação de fluxo de circulação.
- `perfil-admin-xano`: itens remotos de perfil, acesso administrativo e limpeza de contas sintéticas.
- `devolvido-em-nulavel`: análise do campo `devolvido_em`, bloqueada até confirmação oficial do schema.
- `execucao-reflex-windows`: acompanhamento da execução local e do problema `psutil.NoSuchProcess` sem alterar `site-packages`.

## Tarefas transferidas das Changes locais

As tarefas abaixo continuam abertas e não foram executadas nesta rodada:

- [ ] `acervo-bibliotecario` 2.5 — sincronização, prova de concorrência, testes sintéticos, pull de conferência e limpeza no Xano remoto.
- [ ] `reserva-pelo-bibliotecario` 2.3 — confirmar execução e atomicidade FIFO no Xano real.
- [ ] `reserva-pelo-bibliotecario` 2.4 — executar fixtures, limpeza individual e conferência remota.
- [ ] `perfil-admin-xano` 1.3 — provar o enum em tabela descartável, confirmar os três perfis, limpar tabela/registro e verificar GET 404.
- [ ] `perfil-admin-xano` 2.2 — publicar `usuario.xs` com dry-run unitário, push autorizado e pull de conferência.
- [ ] `perfil-admin-xano` 2.4 — publicar individualmente os endpoints de autorização com dry-run, push e pull de conferência por arquivo.
- [ ] `perfil-admin-xano` 2.6 — executar testes Xano com contas sintéticas, limpar fixtures pela Metadata API e confirmar respostas 404 e contagens finais.

## Pendências de contrato para `simplifica-navegacao`

Estas validações são somente backlog. Nenhuma operação remota no Xano foi executada.

- [ ] Campo opcional `capa_url` na tabela `titulo` (URL HTTPS da capa do livro).
- [ ] Campo opcional `descricao` na tabela `titulo` (descrição do livro).
- [ ] Expor `titulo_id` ou os dados do título em `GET /minhas/emprestimos` para identificar cada empréstimo pessoal.
- [ ] Confirmar que `GET /minhas/solicitacoes` retorna `solicitada_em` quando a jornada exigir a data do pedido.
- [ ] Disponibilizar uma contagem confiável de empréstimos por título para uma futura seção de popularidade no catálogo.
- [ ] Definir um endpoint autorizado para alteração genérica do perfil de contas; até então, a interface limita a gestão ao cadastro, ativação e desativação de bibliotecários.
- [ ] Confirmar em runtime o comportamento de `PATCH /catalogo/titulos/{titulo_id}` para desativar e reativar títulos. O arquivo local e o pull somente de definições são `xano/api/default/catalogo/titulos_id_PATCH.xs` e `api/biblioteca/catalogo/titulos/titulo_id_PATCH.xs`; validar perfil, empréstimo ativo, reserva ativa e respostas 404/403/200 sem gravar dados reais. O usuário precisa publicar ou confirmar esta rota no ambiente antes de testar desativação remota.

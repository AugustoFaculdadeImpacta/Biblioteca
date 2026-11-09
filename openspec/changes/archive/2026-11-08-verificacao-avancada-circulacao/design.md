# Design

## Context

Veja `proposal.md` para a motivação. O único workspace disponível é `151966/v1` live; não há ambiente isolado separado. Os testes avançados incluem alteração de datas, processamento global de ofertas e disputas concorrentes, portanto não podem começar sem os gates desta Change.

## Goals / Non-Goals

**Goals:**

- Preparar uma verificação segura no workspace live, condicionada a backup/export do usuário, aprovação explícita no Review e pré-check somente leitura aprovado.
- Garantir que cada fixture, mutação temporal e exclusão seja rastreável por ID e reversível pela limpeza.
- Verificar como cenário a divergência FIFO registrada em `reconciliar-xano-com-git`, sem corrigir a implementação.

**Non-Goals:**

- Alterar regras de produto, tabelas, endpoints, grupo de API ou a aplicação Reflex.
- Executar qualquer Apply sem os gates aprovados ou prosseguir após identificar dados não-fixture.

## Decisions

### Aplicar somente após backup, aprovação e pré-check Metadata API

O usuário confirmou backup/export e aprovou Apply. O pré-check completo das cinco tabelas pela Metadata API já passou. Antes de cada chamada a um processador global, repetir a leitura completa de `reserva`, `emprestimo`, `solicitacao_emprestimo`, `usuario` e `exemplar`. Exigir branch `v1` live, paginação completa, ausência de reservas ofertadas vencidas que não sejam fixtures desta Change, ausência de empréstimos ativos não-fixture e ausência de solicitações pendentes não-fixture. Como o cenário de expiração cria deliberadamente uma oferta vencida, o processador global só pode ser chamado se a enumeração completa provar que cada registro que ele poderia alterar é uma fixture registrada nesta Change. Se a cobertura ou propriedade não puder ser provada, parar sem chamar o processador.

Manter os registros apenas em memória durante a agregação. Não imprimir nem gravar nomes, e-mails, tokens ou conteúdo pessoal. Calcular apenas: total de registros por tabela; reservas ofertadas com `expira_em` anterior ao instante atual; empréstimos ativos (`devolvido_em` nulo); solicitações pendentes (`estado = pendente`). O gate passa somente se os três estados críticos tiverem contagem zero e todas as páginas das cinco tabelas forem lidas sem erro, com IDs e branch confirmados. Qualquer contagem crítica positiva, tabela ausente, paginação incompleta, falha de autorização ou resposta inesperada exige parar sem fixtures nem processamento global.

### Usar fixtures rastreadas e limpeza confirmada

Para esta execução, o usuário autorizou a Metadata API apenas para criar, atualizar e excluir registros nas tabelas `usuario`, `titulo`, `exemplar`, `solicitacao_emprestimo`, `emprestimo` e `reserva` do workspace `151966`/branch `v1`; nenhuma definição será alterada. A documentação oficial define `POST /workspace/{workspace_id}/table/{table_id}/content`, `PUT .../content/{content_id}`, `DELETE .../content/{content_id}` e GET individual para confirmar 404. Criar/atualizar/excluir é permitido somente para IDs de fixtures registrados nesta Change, nunca para os dois usuários preexistentes.

Criar usuários de teste com endereços sintéticos no domínio reservado para testes e senhas aleatórias somente em memória. O endereço é montado em tempo de execução. O campo Xano `password` recebe o valor de senha e é armazenado criptografado; testar login de cada usuário via `/auth/login`, mantendo o token apenas em memória. Nunca registrar senha, token ou dados pessoais no relatório. A promoção de bibliotecário é permitida somente no registro sintético recém-criado.

Cada criação deve ser seguida imediatamente pelo registro local do nome da tabela e ID. Alterações em `vence_em`, `expira_em`, estado e demais campos são permitidas somente nesses IDs. Limpar em ordem de dependência `reserva`, `emprestimo`, `solicitacao_emprestimo`, `exemplar`, `titulo`, `usuario`; excluir somente via DELETE individual e confirmar cada ID com GET 404. Truncar tabelas, apagar em massa ou tocar nos dois usuários existentes é proibido.

Antes de criar recursos dependentes de rotas administrativas, confirmar que o usuário de teste bibliotecário conseguiu autenticar via `/auth/login`. Se criação, login ou exclusão individual falhar, parar, registrar somente os IDs já criados e contagens agregadas, tentar apenas a limpeza autorizada desses IDs e não arquivar se algum GET 404 não for confirmado. O usuário autorizou criar um bibliotecário e um estudante sintéticos; um segundo estudante pode ser criado somente se necessário para testar fila FIFO ou concorrência.

### Verificar FIFO como achado, sem corrigir nesta Change

A Change `reconciliar-xano-com-git` registrou que o remoto omite ordenação FIFO na consulta da fila, na oferta da próxima reserva e em fluxos de devolução/expiração. O cenário deve verificar seleção da reserva elegível mais antiga e reoferta após expiração, usando somente fixtures e evidência observável por API. Qualquer falha é registrada em `RESULTS.md`; a implementação não é alterada nesta Change.

### Resultado e critério de conclusão

Esta Change conclui a verificação, não a correção das regras de produto. Os cenários de atraso, limite de empréstimo e FIFO foram executados; resultados que contrariam o comportamento esperado são achados do backend e contam como verificação concluída, desde que a evidência esteja sanitizada e todas as fixtures tenham sido removidas individualmente. A disputa do último exemplar e a geração concorrente de código de tombo passaram nos invariantes observados.

No cenário FIFO, a consulta confirmou a ordem criada, mas a oferta da próxima reserva retornou HTTP 500. Como não foi possível confirmar uma reserva em estado `ofertada` com expiração vencida, o pré-check impediu chamar o processador global. A etapa de expiração/reoferta e a análise de fuso permanecem não avaliadas; não contornar esse gate para concluir o teste.

Achados para correção em Change separada: solicitação de empréstimo aceita apesar de atraso; duas retiradas concorrentes aceitas para o mesmo estudante; e erro HTTP 500 na oferta FIFO, relacionado à ordenação removida no remoto. Esta Change não altera regras nem endpoints para corrigir esses achados. Pode ser arquivada com os achados documentados, desde que limpeza, contagens finais e sanitização sejam verificadas.

## Risks / Trade-offs

- [O pré-check não comprova cobertura integral ou encontra registros críticos não-fixture] → interromper antes de qualquer teste global.
- [Falha de limpeza] → interromper os próximos cenários, registrar os IDs e não arquivar a Change.
- [Concorrência não reproduzível] → registrar comandos, paralelismo e respostas para permitir repetição, sem declarar atomicidade sem evidência.
- [A oferta FIFO falha antes da expiração/reoferta] → registrar o HTTP 500, não chamar o processador global sem a fixture ofertada vencida confirmada e tratar a lacuna na Change de correção.

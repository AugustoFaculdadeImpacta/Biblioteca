# Design

## Context

Consulte `proposal.md` para a motivação e o escopo. A tabela local declara `timestamp devolvido_em?`; evidências do workspace da Change anterior mostram `nullable=false` e valor `0` para um empréstimo ainda ativo. A Change anterior comprovou que filtros em memória Xano persistem quando ordenação em `db.query` não persiste, e deixou as comparações de sentinel em sete endpoints.

## Goals / Non-Goals

**Goals:**

- Impedir qualquer alteração produtiva antes de provar, em tabela descartável, que o schema Xano nullable mantém null através do ciclo de gravação e leitura.
- Migrar o campo de empréstimo somente quando GET do schema comprovar `nullable=true` e um registro POST/GET comprovar null persistido.
- Manter evidência de rollback individual e pushes limitados a um documento por operação.
- Garantir que o estado `devolvido_em=null` seja o único indicador de empréstimo ainda não devolvido nas rotas que verificam essa condição.

**Non-Goals:**

- Alterar as regras de circulação, contratos HTTP ou interface.
- Reescrever `fila_GET`, que não consulta `devolvido_em`.
- Executar processador global de expiração ou sincronizar o diretório `xano/` inteiro.

## Decisions

### Gate descartável precede alterações produtivas

Em Apply, reconfirmar o workspace e branch pelo Xano CLI e registrar a identidade no resultado. O destino esperado é workspace `151966`, branch live `v1`, mas a confirmação é obrigatória antes de qualquer operação remota. Consultar a documentação oficial Xano para a sintaxe de nulabilidade e para as rotas Metadata API de schema/registros; validar o XanoScript antes do push.

Criar uma definição mínima `zz_teste_nota` com um timestamp realmente nullable, guardar evidência de que o nome/ID não existe antes da criação e limitar o push ao arquivo da tabela. A prévia deve listar somente essa tabela como `CREATE`. Ler seu schema e criar um registro sintético com o campo explicitamente null; somente GET do registro confirmando null exato prova a hipótese. Depois, excluir o registro individual e a tabela por Metadata API, confirmando GET 404 em cada recurso. Se qualquer evidência falhar, não tocar na tabela `emprestimo` nem em endpoints produtivos; registrar a limitação e interromper a execução.

### Migração da tabela de empréstimo é condicional e reversível

Depois da prova descartável, confirmar por GET paginado que `emprestimo` tem contagem zero e salvar o schema remoto atual fora do repositório como rollback. Se a tabela não estiver vazia, parar antes de alteração produtiva. Atualizar somente a definição `table/emprestimo.xs`; revisar diff e exigir um dry-run delimitado com exatamente um `UPDATE` dessa tabela antes do push. Após o push, confirmar pelo GET do schema `nullable=true`.

Para validar persistência em produção, criar um único registro sintético com `devolvido_em=null` e dependências referenciais válidas. A inspeção somente leitura determina se já há referências seguras; não usar nem modificar registros preexistentes. Se for necessário criar entidades de apoio, ou se não for possível provar sem tocar em dados existentes, interromper e pedir decisão em vez de ampliar silenciosamente o escopo. Registrar o ID do empréstimo imediatamente, confirmar null por GET, excluir o registro individualmente, verificar GET 404 e retornar a tabela à contagem zero antes de atualizar endpoints.

### Atualização dos endpoints é um lote sequencial de mudanças isoladas

O inventário do Git encontrou sentinel em sete definições: `emprestimos/solicitacoes_POST.xs`, `emprestimos/retirada_POST.xs`, `emprestimos/devolucao_POST.xs`, `reservas/reservas_POST.xs`, `reservas/retirada_POST.xs`, `reservas/ofertar_proxima_POST.xs` e `reservas/processar_expiradas_POST.xs`. `reservas/fila_GET.xs` é o oitavo endpoint relacionado da Change anterior, mas não lê `devolvido_em`; confirmar que continua sem sentinel e não o alterar.

Para cada endpoint, preservar um pull isolado e rollback fora de `xano/`, comparar com o arquivo Git e editar somente seus predicados para `devolvido_em == null`. Fazer dry-run com `-i` de um único endpoint; prosseguir apenas se a prévia listar exatamente um `UPDATE` daquele endpoint. Fazer push do mesmo arquivo, nunca da pasta, e confirmar por pull que o sentinel foi removido. Parar ao primeiro resultado diferente, erro ou regressão. Não alterar `allow_push`; se o push delimitado não for permitido, parar.

### Cenários e limpeza

Após todos os sete endpoints estarem confirmados no pull, executar `atraso`, `limite` e `fifo` separadamente com o runner existente, sem executar rotinas globais. Cada cenário deve passar, limpar cada fixture com DELETE individual e GET 404, e verificar contagens `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2` antes de iniciar o próximo.

### Sem delta de comportamento

As specs atuais já definem empréstimo ativo até a devolução e os bloqueios de elegibilidade; esta Change ajusta a representação persistida para refletir esse contrato, sem alterar comportamento observável. Portanto, `skip_specs: true` evita criar um delta artificial de especificação.

## Risks / Trade-offs

- [Xano ignora ou transforma null mesmo com schema nullable] → o gate descartável deve falhar de forma explícita; não atualizar `emprestimo` nem endpoints e manter o sentinel como estado operacional atual.
- [O dry-run aponta CREATE, mais de um recurso ou um recurso diferente do esperado] → não fazer push; investigar apenas após nova revisão.
- [O schema produtivo contém registros ou referências de fixture exigem dados existentes] → interromper a migração/registro até haver caminho seguro; nunca editar ou apagar dados preexistentes.
- [Um endpoint ou cenário diverge] → interromper imediatamente, preservar IDs e rollbacks, não prosseguir ao próximo endpoint/cenário nem arquivar.

## Migration Plan

1. Reconfirmar o destino Xano; validar documentação oficial, sintaxe XanoScript e endpoints Metadata API necessários.
2. Provar nulabilidade em `zz_teste_nota` com push isolado, GET do schema e POST/GET de registro null; limpar e confirmar 404. Falha encerra a Change sem tocar em produção.
3. Confirmar `emprestimo=0`, preservar schema remoto de rollback, fazer push isolado de `table/emprestimo.xs`, verificar `nullable=true`, POST/GET de null e remoção confirmada do registro de teste.
4. Atualizar cada um dos sete endpoints separadamente, com rollback, diff, dry-run de um UPDATE, push individual e pull de confirmação. Não alterar `fila_GET`.
5. Executar os três cenários isolados e confirmar limpeza e contagens após cada um.
6. Atualizar README e resultados sanitizados; rodar testes, `openspec validate --strict` e inspeção final de segredos e diffs.
7. Arquivar somente após Verify completo e aprovação Review explícita. Não criar commit Git.

Rollback: manter a cópia do schema anterior de `emprestimo` e o pull de cada endpoint fora do repositório. Qualquer reversão remota deve ser delimitada ao documento alterado, precedida de revisão de destino e dry-run; não usar push amplo ou `--delete --sync`.

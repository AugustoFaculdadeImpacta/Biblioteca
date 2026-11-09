# Tarefas

## 1. Gates de Apply e definição comum

- [x] 1.1 Backup/export confirmado; Review aprovado; `:focus-visible` verificado na Change arquivada `fundacao-frontend-reflex`.
- [x] 1.2 Confirmar o workspace `151966` (`Augusto's Workspace`), branch live `v1`, pelo Xano CLI em 2026-11-09; manter `allow_push` inalterado.
- [x] 1.3 Adicionar asserções estruturais para o predicado de empréstimo ativo aceitar `devolvido_em == null || devolvido_em == 0` e, conforme os lotes forem implementados, para a correção temporal FIFO e a ordenação estável.

## 2. Lote 1 — solicitação e retirada de solicitação

- [x] 2.1 Atualizar `emprestimos/solicitacoes_POST.xs` e `emprestimos/retirada_POST.xs` para que as verificações de empréstimo ativo/atrasado aceitem nulo e zero como “não devolvido”. Manter a precondição de atraso antes de qualquer efeito colateral.
- [x] 2.2 Para cada endpoint, separadamente: obter pull de rollback fora de `xano/`, comparar com o Git e executar `xano workspace push ... -i "<arquivo-unico>" --dry-run`. Prosseguir somente se a prévia listar exatamente esse endpoint como um `UPDATE`; parar se listar `CREATE`, outro recurso ou qualquer outro estado. Enviar somente o mesmo arquivo com o mesmo `-i`; usar `--force` apenas depois de revisar essa prévia.
- [x] 2.3 Executar `scripts/run-advanced-circulation-scenario.ps1 -Scenario atraso` (somente solicitação) e depois `-Scenario limite`, uma execução por vez. Exigir aprovação funcional, GET 404 individual das fixtures e contagens `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2` após cada cenário. Parar se o atraso não for bloqueado ou se mais de uma retirada for aceita. Se o limite ainda aceitar duas retiradas após a correção do sentinel, pausar para escolha explícita e validação por teste do mecanismo de índice único; não iniciar o Lote 2.

## 3. Lote 2 — devolução e elegibilidade de reservas

- [x] 3.1 Atualizar `emprestimos/devolucao_POST.xs` para que o guard de empréstimo ativo aceite nulo ou zero e os registros devolvidos recebam timestamp real, não zero. Atualizar `reservas/reservas_POST.xs` e `reservas/retirada_POST.xs` para usar o mesmo predicado de sentinel ativo/atrasado.
- [x] 3.2 Para cada endpoint, preservar separadamente o pull de rollback, comparar, exigir dry-run com exatamente um `UPDATE` daquele arquivo e enviar somente esse arquivo com `-i`; parar se a prévia indicar `CREATE` ou qualquer outro estado.
- [x] 3.3 Adicionar/ajustar testes estruturais e verificar que a transição de devolução grava timestamp (não zero) e que as verificações de elegibilidade usam o predicado comum. Executar `scripts/run-advanced-circulation-scenario.ps1 -Scenario atraso -CheckReservation` para verificar também a rota de reservas. Antes do Lote 3, confirmar GET 404 de todas as fixtures e contagens `0/0/0/0/0` com `usuario=2`.

## 4. Lote 3 — oferta FIFO e reoferta

- [x] 4.1 Atualizar `reservas/ofertar_proxima_POST.xs` para comparar com timestamp pré-calculado do tipo compatível, ordenar em memória o array de candidatos por `criada_em ASC, id ASC` e usar o predicado comum de empréstimo ativo. Atualizar `reservas/fila_GET.xs` para ordenar em memória a resposta pela mesma chave.
- [x] 4.2 Atualizar `reservas/processar_expiradas_POST.xs` para ordenar em memória as ofertas expiradas por `expira_em ASC, id ASC` e a fila de reoferta por `criada_em ASC, id ASC`, além de usar o predicado comum de empréstimo ativo. Não executar o processador global no runner.
- [x] 4.3 Para cada endpoint, preservar um pull de rollback fora de `xano/`, comparar, exigir `UPDATE` de um único recurso no dry-run delimitado ao arquivo e enviar somente esse arquivo. Confirmar por pull que os filtros `sort` em memória persistiram; parar diante de `CREATE`, recursos não relacionados, prévia ambígua ou filtro ausente.
- [x] 4.4 Executar `scripts/run-advanced-circulation-scenario.ps1 -Scenario fifo` sem o processador global, criando três reservas com `criada_em` igual e IDs em ordem conhecida. Confirmar a fila por `id ASC`, a oferta da reserva mais antiga e ausência de HTTP 500; depois confirmar GET 404 individual de cada fixture e contagens `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`.

## 5. Verificação final

- [x] 5.1 Executar os testes estruturais direcionados e completos; validar XanoScript com o validador oficial/local disponível. Confirmar os três cenários e ausência de efeitos colaterais inesperados. Os testes passaram; não há lint local, e cada dry-run/import/pull validou as definições no Xano.
- [x] 5.2 Atualizar `RESULTS.md` e `xano/README.md` com resultados sanitizados, caminhos de rollback e evidências dos pushes delimitados; garantir que não haja tokens, senhas, e-mails ou dados pessoais.
- [x] 5.3 Reconfirmar contagens paginadas e GET 404 das fixtures; inspecionar somente diffs dos endpoints desta Change e registros dos dry-runs; verificar que não houve push do diretório inteiro, `push --delete --sync` nem alteração de `allow_push`; executar `openspec validate corrigir-regras-circulacao --strict`.

## Acompanhamento do fluxo

- A ordem de Apply é Lote 1 → Lote 2 → Lote 3. Falha de cenário, limpeza, contagem, dry-run ambíguo ou regressão bloqueia o lote seguinte.
- Cada endpoint exige pull de rollback próprio, diff, dry-run delimitado mostrando somente um `UPDATE` e push do mesmo arquivo. `--force` só é permitido nesse push delimitado após revisão do dry-run.
- Se a leitura pós-push não preservar uma alteração necessária, interromper a Change antes de enviar outros endpoints ou iniciar o cenário correspondente; o bloqueio atual está registrado em `RESULTS.md`.
- Nunca enviar `xano/` inteiro, nunca usar `push --delete --sync`, nunca alterar `allow_push` e não criar commit Git.
- Arquivar somente depois que todas as tarefas e verificações estiverem concluídas.

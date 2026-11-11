# Tasks

## 1. Prova descartável de nulabilidade

- [ ] 1.1 Antes da primeira operação remota, confirmar por Xano CLI workspace `151966`, branch live `v1` e ambiente; consultar documentação oficial de nulabilidade XanoScript e Metadata API de schema/registros, sem exibir credenciais, e registrar evidência sanitizada do destino e das rotas usadas.
- [ ] 1.2 Confirmar por GET que `zz_teste_nota` não existe e preservar a evidência; criar a definição mínima com campo timestamp nullable usando sintaxe documentada, salvar rollback do estado ausente e executar dry-run com `-i` listando somente um `CREATE` da tabela; fazer push somente após revisar essa prévia e confirmar por GET do schema que o campo está nullable.
- [ ] 1.3 Criar um registro descartável com o campo explicitamente null pela Metadata API, reler o mesmo ID e confirmar null exato; registrar ID/tabela, excluir o registro individualmente e confirmar GET 404, excluir a tabela pelo ID/nome recém-confirmados e confirmar GET 404. Se schema ou registro não preservar null, parar sem alterar `emprestimo` ou endpoints e documentar o sentinel como estado mantido.

## 2. Schema produtivo de empréstimo

- [ ] 2.1 Somente após a prova descartável passar, confirmar por GET paginado que `emprestimo` tem contagem zero, salvar o schema remoto atual fora do repositório como rollback e verificar se há referências válidas para o registro de teste sem usar ou alterar dados preexistentes; se a contagem não for zero ou referências seguras não existirem, parar e reportar.
- [ ] 2.2 Atualizar `xano/table/emprestimo.xs` para declarar `devolvido_em` nullable conforme sintaxe comprovada; validar localmente a estrutura e revisar o diff para confirmar que nenhum outro campo/índice mudou.
- [ ] 2.3 Fazer dry-run delimitado a `table/emprestimo.xs` e exigir exatamente um `UPDATE`; fazer push somente desse arquivo e confirmar pelo GET do schema remoto `nullable=true`. Criar um registro de empréstimo de teste com referências válidas e `devolvido_em=null`, confirmar null por GET, remover o registro e confirmar GET 404 e contagem zero; parar diante de qualquer divergência.

## 3. Remoção do sentinel, endpoint por endpoint

- [ ] 3.1 Em `emprestimos/solicitacoes_POST.xs`, remover `|| devolvido_em == 0`; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull que os filtros usam apenas `devolvido_em == null`.
- [ ] 3.2 Em `emprestimos/retirada_POST.xs`, remover `|| devolvido_em == 0`; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull que os filtros usam apenas `devolvido_em == null`.
- [ ] 3.3 Em `emprestimos/devolucao_POST.xs`, remover `|| devolvido_em == 0` dos guards e consultas; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull que empréstimo ativo é identificado apenas por null e que a gravação da devolução continua usando timestamp real.
- [ ] 3.4 Em `reservas/reservas_POST.xs`, remover `|| devolvido_em == 0`; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull que os filtros usam apenas `devolvido_em == null`.
- [ ] 3.5 Em `reservas/retirada_POST.xs`, remover `|| devolvido_em == 0`; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull que os filtros usam apenas `devolvido_em == null`.
- [ ] 3.6 Em `reservas/ofertar_proxima_POST.xs`, remover `|| devolvido_em == 0` sem alterar a ordenação FIFO em memória; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull o predicado null-only e a ordenação persistida.
- [ ] 3.7 Em `reservas/processar_expiradas_POST.xs`, remover `|| devolvido_em == 0` sem alterar as ordenações em memória; antes do push guardar pull/rollback isolado, revisar diff, exigir dry-run `-i` com exatamente um `UPDATE`, enviar somente o arquivo e confirmar por pull os predicados null-only e as ordenações persistidas. Não executar o processador global.
- [ ] 3.8 Confirmar que `reservas/fila_GET.xs`, o oitavo endpoint relacionado da Change anterior, não contém referência a `devolvido_em` nem sentinel e não precisa de alteração; verificar por diff local e pull, sem fazer push.

## 4. Regressão funcional e documentação

- [ ] 4.1 Atualizar testes estruturais para exigir nullable na definição local e predicados `devolvido_em == null` nos sete endpoints, sem sentinel; manter verificação de ordenação FIFO. Executar os testes Xano e confirmar que passam.
- [ ] 4.2 Executar o cenário `atraso` isoladamente; confirmar bloqueios esperados, limpeza por GET 404 e contagens `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2` antes de iniciar outro cenário.
- [ ] 4.3 Executar o cenário `limite` isoladamente; confirmar que somente uma retirada concorrente é aceita, limpar cada fixture com GET 404 e confirmar as mesmas contagens antes de iniciar outro cenário.
- [ ] 4.4 Executar o cenário `fifo` isoladamente sem processador global; confirmar fila por `criada_em ASC, id ASC`, oferta HTTP 200 da reserva elegível mais antiga, limpeza individual por GET 404 e as mesmas contagens.
- [ ] 4.5 Atualizar `xano/README.md` removendo o sentinel como dívida técnica e registrar em `RESULTS.md` a prova descartável, migração, IDs de fixtures, rollbacks e resultados sanitizados; verificar ausência de tokens, senhas, e-mails e dados pessoais.

## 5. Verify final

- [ ] 5.1 Reconfirmar contagem paginada zero da tabela `emprestimo`, GET 404 de cada fixture e da tabela descartável, revisar todos os diffs e dry-runs, executar testes estruturais, validação XanoScript oficial/local disponível e `openspec validate devolvido-em-nulavel --strict`; registrar evidências e limitações.

## Workflow follow-up

- Aguardar aprovação humana explícita dos artefatos no Review antes de iniciar Apply.
- Arquivar somente após todos os gates e cenários passarem e a limpeza ser confirmada; se a prova de nulabilidade falhar, parar e reportar sem arquivar como concluída.
- Não fazer commit Git, push de `xano/` inteiro, `push --delete --sync` nem alterar `allow_push`.

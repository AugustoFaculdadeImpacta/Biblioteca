# Design

## Context

Veja `proposal.md` para os achados. Os contratos existentes em `loan-circulation` e `reservations` já exigem bloqueio por atraso, no máximo um empréstimo ativo por estudante e oferta FIFO. O código Xano versionado contém algumas verificações/ordenações esperadas, mas a execução no workspace live divergiu; a implementação deve ser guiada por comparação sanitizada entre Git e o destino confirmado, não pela suposição de que o remoto corresponde ao repositório.

O destino confirmado para este Apply é o workspace `151966` (`Augusto's Workspace`), branch `v1` live; identidade reconfirmada via Xano CLI em 2026-11-09. Não há ambiente isolado. O usuário aprovou os três lotes nesta Change. Antes de cada escrita, confirmar o destino novamente e preservar um pull somente leitura fora de `xano/`.

## Goals / Non-Goals

**Goals:**

- Fazer as regras de empréstimo ativo e atraso reconhecerem tanto `devolvido_em = null` quanto o sentinel `devolvido_em = 0`, observado no schema/GET remoto.
- Revalidar atraso e limite após o primeiro lote, antes de qualquer lote posterior.
- Se a corrida de limite persistir depois de corrigir o sentinel, parar e solicitar escolha/aprovação de garantia atômica; índices únicos são a opção inicial a avaliar por teste.
- Corrigir a comparação temporal que provoca `ERROR_FATAL` na oferta FIFO e ordenar os arrays em memória por `criada_em ASC, id ASC` na fila e na oferta, pois o sort dentro de `db.query` não persistiu no remoto.
- Provar cada lote por cenários isolados e registrar respostas sanitizadas e limpeza das fixtures.

**Non-Goals:**

- Alterar os requisitos de produto já especificados ou criar uma capability/spec redundante.
- Alterar frontend Reflex, interface ou funcionalidades fora das regras de circulação aprovadas.
- Alterar o schema `emprestimo` para aceitar null nesta etapa; a decisão é usar `null OU 0` como “não devolvido”.
- Sincronizar todo o diretório `xano/`, alterar a preferência `allow_push`, operar em registros preexistentes ou fazer deploy fora dos pushes delimitados aprovados.

## Decisions

### Comparar o destino com as definições versionadas antes de corrigir

Antes de qualquer escrita, confirmar workspace, branch e ambiente selecionados via Xano CLI e registrar a identificação. Fazer pull somente leitura das definições necessárias para fora do diretório versionado; revisar status/diff e sanitizar `swagger.token` ou qualquer segredo antes de trazer conteúdo ao Git. Comparar, no mínimo, as definições das rotas de solicitação, retirada e fila/oferta. Não assumir que um endpoint existente em `xano/` já está aplicado no remoto.

Para a solicitação com atraso, confirmar na definição efetivamente implantada que a consulta de empréstimos ativos vencidos ocorre antes de criar solicitação ou reserva e reproduzir o comportamento com fixture isolada. Para HTTP 500 na oferta FIFO, correlacionar a resposta com logs disponíveis sem copiar conteúdo pessoal/segredo, e comparar o fluxo executado com a definição versionada. Corrigir a causa observada, não apenas mascarar o status.

### Revalidar atraso antes de qualquer efeito colateral

O schema remoto indica `devolvido_em` como `timestamp`, `nullable=false`, `required=false`, enquanto a definição local usa `timestamp devolvido_em?`. Tanto POST/PUT explícito de null quanto empréstimo criado pela rota retornaram `devolvido_em=0`. Portanto, o predicado para “não devolvido” deve aceitar `devolvido_em == null || devolvido_em == 0`, sem alterar o schema nesta Change.

A rota de solicitação deve validar empréstimos ativos vencidos antes de criar solicitação, reserva ou alterar disponibilidade. O teste deve confirmar rejeição e ausência de registros/efeitos colaterais, não somente um status de erro. A mesma definição de “ativo” precisa ser aplicada a retiradas, devolução e elegibilidade de reservas/reoferta para manter o domínio consistente.

### Adiar garantia atômica até revalidar o sentinel

O limite concorrente será reexecutado no primeiro lote depois de atualizar os predicados para `null OU 0`. Se o cenário passar (uma única retirada aceita), não adicionar índice/campo/lock. Se ainda aceitar duas retiradas, interromper a Change antes do Lote 2 e pedir decisão humana sobre a opção de índices únicos para empréstimo ativo. Não implementar garantia atômica nesta autorização sem a escolha explícita do mecanismo e validação por teste.

### Restaurar seleção FIFO e corrigir a falha da oferta

A mensagem sanitizada de `ERROR_FATAL` foi `Invalid cast: "('now')::timestamptz" is of type:"timestamp", but trying to be of type:"epochms"`. A oferta compara `vence_em` com uma expressão inline `"now"|to_timestamp`; substituir por instante previamente calculado e compatível com o tipo do campo antes da comparação. Não inferir que isso por si só garante FIFO.

A consulta GET e a seleção de oferta remotas não definem `sort`. A tentativa de declarar `sort` em `db.query` foi normalizada pelo parser como equivalente e não gerou alteração no dry-run. Usar o filtro XanoScript `sort` sobre o array retornado: ordenar primeiro por `id` numérico crescente e depois pelo campo temporal primário crescente (`criada_em` na fila/oferta, `expira_em` no conjunto expirado). A ordenação por ID é o desempate; o cenário real usa três reservas com o mesmo `criada_em` para validar a ordem por ID. A oferta deve percorrer o array já ordenado, ignorar candidatos inelegíveis conforme regras existentes (incluindo `devolvido_em == null || devolvido_em == 0`) e alocar sem HTTP 500.

No processador, a ordem também é relevante: ao processar várias ofertas expiradas do mesmo título, ela pode determinar qual exemplar liberado é atribuído a cada reserva aguardando. Ordenar esse conjunto por `expira_em ASC, id ASC` e a fila de reoferta por `criada_em ASC, id ASC`. O cenário FIFO desta Change não deve chamar o processador global de expiração.

### Aplicação e testes no Xano

Antes de implementar comportamento de produto, confirmar que a mitigação `:focus-visible` da busca foi implementada e verificada. Antes de qualquer deploy, confirmar ambiente acadêmico validado, segredos somente no backend e inspeção de logs.

O usuário confirmou backup/export do workspace e informou que o Xano CLI reportou que push é sempre habilitado em workspaces do plano Free. Tratar esse fato como contexto operacional; não alterar nem tentar alterar a preferência `allow_push`.

Aplicar em lotes e respeitar os gates sequenciais:

1. **Lote 1:** `emprestimos/solicitacoes_POST.xs` e `emprestimos/retirada_POST.xs`, ambos com o predicado `null OU 0`. Fazer push individual por endpoint e executar cenários `atraso` (somente a solicitação) e `limite`, com limpeza/contagens entre eles. A validação da rota `reservas` é adiada porque sua definição pertence ao Lote 2. Se limite continuar aceitando duas retiradas, parar antes do Lote 2 e pedir decisão sobre índices únicos.
2. **Lote 2:** `emprestimos/devolucao_POST.xs` (gravar timestamp real ao devolver e tratar sentinel), `reservas/reservas_POST.xs` e `reservas/retirada_POST.xs`. Confirmar por teste estrutural que devolução grava timestamp não-zero e que predicados de ativo/atraso são consistentes; executar `atraso -CheckReservation` para verificar também a rota de reservas. Após o lote, verificar limpeza e contagens.
3. **Lote 3:** `reservas/ofertar_proxima_POST.xs`, `reservas/fila_GET.xs` e `reservas/processar_expiradas_POST.xs`. Corrigir cast temporal e ordenação nos caminhos de oferta/reoferta. Executar somente cenário `fifo`; nunca chamar o processador global no runner. Confirmar limpeza e contagens.

Para cada endpoint corrigido, antes do push:

1. Guardar o pull isolado do endpoint fora de `xano/` como cópia de rollback; comparar com o arquivo Git e relatar a divergência, sanitizando segredos. Não substituir a definição local pelo remoto sem autorização.
2. Executar `--dry-run` com `-i` apontando somente ao arquivo do endpoint. Prosseguir somente se a prévia listar exatamente um recurso como `UPDATE`. Se listar `CREATE`, qualquer outro estado, mais de um recurso ou não corresponder inequivocamente ao endpoint, parar e reportar provável divergência de caminho (`api/biblioteca` remoto vs `api/default` local).
3. Executar push do mesmo arquivo, com o mesmo `-i`; `--force` somente nesse push delimitado após validar o dry-run. Nunca ampliar escopo.

Repetir pull, comparação, dry-run e push por endpoint e na ordem dos lotes. Se o diff remoto revelar alteração não compreendida, ou a prévia não for o único `UPDATE`, parar antes do push. Nunca usar `push --delete --sync`, nunca enviar `xano/` inteiro e nunca alterar `allow_push`. Após cada lote, limpar fixtures por GET 404 e confirmar `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2` antes de iniciar o próximo.

Cada cenário deve usar fixtures sintéticas próprias, IDs registrados imediatamente e limpeza individual em ordem de dependência com GET 404. Executar atraso, limite concorrente e FIFO separadamente; não encadear cenários se a limpeza não tiver sido confirmada. Nenhum token, senha, e-mail ou dado pessoal vai para arquivos ou logs da Change.

## Risks / Trade-offs

- [O remoto diverge das definições versionadas ou há segredo em arquivos exportados] → usar pull somente leitura, revisar diff e sanitizar antes de atualizar `xano/`.
- [O mecanismo atômico não é suportado ou exige mudança de schema] → interromper e retornar a design/Review; não aplicar uma checagem que apenas repete a corrida.
- [A causa do HTTP 500 depende de dados não-fixture ou de log com dados pessoais] → não copiar esses dados; parar e documentar somente evidência sanitizada.
- [Dry-run inclui `CREATE`, recursos fora do escopo ou estado diferente de um único `UPDATE`] → não alterar configuração nem ampliar o push; parar e reportar.
- [Filtro `sort` em memória não persiste no pull pós-push] → parar antes de enviar o próximo endpoint ou executar o cenário FIFO; registrar a divergência e não arquivar.
- [Sentinel zero não é aceito pelo predicado Xano esperado] → parar após primeiro lote e revisar evidência; não iniciar Lote 2.
- [Falha na criação/limpeza ou contagem final] → interromper os cenários seguintes e não arquivar.

## Migration Plan

1. Confirmar workspace `151966`/branch `v1`, preservar pull isolado, aplicar e verificar Lote 1; parar se atraso falhar ou limite aceitar mais de uma retirada.
2. Somente se Lote 1 passar, aplicar e verificar Lote 2; exigir devolução gravada como timestamp real e estado de fixture limpo.
3. Somente se Lote 2 passar, aplicar e verificar Lote 3. As ordenações FIFO são filtros em memória sobre os arrays retornados, não opções `sort` de `db.query`; o cenário cria três reservas em ordem conhecida, valida consulta e oferta, e não chama o processador global.
4. Em cada definição, manter cópia de rollback, diff, dry-run único `UPDATE`, push individual com `--force` somente no caso delimitado.
5. Após cada lote, confirmar GET 404 de cada fixture e contagens paginadas finais `0/0/0/0/0`, usuário=2; interromper ao primeiro desvio.
6. Sanitizar evidências, executar testes estruturais e `openspec validate --strict`. Arquivar somente após critérios de Verify aprovados.

Rollback: manter o diff local e as definições anteriores obtidas por pull somente leitura. Se uma sincronização aprovada produzir regressão, parar os testes e preparar uma reversão delimitada a esses mesmos recursos, sujeita a nova revisão do destino e diff; nunca restaurar com push amplo ou exclusão sincronizada.

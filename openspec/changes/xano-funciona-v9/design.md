# Design

## Context

Ver [proposal.md](./proposal.md) e os contratos em `specs/`. O cliente compartilha transporte Xano, mas as telas autenticadas convertem listas para modelos próprios. O diagnóstico deve respeitar as permissões já validadas no backend e não persistir resultados.

## Goals / Non-Goals

**Goals:**
- Aceitar variações compatíveis de envelope e valores sem enfraquecer as permissões nem os campos identificadores necessários.
- Separar a confirmação HTTP de uma escrita da leitura opcional de seu corpo.
- Produzir um relatório útil para comparar contratos sem copiar valores pessoais.
- Dar ao usuário uma referência correlacionável entre a mensagem da interface e um bloco de erro sanitizado no stderr do backend.
- Diagnosticar a desativação e validar a acessibilidade do cabeçalho sem alterar o layout aprovado ou publicar no Xano.

**Non-Goals:**
- Alterar endpoints, permissões, modelos de dados ou contratos remotos.
- Escrever no Xano, sincronizar definições de volta ou mudar o layout aprovado.

## Decisions

- Fazer a extração do envelope e as conversões escalares na fronteira comum de leitura; manter a validação de campos por modelo e isolar a rejeição a cada registro, agregando a contagem para a interface.
- Tratar `0`/`null` em IDs e datas opcionais como ausência, manter IDs obrigatórios positivos e aceitar qualquer estado textual sem descartar o registro. Falhas de estrutura são adiadas durante a validação da lista para emitir um único bloco detalhado por chamada, com índice, campo e motivo; a duração vem do tempo da requisição e o perfil/ação usa o contexto de sessão do evento.
- Tratar status 2xx como resultado da escrita independentemente da legibilidade do corpo. Para solicitação de reserva, confirmar imediatamente quando a resposta contém ID válido e o mesmo `titulo_id`, acrescentar o registro ao estado local e não reler listas. Somente quando a resposta não puder ser interpretada, reler imediatamente e após 1,5 s e 4 s desde o POST, sem repetir a escrita. Se continuar ausente, manter o bloqueio até ação explícita de atualização manual; o botão de nova tentativa da página Reservas somente relê listas.
- Gerar o diagnóstico a partir das operações GET já existentes, com seleção por perfil no servidor. Usar a sessão corrente; a lista de contas bibliotecárias fica restrita ao admin. Remover valores antes de montar linhas e texto copiável.
- Centralizar a criação das referências e a sanitização dos blocos de falha na fronteira Xano. Falhas são sempre enviadas ao stderr com flush salvo `BIBLIOTECA_LOG_ERROS=0`; registrar respostas bem-sucedidas continua condicionado a `BIBLIOTECA_DIAGNOSTICO=1`. O handler de exceções do backend Reflex registra tracebacks higienizados sem suprimir o comportamento padrão.
- Correlacionar referências de falha com mensagens de botão. Mensagens curtas do Xano só podem ser mostradas quando não contiverem e-mail nem sequências numéricas longas.
- Comparar o PATCH local e a cópia remota previamente existente, linha a linha, sem novo pull; qualquer correção fica local e a aplicação remota é instrução manual.
- Aplicar tokens de tema para texto e fundo dos dois controles do cabeçalho e testar contraste mínimo 4,5:1 em tema claro/escuro, repouso/hover/foco, sem alterar geometria.
- Antes de qualquer sincronização, confirmar por Xano CLI que o workspace é `151966`, que a branch `v1` está marcada como live e qual ambiente está selecionado; registrar os resultados sem credenciais, tokens ou URLs. O `.env` somente ajuda a confirmar a instância/grupo configurados e não prova, sozinho, a branch.
- Fazer pull somente leitura das definições para um diretório temporário fora do repositório, sem registros ou variáveis de ambiente, como cópia local de referência. Comparar apenas `table/titulo.xs`, `table/reserva.xs`, `api/default/catalogo/titulos_id_PATCH.xs`, `api/default/admin/acervo_GET.xs`, `api/default/emprestimos/solicitacoes_POST.xs`, `api/default/emprestimos/minhas_solicitacoes_GET.xs`, `api/default/reservas/minhas_GET.xs` e `api/default/reservas/reservas_POST.xs` com os arquivos de `xano/`.
- Validar os oito arquivos com o Xano Developer MCP e usar `xano workspace push` a partir de uma pasta temporária que contenha somente esses arquivos, com workspace e branch explícitos, sem dados ou variáveis. Executar primeiro `--dry-run`, revisar que o diff contém somente os objetos aprovados e preservar o comportamento transacional padrão. Não usar `--sync`, `--delete`, `--records`, `--env`, `--truncate` ou `--force` no push.
- Não habilitar nem alterar `allow_push`. Se a preferência do workspace impedir o push direto, interromper sem substituir o destino por sandbox e sem alterar a preferência.
- Após o push, fazer novo pull somente de definições para confirmar que os oito objetos publicados correspondem às fontes locais. Validar estruturalmente os contratos: PATCH persiste `ativo=false` e GET administrativo o reflete; POST de solicitação persiste o pedido e a leitura pessoal encontra uma solicitação ativa ou reserva correspondente. Não criar reservas nem desativar títulos reais em produção; testes HTTP com escrita exigem fixtures e conta de teste autorizadas.
- Inventariar as diferenças, autorização, entradas, campos de resposta e resultados da conferência em `docs/xano-diferencas.md`, sem incluir URLs ou segredos.

## Risks / Trade-offs

- [Conversão permissiva mascara incompatibilidades] → campos identificadores permanecem obrigatórios; outros registros inválidos são contados e o relatório diagnóstico mantém os nomes dos campos problemáticos.
- [Resposta ilegível após escrita confirmada] → não repetir a escrita; mostrar aviso e atualizar a lista antes de liberar nova tentativa.
- [Leitura da gravação atrasada] → fazer somente releituras GET limitadas e manter a solicitação bloqueada até confirmação ou atualização manual.
- [Relatório expõe dados pessoais] → coletar e exibir somente status, tempos, nomes de chaves, tipos e motivos de validação; não registrar valores nem persistir o relatório.
- [Destino Xano ambíguo] → não executar pull nem push até confirmar workspace, branch e ambiente pelo CLI.
- [Push inclui objetos ou dados fora do escopo] → restringir por filtros explícitos e inspecionar o dry-run; interromper se aparecer qualquer objeto adicional, registro, variável ou exclusão.
- [Push live indisponível por allow_push=false] → manter a preferência intacta e interromper; não habilitar push direto nem trocar para sandbox.
- [Investigação da falha exige diagnóstico real] → não registrar segredos ou dados pessoais, não repetir POST para confirmar e deixar qualquer escrita remota explicitamente fora desta execução.

## Migration Plan

Não há migração de dados. Validar localmente com testes simulados, `reflex compile --dry` e pytest em sequência. Nesta execução, não escrever no Xano nem fazer novo pull; usar apenas a cópia de referência já existente para comparação e instruções de correção manual. Manter a Change aberta enquanto as tarefas de publicação que exigem escrita remota não puderem ser concluídas.

# Proposal

## Why

Algumas telas autenticadas não conseguem interpretar respostas do Xano que variam entre listas e objetos embrulhados, e operações concluídas podem ser apresentadas como falha quando o corpo de resposta é ilegível. A mudança torna essas jornadas tolerantes e recuperáveis, e fornece um relatório de diagnóstico sanitizado para que o usuário identifique diferenças do contrato sem expor dados privados.

## What Changes

- Interpretar listas autenticadas por registro, aceitar os formatos e tipos compatíveis definidos nos requisitos, ignorar campos desconhecidos e informar quantos registros foram pulados.
- Tratar POST/PATCH com status 2xx e corpo ilegível como sucesso com aviso, atualizar as listas e nunca repetir a escrita automaticamente; para solicitações de reserva, fazer até duas releituras GET limitadas quando a gravação ainda não estiver visível, mantendo o bloqueio até confirmar ou oferecer atualização manual.
- Registrar sempre falhas do Xano no terminal do backend com referência curta, metadados e conteúdo higienizado; permitir desligar somente esse registro com `BIBLIOTECA_LOG_ERROS=0`, mantendo sucessos restritos a `BIBLIOTECA_DIAGNOSTICO=1`.
- Exibir a referência do log nas mensagens de erro de ações, incluir mensagens curtas e seguras enviadas pelo Xano e confirmar reservas por até três leituras no intervalo especificado sem repetir o POST.
- Investigar a desativação enviando `ativo` como booleano, comparando o PATCH local com a cópia remota já existente e documentando correção e aplicação manual sem publicar no Xano.
- Preservar e testar o bloqueio de submissão de reserva durante a escrita e suas releituras, corrigir o contraste dos controles do cabeçalho com os tokens existentes e concluir o diagnóstico autenticado e o resumo independente da home.
- Fazer cada indicador do resumo da home carregar e falhar de forma independente.
- Disponibilizar no menu Perfil um diagnóstico somente leitura, limitado às chamadas autorizadas pelo perfil e usando a sessão existente; somente admin consulta a lista de contas bibliotecárias, conforme a autorização administrativa já definida. Mostrar metadados de estrutura sem valores pessoais e permitir copiar relatório sanitizado.
- Confirmar pelo Xano CLI o workspace, ambiente e branch selecionados; comparar os contratos locais com um pull somente leitura fora do repositório e registrar diferenças e recomendação de publicação em `docs/xano-diferencas.md`.
- Sincronizar e publicar somente `table/titulo.xs`, `table/reserva.xs`, `api/default/catalogo/titulos_id_PATCH.xs`, `api/default/admin/acervo_GET.xs`, `api/default/emprestimos/solicitacoes_POST.xs`, `api/default/emprestimos/minhas_solicitacoes_GET.xs`, `api/default/reservas/minhas_GET.xs` e `api/default/reservas/reservas_POST.xs` no workspace `151966`, branch `v1` marcada como live, após confirmar o destino e revisar um dry-run.
- Após a publicação, conferir por pull que os oito contratos publicados correspondem aos arquivos locais e validar os fluxos de desativação e confirmação de solicitação/reserva; não alterar dados de produção durante a validação.
- Manter o layout aprovado; não executar o ajuste opcional de rolagem da barra.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `xano-communication`: tolerância a formatos de resposta e sucesso de escritas 2xx ilegíveis; diagnóstico interativo autenticado, somente leitura e sanitizado.
- `primary-journeys`: carregamento e recuperação independentes para cada indicador da home.
- `reservations`: prevenção de cliques duplicados durante a escrita e até a atualização das listas.

## Impact

- Código Reflex e serviços Xano em `biblioteca_mais_nova/`, incluindo parsers de catálogo, circulação, reservas e contas e os eventos da interface.
- Testes pytest com respostas simuladas para variações de formato, status, avisos de escrita, independência de indicadores e privacidade do relatório.
- Documentação em `docs/diagnostico-xano.md` e novo inventário `docs/xano-diferencas.md`.
- Logs de falha sanitizados, mensagens de erro com referência, confirmação de reserva por releitura, evidência de PATCH para desativação, teste de prevenção de envio duplicado e testes numéricos de contraste do cabeçalho.
- Xano remoto: pull somente leitura para cópia de referência e publicação delimitada aos oito arquivos listados, apenas após confirmação do workspace `151966`, branch `v1` live e ambiente selecionado. Não publicar registros nem variáveis, não usar sincronização completa ou exclusões e não alterar `allow_push`; se o push delimitado não for permitido, interromper.

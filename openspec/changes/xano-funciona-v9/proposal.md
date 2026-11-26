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
- Preparar comparação e recomendações locais para as oito definições Xano; transferir ao usuário a validação e publicação manual porque o MCP de validação não concluiu e o workspace está com `allow_push=false`.
- Não publicar no Xano nem fazer novo pull nesta execução. O usuário poderá conferir manualmente no painel os contratos de desativação, solicitações e reservas conforme `docs/xano-diferencas.md` e `docs/xano-correcao-ativo.md`.
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
- Xano remoto: as diferenças e passos de validação/publicação manual estão registrados localmente. A publicação e confirmação de runtime ficam transferidas ao usuário; nenhum dado, definição ou configuração remota foi alterado nesta execução.

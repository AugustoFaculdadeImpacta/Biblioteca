# Proposal

## Why

Algumas telas autenticadas não conseguem interpretar respostas do Xano que variam entre listas e objetos embrulhados, e operações concluídas podem ser apresentadas como falha quando o corpo de resposta é ilegível. A mudança torna essas jornadas tolerantes e recuperáveis, e fornece um relatório de diagnóstico sanitizado para que o usuário identifique diferenças do contrato sem expor dados privados.

## What Changes

- Interpretar listas autenticadas por registro, aceitar os formatos e tipos compatíveis definidos nos requisitos, ignorar campos desconhecidos e informar quantos registros foram pulados.
- Tratar POST/PATCH com status 2xx e corpo ilegível como sucesso com aviso, atualizar as listas e nunca repetir a escrita automaticamente; impedir reserva duplicada enquanto a tentativa aguarda e as listas recarregam.
- Fazer cada indicador do resumo da home carregar e falhar de forma independente.
- Disponibilizar no menu Perfil um diagnóstico somente leitura, limitado às chamadas autorizadas pelo perfil e usando a sessão existente; somente admin consulta a lista de contas bibliotecárias, conforme a autorização administrativa já definida. Mostrar metadados de estrutura sem valores pessoais e permitir copiar relatório sanitizado.
- Comparar, por pull de definições somente leitura, as chamadas e contratos do app com o Xano remoto e registrar diferenças e recomendação de publicação em `docs/xano-diferencas.md`.
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
- Xano remoto: somente leitura de definições, após confirmar workspace, branch e ambiente pelo Xano CLI; nenhum push, sync ou alteração remota.

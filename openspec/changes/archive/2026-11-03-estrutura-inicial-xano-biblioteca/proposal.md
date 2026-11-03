# Proposal

## Why

A biblioteca precisa de uma estrutura Xano greenfield e de contratos de API para representar as regras aprovadas de identidade, acervo, circulação, reservas e condição dos exemplares. Esta Change prepara o backend para uma futura integração com Reflex, sem implementar a aplicação Reflex.

## What Changes

- Definir o modelo lógico Xano, suas tabelas e relações para as cinco áreas funcionais da biblioteca, sem usar o schema legado nem a implementação de `biblioteca-nova` como modelo.
- Documentar contratos lógicos de endpoints para cadastro/login/perfil, catálogo, administração do acervo, solicitação e confirmação física de empréstimo, devolução, reservas FIFO e histórico de condição.
- Incorporar as decisões já fornecidas: cadastro com nome e e-mail normalizado único; pedido sem exemplar entra na fila FIFO de reservas do título e recebe exemplar quando chega sua vez; títulos exigem título e autor(es), com outros metadados bibliográficos opcionais; cada exemplar recebe código de tombo único e imutável atribuído pelo sistema; a oferta de retirada dura 48 horas corridas desde a associação do exemplar, com timestamps UTC e apresentação em `America/Sao_Paulo`; não incluir cancelamento nem exclusão/arquivamento nesta Change.
- Provisionar o primeiro bibliotecário manualmente por operador autorizado no Xano; não criar endpoint público de promoção nem registrar senha ou token em arquivos.
- Planejar candidatos Xano e contratos documentais para consumo futuro pelo Reflex. A implementação de telas, sessão Reflex e aplicação cliente não faz parte desta Change.
- Preparar todos os candidatos localmente, verificar o destino e o diff, e aplicar somente tabelas/endpoints necessários à biblioteca. O usuário autorizou a reconstrução desses recursos no destino indicado, incluindo substituição dos recursos legados; não alterar outros tipos de recurso.
- Registrar a exceção deliberada ao processo usual de Changes verticais pequenas: por pedido explícito, esta Change abrange de uma vez a camada Xano das cinco áreas, sem alegar conformidade com a orientação vertical.
- Destino autorizado pelo usuário para esta Change: workspace Xano `151966`, branch `v1` (live). Em 2026-10-27 o CLI confirmou novamente que `allow_push: false`; portanto escrita continua bloqueada. Não escolher outro destino nem tentar contornar a restrição.
- Limitar todas as operações remotas desta Change a tabelas e endpoints necessários à biblioteca. Não alterar funções, addons, definições/configurações do workspace, variáveis de ambiente ou outros recursos.
- O usuário autorizou reconstruir tabelas e endpoints legados necessários à biblioteca no destino confirmado. Registros não foram consultados durante Apply; remoção/recriação de tabelas pode perder dados nelas e esse risco deve ser informado no relatório. A verificação segura concluída usou somente dados sintéticos pelos endpoints existentes, com IDs registrados, leitura individual e remoção confirmada desses mesmos IDs. Ajustes temporais, testes globais de expiração e concorrência foram separados para `verificacao-avancada-circulacao`, em ambiente isolado. Não incluir cancelamento de pedidos/reservas nem exclusão/arquivamento de títulos, categorias ou exemplares como funcionalidade da API.
- Não registrar credenciais do bibliotecário nos artefatos nem nos candidatos locais; o provisionamento manual ocorre no Xano por operador autorizado.
- Preservar as Changes substituídas e seu histórico; não as apagar nem arquivá-las como concluídas.

## Capabilities

### New Capabilities

- `identity-session`: cadastro imediato de estudante, login e perfil confiável, com Xano como autoridade de identidade.
- `catalog`: consulta pública e administração autorizada de títulos, categorias, relações e exemplares individuais.
- `loan-circulation`: solicitação de empréstimo, retirada física e devolução, com prazo e elegibilidade aprovados.
- `reservations`: reservas de títulos em FIFO, unicidade ativa e oportunidade de retirada conforme decisões aprovadas.
- `copy-condition`: registro de dano/perda, indisponibilidade e histórico de condição de exemplares.

### Modified Capabilities

Nenhuma. Ainda não existem specs consolidadas.

## Impact

- Xano: estrutura greenfield de tabelas, relações e endpoints para as capacidades listadas. As decisões de domínio foram fornecidas; a validação avançada de concorrência, geração de tombo sob disputa e expiração/reoferta pertence à Change `verificacao-avancada-circulacao`.
- Integração futura: contratos documentados para que Reflex possa consumir a API; não inclui telas, aplicação Reflex, sessão no cliente, configuração de ambiente Reflex nem testes de integração Reflex.
- Consulta de metadados nesta execução: workspace `151966` (`Augusto's Workspace`), branch `v1` live, `allow_push: false`. Nenhum registro ou variável foi lido. O inventário conhecido de 35 definições veio de pull somente de definições anterior; não foi atualizado nesta execução. Não usar schema legado como modelo greenfield. Remover/substituir tabelas e endpoints legados somente se necessários ao contrato aprovado; preservar todos os outros tipos de recurso.
- Apply permanece bloqueado enquanto `allow_push: false`. Se a permissão mudar, reconfirmar destino/branch/autorização, revisar dry-run e diff para garantir que somente tabelas/endpoints necessários à biblioteca sejam afetados e aplicar apenas esse escopo autorizado.
- Não inclui renovação, multas, regularização/recuperação de exemplares perdidos, cancelamento de pedidos/reservas, exclusão/arquivamento de títulos/categorias/exemplares como operação de API ou deploy. Operações diretas sobre registros permanecem fora do escopo, exceto a limpeza individual já concluída das fixtures da verificação segura. A reconstrução autorizada de tabelas legadas pode perder dados não consultados nelas.

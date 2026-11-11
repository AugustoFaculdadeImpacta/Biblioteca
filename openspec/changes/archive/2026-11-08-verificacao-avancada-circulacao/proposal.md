# Proposal

## Why

Restam regras que exigem manipulação temporal, processamento global de ofertas ou disputas concorrentes. Só há o workspace live `151966/v1`, sem ambiente isolado. Portanto, qualquer Apply depende de backup/export feito pelo usuário, aprovação explícita no Review e pré-check somente leitura que prove a segurança do estado live; se algum gate falhar, os testes param.

## What Changes

- Exigir backup/export feito pelo usuário e aprovação explícita antes de iniciar Apply.
- Antes de qualquer teste global, fazer pré-check somente leitura completo pela Metadata API oficial e parar se houver reserva ofertada vencida, empréstimo ativo ou solicitação pendente.
- Criar, ajustar e excluir registros de teste somente pela Metadata API, nas seis tabelas autorizadas; registrar cada tabela/ID no momento da criação e nunca alterar os dois usuários preexistentes.
- Após os gates, executar cenários isolados de atraso, limite de empréstimos ativos, FIFO, expiração/reoferta (somente se o pré-check confirmar a fixture vencida), concorrência e geração de código de tombo; registrar aprovação ou achado observado usando somente fixtures rastreadas.
- Registrar a divergência FIFO observada entre Git e remoto como cenário de verificação, sem corrigir implementação nesta Change.
- Não alterar requisitos de produto, tabelas, endpoints ou o frontend nesta Change.
- Registrar evidências sanitizadas, IDs/tabelas das fixtures e limpeza individual confirmada por GET 404 antes de consolidar o resultado; terminar com contagens zero nas quatro tabelas de circulação e exemplares, e `usuario=2`.

## Capabilities

Nenhuma alteração de requisito de produto. Esta Change é exclusivamente de verificação; `skip_specs: true` está declarado em `.openspec.yaml`.

## Impact

- Xano: o único destino disponível é o live `151966/v1`; escritas ficam limitadas aos registros sintéticos e às seis tabelas explicitamente autorizadas, após backup/export, aprovação explícita e pré-check aprovado.
- OpenSpec: a Change `reconciliar-xano-com-git` registra as divergências remotas FIFO que esta Change deverá testar sem corrigir.

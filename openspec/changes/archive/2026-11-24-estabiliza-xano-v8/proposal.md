# Proposal

## Why

Chamadas frequentes e falhas pouco específicas do Xano deixam algumas telas presas ou difíceis de diagnosticar, enquanto capas externas quebradas e o realce incompleto da navegação prejudicam a experiência. Esta mudança preserva a aparência aprovada, reduz chamadas redundantes e torna falhas e importações recuperáveis sem repetir gravações automaticamente.

## What Changes

- Corrigir o realce de links e botões da barra para cobrir integralmente emoji e rótulo, sem alterar a aparência aprovada fora desse defeito.
- Exibir sempre a capa gerada por baixo da imagem remota; resolver capas Open Library por título/autoria em segundo plano, com cache, concorrência limitada e opção sem rede.
- Adicionar diagnóstico opt-in do cliente Xano no terminal, mensagens de erro específicas, repetição somente para leituras, limite de concorrência e cache público em memória.
- Auditar carregamentos por rota, eliminar consultas duplicadas, garantir encerramento de indicadores de carregamento e permitir recuperação visível de falhas.
- Adicionar ao Acervo diagnóstico de cinco leituras públicas para admin real e tornar a importação dos livros de exemplo pausada, retomável e segura diante de falhas transitórias.
- Registrar a comparação do endpoint de desativação com o pull remoto apenas se o destino Xano selecionado puder ser confirmado; nenhuma escrita remota será executada.

## Capabilities

### New Capabilities

- `xano-communication`: diagnóstico opt-in, controle de concorrência, cache público, política segura de repetição e mensagens de falha para comunicação com Xano.

### Modified Capabilities

- `frontend-foundation`: realce integral e não encolhível dos controles da barra.
- `cover-isbn`: imagem gerada permanente, fallback de falha sem texto/ícone quebrado e resolução remota por título/autoria.
- `catalog`: abertura sem rajada de consultas, resumo parcial, ferramenta de diagnóstico do Acervo e importação retomável e tolerante a falhas transitórias.
- `primary-journeys`: estatísticas da home independentes, com recuperação por indicador.
- `reservations`: falhas de leitura e gravação com mensagens distintas, estado recuperável e ação de tentar novamente.

## Impact

- Reflex/backend em `biblioteca_mais_nova/`, em especial `icons.py`, `covers.py`, `capas_isbn.py`, `xano_client.py` e carregadores de estado.
- Testes locais com cliente HTTP e estado simulados; documentação operacional em `docs/diagnostico-xano.md`.
- Dependência externa de consulta somente à Open Library, desativada por `BIBLIOTECA_SEM_REDE=1`; nenhuma dependência nova.
- Xano permanece somente leitura nesta Change; não usar comandos de sincronização ou escrita.

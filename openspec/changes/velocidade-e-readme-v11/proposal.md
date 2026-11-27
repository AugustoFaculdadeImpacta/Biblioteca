# Proposal

## Why

O README atual está extenso e não oferece uma configuração de execução direta para o projeto. Além disso, respostas reais de configuração e carregamentos lentos precisam ser tolerados sem perder dados já disponíveis nem repetir escritas.

## What Changes

- Substituir o README da raiz por instruções curtas em português, incluindo a configuração da API.
- Aceitar os metadados reais retornados pelo endpoint de regras.
- Reutilizar cópias temporárias de dados enquanto as atualizações remotas estão em andamento.
- Pré-carregar dados públicos, usar atualizações otimistas seguras e agrupar releituras após escritas.
- Registrar evidências de desempenho e resolver as Changes locais ou transferíveis já ativas.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `library-rules`: tolerância a metadados reais e campos adicionais na resposta de regras.
- `xano-communication`: cópias de dados, pré-carga, atualização em segundo plano e medição de carregamentos.
- `primary-journeys`: estados otimistas de ações e releitura agrupada após escrita.

## Impact

README.md, analisador de regras, cliente Xano, carregamentos Reflex, estado das ações, API de demonstração, testes e documentação de desempenho e execução.

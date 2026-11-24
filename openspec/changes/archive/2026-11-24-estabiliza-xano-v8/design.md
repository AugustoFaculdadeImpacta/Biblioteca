# Design

## Context

O cliente Xano atual cria um `AsyncClient` por chamada, não limita concorrência e converte falhas de transporte em exceções sanitizadas sem política comum de retry nem métricas por página. Os carregadores públicos consultam catálogo/categorias repetidamente; a home aguarda os dois resultados antes de atualizar os indicadores. As capas reais são resolvidas por ISBN e o fallback visual ainda pode ser substituído pela imagem quebrada. A importação de exemplo executa no evento interativo e para na primeira resposta falha.

## Goals / Non-Goals

**Goals:**
- Aplicar o contrato público da v8 mantendo Reflex, as cores e a aparência aprovada fora dos defeitos apontados.
- Centralizar observabilidade, concorrência, retries de leitura, mensagens e cache público no cliente/serviços existentes.
- Permitir que a pessoa continue uma importação parcialmente aplicada após revalidar o estado remoto.

**Non-Goals:**
- Alterar endpoints, schemas ou dados do Xano, publicar alterações remotas ou mudar a lista de livros.
- Criar persistência nova para cache ou fila de trabalho.
- Executar chamadas Open Library quando `BIBLIOTECA_SEM_REDE=1`.

## Decisions

- Corrigir as caixas externas dos controles da barra em `app.style`; spans de ícone/rótulo ficam neutros. O teste lê os estilos computados declarados pela aplicação para impedir cortes e encolhimento.
- A camada SVG gerada será sempre renderizada. A imagem real sobreposta terá `alt=""`, `aria-hidden` e classe estável; um único script global trata falha em captura e reconcilia imagens já quebradas após mutações.
- A resolução Open Library será um serviço assíncrono isolado, com cliente HTTP injetável, timeout de 3 s, User-Agent do aplicativo, comparação normalizada de títulos, cache com expiração e semáforo de três consultas. A página publica os dados e capas SVG antes de disparar a resolução como evento Reflex em segundo plano.
- O cliente Xano manterá semáforo global de três operações, retry apenas para GET transitório e registros em `logging` somente quando o diagnóstico estiver habilitado. Um `ContextVar` por carregamento agrega contagem de chamadas/falhas sem misturar sessões concorrentes.
- Cache público por processo guarda apenas catálogo e categorias por 60 s; mutações de catálogo invalidam antes e depois da tentativa para cobrir respostas incertas. Respostas autenticadas nunca entram nesse cache.
- Os carregadores das seis rotas usam `finally` para encerrar flags. A home calcula os indicadores a partir de leituras independentes e mantém resultados parciais. Falhas finais oferecem retry manual.
- A importação usará `@rx.event(background=True)` e atualizações de estado em blocos `async with self`; pausas e I/O ocorrem fora do lock. Como eventos de fundo Reflex não são uma fila durável, retomada é uma ação explícita que relê catálogo, categorias e exemplares para reconciliar cada passo e não duplicar gravações.
- Comparação do endpoint PATCH será estritamente leitura local: usar somente um pull de referência já disponível e um alvo remoto inequivocamente selecionado pelo Xano CLI. Se não houver pull correspondente ou destino confirmável, registrar a limitação sem acessar outros workspaces.

## Risks / Trade-offs

- [API pública lenta ou indisponível] → a capa SVG aparece primeiro e falhas são cacheadas por período menor; limite de três chamadas mantém a página responsiva.
- [Timeout após gravação confirmada] → reler catálogo e exemplares antes da repetição; nunca habilitar retry automático no cliente genérico para métodos de escrita.
- [Cache público temporariamente desatualizado] → invalidar em qualquer tentativa de mutação de catálogo e manter TTL curto de 60 s.
- [Diagnóstico expõe dados] → registrar apenas caminho relativo, metadados de transporte, chaves e status; nunca corpo, cabeçalho, token, URL base ou identidade.
- [Evento de fundo termina com a sessão/servidor] → oferecer continuidade na sessão existente e reconstruir progresso por leituras; não prometer execução durável após reinício do processo.

## Migration Plan

Não há migração de dados nem deploy remoto nesta Change. Aplicar e validar localmente, sincronizar as specs após os testes e arquivar somente após registrar os resultados do robô e as limitações visuais.

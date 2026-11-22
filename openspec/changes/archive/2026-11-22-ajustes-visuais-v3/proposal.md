# Proposal

## Why

Alguns controles visuais deixam ações primárias ilegíveis no modo escuro, os formulários precisam de alinhamento e tratamento de autofill consistentes, e o Acervo ainda usa uma lista pesada em vez da busca compacta solicitada. Também faltam feedback confiável nas ações administrativas, capas determinísticas por título e um seed seguro para preparar dados reais.

## What Changes

- Corrigir contraste e estados visuais de ações primárias, campos, tema, emojis, animações e capas.
- Simplificar o Acervo com busca, cadastro fechado por padrão, edição em painel único, paginação e ação de edição no catálogo/detalhe para staff.
- Diferenciar a desativação de título em fluxo confirmável com estado de processamento e feedback seguro.
- Gerar capas SVG determinísticas sem rede ou scripts externos e limitar o tamanho dos grids.
- Preparar um seed de cerca de 30 títulos em modo dry-run por padrão, sem aplicar dados ao Xano nesta Change.
- Arquivar a Change `refino-visual-biblioteca` por estar superada, sem sincronizar seus deltas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `frontend-foundation`: aparência, controles, animações, identidade visual com emojis e navegação responsiva.
- `catalog`: capas geradas, interface compacta do Acervo, ações administrativas com feedback e preparação do seed.

## Impact

- Frontend, estilos, testes e utilitário de capas em `biblioteca_mais_nova/`.
- Script novo `scripts/seed_catalogo_real.py` e documentação de seed.
- Diagnóstico e pendência documentais em `docs/publicacao-xano-pendente.md`, `docs/relatorio-noite.md` e `openspec/changes/validacao-remota-xano/tasks.md`.
- Nenhuma escrita, publicação ou exclusão no Xano real nesta sessão.

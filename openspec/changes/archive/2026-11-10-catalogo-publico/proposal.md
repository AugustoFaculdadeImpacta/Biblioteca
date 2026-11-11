# Proposal

## Why

Visitantes e estudantes ainda não conseguem consultar o acervo no app, embora a consulta pública seja a principal forma de descobrir livros disponíveis. Esta Change entrega a navegação e consulta de catálogo sem alterar o backend Xano.

## What Changes

- Adicionar uma página pública de catálogo com cards de títulos e uma página de detalhe por título.
- Permitir busca textual por título/autoria, filtro por categoria, filtro "somente disponíveis" e ordenação A-Z/Z-A calculados em memória no frontend.
- Exibir no detalhe a quantidade de exemplares disponíveis conforme os dados retornados pelos GETs existentes.
- Atualizar a navegação para que visitantes, estudantes e bibliotecários encontrem o catálogo, preservando o acesso administrativo atual.
- Usar exclusivamente GETs existentes; não criar nem alterar endpoints, tabelas ou dados no Xano nesta Change.

## Capabilities

### New Capabilities

### Modified Capabilities

- `catalog`: especificar consulta visual pública por lista e detalhe, disponibilidade agregada, busca, filtros, ordenação e acesso pela navegação.
- `frontend-foundation`: incluir o acesso ao catálogo na navegação compartilhada para todos os perfis.

## Impact

- Frontend Reflex: página inicial, cabeçalho, páginas e estado de consulta do catálogo, usando chamadas HTTP somente de leitura.
- Testes pytest com respostas mockadas e verificações de acessibilidade e navegação.
- Nenhuma alteração a `xano/`, APIs, schemas, dependências ou dados remotos.

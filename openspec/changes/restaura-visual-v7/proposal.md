# Proposal

## Why

A reformulação recente da home afastou a interface do modelo visual azul-marinho, serifado e espaçado que deve orientar o produto, enquanto algumas correções e funcionalidades posteriores precisam ser mantidas. Também há uma falha concreta nas pílulas de categoria do catálogo e falta uma forma administrativa, controlada e idempotente de incluir os livros de exemplo pelo site.

## What Changes

- Restaurar tokens dos dois temas, tipografia, cartões, cabeçalho, home, cartões de livro e rodapé com a aparência do modelo, preservando a busca global, as visões por perfil, os estados da home e os fluxos existentes.
- Colocar a indicação de visão do admin em uma faixa abaixo do cabeçalho e reorganizar o painel de Acessibilidade em linhas acessíveis, sem sobreposição.
- Corrigir as pílulas do catálogo para exibir contagens reais ou omiti-las quando ausentes.
- Compartilhar os 30 livros de exemplo entre o app e o script local e oferecer no Acervo uma prévia somente leitura e importação confirmada, sequencial e idempotente, exclusiva ao admin real.

## Capabilities

### New Capabilities

Nenhuma. A importação administra o mesmo catálogo existente e não introduz uma capacidade ou estrutura de dados independente.

### Modified Capabilities

- `frontend-foundation`: aparência global, cabeçalho e faixa de visão, painel de Acessibilidade, home e rodapé.
- `catalog`: cartões e pílulas de categoria, dados compartilhados dos livros de exemplo e importação administrativa pelo site.

## Impact

- Frontend Reflex em `biblioteca_mais_nova/biblioteca_mais_nova.py` e estilos e componentes de `biblioteca_mais_nova/`.
- Novo módulo de dados `biblioteca_mais_nova/seed_data.py` e adaptação de `scripts/seed_catalogo_real.py` para continuar como alternativa.
- Testes de CSS, navegação, catálogo e importação usando clientes simulados.
- Nenhuma alteração de schema ou endpoint Xano. A Change não executará escrita remota; a importação só poderá ocorrer por ação explícita de um admin autenticado no site.

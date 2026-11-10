# Proposal

## Why

O catálogo e a spec já definem busca, categoria, disponibilidade e ordenação separadamente, mas faltam critérios explícitos de combinação e categoria sem títulos; os testes não cobrem esses casos conjuntamente. Formalizar e fechar essa cobertura reduz regressões sem duplicar funcionalidades existentes.

## What Changes

- Especificar que busca por título/autoria, filtro de categoria, somente disponíveis e ordenação A-Z/Z-A podem ser combinados no catálogo público.
- Cobrir combinações de filtros, busca sem resultado e categoria sem títulos com testes automatizados.
- Preservar filtragem e ordenação em memória no Reflex, sem alterar endpoints ou dados do Xano.

## Capabilities

### New Capabilities

### Modified Capabilities
- `catalog`: documentar comportamento dos filtros públicos e resultados vazios.

## Impact

- OpenSpec: delta da capability `catalog`.
- Reflex: comportamento existente em `State.filtered_public_catalog`; mudanças de interface somente se os testes identificarem regressão de mensagem/estado vazio.
- Testes: `tests/test_catalog.py`, usando estado local, sem chamadas ou escritas ao Xano.

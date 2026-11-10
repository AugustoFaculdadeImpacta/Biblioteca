# Design

## Context

Consulte [proposal.md](./proposal.md) e a delta de [catalog](./specs/catalog/spec.md). A spec consolidada já cobre cada filtro individualmente. A implementação atual mantém texto, categoria, disponibilidade e ordenação no estado Reflex e calcula os resultados em memória; a página já apresenta um estado vazio acessível.

## Goals / Non-Goals

**Goals:**

- Fazer os cenários combinados e vazios serem regressões testáveis.
- Preservar a interface e os contratos HTTP existentes se as verificações confirmarem o comportamento atual.

**Non-Goals:**

- Alterar endpoints Xano, persistência, autenticação ou formato de respostas.
- Adicionar dependências ou reorganizar o estado de catálogo.

## Decisions

### Decisões tomadas por delegação (revisar)

- Nenhuma decisão delegada sobre admin, remoção ou reservas se aplica a esta Change. Busca por título/autoria e filtros combináveis preservam o comportamento já observado no catálogo.
- Categoria existente sem itens deve resultar em lista vazia e mensagem acessível, sem erro; essa é a interpretação conservadora de “categoria vazia”.

### Verificação do comportamento

Adicionar cobertura de estado Reflex que combina texto, categoria, somente disponíveis e ordenação no mesmo conjunto de dados; verificar busca sem correspondência, categoria sem itens e remoção isolada do filtro de categoria. Não alterar código de produção se esses testes passarem.

**Alternativa considerada:** reimplementar os filtros em serviços/API; rejeitada porque os GETs existentes já retornam os campos necessários e a ordenação deve continuar em memória.

## Risks / Trade-offs

- [Teste apenas dos filtros individuais não detectar regressão na combinação] → validar todas as condições no mesmo estado e confirmar o resultado ordenado.
- [Categoria vazia ser confundida com falha de rede] → verificar lista vazia e mensagem de resultado, mantendo `public_catalog_message` vazio.

## Migration Plan

Sem migração ou escrita Xano. Rodar os testes de catálogo, a suíte pytest, validação OpenSpec e compilação Reflex. Arquivar apenas após esses gates passarem.

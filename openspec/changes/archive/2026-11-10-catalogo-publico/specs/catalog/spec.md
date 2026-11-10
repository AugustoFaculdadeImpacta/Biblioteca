# Spec Delta

## ADDED Requirements

### Requirement: Interface pública apresenta títulos e disponibilidade
A interface MUST permitir que visitantes e estudantes consultem o catálogo público por lista e detalhe, sem autenticação, exibindo a quantidade de exemplares disponíveis informada pelo serviço.

#### Scenario: Consultar títulos públicos
- **WHEN** visitante ou estudante abre o catálogo
- **THEN** a interface apresenta os títulos retornados pela consulta pública em cards e permite abrir o detalhe de um título

#### Scenario: Consultar disponibilidade no detalhe
- **WHEN** visitante ou estudante abre o detalhe de um título
- **THEN** a interface apresenta a quantidade de exemplares disponíveis retornada pelo serviço, sem expor dados pessoais de estudantes

### Requirement: Busca, filtros e ordenação do catálogo são aplicados em memória
A interface MUST permitir refinar os títulos carregados sem enviar filtros ou ordenações adicionais ao backend.

#### Scenario: Buscar por texto
- **WHEN** pessoa informa um texto no campo de busca
- **THEN** a lista em memória é filtrada pelos campos de título e autoria retornados pelo catálogo

#### Scenario: Filtrar por categoria e disponibilidade
- **WHEN** pessoa seleciona uma categoria ou ativa "Somente disponíveis"
- **THEN** a lista em memória contém somente títulos associados à categoria selecionada e, quando aplicável, com quantidade disponível maior que zero

#### Scenario: Ordenar alfabeticamente
- **WHEN** pessoa seleciona A-Z ou Z-A
- **THEN** os títulos visíveis são ordenados em memória pelo título, respeitando a direção selecionada

#### Scenario: Catálogo sem resultados
- **WHEN** a busca ou os filtros não correspondem a nenhum título
- **THEN** a interface informa claramente que nenhum título corresponde aos critérios atuais

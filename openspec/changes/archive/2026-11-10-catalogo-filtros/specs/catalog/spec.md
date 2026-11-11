# Spec Delta

## MODIFIED Requirements

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

#### Scenario: Filtros combinados
- **WHEN** pessoa informa texto, seleciona uma categoria, ativa somente disponíveis e escolhe ordenação A-Z ou Z-A
- **THEN** a lista em memória contém somente títulos que atendem simultaneamente aos filtros e os ordena pelo título

#### Scenario: Categoria sem títulos correspondentes
- **WHEN** visitante seleciona uma categoria existente sem títulos correspondentes
- **THEN** a interface não exibe títulos, mantém os outros filtros utilizáveis e informa que nenhum título corresponde aos critérios atuais

#### Scenario: Remover filtro de categoria
- **WHEN** visitante seleciona novamente todas as categorias
- **THEN** a interface remove apenas o filtro de categoria e preserva busca, disponibilidade e ordenação

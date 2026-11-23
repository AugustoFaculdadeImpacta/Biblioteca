# catalog Delta

## ADDED Requirements

### Requirement: Seed real da livraria v6 contém 30 títulos
O seed MUST conter exatamente 30 títulos reais nas oito categorias aprovadas e MUST manter todas as escritas remotas restritas ao modo explícito `--apply`.

O catálogo público deve apresentar livros reais distribuídos nas oito categorias aprovadas.

#### Scenario: Carregamento do catálogo
- **WHEN** o catálogo público é listado
- **THEN** os títulos usam ISBN-13 reais, descrição própria e até três exemplares por título

#### Scenario: Filtro por categoria
- **WHEN** o visitante escolhe uma das oito categorias
- **THEN** somente títulos associados aparecem na grade

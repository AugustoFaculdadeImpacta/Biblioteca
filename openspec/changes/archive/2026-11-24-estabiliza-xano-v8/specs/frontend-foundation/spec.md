# Spec Delta

## ADDED Requirements

### Requirement: Realce da barra cobre cada controle por inteiro
Links e botões da barra MUST aplicar fundo, raio e foco visível na caixa externa inteira, mantendo emoji e rótulo em uma única linha sem encolher ou cortar conteúdo.

#### Scenario: Realce ao apontar ou focar
- **WHEN** pessoa aponta ou navega por teclado até marca, link ou controle da barra
- **THEN** o realce e o foco abrangem o controle completo, inclusive emoji e rótulo

#### Scenario: Navegação estreita
- **WHEN** os itens da barra excedem a largura disponível
- **THEN** o contêiner pode rolar horizontalmente, mas os itens não encolhem, não cortam conteúdo e não têm largura máxima artificial

#### Scenario: Conteúdo interno sem fundo
- **WHEN** um controle contém emoji e texto em spans
- **THEN** o fundo pertence ao link ou botão, e os spans internos permanecem transparentes

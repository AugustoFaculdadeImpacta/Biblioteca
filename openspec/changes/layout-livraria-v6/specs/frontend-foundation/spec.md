# frontend-foundation Delta

## ADDED Requirements

### Requirement: Cabeçalho da livraria v6 usa composição única
O sistema MUST renderizar um único cabeçalho por página e MUST usar links transparentes na navegação principal.

A interface deve apresentar um cabeçalho único por perfil, navegação por links e uma grade responsiva sem sobreposições.

#### Scenario: Desktop com perfil visitante
- **WHEN** o visitante abre uma rota pública em largura de pelo menos 64 rem
- **THEN** o cabeçalho usa uma única linha com logo, navegação, busca e ações

#### Scenario: Tela estreita
- **WHEN** a interface é renderizada em largura de 360 px
- **THEN** o cabeçalho usa logo e ações na primeira linha, navegação rolável na segunda e busca na terceira
- **AND** não renderiza botão hambúrguer

### Requirement: Hierarquia visual da livraria v6
Cada página MUST usar o contêiner principal compartilhado e MUST evitar sobreposição horizontal ou vertical de conteúdo visível.

Cada página deve usar o contêiner de largura máxima e estilos consistentes de seção.

#### Scenario: Home
- **WHEN** o visitante abre `/`
- **THEN** vê banner, faixa de estatísticas, estante, novidades, categorias e instruções de reserva

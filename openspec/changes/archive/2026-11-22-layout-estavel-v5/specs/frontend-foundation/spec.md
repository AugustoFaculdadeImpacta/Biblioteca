# Spec Delta

## ADDED Requirements

### Requirement: Cabeçalho é estável e navegação não usa estilos de botão
O sistema MUST apresentar uma barra superior sticky não quebrável no desktop, com marca, navegação por perfil, ações de cabeçalho e rodapé textual sem vazamento de classes de ação.

#### Scenario: Cabeçalho desktop
- **WHEN** pessoa abre qualquer página em largura desktop
- **THEN** a barra fica fixa no topo, alinhada em uma linha, centralizada em largura máxima de 1200 px e não cresce verticalmente

#### Scenario: Navegação sem estilo de botão
- **WHEN** links de navegação são renderizados
- **THEN** usam `site-nav-link` sem `focus-demo-button`, `nav-logout` ou tipo de ação e mantêm contraste AA

#### Scenario: Navegação móvel
- **WHEN** viewport é menor ou igual a 48 rem
- **THEN** o botão móvel aparece, a navegação é exibida em painel abaixo e o nome da marca não é sobreposto

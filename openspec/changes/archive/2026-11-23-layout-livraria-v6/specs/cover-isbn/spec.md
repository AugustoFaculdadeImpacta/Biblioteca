# cover-isbn Delta

## ADDED Requirements

### Requirement: Resolução de capas da livraria v6
O sistema MUST resolver capas pela prioridade `capa_url`, índice ISBN, Open Library e fallback local.

Cada capa deve seguir a prioridade HTTPS do título, índice ISBN local, Open Library pelo ISBN e fallback gerado.

#### Scenario: Capa real disponível
- **WHEN** uma URL HTTPS ou ISBN válido está disponível
- **THEN** a capa real é exibida sobre o fallback

#### Scenario: Falha de carregamento
- **WHEN** a capa real não pode ser carregada
- **THEN** o elemento não deixa imagem quebrada visível

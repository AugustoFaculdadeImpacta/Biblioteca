# cover-isbn Specification

## Purpose
Definir a prioridade, normalização e fallback das capas bibliográficas sem baixar imagens para o repositório.

## Requirements

### Requirement: Capa bibliográfica usa somente fontes resolvíveis em runtime
O sistema MUST selecionar uma imagem real somente por HTTPS e MUST remover a imagem quebrada antes de revelar a capa gerada.

#### Scenario: ISBN disponível
- **WHEN** título possui ISBN-13 válido
- **THEN** a URL Open Library usa esse ISBN normalizado e mantém proporção 2:3

#### Scenario: Índice local conhecido
- **WHEN** resposta pública não traz ISBN
- **THEN** o sistema consulta um índice local normalizado por título e autoria antes da capa gerada

#### Scenario: Falha sem requisito externo no servidor
- **WHEN** o navegador tenta carregar uma capa
- **THEN** o servidor não faz download externo e `onerror` libera o fallback local

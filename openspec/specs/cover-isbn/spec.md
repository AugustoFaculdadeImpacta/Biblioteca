# cover-isbn Specification

## Purpose
Definir a prioridade, normalização e fallback das capas bibliográficas sem baixar imagens para o repositório.

## Requirements

### Requirement: Capa bibliográfica usa somente fontes resolvíveis em runtime
O sistema MUST manter a capa gerada visível sob a imagem real e buscar capas por título e primeira autoria no servidor, usando ISBN fornecido pelo título somente como fallback.

#### Scenario: ISBN disponível
- **WHEN** título possui ISBN-13 válido
- **THEN** a URL de capa de ISBN usa esse valor somente após a busca por título/autoria, preserva a proporção 2:3 e não substitui a base gerada

#### Scenario: Índice local conhecido
- **WHEN** resposta pública não traz ISBN e a rede está habilitada
- **THEN** o servidor consulta a Open Library por título e primeira autoria, escolhe o resultado com capa e título normalizado mais parecido e fornece a URL grande da capa

#### Scenario: ISBN informado pelo título
- **WHEN** a busca por título não encontra capa adequada e o título contém ISBN-13 válido
- **THEN** o ISBN normalizado pode ser usado como fallback antes da capa gerada

#### Scenario: Busca de capa com cache
- **WHEN** uma capa é resolvida ou uma busca falha
- **THEN** o resultado é mantido em cache por título/autoria normalizados por 24 horas ou 10 minutos, respectivamente

#### Scenario: Rede desabilitada ou indisponível
- **WHEN** `BIBLIOTECA_SEM_REDE=1` ou ocorre falha de rede na Open Library
- **THEN** nenhuma falha técnica é mostrada à pessoa e a capa gerada continua disponível

#### Scenario: Falha sem requisito externo no servidor
- **WHEN** uma consulta de metadados externa falha ou a imagem real não carrega no navegador
- **THEN** a falha é ignorada sem erro visível, a imagem real desaparece se necessário e a capa gerada continua disponível

#### Scenario: Capa acessível
- **WHEN** a capa é apresentada em cartão ou detalhe
- **THEN** o contêiner anuncia “Capa de «título»” e a imagem decorativa interna não duplica o nome acessível

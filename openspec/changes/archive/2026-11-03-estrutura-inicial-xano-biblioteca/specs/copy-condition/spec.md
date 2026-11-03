# Spec Delta

## Purpose

Definir o registro auditável de danos e perdas de exemplares e impedir que unidades comprometidas sejam consideradas disponíveis.

## ADDED Requirements

### Requirement: Bibliotecário registra condição de exemplar
O sistema MUST permitir a bibliotecários registrar dano ou perda com observação, instante e responsável autenticado associados ao exemplar.

#### Scenario: Dano registrado
- **WHEN** bibliotecário registra dano com observação para um exemplar
- **THEN** o sistema guarda o evento no histórico do exemplar e o torna indisponível

#### Scenario: Perda registrada
- **WHEN** bibliotecário registra perda com observação para um exemplar
- **THEN** o sistema guarda o evento no histórico do exemplar e o torna indisponível

#### Scenario: Usuário sem perfil bibliotecário
- **WHEN** estudante ou visitante tenta registrar condição
- **THEN** o backend recusa a operação sem alterar o exemplar ou seu histórico

### Requirement: Histórico de condição é preservado
O sistema MUST manter eventos de condição ligados ao exemplar e permitir consulta autorizada sem substituir registros anteriores.

#### Scenario: Consulta de histórico por bibliotecário
- **WHEN** bibliotecário consulta condição de exemplar
- **THEN** o sistema retorna os registros históricos associados, com instante, observação e responsável

#### Scenario: Consulta pública
- **WHEN** visitante consulta disponibilidade agregada do catálogo
- **THEN** exemplar danificado ou perdido não conta como disponível e detalhes internos do histórico não são expostos

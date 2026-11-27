# Spec Delta

## ADDED Requirements

### Requirement: Metadados de regras aceitam formatos do Xano
O cliente MUST aceitar metadados opcionais de atualização sem rejeitar uma configuração válida.

#### Scenario: Metadados em milissegundos e usuário numérico
- **WHEN** a resposta contém `atualizado_em` como inteiro em segundos ou milissegundos e `atualizado_por` como inteiro
- **THEN** a configuração é aceita e a data é normalizada para apresentação

#### Scenario: Metadados ausentes ou nulos
- **WHEN** `atualizado_em` ou `atualizado_por` é nulo, zero ou ausente
- **THEN** a configuração é aceita sem metadado correspondente

#### Scenario: Metadados textuais e campos extras
- **WHEN** a resposta contém data ISO, autor textual ou chaves extras
- **THEN** datas compatíveis e autor são preservados e campos extras são ignorados

#### Scenario: Regras obrigatórias continuam validadas
- **WHEN** qualquer um dos sete campos de regra tem valor ou tipo inválido
- **THEN** a resposta é rejeitada e o diagnóstico identifica o campo inválido

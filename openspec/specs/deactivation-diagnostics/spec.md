# deactivation-diagnostics Specification

## Purpose
Permitir diagnóstico seguro do PATCH de desativação em ambiente local sem registrar dados sensíveis.

## Requirements

### Requirement: Diagnóstico da desativação é opt-in
O aplicativo MUST registrar o PATCH de desativação no terminal somente quando `BIBLIOTECA_DIAGNOSTICO=1`.

#### Scenario: Variável desativada
- **WHEN** o ambiente não habilita o diagnóstico
- **THEN** nenhuma mensagem de desativação é registrada no terminal

#### Scenario: Variável habilitada
- **WHEN** usuário desativa um título com a variável habilitada
- **THEN** o terminal recebe método, caminho relativo, nomes das chaves, status, chaves da resposta e estado ativo antes e depois da releitura

#### Scenario: Dados sensíveis ausentes
- **WHEN** o diagnóstico é registrado
- **THEN** host, token, e-mail, senha e valores do corpo não aparecem na mensagem

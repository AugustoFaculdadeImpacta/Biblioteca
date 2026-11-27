# Spec Delta

## ADDED Requirements

### Requirement: Configuração da biblioteca usa cache curto invalidável
O cliente Xano MUST reutilizar a configuração da biblioteca por até 60 segundos e invalidá-la após gravação bem-sucedida.

#### Scenario: Configuração em cache
- **WHEN** a configuração é solicitada novamente dentro de 60 segundos
- **THEN** o cliente reutiliza o resultado em cache sem nova chamada

#### Scenario: Gravação invalida configuração
- **WHEN** gravação de configuração termina com sucesso
- **THEN** o cache da configuração é invalidado antes da próxima leitura

#### Scenario: Leitura respeita limitador
- **WHEN** cliente solicita configuração fora do cache
- **THEN** a chamada GET usa o cliente comum e respeita seu limitador, retries seguros e higienização de erros

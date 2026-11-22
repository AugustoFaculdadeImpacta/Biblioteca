# Spec Delta

## ADDED Requirements

### Requirement: Falhas ao solicitar reserva têm mensagens específicas
A interface MUST traduzir falhas conhecidas ao solicitar reserva em mensagens curtas em português com código identificador, sem revelar detalhes internos ou credenciais.

#### Scenario: Sessão expirada
- **WHEN** serviço recusa a reserva com HTTP 401
- **THEN** a interface mostra `[RES-401] Sua sessão expirou, entre de novo`

#### Scenario: Perfil sem permissão
- **WHEN** serviço recusa a reserva com HTTP 403
- **THEN** a interface mostra `[RES-403] Seu perfil não pode reservar`

#### Scenario: Recurso ou endpoint indisponível
- **WHEN** serviço responde HTTP 404 à solicitação
- **THEN** a interface mostra `[RES-404] Este recurso ainda não está disponível no servidor`

#### Scenario: Regra de negócio conflita com a reserva
- **WHEN** serviço responde HTTP 409 por limite ou duplicidade
- **THEN** a interface mostra `[RES-409]` e a mensagem de negócio segura correspondente ao limite ou à reserva já existente

#### Scenario: Erro do servidor
- **WHEN** serviço responde com código HTTP entre 500 e 599
- **THEN** a interface mostra `[RES-5XX] O servidor teve um problema (código 5xx)`

#### Scenario: Tempo esgotado
- **WHEN** a solicitação de reserva termina por timeout
- **THEN** a interface mostra `[RES-TIMEOUT] Sem resposta do servidor. Confira Minhas reservas antes de tentar de novo`

#### Scenario: Outros erros de comunicação
- **WHEN** ocorre falha diferente de status conhecido ou timeout
- **THEN** a interface mostra código curto e mensagem genérica segura, sem resposta bruta do serviço

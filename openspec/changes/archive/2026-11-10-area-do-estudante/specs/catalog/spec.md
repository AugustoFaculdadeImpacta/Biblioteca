# Spec Delta

## ADDED Requirements

### Requirement: Estudante inicia solicitação a partir do catálogo
A interface MUST permitir que estudante autenticado inicie o fluxo de empréstimo ou reserva de um título do catálogo, submetendo a decisão final de disponibilidade e elegibilidade ao backend.

#### Scenario: Há exemplar disponível no catálogo
- **WHEN** estudante autenticado abre o detalhe de título que informa exemplares disponíveis
- **THEN** a interface oferece solicitar empréstimo e envia a solicitação autenticada ao backend

#### Scenario: Não há exemplar disponível no catálogo
- **WHEN** estudante autenticado abre o detalhe de título sem exemplares disponíveis
- **THEN** a interface oferece entrar na fila de reserva pelo fluxo de solicitação autenticado

#### Scenario: Disponibilidade muda antes do envio
- **WHEN** disponibilidade ou elegibilidade muda entre a consulta do catálogo e o envio
- **THEN** a interface apresenta o resultado retornado pelo backend e não presume que a contagem previamente exibida ainda seja válida

#### Scenario: Visitante ou bibliotecário tenta iniciar o fluxo de estudante
- **WHEN** pessoa sem perfil estudante tenta enviar uma solicitação pelo catálogo
- **THEN** a interface bloqueia a ação e o backend continua responsável por recusar a operação não autorizada

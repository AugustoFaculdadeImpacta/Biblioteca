# Spec Delta

## MODIFIED Requirements

### Requirement: Elegibilidade da reserva é revalidada no backend
O sistema MUST verificar autenticação, perfil estudante, situação ativa do título e bloqueios vigentes antes de criar ou atender uma reserva.

#### Scenario: Estudante com empréstimo atrasado
- **WHEN** estudante com empréstimo vencido e não devolvido solicita reserva de título ativo
- **THEN** o backend recusa a solicitação sem alterar a fila

#### Scenario: Visitante ou bibliotecário sem contexto de estudante tenta reservar
- **WHEN** perfil não estudante envia uma solicitação de reserva
- **THEN** o backend recusa a operação

#### Scenario: Título desativado
- **WHEN** estudante tenta criar reserva para título inativo
- **THEN** o backend recusa a operação sem adicionar ou alterar itens da fila

## ADDED Requirements

### Requirement: Estudante abre detalhes do título reservado
A área pessoal MUST permitir que estudante abra os detalhes públicos do título associado à própria solicitação ou reserva, sem alterar o estado ou o prazo.

#### Scenario: Abrir detalhes de uma solicitação ou reserva
- **WHEN** estudante seleciona o título exibido em uma solicitação ou reserva própria
- **THEN** a interface abre a rota pública de detalhes do mesmo `titulo_id` e preserva o estado e o prazo apresentados na área pessoal

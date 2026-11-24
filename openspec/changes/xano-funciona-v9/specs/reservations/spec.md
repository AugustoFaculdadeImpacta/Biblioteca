# Spec Delta

## ADDED Requirements

### Requirement: A solicitação de reserva impede envios duplicados
A interface MUST bloquear nova submissão de reserva desde o início da tentativa até que as listas relacionadas terminem de recarregar.

#### Scenario: Tentativa de reserva pendente
- **WHEN** estudante inicia uma solicitação de reserva
- **THEN** o controle impede novo envio enquanto a escrita estiver pendente

#### Scenario: Escrita concluída e listas em atualização
- **WHEN** a escrita termina com sucesso, inclusive com corpo ilegível, e as listas ainda estão recarregando
- **THEN** o controle continua bloqueado até as listas terminarem de atualizar

#### Scenario: Listas atualizadas
- **WHEN** o recarregamento das listas relacionadas termina
- **THEN** uma nova solicitação pode ser iniciada conforme o estado atualizado

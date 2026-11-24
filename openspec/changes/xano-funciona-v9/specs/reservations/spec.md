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

#### Scenario: Escrita ilegível ainda não aparece nas listas
- **WHEN** a escrita recebe HTTP 2xx sem resposta interpretável e a releitura ainda não mostra a solicitação ou reserva
- **THEN** a interface não afirma que o pedido foi confirmado, mantém nova submissão bloqueada e oferece atualizar as listas antes de tentar novamente

#### Scenario: Escrita ilegível confirmada pela releitura
- **WHEN** a escrita recebe HTTP 2xx sem resposta interpretável e a releitura encontra a solicitação ou reserva do título
- **THEN** a interface confirma o resultado sem repetir a escrita e libera uma nova ação conforme o estado atualizado

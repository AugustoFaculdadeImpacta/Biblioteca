# Spec Delta

## ADDED Requirements

### Requirement: A solicitação de reserva impede envios duplicados
A interface MUST bloquear nova submissão de reserva desde o início da tentativa até que o resultado confirmado esteja refletido no estado local ou as listas relacionadas terminem de recarregar.

#### Scenario: Resposta POST confirma diretamente o pedido
- **WHEN** o POST retorna HTTP 2xx com um objeto contendo ID válido e `titulo_id` igual ao título solicitado
- **THEN** a interface confirma “Pedido enviado” e acrescenta o pedido ao estado local sem reler listas

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
- **WHEN** a escrita recebe HTTP 2xx sem resposta interpretável e as releituras limitadas ainda não mostram a solicitação ou reserva
- **THEN** a interface não afirma que o pedido foi confirmado, mantém nova submissão bloqueada e oferece atualizar as listas antes de tentar novamente

#### Scenario: Escrita ilegível confirmada pela releitura
- **WHEN** a escrita recebe HTTP 2xx sem resposta interpretável e a releitura encontra a solicitação ou reserva do título
- **THEN** a interface confirma o resultado sem repetir a escrita e libera uma nova ação conforme o estado atualizado

#### Scenario: Gravação fica visível após atraso
- **WHEN** a primeira leitura após uma escrita 2xx ilegível ainda não mostra a solicitação ou reserva
- **THEN** o sistema faz até duas releituras GET adicionais após 1,5 s e 4 s desde o POST, confirma somente quando encontra o registro correspondente e nunca repete a escrita

#### Scenario: Pedido visível na segunda leitura
- **WHEN** o POST retorna 2xx ilegível e a segunda releitura encontra o pedido para o título solicitado
- **THEN** a interface confirma “Pedido enviado” e libera a ação conforme os dados atualizados

#### Scenario: Pedido não aparece após três leituras
- **WHEN** o POST retorna 2xx ilegível e nenhuma das três leituras encontra o pedido
- **THEN** a interface mostra erro com referência, mantém o botão bloqueado e o terminal registra a ausência sem repetir POST

#### Scenario: Tentar de novo na página Reservas
- **WHEN** estudante aciona “Tentar de novo” após resultado incerto
- **THEN** o sistema somente relê solicitações e reservas, sem criar outro POST

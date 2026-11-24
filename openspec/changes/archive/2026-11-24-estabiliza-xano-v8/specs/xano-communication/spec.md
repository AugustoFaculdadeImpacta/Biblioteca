# Spec Delta

## Purpose

Estabelece comunicação previsível e diagnóstica entre o backend da Biblioteca e o Xano, limitando rajadas e repetindo somente leituras seguras.

## ADDED Requirements

### Requirement: Diagnóstico de chamadas Xano é opt-in e sanitizado
O backend MUST registrar detalhes operacionais de chamadas e resumos por carregamento de página somente quando `BIBLIOTECA_DIAGNOSTICO=1`.

#### Scenario: Diagnóstico desabilitado
- **WHEN** uma chamada ou carregamento termina sem a variável habilitada
- **THEN** nenhum registro diagnóstico é emitido

#### Scenario: Chamada concluída ou falha
- **WHEN** uma chamada ao Xano termina com o diagnóstico habilitado
- **THEN** o terminal registra método, caminho relativo sem host, status ou tipo de falha, duração, content-type, tamanho da resposta e número da tentativa

#### Scenario: Resumo do carregamento
- **WHEN** um carregamento de página termina com o diagnóstico habilitado
- **THEN** o terminal registra quantas chamadas ocorreram e quantas falharam

#### Scenario: Dados privados
- **WHEN** qualquer evento diagnóstico é registrado
- **THEN** token, autorização, URL base, e-mail, senha e valores de corpo não são registrados

### Requirement: Leituras repetem falhas transitórias com limite
O cliente MUST repetir somente GET em timeout, falha de conexão e respostas HTTP 429, 502, 503 ou 504, limitando as tentativas e respeitando `Retry-After` até dez segundos.

#### Scenario: Leitura com falha transitória
- **WHEN** GET recebe timeout, falha de conexão ou um dos status transitórios
- **THEN** tenta novamente no máximo três vezes, com espera crescente de 0,5 s, 1,5 s e 3 s, usando `Retry-After` quando presente e limitado a 10 s

#### Scenario: Escrita falha
- **WHEN** POST, PATCH ou DELETE recebe erro ou timeout
- **THEN** a chamada não é repetida automaticamente

#### Scenario: Falha persistente
- **WHEN** GET esgota as tentativas
- **THEN** a operação termina com erro sanitizado distinto de timeout e falha de conexão e preserva a causa real somente no diagnóstico opt-in

### Requirement: Respostas Xano têm mensagens públicas específicas
O backend MUST converter erros de comunicação e respostas incompatíveis em mensagens simples, distintas e sem conteúdo técnico sensível.

#### Scenario: Limite de requisições
- **WHEN** Xano retorna HTTP 429
- **THEN** a interface informa “O Xano limitou as requisições por alguns segundos. Aguarde um pouco e tente de novo.”

#### Scenario: Resposta HTTP não JSON
- **WHEN** uma resposta de erro contém uma página ou corpo que não é JSON
- **THEN** a interface informa “O Xano devolveu uma página de erro (código N).”

#### Scenario: JSON incompatível
- **WHEN** Xano retorna JSON em formato incompatível com o contrato solicitado
- **THEN** a interface informa “O Xano respondeu em formato inesperado.”

#### Scenario: Timeout e conexão
- **WHEN** uma chamada excede o tempo limite ou falha ao conectar
- **THEN** a interface apresenta mensagens diferentes para timeout e falha de conexão

### Requirement: Cliente limita concorrência e reutiliza dados públicos recentes
Chamadas simultâneas ao Xano MUST ser limitadas a três, e catálogo público e categorias MUST ser reutilizados por até 60 segundos no processo do backend.

#### Scenario: Limite de concorrência
- **WHEN** mais de três chamadas Xano são solicitadas simultaneamente no processo
- **THEN** somente três ficam em execução e as demais aguardam sua vez

#### Scenario: Reuso de dados públicos
- **WHEN** uma rota solicita catálogo ou categorias lidos há menos de 60 segundos
- **THEN** o backend reutiliza os dados em memória sem nova leitura ao Xano

#### Scenario: Invalidação administrativa
- **WHEN** uma escrita administrativa de catálogo termina
- **THEN** o cache público de catálogo e categorias é invalidado antes da próxima leitura

#### Scenario: Dados privados não são compartilhados
- **WHEN** uma rota solicita empréstimos, reservas ou contas
- **THEN** o resultado autenticado não é colocado no cache público compartilhado

### Requirement: Carregamentos de página sempre terminam em estado recuperável
Carregamentos de dados MUST terminar em sucesso ou erro visível, sempre encerrando o indicador de carregamento e oferecendo nova tentativa quando aplicável.

#### Scenario: Sucesso ou falha da leitura
- **WHEN** um carregamento de página termina ou falha
- **THEN** seu indicador de carregamento é encerrado em qualquer caminho de execução

#### Scenario: Erro após retries
- **WHEN** a leitura falha após as tentativas permitidas
- **THEN** a interface mostra mensagem clara e botão “Tentar de novo”, sem permanecer em “Carregando”

#### Scenario: Nova tentativa
- **WHEN** pessoa ativa “Tentar de novo”
- **THEN** a leitura correspondente é executada novamente com seu estado de carregamento atualizado

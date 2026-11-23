# Spec Delta

## ADDED Requirements

### Requirement: Execução local do Reflex funciona no Windows
O projeto MUST oferecer um fluxo documentado para iniciar frontend e backend Reflex no Windows com `reflex run`, sem editar manualmente a saída gerada nem reduzir as proteções do sistema operacional.

#### Scenario: Inicialização local completa
- **WHEN** desenvolvedor executa `reflex run` no ambiente Windows configurado conforme o projeto
- **THEN** frontend e backend iniciam e o navegador consegue carregar uma rota da aplicação e estabelecer a conexão de estado com o backend

#### Scenario: Configuração regenerada
- **WHEN** o Reflex recria seus arquivos de frontend gerados
- **THEN** o fluxo documentado continua iniciando a aplicação sem depender de edições manuais nesses arquivos

### Requirement: Falha de inicialização preserva o erro original
O projeto MUST encerrar os processos iniciados pela tentativa e apresentar a falha original de inicialização sem substituí-la por uma exceção secundária de limpeza.

#### Scenario: Frontend falha ao iniciar
- **WHEN** o processo frontend iniciado pelo comando Reflex termina antes de ficar disponível
- **THEN** o comando reporta a causa original, não gera uma exceção de processo inexistente durante a limpeza e não deixa subprocessos da tentativa em execução

# Spec Delta

## ADDED Requirements

### Requirement: Dados públicos permanecem disponíveis durante atualização
O sistema MUST exibir a última cópia conhecida do catálogo e das regras enquanto busca dados atualizados.

#### Scenario: Cópia temporária disponível
- **WHEN** home, catálogo ou detalhe inicia antes de completar a consulta remota e há cópia salva de até 24 horas
- **THEN** a interface mostra a cópia imediatamente e substitui os dados quando a atualização termina

#### Scenario: Atualização remota falha ou é limitada
- **WHEN** a consulta retorna erro, 429 ou excede o tempo esperado e existe cópia salva
- **THEN** a interface mantém os dados salvos e apresenta um aviso discreto de atualização ou última lista salva

#### Scenario: Sem cópia utilizável
- **WHEN** não há cópia salva disponível
- **THEN** a interface mantém o estado atual de carregamento e erro

### Requirement: Cópia pública persiste somente em armazenamento temporário
O backend MUST guardar catálogo, categorias e regras em memória e em arquivo JSON sob o diretório temporário do sistema, com instante da última atualização.

#### Scenario: Atualização de cópia
- **WHEN** uma consulta pública recebe dados válidos
- **THEN** a cópia em memória e o arquivo temporário são atualizados com os dados e a data

#### Scenario: Arquivo temporário
- **WHEN** o backend grava a cópia persistente
- **THEN** o arquivo fica em `tempfile.gettempdir()` e nunca dentro do repositório

### Requirement: Pré-carga pública ocorre uma vez
O backend MUST iniciar uma única pré-carga de catálogo, categorias e regras no startup ou na primeira visita.

#### Scenario: Inicialização do servidor
- **WHEN** o servidor inicia ou recebe sua primeira visita
- **THEN** dispara uma pré-carga pública única sem bloquear a resposta inicial

### Requirement: Abertura de página limita e mede consultas
Cada rota MUST executar uma rodada de consultas independentes em paralelo sob o limitador, sem aguardar capas ou conteúdo não essencial.

#### Scenario: Consultas independentes
- **WHEN** uma página precisa de várias listas independentes
- **THEN** inicia uma única rodada paralela e não duplica carregadores para a mesma abertura

#### Scenario: Medição diagnóstica
- **WHEN** `BIBLIOTECA_DIAGNOSTICO=1` e uma página conclui sua abertura
- **THEN** o terminal registra a rota, quantidade de chamadas e tempo até mostrar dados

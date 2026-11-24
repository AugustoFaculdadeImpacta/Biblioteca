# Spec Delta

## ADDED Requirements

### Requirement: Leituras de listas autenticadas toleram variações de formato por registro
O sistema MUST interpretar listas de respostas autenticadas sem rejeitar registros válidos por campos extras, opcionais ou formatos de valor aceitos.

#### Scenario: Lista simples ou embrulhada
- **WHEN** uma leitura de lista recebe uma lista ou um objeto com lista em `items`, `result`, `data`, `results` ou `records`
- **THEN** a interface interpreta os registros da lista e ignora campos desconhecidos

#### Scenario: Valores compatíveis
- **WHEN** um registro contém identificador inteiro ou numérico em texto, data ISO ou numérica em segundos/milissegundos, booleano `true`/`false`, `1`/`0` ou `"true"`/`"false"`, ou texto opcional nulo
- **THEN** a interface normaliza esses valores; datas `null` e `0` significam ausência de data, e campos opcionais ausentes resultam em `None`

#### Scenario: Registro ilegível
- **WHEN** um registro não pode ser interpretado sem invalidar os demais
- **THEN** somente esse registro é ignorado, a lista é exibida e informa “N registros não puderam ser lidos”

#### Scenario: Topo ou identificador inválido
- **WHEN** a resposta não contém uma lista no topo nem em um envelope aceito, ou não há identificador para o registro
- **THEN** a leitura apresenta erro de formato inesperado em vez de fabricar dados

### Requirement: Escritas 2xx com corpo ilegível preservam o resultado da operação
O sistema MUST tratar escrita HTTP 2xx com resposta ilegível como concluída com aviso, atualizar as listas relacionadas e nunca repetir a escrita automaticamente.

#### Scenario: Escrita concluída sem resposta interpretável
- **WHEN** POST ou PATCH termina com status 2xx e o corpo não pode ser interpretado
- **THEN** a interface informa sucesso com aviso para conferir a lista atualizada e recarrega os dados relacionados

#### Scenario: Escrita não concluída
- **WHEN** POST ou PATCH termina com status 4xx/5xx ou falha de transporte
- **THEN** a interface apresenta erro e não apresenta confirmação de sucesso

#### Scenario: Escrita incerta não é repetida
- **WHEN** uma escrita termina sem corpo interpretável
- **THEN** nenhuma repetição automática de POST ou PATCH é iniciada

### Requirement: Diagnóstico no site respeita sessão, perfil e privacidade
O sistema MUST oferecer a usuários autenticados um relatório somente leitura que execute apenas consultas públicas ou autorizadas ao próprio perfil.

#### Scenario: Chamadas permitidas por perfil
- **WHEN** usuário autenticado solicita o diagnóstico
- **THEN** estudante consulta somente seus empréstimos, pedidos e reservas; bibliotecário consulta as listas de equipe e o acervo administrativo permitidos ao perfil; admin também consulta listas de bibliotecários; todos consultam catálogo e categorias públicas, usando a própria sessão

#### Scenario: Resultado estrutural sem valores
- **WHEN** uma chamada de diagnóstico retorna
- **THEN** a tabela mostra nome, status HTTP, duração, tipo do topo, quantidade de registros, nomes e tipos dos campos do primeiro registro e resultado da validação com campos problemáticos e motivo

#### Scenario: Relatório copiável sanitizado
- **WHEN** usuário copia o relatório
- **THEN** o texto inclui os resultados estruturais e não inclui valores de campos, e-mail, identificadores pessoais, token, URL do Xano ou dados persistidos

#### Scenario: Falha de chamada diagnóstica
- **WHEN** uma chamada retorna erro HTTP ou resposta não JSON
- **THEN** o diagnóstico registra o status e a condição de formato sem expor o corpo da resposta nem valores sensíveis

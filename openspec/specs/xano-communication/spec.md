# xano-communication Specification

## Purpose

Estabelece comunicação previsível e diagnóstica entre o backend da Biblioteca e o Xano, limitando rajadas e repetindo somente leituras seguras.

## Requirements

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

### Requirement: Leituras de listas autenticadas toleram variações de formato por registro
O sistema MUST interpretar listas de respostas autenticadas sem rejeitar registros válidos por campos extras, opcionais ou formatos de valor aceitos.

#### Scenario: Lista simples ou embrulhada
- **WHEN** uma leitura de lista recebe uma lista ou um objeto com lista em `items`, `result`, `data`, `results` ou `records`
- **THEN** a interface interpreta os registros da lista e ignora campos desconhecidos

#### Scenario: Valores compatíveis
- **WHEN** um registro contém identificador inteiro ou numérico em texto, data ISO ou numérica em segundos/milissegundos, booleano `true`/`false`, `1`/`0` ou `"true"`/`"false"`, ou texto opcional nulo
- **THEN** a interface normaliza esses valores; datas e IDs opcionais `null` e `0` significam ausência (`None`), IDs obrigatórios continuam positivos, campos opcionais ausentes resultam em `None`, e estados textuais não reconhecidos são preservados sem descartar o registro

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

#### Scenario: Erro estrutural identifica o campo
- **WHEN** uma resposta 2xx contém um registro incompatível com o contrato
- **THEN** o log sanitizado indica índice do registro, campo e motivo em um único bloco por chamada, com duração medida e ação/perfil da sessão quando disponíveis

### Requirement: Leituras pessoais reduzem chamadas redundantes
O sistema MUST compartilhar GETs idênticos simultâneos e reutilizar por até 20 segundos as listas autenticadas de empréstimos, solicitações e reservas da mesma sessão. Qualquer escrita autenticada MUST invalidar essas respostas em cache; um GET 2xx estruturalmente incompatível MUST NOT ser repetido.

#### Scenario: Carregadores simultâneos
- **WHEN** carregadores da mesma sessão solicitam simultaneamente a mesma lista pessoal
- **THEN** todos recebem o resultado da mesma requisição HTTP

#### Scenario: Cache pessoal
- **WHEN** a mesma sessão solicita a mesma lista novamente dentro de 20 segundos
- **THEN** o cliente reutiliza a resposta sem outra chamada HTTP

#### Scenario: Escrita invalida as listas pessoais
- **WHEN** a sessão realiza uma escrita autenticada
- **THEN** as listas pessoais em cache dessa sessão são invalidadas antes da próxima leitura

#### Scenario: Lista 2xx incompatível
- **WHEN** um GET recebe HTTP 2xx com estrutura incompatível
- **THEN** a falha é registrada sem repetir a chamada HTTP

### Requirement: Chamadas ao Xano respeitam uma janela deslizante global
O sistema MUST compartilhar por host um limitador assíncrono configurável de oito requisições por 20 segundos por padrão, com espera máxima de 25 segundos e prioridade para escritas e leituras acionadas pelo usuário.

#### Scenario: Janela excedida
- **WHEN** 20 chamadas simultâneas usam o mesmo host
- **THEN** no máximo oito são admitidas em cada janela deslizante configurada

#### Scenario: Resposta 429
- **WHEN** o Xano responde 429
- **THEN** todas as chamadas do host são pausadas até o fim da janela mais um segundo, somente GET é repetido uma vez e escrita não é repetida

#### Scenario: Prioridade
- **WHEN** uma escrita ou leitura acionada pelo usuário espera ao lado de carregamento em segundo plano
- **THEN** a escrita e a leitura acionada pelo usuário são admitidas antes do trabalho em segundo plano

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

### Requirement: Contratos de catálogo e circulação publicados correspondem às definições locais aprovadas
As definições Xano publicadas para catálogo, solicitações de empréstimo e reservas MUST corresponder aos arquivos locais aprovados, sem alterar objetos ou dados fora do escopo confirmado para a publicação.

#### Scenario: Desativação de título
- **WHEN** bibliotecário ou admin autorizado envia `PATCH /catalogo/titulos/{titulo_id}` com `ativo=false`
- **THEN** o endpoint persiste `ativo=false`, sua resposta inclui o identificador e o estado, e `GET /admin/acervo` retorna o título com `titulo.ativo=false`

#### Scenario: Confirmação de solicitação depois da escrita
- **WHEN** estudante envia `POST /solicitacoes-emprestimo` para um título elegível
- **THEN** o pedido persistido fica visível em `GET /minhas/solicitacoes` com estado `pendente` ou `em_reserva`, ou a reserva associada fica visível em `GET /minhas/reservas` com estado `aguardando` ou `ofertada`, vinculada ao mesmo `titulo_id`

#### Scenario: Criação e consulta direta de reserva
- **WHEN** estudante autorizado cria uma reserva por `POST /reservas`
- **THEN** a reserva persistida fica visível em `GET /minhas/reservas` para o mesmo estudante e título, com estado permitido pelo fluxo

#### Scenario: Publicação delimitada no workspace autorizado
- **WHEN** as definições são publicadas após confirmação do workspace `151966`, da branch `v1` marcada como live e do ambiente
- **THEN** somente `titulo.xs`, `reserva.xs`, `titulos_id_PATCH.xs`, `admin/acervo_GET.xs`, `solicitacoes_POST.xs`, `minhas_solicitacoes_GET.xs`, `minhas_GET.xs` e `reservas_POST.xs` são sincronizados, e a conferência posterior confirma essas versões sem importar registros ou variáveis de ambiente

### Requirement: Falhas Xano são rastreáveis e sanitizadas
O backend MUST escrever no stderr um bloco de diagnóstico para cada falha de transporte, status HTTP de erro, resposta 2xx ilegível ou resultado inesperado, salvo quando `BIBLIOTECA_LOG_ERROS=0`. Sucessos MUST permanecer silenciosos, exceto quando `BIBLIOTECA_DIAGNOSTICO=1`.

#### Scenario: Falha HTTP ou de transporte
- **WHEN** uma chamada Xano falha com 4xx/5xx, timeout ou erro de conexão
- **THEN** o stderr contém referência, horário, ação, perfil, método e caminho sem host, status e duração, content-type, tamanho, chaves enviadas e corpo recebido sanitizado, com flush imediato

#### Scenario: Resposta ilegível ou resultado inesperado
- **WHEN** a chamada retorna 2xx ilegível, ou a releitura esperada não confirma a operação
- **THEN** o stderr identifica o resultado e usa a mesma referência exibida na interface

#### Scenario: Higienização do diagnóstico
- **WHEN** conteúdo contém autorização, token, senha ou e-mail
- **THEN** nenhum segredo ou e-mail é registrado; valores do corpo enviado são omitidos, exceto o booleano `ativo`

#### Scenario: Desligar logs de falha
- **WHEN** `BIBLIOTECA_LOG_ERROS=0`
- **THEN** blocos de falha deixam de ser escritos, sem alterar o resultado funcional das chamadas

#### Scenario: Erro inesperado em evento Reflex
- **WHEN** manipulador de evento do backend lança exceção não prevista
- **THEN** o handler do Reflex registra traceback higienizado no stderr e preserva o tratamento padrão da exceção

### Requirement: Mensagens de ação relacionam interface e diagnóstico
Mensagens de erro apresentadas após ações MUST terminar com a referência do diagnóstico correspondente. Mensagens de 4xx retornadas pelo Xano podem ser apresentadas quando curtas e livres de e-mail e números longos.

#### Scenario: Erro de botão
- **WHEN** uma ação iniciada por botão falha
- **THEN** a mensagem visível termina com `(ref. XXXXX)` usando a mesma referência do bloco do terminal

#### Scenario: Detalhe curto e seguro do Xano
- **WHEN** um 4xx inclui mensagem de até 140 caracteres sem e-mail ou sequência numérica longa
- **THEN** a interface mostra essa mensagem em português simples junto da referência

### Requirement: Diagnóstico de desativação identifica o valor persistido
O sistema MUST enviar `ativo` como booleano JSON e fornecer evidência sanitizada do valor enviado, da resposta e da releitura do acervo.

#### Scenario: Desativação
- **WHEN** usuário autorizado confirma desativação
- **THEN** o corpo contém `ativo: false` booleano; a releitura confirma `ativo=false` ou o diagnóstico registra enviado, resposta e releitura para localizar a divergência

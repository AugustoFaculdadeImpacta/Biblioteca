# Diagnóstico da comunicação com o Xano

## Logs no terminal

Blocos de falha são registrados no `stderr` por padrão. Defina
`BIBLIOTECA_LOG_ERROS=0` no ambiente do processo backend para desligá-los.
Registros de chamadas bem-sucedidas permanecem desligados por padrão e podem
ser habilitados com `BIBLIOTECA_DIAGNOSTICO=1`. Os logs vão somente para o
terminal do backend; nunca são mostrados na interface.

Cada tentativa registra método, caminho relativo sem query string, status HTTP
ou tipo da falha, duração, tipo de conteúdo, tamanho da resposta, número da
tentativa e classe da exceção de transporte, quando houver. O corpo e os
cabeçalhos da resposta, parâmetros de consulta, URL de origem, token, e-mail e
senha não são registrados. Blocos de falha incluem uma referência para
correlacionar o terminal com a mensagem apresentada após uma ação. Ao terminar
um carregamento de página, é emitido um resumo com a rota, o total de tentativas
ao Xano e quantas falharam.

Rotas instrumentadas:

| Rota | Identificador do resumo |
| --- | --- |
| Início | `home` |
| Catálogo público | `catalogo` |
| Diagnóstico pelo Perfil | `perfil_diagnostico` |
| Detalhe do título | `detalhe` |
| Reservas do estudante | `reservas` |
| Acervo | `acervo` |
| Gestão de bibliotecários | `contas` |
| Reservas administrativas | `reservas_admin` |
| Empréstimos administrativos | `emprestimos_admin` |

Chamadas feitas por carregadores aninhados são contabilizadas no carregamento
externo, evitando resumos duplicados para uma única navegação.

## Auditoria de chamadas por rota

Cada abertura de página deve iniciar no máximo quatro leituras HTTP. Chamadas
acionadas explicitamente pelo usuário, como o diagnóstico do Perfil, não fazem
parte dessa contagem. Respostas 2xx incompatíveis são registradas como erro de
formato e nunca causam repetição HTTP.

| Rota | Leituras feitas na abertura | Dados pessoais | Reuso/cancelamento |
| --- | --- | --- | --- |
| `/` | catálogo público e categorias (até 2) | Nenhum carregamento pessoal ou administrativo automático | catálogo/categorias reutilizados por 60 s |
| `/catalogo` | catálogo público e categorias (até 2) | Nenhum | catálogo/categorias reutilizados por 60 s |
| `/catalogo/<id>` | título público e categorias (até 2) | Nenhum | categorias reutilizadas por 60 s; pendência termina em `finally` |
| `/perfil` | nenhuma chamada automática (0); “Testar conexão” é acionado pelo usuário | Token próprio somente nas leituras privadas; admin inclui contas bibliotecárias | relatório estrutural temporário, sem valores nem persistência |
| `/reservas` | empréstimos, pedidos e reservas próprios e catálogo para nomes (até 4) | Somente com token de estudante ou admin em visão estudante | cache autenticado de 20 s por sessão; falha encerra `pending` |
| `/admin/acervo` | categorias e acervo administrativo (até 2) | Somente com sessão administrativa/bibliotecária | categorias públicas reutilizadas por 60 s |
| `/admin/bibliotecarios` | contas bibliotecárias (1) | Somente com sessão admin | sem cache autenticado |
| `/admin/reservas` e `/admin/emprestimos` | pedidos, reservas, empréstimos e acervo administrativo (até 4) | Somente com sessão bibliotecária/admin | pendência encerrada em `finally` |

Uma mutação administrativa de título, categoria ou exemplar invalida os caches
públicos antes da próxima leitura. Navegar entre rotas públicas reutiliza
catálogo e categorias durante até 60 segundos no processo. Dados pessoais,
autorizados por token ou perfil, nunca entram no cache público compartilhado.

As listas autenticadas de empréstimos, solicitações e reservas são reutilizadas
por até 20 segundos somente para a mesma sessão e o mesmo host. A chave usa
HMAC do token, sem armazená-lo em texto claro; GETs idênticos simultâneos
compartilham uma requisição HTTP. Qualquer escrita autenticada invalida o cache
daquela sessão antes da chamada, inclusive quando a resposta da escrita for
incerta.

## Diagnóstico somente leitura pelo Perfil

Em `/perfil`, uma pessoa autenticada pode acionar “Testar conexão”. A ação não
faz gravações e envia o token da sessão somente às leituras privadas permitidas
ao perfil:

- Estudante: catálogo e categorias públicos, além de empréstimos, solicitações
  e reservas próprias.
- Bibliotecário: catálogo e categorias públicos, acervo e listas operacionais
  administrativas permitidas ao perfil.
- Admin: as mesmas leituras operacionais e, adicionalmente, a lista de contas
  bibliotecárias.

A tabela informa consulta, status HTTP, duração, tipo do topo JSON, quantidade
de registros, nomes e tipos dos campos do primeiro registro, validação,
campos problemáticos, motivo e referência do log quando houver. O relatório
copiável contém somente esses metadados; não inclui valores dos campos, e-mails,
identificadores pessoais, token, corpo da resposta nem URL do Xano. Respostas
HTTP recusadas e corpos não JSON mostram apenas o status e a condição, sem
reproduzir o conteúdo recebido.

## Comparação local do PATCH de desativação

O arquivo local [xano/api/default/catalogo/titulos_id_PATCH.xs](../xano/api/default/catalogo/titulos_id_PATCH.xs)
declara `bool ativo?` na entrada. Quando recebe valor, adiciona `ativo` ao mapa
`dados_atualizacao`, passa esse mapa ao `db.patch titulo` e devolve
`ativo: $titulo_atualizado.ativo`. O cliente envia `ativo` no corpo quando a
operação o fornece e a interface compara o valor da resposta com uma releitura
do acervo. A comparação foi feita contra a cópia remota local de referência já
existente; não foi feito novo pull nem escrita remota. A análise e os passos
manuais estão em [xano-correcao-ativo.md](./xano-correcao-ativo.md).

## Concorrência e repetição

O cliente limita a três as chamadas Xano simultâneas por processo/event loop.
Somente `GET` é repetido automaticamente em timeout, falha de conexão e
respostas HTTP 429, 502, 503 ou 504. Uma resposta 2xx com formato incompatível
não é repetida. A chamada inicial pode ser seguida de até três repetições, com
esperas de 0,5 s, 1,5 s e 3 s. Um cabeçalho `Retry-After` substitui a espera
correspondente e é limitado a 10 s. O tempo de espera ocorre fora do limite de
concorrência. `POST`, `PATCH` e `DELETE` nunca são repetidos automaticamente.

Além desse limite de concorrência, o processo mantém uma janela deslizante
por host do Xano. O padrão é oito requisições em 20 segundos,
configurável por `BIBLIOTECA_XANO_LIMITE_REQ` e
`BIBLIOTECA_XANO_JANELA_S`. Chamadas aguardam em uma fila assíncrona com
espera máxima de 25 segundos; escritas têm prioridade sobre leituras e uma
leitura acionada pelo usuário tem prioridade sobre trabalho em segundo plano.
Ao receber 429, todas as chamadas daquele host entram em pausa até o fim da
janela mais um segundo. Somente uma releitura `GET` tenta novamente; escritas
nunca são repetidas.

## Mensagens apresentadas

- HTTP 429: “O Xano limitou as requisições por alguns segundos. Aguarde um pouco
  e tente de novo.”
- Resposta de erro que não é JSON: “O Xano devolveu uma página de erro (código
  N).”
- JSON incompatível com o contrato: “O Xano respondeu em formato inesperado.”
- Timeout e falha de conexão apresentam mensagens distintas.

Falhas de rede são registradas somente por classe de exceção; o texto original
da exceção não é incluído porque pode conter a origem da API ou dados da
requisição.

# Diagnóstico da comunicação com o Xano

## Ativação

O diagnóstico fica desligado por padrão. Para habilitá-lo, defina
`BIBLIOTECA_DIAGNOSTICO=1` somente no ambiente do processo backend. As mensagens
vão para o terminal; nunca são mostradas na interface. Remova a variável para
desabilitar os registros.

Cada tentativa registra método, caminho relativo sem query string, status HTTP
ou tipo da falha, duração, tipo de conteúdo, tamanho da resposta, número da
tentativa e classe da exceção de transporte, quando houver. O corpo e os
cabeçalhos da resposta, parâmetros de consulta, URL de origem, token, e-mail e
senha não são registrados. Ao terminar um carregamento de página, é emitido um
resumo com a rota, o total de tentativas ao Xano e quantas falharam.

Rotas instrumentadas:

| Rota | Identificador do resumo |
| --- | --- |
| Início | `home` |
| Catálogo público | `catalogo` |
| Detalhe do título | `detalhe` |
| Reservas do estudante | `reservas` |
| Acervo | `acervo` |
| Gestão de bibliotecários | `contas` |
| Reservas administrativas | `reservas_admin` |
| Empréstimos administrativos | `emprestimos_admin` |

Chamadas feitas por carregadores aninhados são contabilizadas no carregamento
externo, evitando resumos duplicados para uma única navegação.

## Auditoria de chamadas por rota

| Rota | Leituras feitas na abertura | Dados pessoais | Reuso/cancelamento |
| --- | --- | --- | --- |
| `/` | catálogo público e categorias; consulta pessoal apenas para estudante autenticado ou dados operacionais somente de visão bibliotecária | Empréstimos, pedidos e reservas somente com sessão própria | catálogo/categorias reutilizados por 60 s; indicadores independentes |
| `/catalogo` | catálogo público e categorias | Nenhum | catálogo/categorias reutilizados por 60 s |
| `/catalogo/<id>` | título público e categorias | Nenhum | categorias reutilizadas por 60 s; pendência termina em `finally` |
| `/reservas` | empréstimos, pedidos e reservas próprios; catálogo para nomes | Somente com token de estudante ou admin em visão estudante | sem cache autenticado; falha encerra `pending` |
| `/admin/acervo` | categorias e acervo administrativo | Somente com sessão administrativa/bibliotecária | categorias públicas reutilizadas por 60 s; acervo autenticado não é cacheado |
| `/admin/bibliotecarios` | contas bibliotecárias | Somente com sessão admin | sem cache autenticado |
| `/admin/reservas` | fila administrativa, reservas, empréstimos e acervo | Somente com sessão bibliotecária/admin | acervo autenticado não é cacheado; pendência encerrada em `finally` |

Uma mutação administrativa de título, categoria ou exemplar invalida os caches
públicos antes da próxima leitura. Navegar entre rotas públicas reutiliza
catálogo e categorias durante até 60 segundos no processo. Dados pessoais,
autorizados por token ou perfil, nunca entram nesse cache compartilhado.

## Comparação local do PATCH de desativação

O arquivo local [xano/api/default/catalogo/titulos_id_PATCH.xs](../xano/api/default/catalogo/titulos_id_PATCH.xs)
declara `bool ativo?` na entrada. Quando recebe valor, adiciona `ativo` ao mapa
`dados_atualizacao`, passa esse mapa ao `db.patch titulo` e devolve
`ativo: $titulo_atualizado.ativo`. O cliente envia `ativo` no corpo quando a
operação o fornece e a interface compara o valor da resposta com uma releitura
do acervo. Não foi feito pull remoto nem acesso a outro workspace para
confrontar uma referência externa; não havia destino inequívoco confirmado.

## Concorrência e repetição

O cliente limita a três as chamadas Xano simultâneas por processo/event loop.
Somente `GET` é repetido automaticamente, em timeout, falha de conexão e
respostas HTTP 429, 502, 503 ou 504. A chamada inicial pode ser seguida de até
três repetições, com esperas de 0,5 s, 1,5 s e 3 s. Um cabeçalho `Retry-After`
substitui a espera correspondente e é limitado a 10 s. O tempo de espera ocorre
fora do limite de concorrência. `POST`, `PATCH` e `DELETE` nunca são repetidos
automaticamente.

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

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

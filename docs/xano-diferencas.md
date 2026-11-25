# Diferenças entre as definições Xano locais e publicadas

## Destino e método

- Consulta feita em 2026-11-24 com Xano CLI 1.3.4.
- Workspace confirmado: `151966` (`Augusto's Workspace`).
- Branch: `v1`, única branch listada e marcada como live.
- Host e grupo da `XANO_API_BASE_URL` foram comparados localmente com `docs/xano-workflow.md`; os valores não são reproduzidos aqui.
- `preferences.allow_push` retornou `false`.
- O pull trouxe somente definições, sem registros ou variáveis de ambiente. A cópia local de referência, fora do repositório, foi reduzida às oito definições comparadas; metadados e objetos não relacionados foram removidos.

## Comparação dos oito objetos aprovados

| Definição local | Objeto no pull | Diferença observada |
| --- | --- | --- |
| [`titulo.xs`](../xano/table/titulo.xs) | `table/titulo.xs` | O export live contém `auth = false`, ausente no arquivo local. O dry-run não propôs atualização para a tabela. A equivalência desse atributo não foi validada pelo Xano Developer MCP. |
| [`reserva.xs`](../xano/table/reserva.xs) | `table/reserva.xs` | O export live contém `auth = false`, ausente no arquivo local. Os campos e índices são os mesmos, com diferenças de formatação. O dry-run não propôs atualização. |
| [`titulos_id_PATCH.xs`](../xano/api/default/catalogo/titulos_id_PATCH.xs) | `api/biblioteca/catalogo/titulos/titulo_id_PATCH.xs` | Diferenças de formatação; a regra de `ativo`, PATCH e as validações de desativação aparecem iguais no diff textual. O dry-run não propôs atualização. |
| [`acervo_GET.xs`](../xano/api/default/admin/acervo_GET.xs) | `api/biblioteca/admin/acervo_GET.xs` | O export live explicita `return = {type: "list"}` em consultas e usa bloco de código no append; o arquivo local usa a forma compacta. Dry-run propôs atualização. |
| [`solicitacoes_POST.xs`](../xano/api/default/emprestimos/solicitacoes_POST.xs) | `api/biblioteca/solicitacoes_emprestimo_POST.xs` | O export live não contém as verificações locais de solicitação/reserva ativa duplicada. Há também diferença na expressão de associação de exemplares. Dry-run propôs atualização. |
| [`minhas_solicitacoes_GET.xs`](../xano/api/default/emprestimos/minhas_solicitacoes_GET.xs) | `api/biblioteca/minhas/solicitacoes_GET.xs` | O arquivo local ordena por `solicitada_em` descendente; o export live não contém essa ordenação. Apesar da diferença textual, o dry-run não propôs atualização. |
| [`minhas_GET.xs`](../xano/api/default/reservas/minhas_GET.xs) | `api/biblioteca/minhas/reservas_GET.xs` | A lógica de consulta e formatação do prazo aparece equivalente; as diferenças observadas são de formatação. O dry-run não propôs atualização. |
| [`reservas_POST.xs`](../xano/api/default/reservas/reservas_POST.xs) | `api/biblioteca/reservas_POST.xs` | Diferenças de formatação/nome da query e na expressão de associação de exemplares. O dry-run não propôs atualização. |

## Resultado e bloqueios

- O dry-run em modo parcial propôs somente duas atualizações: `admin/acervo GET` e `solicitacoes-emprestimo POST`.
- Um segundo dry-run com `--sync`, usando uma pasta contendo somente os oito arquivos aprovados, também mostrou duas atualizações e listou 105 objetos remotos fora dessa pasta. Não foi usado `--delete`; nenhum objeto remoto foi removido.
- Em nova conferência, o dry-run com staging exatamente nos caminhos publicados (`api/biblioteca/...` e `table/...`) também propôs somente `admin/acervo GET` e `solicitacoes-emprestimo POST`. O mapeamento do grupo, portanto, não resolveu as outras diferenças que o diff textual mostra.
- O preview parcial não inclui as diferenças textuais da ordenação de `minhas/solicitacoes` nem os atributos `auth = false` das tabelas. Não é seguro afirmar que a publicação delimitada resolveria todas as diferenças sem validar a interpretação dessas definições.
- As chamadas ao Xano Developer MCP para documentação/validação XanoScript falharam na inicialização. Não foi possível validar esses arquivos pelo MCP.
- Nenhum push foi feito. Com `allow_push=false`, a publicação direta não foi confirmada como permitida; a preferência não foi alterada e não houve fallback para sandbox.
- Não foram executadas chamadas HTTP de escrita nem testes com contas ou dados reais.

## Revalidação do fluxo de confirmação (2026-11-24)

- O pull live declara `POST /solicitacoes-emprestimo` (`query "solicitacoes-emprestimo" verb=POST`) com entrada `titulo_id`; a resposta é o registro `$solicitacao_resultado`.
- O pull live declara `GET /minhas/solicitacoes` (`query "minhas/solicitacoes" verb=GET`) e retorna diretamente a lista `$solicitacoes`.
- O pull live declara `GET /minhas/reservas` (`query "minhas/reservas" verb=GET`) e retorna diretamente a lista `$resultado`.
- O Reflex envia `{"titulo_id": <id>}` no POST e consulta exatamente os dois caminhos GET acima. Os parsers usam `titulo_id` e `estado`, aceitando `pendente`/`em_reserva` para solicitações e `aguardando`/`ofertada` para reservas. Não foi encontrada divergência estática de método, caminho ou nomes de campos usados na confirmação.
- As definições remotas mostram retorno direto de registros/listas; isso não comprova o corpo de uma chamada real. Nenhuma escrita ou leitura de registros reais foi executada. O cenário reproduzido pelos testes é a primeira leitura não encontrar o registro ainda: o Reflex anteriormente fazia só essa leitura imediata e mantinha a solicitação incerta.
- A definição local de `solicitacoes_POST.xs` tem verificações contra solicitação/reserva ativa duplicada que não aparecem na versão live. A definição local de `minhas_solicitacoes_GET.xs` ordena por `solicitada_em` descendente, enquanto a live não ordena. Essas diferenças devem ser revisadas para publicação; não explicam por si só a confirmação atrasada.

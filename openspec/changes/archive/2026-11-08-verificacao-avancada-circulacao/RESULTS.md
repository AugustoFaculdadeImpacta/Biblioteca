# Resultados da verificação avançada

## Resumo executivo

Verificação concluída no workspace `151966`, branch `v1` live, com achados de comportamento no backend. Os cenários foram executados individualmente; as falhas observadas são resultado da verificação, não falhas pendentes do runner.

| Cenário | Resultado observado | Conclusão |
|---|---|---|
| Atraso | Revalidado na Change de correção com empréstimo criado pela rota de negócio, atualização somente de `vence_em` e GET confirmando vencimento passado; solicitação HTTP 200 e resposta com objeto de solicitação | Achado confirmado; não é falso positivo exclusivo da fixture direta da Metadata API. O GET expôs `devolvido_em=0` mesmo antes da mutação, exigindo análise do sentinel/semântica Xano |
| Limite de empréstimo | Revalidado na Change de correção: duas retiradas concorrentes HTTP 200/200, com empréstimos criados pela rota de negócio | Achado confirmado: limite de um empréstimo ativo não é protegido contra concorrência |
| FIFO | Reproduzido na Change de correção: consulta ordenada; oferta HTTP 500 (`ERROR_FATAL`) | Achado confirmado; mensagem e trace não foram registrados |
| Concorrência | Último exemplar HTTP 200/403; geração de tombo HTTP 200/200, dois códigos distintos | Passou nos invariantes observados |
| Expiração/reoferta | Não chamada: a oferta elegível vencida não pôde ser confirmada após a falha na oferta FIFO | Processador global bloqueado pelo pré-check, sem alteração global |

Após cada invocação, a limpeza individual foi confirmada com GET 404. A contagem paginada final, revalidada pela Metadata API, foi `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0` e `usuario=2`.

## Achados para correção

1. **Atraso:** a primeira verificação usou um empréstimo criado diretamente pela Metadata API, cujo `devolvido_em` apareceu como `0`; esses testes isolados são classificados como fixtures inadequadas para afirmar a semântica de `null`. A Metadata API também retornou `0` após POST e PUT com JSON `null`. Na revalidação, um empréstimo criado pela rota de retirada já apresentava `devolvido_em=0` antes da mutação; após PUT somente de `vence_em` (epoch-ms vencido), a solicitação foi aceita (HTTP 200) e retornou objeto de solicitação. Portanto, o achado não é falso positivo exclusivo da fixture direta e permanece confirmado. Antes da correção, esclarecer se `0` é o sentinel Xano de campo não preenchido ou timestamp efetivamente gravado, e alinhar a condição de elegibilidade à semântica confirmada.
2. **Limite de empréstimo ativo:** duas retiradas concorrentes para o mesmo estudante foram aceitas (HTTP 200/200), inclusive na repetição com empréstimos criados pelas rotas de negócio, indicando ausência de exclusão mútua/revalidação atômica efetiva no backend.
3. **FIFO:** a consulta da fila respeitou a ordem criada, e a oferta foi reproduzida como HTTP 500 (`ERROR_FATAL`) em fixture isolada. A reconciliação registrou que a ordenação FIFO foi removida no remoto; corrigir a ordenação e a falha da oferta. Mensagem e trace não foram registrados.

Esses três achados ficam fora do escopo desta verificação e devem ser tratados na Change planejada `corrigir-regras-circulacao`. Nenhuma correção foi aplicada aqui.

## Estado

Apply aprovado pelo usuário após confirmação de backup/export e rotação do `swagger.token`. Pré-check completo via Metadata API passou. O usuário autorizou criar, atualizar e excluir individualmente registros somente nas seis tabelas especificadas, preservando integralmente os dois usuários preexistentes.

## Pré-check somente leitura pela Metadata API

A documentação oficial confirma:

- `GET /workspace/{workspace_id}/branch` para confirmar a branch e o indicador live.
- `GET /workspace/{workspace_id}/table` para resolver IDs de tabelas pelo nome.
- `GET /workspace/{workspace_id}/table/{table_id}/content?page={page}&per_page={per_page}` para listar registros paginados; data source `live` é o padrão documentado no header `x-data-source`.

Referências oficiais: [branches](https://docs.xano.com/xano-features/metadata-api/instance_api/retrieve_all_branches_in_a_workspace), [tabelas](https://docs.xano.com/xano-features/metadata-api/instance_api/retrieve_all_tables_in_a_workspace_with_optional_filtering_and_pagination), [conteúdo paginado de tabela](https://docs.xano.com/xano-features/metadata-api/instance_api/retrieve_paginated_records_from_a_table).

O pré-check consultou todas as páginas de `reserva`, `emprestimo`, `solicitacao_emprestimo`, `usuario` e `exemplar` no workspace `151966`/branch `v1` live. IDs vieram da listagem GET atual de tabelas; os registros foram processados em memória e não foram impressos nem gravados.

### Resultado

Cobertura completa confirmada: branch `v1` é live, IDs das cinco tabelas foram resolvidos pela Metadata API e todas as páginas foram lidas. Somente contagens agregadas:

| Tabela | Registros |
|---|---:|
| `reserva` | 0 |
| `emprestimo` | 0 |
| `solicitacao_emprestimo` | 0 |
| `usuario` | 2 |
| `exemplar` | 0 |

| Estado crítico | Contagem |
|---|---:|
| Reservas ofertadas vencidas | 0 |
| Empréstimos ativos | 0 |
| Solicitações pendentes | 0 |
| Reservas ofertadas sem expiração classificável | 0 |

**Gate do pré-check: PASSOU.** Nenhum nome, e-mail, token ou valor de registro foi incluído neste resultado.

### Revalidação antes das fixtures

Uma nova leitura GET integral confirmou `v1` live, todas as seis tabelas autorizadas presentes e nenhuma página pendente. Totais: `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `usuario=2`, `exemplar=0`, `titulo=0`. Ofertas vencidas/não classificáveis, empréstimos ativos e solicitações pendentes: todos `0`. Gate: PASSOU. IDs das tabelas e usuários preexistentes permaneceram somente em memória.

## Autorizações para registros de teste

A documentação oficial consultada confirma:

- Criação individual: `POST /workspace/{workspace_id}/table/{table_id}/content`.
- Atualização individual: `PUT /workspace/{workspace_id}/table/{table_id}/content/{content_id}`.
- Exclusão individual: `DELETE /workspace/{workspace_id}/table/{table_id}/content/{content_id}`.
- Verificação individual: `GET /workspace/{workspace_id}/table/{table_id}/content/{content_id}`, com HTTP 404 após exclusão.
- O tipo Password do Xano não armazena texto puro; signup recebe o valor da senha e a plataforma o armazena criptografado.

Referências oficiais: [criar registro](https://docs.xano.com/xano-features/metadata-api/instance_api/create_a_new_record_in_the_table), [atualizar registro](https://docs.xano.com/xano-features/metadata-api/instance_api/update_a_specific_record_by_id), [excluir registro](https://docs.xano.com/xano-features/metadata-api/instance_api/delete_a_specific_record_by_id), [consultar por ID](https://docs.xano.com/xano-features/metadata-api/instance_api/retrieve_a_specific_record_by_id), [listar grupos de API](https://docs.xano.com/xano-features/metadata-api/instance_api/retrieve_a_list_of_api_groups_inside_of_a_workspace_use_the_optional_filtering_and_sorting_parameters_for_more_granular_returns), [OpenAPI de um grupo](https://docs.xano.com/xano-features/metadata-api/instance_api/get_the_openapi_specification_for_an_api_group_returns_the_complete_swagger_json_for_all_endpoints), [tipo Password](https://docs.xano.com/the-database/database-basics/field-types).

A Metadata API GET identificou o grupo `Biblioteca` em `v1` e confirmou no OpenAPI do grupo as rotas usadas nos cenários: `/auth/login`, `/solicitacoes-emprestimo`, `/reservas`, `/admin/solicitacoes/{solicitacao_id}/retirada`, `/admin/reservas/ofertar-proxima`, `/admin/reservas/processar-expiradas` e `/admin/exemplares`. A URL base foi mantida em memória; nenhum campo `swagger.token` foi consultado, exibido ou salvo.

## Limpeza das fixtures interrompida anteriormente

- O pré-check imediatamente antes das fixtures passou: `v1` live; `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`; ofertas vencidas, empréstimos ativos e solicitações pendentes: `0`.
- Três usuários sintéticos autenticaram com sucesso: `usuario/19` (bibliotecário), `usuario/20` e `usuario/21` (estudantes). Tokens e senhas permaneceram em memória; nenhum e-mail, nome ou segredo foi registrado.
- Também foram criados e registrados `titulo/5`, `exemplar/5` e `emprestimo/5`.
- A mutação de `vence_em` em `emprestimo/5` não foi confirmada por GET; nenhum cenário de negócio foi executado.
- Na retomada, a limpeza foi executada sequencialmente, somente para os seis IDs autorizados, com dois segundos entre chamadas e espera crescente de 3, 6, 12, 24, 48 e até 60 segundos para HTTP 429.
- Resultados: DELETE HTTP 200 seguido de GET HTTP 404 para `emprestimo/5`, `exemplar/5`, `titulo/5`, `usuario/19`, `usuario/20` e `usuario/21`. Nenhum outro ID foi alvo de DELETE.
- Leitura paginada completa após a limpeza confirmou: `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`. A limpeza foi confirmada e os dois usuários originais permanecem.

## Diagnóstico da mutação `vence_em`

- Na primeira tentativa, o runner não registrou separadamente o status do PUT, o status do GET nem o valor lido. A falha exata de confirmação naquela tentativa não pode ser determinada retrospectivamente; não há evidência para atribuí-la ao formato do timestamp, ao método HTTP ou ao rate limit.
- A repetição isolada enviou `vence_em` como inteiro Unix epoch em milissegundos por PUT. Resultado sanitizado: PUT HTTP 200; GET HTTP 200; tipo lido `System.Int64`; comparação anterior ao instante atual: verdadeira. Isso confirma que o formato, PUT e leitura funcionaram na repetição.
- A Metadata API documenta `PUT` para atualizar um registro específico; PATCH não é o método documentado para essa rota.
- O runner registra separadamente os status e o tipo lido, normaliza epoch-ms e somente prossegue após GET 200 e comparação temporal aprovada. Também aplica pausas e backoff crescente em 429.
- Referências: [Timestamp do Xano](https://docs.xano.com/the-database/database-basics/field-types) e [PUT de atualização individual da Metadata API](https://docs.xano.com/xano-features/metadata-api/instance_api/update_a_specific_record_by_id).

## Execução dos cenários e runner

O runner [run-advanced-circulation-scenario.ps1](../../../scripts/run-advanced-circulation-scenario.ps1) exige exatamente um argumento `-Scenario` (`atraso`, `limite`, `fifo` ou `concorrencia`), aplica pausas e backoff crescente para HTTP 429, registra IDs à medida que cria fixtures e limpa/verifica registros individualmente. Cada cenário deve ser executado em uma invocação separada; ele não encadeia cenários.

O arquivo não contém valores de token, senhas, e-mails pessoais ou endereços de e-mail literais: obtém a credencial da CLI em memória (`xano profile token`), monta o endereço sintético em tempo de execução e não grava credenciais. Para repetir um cenário autorizado, na raiz do repositório:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\scripts\run-advanced-circulation-scenario.ps1 -Scenario atraso
```

Substitua `atraso` por exatamente um entre `limite`, `fifo` ou `concorrencia`. O runner executa gravações no workspace live `151966/v1`; não o execute para simples consulta nem execute vários cenários em sequência sem confirmar a limpeza de cada invocação.

- Fuso de `ofertada_em`: não foi possível avaliar; a oferta FIFO falhou antes da etapa de expiração/reoferta.
- Pré-check do cenário `atraso`: branch `v1` live; contagens-base `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`; estados críticos `0`. PASSOU.
- Fixtures criadas e posteriormente removidas: `usuario/22`, `titulo/6`, `exemplar/6`, `emprestimo/6`, `solicitacao_emprestimo/5` e `reserva/7`.
- Mutação diagnóstica de `vence_em`: valor enviado em epoch-ms; PUT HTTP 200; GET HTTP 200; tipo retornado `System.Int64`; comparação anterior ao instante atual: verdadeira. A falha da tentativa anterior não foi reproduzida.
- Resultado da regra: `/solicitacoes-emprestimo` respondeu HTTP 200, embora se esperasse rejeição por atraso; `/reservas` respondeu HTTP 403. O processamento da solicitação também criou a reserva `reserva/7` como efeito colateral.
- A limpeza automática confirmou DELETE HTTP 200 e GET HTTP 404 para `emprestimo/6`, `solicitacao_emprestimo/5`, `exemplar/6`, `titulo/6` e `usuario/22`. A reserva relacionada não foi registrada pela primeira versão do runner; ela foi identificada por `usuario_id=22` e `titulo_id=6`, removida individualmente como `reserva/7` (DELETE HTTP 200, GET HTTP 404).
- Contagens paginadas após a limpeza manual da reserva: `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`; IDs dos dois usuários originais: `4` e `5`, preservados.
- A repetição do cenário de atraso foi concluída pelo runner corrigido; detalhes sanitizados e limpeza individual aparecem abaixo.
- Pré-check do cenário `atraso`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/23` (usuario sintetico estudante).
- Fixture registrada: `titulo/7` (titulo sintetico atraso).
- Fixture registrada: `exemplar/7` (exemplar sintetico atraso).
- Fixture registrada: `emprestimo/7` (emprestimo sintetico atraso).
- Diagnóstico vence_em: envio numérico epoch-ms; método PUT HTTP 200; GET HTTP 200; tipo lido=System.Int64; comparação anterior ao instante atual=True.
- Fixture registrada: `solicitacao_emprestimo/6` (solicitacao inesperada pela API).
- Fixture registrada: `reserva/8` (reserva vinculada a solicitacao do cenario).
- Achado atraso: solicitação HTTP 200, reserva HTTP 403; bloqueio esperado não foi confirmado em ambas.
- Limpeza confirmada: `reserva/8`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `emprestimo/7`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/6`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/7`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/7`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/23`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Primeira tentativa isolada de `concorrencia`: a disputa do último exemplar produziu exatamente uma retirada aceita (HTTP 200/403). O runner então falhou por conversão de tipo ao correlacionar exemplares da disputa de código. DELETE individual e GET 404 foram confirmados para todas as fixtures, com contagens finais corretas.
- Segunda tentativa isolada de `concorrencia`: ambos os exemplares criados foram identificados pelos IDs das respostas, mas uma guarda do runner exigiu também encontrá-los na listagem por `titulo_id` e interrompeu o cenário. Todas as fixtures foram removidas individualmente e as contagens finais confirmadas.
- Ajuste do runner: consolidar IDs retornados e IDs encontrados por listagem, e ler `codigo_tombo` diretamente por GET individual. A repetição isolada foi concluída e está registrada no final deste arquivo.
- Cenário `atraso` terminou e suas fixtures foram removidas antes de qualquer outro cenário.
- Primeira tentativa isolada do cenário `limite`: o runner interrompeu ao correlacionar empréstimos por IDs devido a uma conversão de tipo (`System.Object[]` para inteiro). A API havia retornado dois empréstimos, cujos IDs foram registrados imediatamente. DELETE individual e GET 404 foram confirmados para todos os empréstimos e demais fixtures; as contagens finais voltaram a zero e `usuario=2`.
- Ajuste do runner: comparar as chaves de usuário/exemplar como texto, sem coerção de objetos retornados pela Metadata API. A repetição isolada aparece abaixo.
- Pré-check do cenário `limite`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/24` (usuario sintetico bibliotecario).
- Fixture registrada: `usuario/25` (usuario sintetico estudante).
- Fixture registrada: `titulo/8` (titulo sintetico limite-a).
- Fixture registrada: `titulo/9` (titulo sintetico limite-b).
- Fixture registrada: `exemplar/8` (exemplar sintetico limite-a).
- Fixture registrada: `exemplar/9` (exemplar sintetico limite-b).
- Fixture registrada: `solicitacao_emprestimo/7` (solicitacao sintetica limite-a).
- Fixture registrada: `solicitacao_emprestimo/8` (solicitacao sintetica limite-b).
- Fixture registrada: `emprestimo/8` (emprestimo criado pela retirada concorrente).
- Fixture registrada: `emprestimo/9` (emprestimo criado pela retirada concorrente).
- Cenário `limite` interrompido em 'execucao do cenario limite': Não é possível converter o valor "System.Object[]" do tipo "System.Object[]" no tipo "System.Int64".
- Limpeza confirmada: `emprestimo/8`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `emprestimo/9`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/7`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/8`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/8`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/9`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/8`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/9`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/24`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/25`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Pré-check do cenário `limite`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/26` (usuario sintetico bibliotecario).
- Fixture registrada: `usuario/27` (usuario sintetico estudante).
- Fixture registrada: `titulo/10` (titulo sintetico limite-a).
- Fixture registrada: `titulo/11` (titulo sintetico limite-b).
- Fixture registrada: `exemplar/10` (exemplar sintetico limite-a).
- Fixture registrada: `exemplar/11` (exemplar sintetico limite-b).
- Fixture registrada: `solicitacao_emprestimo/9` (solicitacao sintetica limite-a).
- Fixture registrada: `solicitacao_emprestimo/10` (solicitacao sintetica limite-b).
- Fixture registrada: `emprestimo/10` (emprestimo criado pela retirada concorrente).
- Fixture registrada: `emprestimo/11` (emprestimo criado pela retirada concorrente).
- Cenário limite concorrente: respostas HTTP 200/200; retiradas aceitas=2, esperado=1.
- Limpeza confirmada: `emprestimo/10`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `emprestimo/11`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/9`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/10`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/10`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/11`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/10`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/11`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/26`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/27`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Cenário `limite` terminou e suas fixtures foram removidas antes de qualquer outro cenário.
- Pré-check do cenário `fifo`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/28` (usuario sintetico bibliotecario).
- Fixture registrada: `usuario/29` (usuario sintetico estudante).
- Fixture registrada: `usuario/30` (usuario sintetico estudante).
- Fixture registrada: `titulo/12` (titulo sintetico fifo).
- Fixture registrada: `exemplar/12` (exemplar sintetico fifo).
- Fixture registrada: `reserva/9` (reserva sintetica fifo-a).
- Fixture registrada: `reserva/10` (reserva sintetica fifo-b).
- Cenário FIFO: consulta de fila retornou as duas reservas na ordem criada.
- Achado FIFO: oferta da próxima reserva HTTP 500 não selecionou a mais antiga.
- Cenário `fifo` interrompido em 'execucao do cenario fifo': Pré-check não encontrou exatamente uma oferta vencida de fixture.
- A mutação de `expira_em` atingiu a comparação temporal, mas a reserva permaneceu fora do estado `ofertada`; o pré-check encontrou zero ofertas vencidas elegíveis. O processador global não foi chamado.
- Limpeza confirmada: `reserva/9`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `reserva/10`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/12`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/12`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/28`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/29`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/30`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Pré-check do cenário `concorrencia`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/31` (usuario sintetico bibliotecario).
- Fixture registrada: `usuario/32` (usuario sintetico estudante).
- Fixture registrada: `usuario/33` (usuario sintetico estudante).
- Fixture registrada: `titulo/13` (titulo sintetico ultimo-exemplar).
- Fixture registrada: `exemplar/13` (exemplar sintetico ultimo-exemplar).
- Fixture registrada: `solicitacao_emprestimo/11` (solicitacao sintetica ultimo-a).
- Fixture registrada: `solicitacao_emprestimo/12` (solicitacao sintetica ultimo-b).
- Fixture registrada: `emprestimo/12` (emprestimo criado na disputa do exemplar).
- Concorrência do último exemplar: respostas HTTP 200/403; retiradas aceitas=1, esperado=1.
- Fixture registrada: `titulo/14` (titulo sintetico codigo-tombo).
- Fixture registrada: `exemplar/14` (exemplar criado na disputa de código).
- Fixture registrada: `exemplar/15` (exemplar criado na disputa de código).
- Cenário `concorrencia` interrompido em 'execucao do cenario concorrencia': Não é possível converter o valor "System.Object[]" do tipo "System.Object[]" no tipo "System.Int64".
- Limpeza confirmada: `emprestimo/12`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/11`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/12`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/13`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/14`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/15`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/13`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/14`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/31`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/32`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/33`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Pré-check do cenário `concorrencia`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/34` (usuario sintetico bibliotecario).
- Fixture registrada: `usuario/35` (usuario sintetico estudante).
- Fixture registrada: `usuario/36` (usuario sintetico estudante).
- Fixture registrada: `titulo/15` (titulo sintetico ultimo-exemplar).
- Fixture registrada: `exemplar/16` (exemplar sintetico ultimo-exemplar).
- Fixture registrada: `solicitacao_emprestimo/13` (solicitacao sintetica ultimo-a).
- Fixture registrada: `solicitacao_emprestimo/14` (solicitacao sintetica ultimo-b).
- Fixture registrada: `emprestimo/13` (emprestimo criado na disputa do exemplar).
- Concorrência do último exemplar: respostas HTTP 200/403; retiradas aceitas=1, esperado=1.
- Fixture registrada: `titulo/16` (titulo sintetico codigo-tombo).
- Fixture registrada: `exemplar/17` (exemplar criado na disputa de código).
- Fixture registrada: `exemplar/18` (exemplar criado na disputa de código).
- Cenário `concorrencia` interrompido em 'execucao do cenario concorrencia': Criação aceita sem exemplar identificável para limpeza.
- Limpeza confirmada: `emprestimo/13`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/13`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/14`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/16`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/17`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/18`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/15`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/16`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/34`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/35`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/36`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Pré-check do cenário `concorrencia`: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU.
- Fixture registrada: `usuario/37` (usuario sintetico bibliotecario).
- Fixture registrada: `usuario/38` (usuario sintetico estudante).
- Fixture registrada: `usuario/39` (usuario sintetico estudante).
- Fixture registrada: `titulo/17` (titulo sintetico ultimo-exemplar).
- Fixture registrada: `exemplar/19` (exemplar sintetico ultimo-exemplar).
- Fixture registrada: `solicitacao_emprestimo/15` (solicitacao sintetica ultimo-a).
- Fixture registrada: `solicitacao_emprestimo/16` (solicitacao sintetica ultimo-b).
- Fixture registrada: `emprestimo/14` (emprestimo criado na disputa do exemplar).
- Concorrência do último exemplar: respostas HTTP 200/403; retiradas aceitas=1, esperado=1.
- Fixture registrada: `titulo/18` (titulo sintetico codigo-tombo).
- Fixture registrada: `exemplar/20` (exemplar criado na disputa de código).
- Fixture registrada: `exemplar/21` (exemplar criado na disputa de código).
- Concorrência de tombo: respostas HTTP 200/200; exemplares criados=2; códigos distintos=2.
- Limpeza confirmada: `emprestimo/14`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/15`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `solicitacao_emprestimo/16`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/19`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/20`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `exemplar/21`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/17`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `titulo/18`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/37`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/38`; DELETE HTTP 200, GET HTTP 404.
- Limpeza confirmada: `usuario/39`; DELETE HTTP 200, GET HTTP 404.
- Contagens após limpeza do cenário: reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; usuários originais preservados=True.
- Cenário `concorrencia` terminou e suas fixtures foram removidas antes de qualquer outro cenário.

## Comandos executados

Cada cenário foi invocado separadamente, sempre após definir `PYTHONDONTWRITEBYTECODE=1`:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\scripts\run-advanced-circulation-scenario.ps1 -Scenario atraso
$env:PYTHONDONTWRITEBYTECODE='1'; .\scripts\run-advanced-circulation-scenario.ps1 -Scenario limite
$env:PYTHONDONTWRITEBYTECODE='1'; .\scripts\run-advanced-circulation-scenario.ps1 -Scenario fifo
$env:PYTHONDONTWRITEBYTECODE='1'; .\scripts\run-advanced-circulation-scenario.ps1 -Scenario concorrencia
```

## Síntese dos cenários

- Atraso: a alteração de `vence_em` foi confirmada, mas a solicitação retornou HTTP 200; a reserva retornou HTTP 403. A regra de bloqueio esperado não passou.
- Limite: duas retiradas concorrentes retornaram HTTP 200; esperava-se somente uma aceita. A regra de limite não passou.
- FIFO: a consulta retornou a ordem esperada; a oferta da próxima reserva respondeu HTTP 500. O pré-check não confirmou uma oferta vencida elegível; o processador global não foi chamado.
- Concorrência: disputa do último exemplar retornou HTTP 200/403, com uma retirada aceita; geração concorrente retornou HTTP 200/200, com dois exemplares e dois códigos distintos.
- As tentativas interrompidas por defeitos do runner foram repetidas após correção. Em cada invocação, a limpeza individual foi confirmada por GET 404 e as contagens finais foram `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`.
- Auditoria dos arquivos da Change e do runner: busca por endereços de e-mail literais e valores de token/segredo não encontrou correspondências; respostas brutas e dados pessoais não foram registrados. O runner monta apenas endereço sintético em memória.

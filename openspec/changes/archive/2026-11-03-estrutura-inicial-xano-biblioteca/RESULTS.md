# Resultados de Apply e verificação parcial

Data: 2026-10-27

## Destino e alterações aplicadas

- Workspace `151966` (`Augusto's Workspace`), instância `x8ki-letl-twmt.n7.xano.io`, branch `v1` (live).
- O usuário criou o grupo de API `Biblioteca`; os 28 arquivos locais foram atualizados para referenciá-lo.
- Dry-run combinado (`table/*.xs` + `api/**/*.xs`) considerou 37 arquivos e listou somente 28 endpoints da biblioteca para criação. Nenhuma tabela ou outro recurso apareceu no preview.
- Push delimitado concluiu com código 0: `Pushed 37 documents to workspace 151966`; 28 GUIDs de endpoint sincronizados.
- Não foram usados `--records`, `--env`, `--truncate`, `--sync` ou `--delete`. A branch é live; registros não foram manipulados.

## Evidência pós-push

- Pull somente de definições: 57 documentos.
- Encontradas 11 tabelas: as 9 da biblioteca (`categoria`, `condicao_exemplar`, `emprestimo`, `exemplar`, `reserva`, `solicitacao_emprestimo`, `titulo`, `titulo_categoria`, `usuario`) e as duas legadas (`event_log`, `user`).
- Comparação local/remota: 9/9 tabelas da biblioteca presentes com declarações de campos e referências coincidentes.
- Grupo `Biblioteca`: 28 endpoints; comparação local/remota encontrou correspondência exata de método e caminho para 28/28. Os grupos e endpoints legados `Authentication` e `Event Logs` continuam presentes.
- Smoke tests públicos: `GET /catalogo/categorias` e `GET /catalogo/titulos` retornaram HTTP 200 e `[]`.
- Não foram criados usuários, empréstimos ou reservas de teste. Nenhum registro de usuário ou variável/segredo foi lido via CLI.

## Verificações locais

- `python -m unittest discover -s xano\tests -v`: 9 testes passaram. A checagem de FK foi atualizada para a sintaxe atual `table = "nome"`.
- `openspec validate "estrutura-inicial-xano-biblioteca" --strict --json`: aprovado sem issues.
- `git diff --check`: aprovado.

## Limitações ainda abertas

1. Teste autenticado em 2026-10-27 antes da correção: cadastro e `GET /auth/me` retornaram HTTP 200, mas `POST /auth/login` retornou HTTP 500. Após o usuário publicar a correção do Xano AI, pull confirmou a alteração no endpoint remoto: senha de entrada como texto simples, sem filtros, e falhas convertidas em `accessdenied`. Repetição controlada: signup HTTP 200, perfil forçado para `estudante` apesar da tentativa de elevação, token imediato válido em `/auth/me`, login HTTP 200 com token e identidade correspondentes e `/auth/me` HTTP 200 após login. A conta sintética dessa execução foi removida pelo ID capturado. Um probe anterior não teve seu ID registrado e sua conta sintética pode permanecer; não foi consultada nem removida. Empréstimos, reservas/expiração, controles administrativos e condição do exemplar ainda não foram testados.
2. Ainda não se comprovou comportamento concorrente para limite de empréstimo, alocação de exemplar e FIFO, nem imutabilidade do código de tombo sob corrida.
3. A expiração é processada por endpoint manual. Não existe tarefa agendada nesta Change; o disparo automático precisa de decisão/implementação autorizada separada.
4. HTTP 200 nos endpoints públicos e importação XanoScript não comprovam os fluxos de negócio autenticados.

A Change não deve ser arquivada como Verify completo enquanto as limitações funcionais acima estiverem pendentes.

## Tentativa de execução da tarefa 5.2

Data: 2026-10-27

- Antes de qualquer dado de teste, o CLI confirmou workspace `151966` (`Augusto's Workspace`) e branch `v1` live. Nenhum registro ou variável foi lido, criado, alterado ou removido nesta tentativa.
- Plano proposto: usar os endpoints `POST /solicitacoes-emprestimo`, `GET /admin/solicitacoes`, `POST /admin/solicitacoes/{solicitacaoId}/retirada`, `POST /admin/emprestimos/{emprestimoId}/devolucao`, `POST /reservas`, `GET /admin/titulos/{tituloId}/fila-reservas`, `POST /admin/reservas/ofertar-proxima`, `POST /admin/reservas/processar-expiradas`, `POST /admin/exemplares/{exemplarId}/condicoes` e `GET /admin/exemplares/{exemplarId}/condicoes`, cobrindo empréstimo, reserva/FIFO, oferta/expiração, histórico de dano/perda e permissões estudante/bibliotecário. O catálogo público seria consultado em `GET /catalogo/titulos`.
- A execução foi bloqueada antes da criação de dados: o contrato publicado não oferece endpoints para remover os registros sintéticos, e o escopo documentado antes desta revisão vedava operações diretas em registros. Naquele escopo, não havia forma autorizada identificada de garantir a remoção apenas pelos IDs de teste.
- Também não foi disponibilizada uma credencial de bibliotecário para chamadas autenticadas. Nenhum segredo foi procurado em arquivos ou variáveis.
- Não houve falha funcional observada, pois os endpoints de negócio não foram chamados. A tarefa 5.2 permanece pendente; não arquivar até a revisão dos bloqueios e a execução/verificação dos cenários.
- Nenhuma tabela, endpoint ou definição Xano foi alterada. Não foi necessário gerar diff ou dry-run de alteração Xano.

## Verificacao segura 5.2 - 2026-11-03

### Cenarios e HTTP/status
- validacao do token de bibliotecario: HTTP 200.
- validacao do token de metadata e destino: HTTP 200.
- cadastro do estudante A: HTTP 200.
- validacao de identidade do estudante A com token de cadastro: HTTP 200.
- login do estudante A: HTTP 200.
- validacao de identidade do estudante A com token de login: HTTP 200.
- criacao do titulo de teste: HTTP 200.
- criacao do exemplar de teste: HTTP 200.
- solicitacao de emprestimo pelo estudante A: HTTP 200.
- retirada pelo bibliotecario: HTTP 200.
- cadastro do estudante B: HTTP 200.
- validacao de identidade do estudante B: HTTP 200.
- cadastro do estudante C: HTTP 200.
- validacao de identidade do estudante C: HTTP 200.
- reserva do estudante B enquanto A esta com o exemplar: HTTP 200.
- reserva do estudante C enquanto A esta com o exemplar: HTTP 200.
- devolucao do emprestimo de A e oferta da fila: HTTP 200.
- consulta das reservas do estudante B: HTTP 200.
- consulta das reservas do estudante C: HTTP 200.
- negacao de criacao de titulo por estudante: HTTP 403.
- registro de condicao danificado: HTTP 200.
- consulta do historico de condicoes: HTTP 200.

### IDs de fixtures (sem dados pessoais)
- estudante sintetico A: ID 16.
- titulo sintetico: ID 4.
- exemplar sintetico: ID 4.
- solicitacao sintetica: ID 4.
- emprestimo sintetico: ID 4.
- estudante sintetico B: ID 17.
- estudante sintetico C: ID 18.
- reserva sintetica B: ID 5.
- reserva sintetica C: ID 6.
- condicao sintetica danificado: ID 1.

### Limpeza
- condicao sintetica danificado, ID 1: GET previo 200, DELETE 200, GET de confirmacao 404.
- reserva sintetica B, ID 5: GET previo 200, DELETE 200, GET de confirmacao 404.
- reserva sintetica C, ID 6: GET previo 200, DELETE 200, GET de confirmacao 404.
- emprestimo sintetico, ID 4: GET previo 200, DELETE 200, GET de confirmacao 404.
- solicitacao sintetica, ID 4: GET previo 200, DELETE 200, GET de confirmacao 404.
- exemplar sintetico, ID 4: GET previo 200, DELETE 200, GET de confirmacao 404.
- titulo sintetico, ID 4: GET previo 200, DELETE 200, GET de confirmacao 404.
- estudante sintetico A, ID 16: GET previo 200, DELETE 200, GET de confirmacao 404.
- estudante sintetico B, ID 17: GET previo 200, DELETE 200, GET de confirmacao 404.
- estudante sintetico C, ID 18: GET previo 200, DELETE 200, GET de confirmacao 404.
- Todas as exclusoes foram confirmadas por GET individual com HTTP 404.

### Limitacoes
- Expiracao/reoferta, atraso, limite de emprestimo e concorrencia nao foram testados nesta execucao live. Foram separados para a Change `verificacao-avancada-circulacao`, que exige ambiente isolado; a verificacao segura desta Change foi concluida.

## Verify da correcao de GET /minhas/reservas

Data: 2026-11-03

- O historico oficial de requisicoes Xano para `GET /minhas/reservas` registrou HTTP 500 com `ERROR_FATAL` e a mensagem `Invalid entry: format_timestamp`.
- A definicao usava `format_timestamp` dentro de `db.query.eval`. O endpoint foi corrigido para consultar apenas as reservas do estudante autenticado e formatar `expira_em` somente quando nao nulo, mantendo os timestamps originais e a apresentacao em `America/Sao_Paulo`.
- O dry-run limitado a `table/*.xs` como contexto e `api/default/reservas/minhas_GET.xs` como alteracao mostrou exclusivamente `UPDATE query minhas/reservas GET`. O push usou os mesmos filtros; o pull posterior confirmou a definicao remota equivalente ao arquivo local. Nenhuma tabela foi alterada.
- O relatorio da execucao live segura acima registra HTTP 200 na consulta de reservas de B e C e confirma cada limpeza por GET individual HTTP 404 apos DELETE HTTP 200.
- Validacoes locais: `openspec validate "estrutura-inicial-xano-biblioteca" --strict` aprovado; `python -m unittest xano.tests.test_candidates -v` com 9 testes aprovados; `git diff --check` aprovado; `openspec status --change "estrutura-inicial-xano-biblioteca"` confirma os 4 artefatos completos.
- A verificacao segura desta Change foi concluida. Expiracao e reoferta, atraso, limite simultaneo de emprestimos e invariantes concorrentes foram separados para `verificacao-avancada-circulacao`, que exige ambiente isolado.

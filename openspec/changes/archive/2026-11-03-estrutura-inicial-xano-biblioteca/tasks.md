# Tasks

## 1. Fixar decisões e validar viabilidade técnica

- [x] 1.1 Confirmar pelo CLI o destino autorizado: workspace `151966`, branch `v1` live; não ler registros nem variáveis. O push explicitamente escopado confirmou `Augusto's Workspace` e a instância `x8ki-letl-twmt.n7.xano.io`. O metadado `allow_push: false` não impediu o push pelo CLI nesta conta; não foi usado para contornar uma falha de autorização.
- [x] 1.2 Registrar as decisões aprovadas: normalização/unicidade do e-mail sem alterar senha; título e autor(es) obrigatórios e metadados opcionais; código de tombo `EX-000001` único, imutável e gerado pelo servidor; oferta por 48 horas corridas desde associação, timestamps UTC e apresentação em `America/Sao_Paulo`; primeiro bibliotecário provisionado manualmente por operador autorizado. Não reabrir nem contradizer essas decisões.
- [x] 1.3 Avaliar importabilidade e garantias técnicas com as ferramentas/documentação Xano e registrar lacunas. Push/pull confirmaram importabilidade dos XS; `RESULTS.md` registra que concorrência e imutabilidade em runtime não foram provadas e que a expiração é manual, sem tarefa agendada nesta Change. Esta conclusão não afirma essas garantias como verificadas.
- [x] 1.4 Fixar o contrato de tabelas, relações e endpoints com as decisões aprovadas. Renovação, multas, regularização de perdas, cancelamento, exclusão/arquivamento como operação de API e aplicação Reflex ficam fora do escopo. Operações diretas em registros também ficam fora, exceto a criação e limpeza já concluídas de fixtures sintéticos da verificação segura.

## 2. Preparar e validar candidatos locais

- [x] 2.1 Preparar localmente todos os candidatos XanoScript para tabelas, relações e endpoints aprovados e contrato OpenAPI completo. Foram preparados candidatos para todas as 28 operações do OpenAPI, incluindo fluxos de empréstimo, reserva/oferta/expiração, exemplar e condição; cobertura de método/caminho conferida localmente.
- [x] 2.2 Validar importabilidade XanoScript e contratos estruturais locais. O import/pull do Xano aceitou os 28 endpoints; os 9 testes estruturais locais passaram e os smoke tests públicos de categorias/títulos retornaram HTTP 200 com listas vazias. Os fluxos autenticados seguros foram verificados em 5.2; cenários avançados pertencem a `verificacao-avancada-circulacao`.
- [x] 2.3 Revisar os candidatos e conferir autorização, entradas e fluxos de erro; teste local compara todas as 28 operações e entradas obrigatórias/propriedades OpenAPI com exatamente um candidato XS, valida guards e regras-chave e confirma ausência de operações de remoção/promoção pública. Esta revisão estrutural não substitui compilação/importação nem prova de execução no Xano.

## 3. Gerar e inspecionar dry-run (bloqueado)

- [x] 3.1 Gerar dry-run no workspace `151966`/branch `v1`, sem `--records`, `--env`, `--truncate` ou `--sync --delete`. A prévia combinada incluiu os 9 schemas como contexto e mostrou somente 28 endpoints da biblioteca a criar; nenhuma tabela nem outro recurso apareceu como alteração.
- [x] 3.2 Inspecionar destino e preview antes de Apply. O preview mostrou apenas 28 criações de endpoints; não incluiu remoções, alterações de tabelas, registros, variáveis, funções, addons ou objetos de IA. Não foi executado `--sync --delete`.

## 4. Aplicar o escopo autorizado

- [x] 4.1 Reconfirmar o destino imediatamente antes da escrita pela prévia explícita (`151966`, `v1`, `Augusto's Workspace`) e aplicar somente arquivos de tabelas/APIs selecionados. O preview combinado listou somente os 28 endpoints; não incluiu registros, variáveis ou tipos de recurso fora do escopo.
- [x] 4.2 Registrar a saída e comparar com o preview. O CLI informou `Pushed 37 documents` (9 schemas incluídos sem mudança de tabela no preview e 28 endpoints) e sincronizou 28 GUIDs. O pull posterior confirmou os 28 endpoints no grupo `Biblioteca` e as 9 tabelas da biblioteca; não houve divergência material.

## 5. Verificar o que foi aplicado

- [x] 5.1 Fazer pull somente de definições após Apply e comparar com o preview. Foram puxados 57 documentos sem registros/variáveis: 11 tabelas (9 da biblioteca e 2 legadas), 28 endpoints no grupo `Biblioteca` e endpoints legados nos grupos `Authentication`/`Event Logs`. O preview e o pull confirmam o escopo aplicado; nenhum recurso legado foi removido.
- [x] 5.2 Verificar no Xano live somente os fluxos seguros de identidade, catálogo, solicitação/retirada/devolução, fila FIFO, oferta de 48 horas, permissões estudante/bibliotecário e condição do exemplar, com fixtures criadas por API e limpeza confirmada por ID. A execução de 2026-11-03 registrou HTTP 200/403 esperados e GET 404 após cada exclusão em `RESULTS.md`. Expiração/reoferta, atraso, limite simultâneo e concorrência foram separados para a Change `verificacao-avancada-circulacao`, pois exigem ambiente isolado.
- [x] 5.3 Registrar evidências e discrepâncias em `RESULTS.md`, incluindo Apply, pull, comparação, testes e limitações. O Verify funcional final e o Archive permanecem condicionados às tarefas 2.2 e 5.2.

## Workflow follow-up

- A implementação da aplicação Reflex, telas, sessão Reflex e integração executável pertence a Changes futuras; esta Change entrega contratos documentais para essa integração.
- O destino desta Change é `151966/v1`. Em 2026-10-27 o CLI aceitou o push delimitado embora o campo de preferência `allow_push` apareça como `false`; esse campo não foi alterado.
- A autorização atual cobre reconstrução de tabelas e endpoints necessários à biblioteca e reconhece perda potencial de dados dessas tabelas. A verificação segura utilizou somente fixtures sintéticos e IDs registrados, já removidos; não ler, importar, alterar ou excluir qualquer outro registro. Preserve todos os demais recursos Xano. Os testes temporais e concorrentes exigem a Change isolada posterior.
- Solicitar Verify após as tarefas de implementação e evidências; arquivar somente após Verify aprovado e todas as tarefas concluídas.

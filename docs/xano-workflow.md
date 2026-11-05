# Fluxo de trabalho Xano pelo VS Code

## Destino confirmado para esta prova

- CLI local: `@xano/cli 1.3.4`.
- Perfil padrão: `default`, no workspace `151966` (`Augusto's Workspace`).
- Instância: `x8ki-letl-twmt.n7.xano.io`.
- Branch: `v1`, única branch listada e marcada como live.
- `workspace get` retornou `preferences.allow_push = false`. A documentação oficial da CLI diz que, em planos pagos, o push por sandbox é o padrão/obrigatório até habilitar **Allow Direct Workspace Push**. Não habilite essa preferência automaticamente; verifique o resultado do dry-run e pare se o push delimitado não estiver permitido.
- A documentação da CLI também informa que `xano sandbox push` não aceita filtros `-i/--include`; portanto, se o push direto for recusado por `allow_push = false`, não substitua por sandbox nem altere a preferência sem nova autorização.
- A credencial padrão é `~/.xano/credentials.yaml`, fora do repositório. Não copie nem imprima seu conteúdo, não o inclua em Git, logs ou documentação. O `.env` do Reflex não precisa armazenar o token Metadata API.

## Comandos reais da CLI

Ajuda consultada na instalação:

```powershell
xano --help
xano workspace pull --help
xano workspace push --help
xano workspace get --help
xano workspace create --help
xano profile --help
xano profile use --help
xano branch --help
```

`xano workspace pull` e `xano workspace push` existem. A CLI não oferece comandos `xano table` nem `xano api` (`xano api --help` retorna “Command api not found”). A CLI pode criar/atualizar documentos `.xs` por push filtrado; a Metadata API oferece operações individuais documentadas para recursos. `xano workspace create` cria um workspace inteiro, não uma tabela.

Pull validado sem `--records`, `--env`, `--draft` ou `--sync-state`:

```powershell
xano workspace pull -w 151966 -b v1 -d "$env:TEMP\biblioteca-xano-reference-151966-v1"
```

O CLI informou 57 documentos. A documentação oficial confirma que o pull padrão exporta definições publicadas, excluindo registros, variáveis de ambiente e versões draft. Mantenha essa referência fora do repositório e compare-a com o checkout antes de qualquer push:

```powershell
git --no-pager diff --no-index -- xano/ "$env:TEMP\biblioteca-xano-reference-151966-v1"
git status --short -- xano/
```

`git diff --no-index` retorna código diferente de zero quando encontra diferenças; isso não significa falha de execução. Inspecione e relate a diferença, não copie o pull inteiro para `xano/`.

### Pull e comparação observados

Na leitura de 2026-11-05, o pull continha 57 arquivos/documentos e `xano/` tinha 41 arquivos. O remoto continha 11 tabelas e 36 endpoints; o checkout tinha 9 tabelas e 28 endpoints, além de OpenAPI, README e testes locais. As nove definições de tabela com nomes em comum tinham conteúdo diferente: `categoria`, `condicao_exemplar`, `emprestimo`, `exemplar`, `reserva`, `solicitacao_emprestimo`, `titulo`, `titulo_categoria` e `usuario`. Por exemplo, o `titulo.xs` remoto declara `auth = false`, ausente no Git.

Também há recursos remotos adicionais de `Authentication` e `Event Logs`, e as rotas/grupos de API remotos estão organizados de forma diferente da árvore `api/default/` local. São divergências preexistentes; não sincronize recursos existentes. O push desta prova deve incluir exclusivamente os arquivos `zz_teste_*`.

## Push delimitado e remoção

O CLI aceita `-i/--include`, `-b/--branch`, `-w/--workspace` e `--dry-run`. Faça uma prévia por cada conjunto exato de arquivos e confira a lista antes de qualquer escrita. Para uma tabela de teste:

```powershell
xano workspace push -d .\xano -w 151966 -b v1 -i "table/zz_teste_nota.xs" --dry-run
xano workspace push -d .\xano -w 151966 -b v1 -i "table/zz_teste_nota.xs"
```

Para endpoints, inclua somente o arquivo de grupo e os endpoints descartáveis correspondentes, cada um com `-i` próprio. Se a prévia listar qualquer recurso fora do prefixo `zz_teste_*`, não confirme o push. O comando de push sem `--sync` é parcial; `--sync` envia todos os arquivos. `--delete` só funciona junto com `--sync` e exclui objetos remotos ausentes do conjunto enviado. **Não use `push --delete --sync` nesta Change.**

O pull/push pelo CLI manipula documentos XanoScript multidoc. A Metadata API também documenta `GET` e `POST /workspace/{workspace_id}/multidoc`, mas o POST aplica conteúdo multidoc ao workspace; não o use como operação pontual de exclusão.

Para operações individuais, a Metadata API oficial documenta:

- Tabelas: `GET`/`POST /workspace/{workspace_id}/table`; atualizar o schema inteiro com `PUT /workspace/{workspace_id}/table/{table_id}/schema`; excluir somente a tabela escolhida com `DELETE /workspace/{workspace_id}/table/{table_id}`.
- Grupos: `GET`/`POST /workspace/{workspace_id}/apigroup`; excluir um grupo descartável com `DELETE /workspace/{workspace_id}/apigroup/{apigroup_id}` (remove os endpoints desse grupo).
- Endpoints: `GET`/`POST /workspace/{workspace_id}/apigroup/{apigroup_id}/api`; alterar com `PUT /workspace/{workspace_id}/apigroup/{apigroup_id}/api/{api_id}`; excluir um endpoint específico com `DELETE /workspace/{workspace_id}/apigroup/{apigroup_id}/api/{api_id}`.

As operações de escrita acima são destrutivas ou mutáveis e exigem os IDs retornados/consultados no próprio workspace e branch. Confirme nome e prefixo antes de cada DELETE. A autenticação da Metadata API usa token bearer da CLI; nunca o exponha em comandos registrados, saída, arquivos ou documentação.

Referências oficiais:

- [Xano CLI: Push & Pull](https://docs.xano.com/xano-cli/push-pull)
- [XanoScript Multidoc](https://docs.xano.com/xanoscript/multidoc)
- [Metadata API](https://docs.xano.com/xano-features/metadata-api)
- [Metadata API: instâncias, tabelas, grupos e endpoints](https://docs.xano.com/xano-features/metadata-api/instanceapi)

## Criar uma tabela/endpoint e consumir no Reflex

1. Confirme workspace, branch e ambiente com `xano workspace get -w 151966 --output json` e `xano branch list -w 151966`; consulte o perfil sem usar a opção de detalhes que exibe metadados de credenciais.
2. Faça pull somente de definições e compare com `git diff --no-index` antes de editar. Não use `--records` ou `--env`.
3. Crie o `.xs` sob `xano/table/` sem `guid` para uma tabela nova. Crie os documentos de API/grupo sob `xano/api/`, com um grupo exclusivo `zz_teste_*`. Faça primeiro `push --dry-run` com `-i` restrito aos documentos novos; revise a prévia; só então execute o mesmo push delimitado.
4. Para modificar um documento existente de teste, altere apenas o `.xs` correspondente e repita `--dry-run` + revisão + `-i`. Para criar endpoints, inclua somente os arquivos novos do grupo de prova.
5. Teste o endpoint Xano com HTTP real somente quando houver credencial de usuário de teste autorizada. Para teste do cliente Reflex, injete `httpx.MockTransport` ao `XanoClient`; valide método, caminho e resposta sem conexão real nem POST de escrita pelo app.
6. Obtenha IDs por GET da Metadata API ou pela resposta de criação. Remova individualmente os endpoints e a tabela/grupo de teste; nunca use exclusão global. Confirme ausência por GET/404, remova somente os arquivos locais temporários e verifique `git status --short -- xano/`.

O endpoint e o teste de cliente descritos acima são o procedimento desta Change; seus resultados reais devem ser anotados aqui somente depois de executados e verificados. Não declare validação XanoScript pelo Developer MCP: esse servidor MCP não está disponível nesta sessão; a referência foi a documentação oficial e a aceitação do servidor Xano durante o push, caso autorizado pelo workspace.

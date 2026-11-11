# Pacote de publicação local do Xano

## Situação e limites

Este roteiro foi preparado para os candidatos locais de `perfil-admin-xano`,
`acervo-bibliotecario` e `reserva-pelo-bibliotecario`. Nenhum destes arquivos
foi publicado nesta sessão. O Xano Developer MCP validou a sintaxe local dos
dois novos endpoints de reservas; isso não comprova existência, autorização,
execução, FIFO ou atomicidade no workspace.

Destino confirmado anteriormente: workspace `151966`, grupo `Biblioteca`,
branch `v1` live e `preferences.allow_push=false`. Nenhum token, senha ou
conteúdo de `.env` deve ser copiado para este documento, terminal compartilhado
ou Git.

## 1. Pré-requisitos obrigatórios

1. No painel Xano, confirme que o workspace selecionado é `151966` e o grupo
   de API é `Biblioteca`.
2. No painel e pela CLI, verifique novamente branches e ambiente:

   ```powershell
   xano workspace get -w 151966 --output json
   xano branch list -w 151966 -o json
   ```

   A última leitura conhecida encontrou somente `v1`, marcada como live. Se
   continuar sem branch de desenvolvimento ou sandbox isolado, **pare**: não
   publique na branch live. Não crie branch sem conferir a política do workspace
   e a autorização do dono.
3. Use uma branch não live confirmada. Defina-a manualmente para cada sessão:

   ```powershell
   $branch = 'NOME_DA_BRANCH_NAO_LIVE_CONFIRMADA'
   ```
4. Antes de qualquer mudança, exporte/backup do workspace e das tabelas
   `usuario` e `titulo`, incluindo os registros necessários à recuperação.
   Guarde cópias fora do repositório, com acesso restrito; não inclua esses
   backups no Git.
5. Confirme que `xano workspace get` ainda mostra `allow_push=false`. O dono do
   workspace deve decidir conscientemente se habilita **Allow Direct Workspace
   Push** nas configurações do Xano para uma janela controlada. A CLI não oferece
   aqui um procedimento seguro documentado para alternar essa preferência.
   Verifique a alteração pelo painel e por `workspace get` antes de publicar.
   Não contorne a recusa usando `xano sandbox push`: esse comando não oferece
   `-i/--include` para delimitar um arquivo.
6. Obtenha uma cópia local de referência somente leitura, fora do repositório:

   ```powershell
   $referencia = "$env:TEMP\biblioteca-xano-antes"
   xano workspace pull -w 151966 -b $branch -d $referencia
   git status --short
   git --no-pager diff -- xano/
   ```

   Compare cada documento com a referência. Não copie nem sincronize o diretório
   `xano/` inteiro. Se o destino, branch, backup, diff ou permissão não forem
   inequívocos, pare.

## 2. Publicação estritamente unitária

Execute o ciclo abaixo **para um único arquivo por vez**. `$arquivo` deve conter
um dos caminhos relativos listados nas seções seguintes. Os padrões `-i` são
relativos a `.\xano`.

```powershell
$arquivo = 'table\usuario.xs'
xano workspace push -d .\xano -w 151966 -b $branch -i "$arquivo" --dry-run
```

Na prévia, confira o workspace, branch, grupo e caminho exatos. Ela deve mostrar
**um único CREATE ou UPDATE do arquivo selecionado**, sem recurso adicional,
DELETE, alteração de outro schema, variável de ambiente ou registro. Se a
prévia não corresponder exatamente, não confirme.

Somente depois de revisar a prévia, execute o mesmo filtro sem `--dry-run` e
responda ao prompt interativo do CLI:

```powershell
xano workspace push -d .\xano -w 151966 -b $branch -i "$arquivo"
```

Após cada envio, faça um pull isolado em diretório temporário e compare somente
o arquivo enviado:

```powershell
$verificacao = "$env:TEMP\biblioteca-xano-depois"
xano workspace pull -w 151966 -b $branch -d $verificacao
git --no-pager diff --no-index -- ".\xano\$arquivo" "$verificacao\$arquivo"
```

Código diferente de zero no `git diff --no-index` indica diferenças; investigue
antes de seguir. Inspecione ainda o diff do pull com a cópia anterior e confirme
que somente o arquivo esperado mudou. Se houver divergência, pare.

### Rollback de um arquivo

Antes do dry-run de cada arquivo, preserve o documento remoto anterior no
diretório temporário de rollback, mantendo sua estrutura relativa:

```powershell
$rollback = "$env:TEMP\biblioteca-xano-rollback"
New-Item -ItemType Directory -Force -Path (Split-Path "$rollback\$arquivo")
Copy-Item "$referencia\$arquivo" "$rollback\$arquivo"
```

Se for necessário reverter, primeiro confirme branch/destino e copie a versão
anterior para uma pasta de staging fora do repositório. Faça dry-run do rollback
com `-i "$arquivo"` e aceite somente um UPDATE desse recurso; depois envie
interativamente e confirme por novo pull isolado e diff. Nunca restaure o
diretório completo nem faça rollback contra `v1` sem nova autorização.

Não use `--sync`, `--delete`, `--force` nem um `-i` com glob amplo neste roteiro.

## 3. Ordem exata dos arquivos `.xs`

Use o ciclo da seção 2 para cada linha, na ordem abaixo. Em cada passo, substitua
`$arquivo` pelo caminho listado, rode primeiro `--dry-run`, revise, envie esse
arquivo sozinho e faça pull/diff antes de avançar.

### 3.1 Schema e autenticação

1. `table\usuario.xs`
2. `table\titulo.xs`
3. `api\default\auth\login_POST.xs`

### 3.2 Guards administrativos existentes

4. `api\default\admin\categorias_POST.xs`
5. `api\default\admin\exemplares_POST.xs`
6. `api\default\admin\titulos_categoria_POST.xs`
7. `api\default\admin\titulos_POST.xs`
8. `api\default\catalogo\categorias_id_PATCH.xs`
9. `api\default\condicoes\condicoes_GET.xs`
10. `api\default\condicoes\condicoes_POST.xs`
11. `api\default\emprestimos\admin_solicitacoes_GET.xs`
12. `api\default\emprestimos\devolucao_POST.xs`
13. `api\default\emprestimos\retirada_POST.xs`
14. `api\default\reservas\fila_GET.xs`
15. `api\default\reservas\ofertar_proxima_POST.xs`
16. `api\default\reservas\processar_expiradas_POST.xs`
17. `api\default\reservas\retirada_POST.xs`

### 3.3 Endpoints de usuários administrados

18. `api\default\admin\usuarios_GET.xs`
19. `api\default\admin\usuarios_POST.xs`
20. `api\default\admin\usuarios_id_PATCH.xs`

### 3.4 Acervo e catálogo

21. `api\default\catalogo\titulos_id_PATCH.xs`
22. `api\default\admin\acervo_GET.xs`
23. `api\default\catalogo\categorias_id_GET.xs`
24. `api\default\catalogo\categorias_titulos_GET.xs`
25. `api\default\catalogo\titulos_GET.xs`
26. `api\default\catalogo\titulos_id_GET.xs`
27. `api\default\emprestimos\solicitacoes_POST.xs`
28. `api\default\reservas\reservas_POST.xs`

### 3.5 Reserva feita por funcionário

29. `api\default\admin\estudantes_GET.xs`
30. `api\default\admin\reservas_POST.xs`

O arquivo `xano/openapi.json` documenta contratos locais, mas não é um
documento XanoScript e não deve ser enviado pelo comando workspace push. Testes
Python e arquivos em `xano/tests/` também permanecem somente locais.

## 4. Primeiro administrador

Somente depois de confirmar no pull que o schema `usuario` aceita `perfil=admin`
e `ativo=true`, o dono do workspace deve provisionar manualmente a primeira
conta pela interface ou fluxo oficialmente suportado pelo Xano. Não use
autocadastro, não invente senha e não coloque senha em arquivo, comando, log,
`.env` ou Git. Se não existir método seguro e suportado para definir a senha,
pare e confirme a documentação Xano antes de criar a conta. O procedimento
permanente está em [xano-workflow.md](./xano-workflow.md).

## 5. Testes sintéticos e limpeza individual

Somente após aprovação do dono e publicação na branch isolada:

1. Crie contas de teste com endereços reservados `example.invalid` e títulos/
   exemplares identificáveis como sintéticos. Registre IDs temporariamente fora
   do repositório; não reutilize dados de estudantes reais.
2. Teste busca por e-mail exato normalizado, e-mail sem estudante, conta
   desativada e tentativa de busca/criação sem papel autorizado.
3. Teste reservas válidas e cada bloqueio: atraso com `devolvido_em` nulo ou
   zero, empréstimo ativo do mesmo título, reserva aguardando/ofertada duplicada,
   estudante inexistente/inativo, título inativo e perfil insuficiente.
4. Teste que a reserva criada entra no fim da fila por timestamp/ID do servidor
   e que nenhum payload pode escolher horário, posição ou prioridade. Não declare
   atomicidade/FIFO real validada sem teste concorrente aprovado no Xano.
5. Para desativação de título e remoção de conta, teste somente com fixtures
   sintéticas, confirme bloqueios e reativação e preserve histórico.
6. Exclua cada registro sintético individualmente, usando o ID confirmado no
   ambiente e a operação oficial suportada pelo Xano. Depois consulte cada ID
   por GET e confirme 404. Nunca use exclusão/truncamento global.
7. Confirme as contagens após limpeza: `reserva=0`, `emprestimo=0`,
   `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0` e `usuario=2` (as duas
   contas base do teste). Se qualquer número diferir, pare e investigue; não
   inicie outro cenário nem arquive a Change.

## 6. Roteiro manual no navegador

Use contas e dados sintéticos e a branch/ambiente que foram aprovados.

1. **Estudante:** entrar, abrir catálogo, buscar um título, combinar categoria,
   ordenação A-Z e “somente disponíveis”; confirmar que títulos inativos não
   aparecem e que a busca sem resultado informa claramente o estado vazio.
2. **Bibliotecário — acervo:** abrir cadastro, criar título com categorias e
   exemplar, adicionar outro exemplar ao título, editar metadados, desativar e
   reativar. Confirmar que inativo some do catálogo público, continua no acervo
   administrativo e é bloqueado para novas solicitações/reservas.
3. **Bibliotecário — reserva:** abrir “Reservas para estudantes”, pesquisar
   e-mail completo, confirmar o nome encontrado, selecionar título ativo e
   registrar. Repetir com cada fixture de bloqueio e confirmar que a fila não
   muda quando a operação é recusada.
4. **Admin:** criar bibliotecário, sair e entrar com a conta sintética, confirmar
   acesso ao acervo/reservas; desativar e reativar a conta. Confirmar que admin
   não consegue desativar a si mesmo ou outro admin.
5. Em cada perfil, tentar URL administrativa direta sem autorização e confirmar
   bloqueio no backend, não apenas ausência de link. Conferir respostas sem
   senha, hash ou token e inspecionar logs antes de qualquer decisão de deploy.

## 7. Encerramento da janela de publicação

Ao fim, confirme pelo painel e por `xano workspace get -w 151966 --output json`
que `allow_push` voltou ao valor anterior `false`. Preserve os backups e pulls
isolados conforme a política do workspace. Não faça push Git, merge ou deploy
como parte deste roteiro. As Changes permanecem sem archive enquanto houver
tarefas remotas, testes reais ou limpeza pendentes.

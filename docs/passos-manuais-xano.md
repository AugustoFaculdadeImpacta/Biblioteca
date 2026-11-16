# Passos manuais no Xano

Este roteiro não contém credenciais nem executa alterações remotas. Confirme
sempre que o painel está no workspace e na branch da Biblioteca antes de
editar dados ou iniciar o seed.

## Promover uma conta sintética

O usuário pode usar uma conta sintética nova, criada por ele, ou conferir os
IDs 80, 81 e 82 registrados nos relatórios da execução. As senhas dessas contas
existiram somente em memória durante os testes e não foram guardadas; para
login autenticado, crie novas contas de teste com senhas conhecidas somente por
você.

1. No painel do Xano, abra **Database** e a tabela `usuario`.
2. Localize a linha pelo ID numérico da conta sintética que você criou.
3. Abra a edição da linha e altere somente `perfil` para `bibliotecario` ou
   `admin`, conforme a conta.
4. Antes de salvar, confira que nenhum outro campo foi alterado. Em especial,
   não substitua `senha`, não altere e-mail ou nome e não edite contas reais.
5. Confira `ativo`. Se estiver `false`, pare e revise com o responsável pelo
   workspace; não mude esse campo como parte da promoção. Um valor nulo não é
   motivo para alterar campos adicionais.
6. Salve e reabra a mesma linha para verificar que somente `perfil` mudou.
7. Faça login e use `scripts/smoke_xano.py` para verificar o perfil. O script
   imprime status e contagens, nunca token, senha, e-mail ou endereço.

A documentação oficial do Xano descreve uma operação Metadata API `PUT` para
atualizar um registro por ID e exige token com escopo de atualização do
conteúdo do workspace. Ela permite enviar um corpo de atualização compatível
com o schema, mas o token precisa ser criado e fornecido conscientemente pelo
operador. Nesta execução não foi lido token de perfil/configuração nem usada a
Metadata API; a edição unitária pelo painel é o caminho manual recomendado.

## Backup dos dados antes do seed

Antes de qualquer `--apply`, no painel Xano, abra **Database** e exporte CSV
das tabelas `categoria`, `titulo`, `titulo_categoria` e `exemplar`:

1. Abra cada tabela, use o menu de configurações e escolha **Export CSV**.
2. Aguarde a conclusão do export e baixe cada arquivo.
3. Guarde os arquivos fora do repositório, com acesso restrito, e confira que
   os quatro exports estão disponíveis antes de continuar.
4. Não importe nem substitua os dados como parte do backup. O seed é uma
   operação separada e não deve ser executado até destino, branch e contagens
   serem conferidos no painel.

## Smoke test de leitura

`scripts/smoke_xano.py` lê `XANO_API_BASE_URL` da configuração local e as
credenciais somente destas variáveis do processo:

- Estudante: `XANO_SMOKE_ESTUDANTE_EMAIL` e `XANO_SMOKE_ESTUDANTE_SENHA`.
- Bibliotecário: `XANO_SMOKE_BIBLIOTECARIO_EMAIL` e
  `XANO_SMOKE_BIBLIOTECARIO_SENHA`.
- Admin: `XANO_SMOKE_ADMIN_EMAIL` e `XANO_SMOKE_ADMIN_SENHA`.

No PowerShell, informe os dados sem salvá-los em arquivo. Exemplo para estudante:

```powershell
$env:XANO_SMOKE_ESTUDANTE_EMAIL = Read-Host "Conta de estudante de teste"
$senhaSegura = Read-Host "Senha da conta de teste" -AsSecureString
$ponteiro = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senhaSegura)
try {
    $env:XANO_SMOKE_ESTUDANTE_SENHA =
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ponteiro)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ponteiro)
}
.\.venv\Scripts\python.exe -m scripts.smoke_xano
Remove-Item Env:XANO_SMOKE_ESTUDANTE_EMAIL, Env:XANO_SMOKE_ESTUDANTE_SENHA
```

Repita o padrão com o par de variáveis do perfil que deseja testar. Os perfis
sem ambas as variáveis são ignorados. Não cole credenciais em scripts, logs,
terminal compartilhado ou arquivos do projeto.

## Seed de catálogo

O script de seed usa `XANO_BASE_URL` e `XANO_ADMIN_TOKEN`, distintos das
variáveis de autenticação do app e do smoke. O token deve ser obtido e mantido
somente pelo operador; nunca o salve no repositório. Primeiro rode apenas a
prévia:

```powershell
.\.venv\Scripts\python.exe -m scripts.seed_xano_demo
```

A prévia não chama o Xano. Depois do backup CSV, confirme manualmente workspace,
branch live e contagens. Somente se o responsável aprovar a escrita, defina
`XANO_BASE_URL` e `XANO_ADMIN_TOKEN` no ambiente do terminal e rode:

```powershell
.\.venv\Scripts\python.exe -m scripts.seed_xano_demo --apply --confirm-destination
```

Não execute esse comando sem backup e confirmação do destino. Após o seed,
verifique as contagens no painel e faça o smoke de leitura por perfil.

## Iniciar o site

Na raiz que contém `rxconfig.py`, com `.venv` ativo:

```powershell
python -m reflex run
```

Para Xano real, `XANO_API_BASE_URL` deve estar configurada localmente. O modo
padrão requer as portas 3000 e 8000 livres. Para descobrir o PID que ocupa a
porta 8000 sem interrompê-lo:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Identifique o processo pelo PID antes de decidir como resolver o conflito.
Para a demonstração local, inicie `python scripts\demo_api.py` em outro
terminal, configure `XANO_API_BASE_URL` no processo Reflex para a API demo e
use `python -m reflex run --backend-port 8001` quando a porta 8000 já estiver
ocupada.

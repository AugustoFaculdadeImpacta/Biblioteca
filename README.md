# Biblioteca — aplicação Reflex

Aplicação frontend em Reflex. A URL base do Xano é lida pelo backend da variável `XANO_API_BASE_URL`; nenhuma URL ou credencial deve ser incluída no código ou em arquivos versionados.

## Início rápido

No PowerShell, entre na pasta que contém `rxconfig.py`, ative o ambiente e
configure `XANO_API_BASE_URL` em `.env`:

```powershell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
# Edite .env e preencha XANO_API_BASE_URL com a URL do seu ambiente Xano.
python -m reflex run
```

Não inclua valores reais de URL ou credenciais neste README nem em arquivos
versionados. O comando padrão usa a porta 3000 para o frontend e a porta 8000
para o backend; ambas precisam estar livres. Para conferir quem escuta na
porta 8000:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

O resultado informa o PID. Para identificar o processo, sem encerrá-lo:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId = <PID>" |
    Select-Object ProcessId, Name, CommandLine
```

Não encerre um processo que não puder identificar. Se a porta estiver ocupada,
resolva o conflito com o responsável pelo processo antes de iniciar o modo
padrão.

## Estado atual

O catálogo está integrado à API Xano; o `GET /catalogo/titulos` no Xano real
retornou HTTP 200. Login e cadastro foram verificados anteriormente com uma
conta sintética; os resultados e IDs estão registrados em
[docs/publicacao-xano-pendente.md](docs/publicacao-xano-pendente.md).
Acessibilidade e as jornadas de acervo, reserva e gestão de bibliotecários
estão cobertas localmente com dados simulados; isso não substitui a validação
integrada dessas operações no Xano.

## Como ler as Changes

Use [docs/mapa-changes.md](docs/mapa-changes.md) como guia curto do que cada Change entrega e quais tarefas ainda dependem do Xano real. Os arquivos em `openspec/changes/` contêm proposta, design e tarefas; os contratos já consolidados ficam em `openspec/specs/`. Essa divisão mantém as tarefas locais separadas do trabalho operacional e da limpeza remota.

## Demonstração com dados simulados

Abra dois terminais na raiz do projeto. No primeiro, inicie a API em memória:

```powershell
python scripts/demo_api.py
```

No segundo, ative o `.venv` e inicie o Reflex apontando para a API simulada:

```powershell
.\.venv\Scripts\Activate.ps1
$env:XANO_API_BASE_URL='http://127.0.0.1:8765'
python -m reflex run --backend-port 8001
```

Use `demo.bibliotecario@example.invalid` ou
`demo.estudante@example.invalid`, ambos com senha `demo123`. A variável de
ambiente vale somente naquele terminal e não altera o arquivo `.env`. A API
simulada mantém os dados apenas em memória e não substitui o Xano. O
autocadastro também funciona nessa demonstração; contas e operações somem ao
reiniciar a API. A porta 8001 evita conflitar com um backend já ocupado na
porta 8000; o frontend permanece na porta 3000.

## Preparar o ambiente no Windows PowerShell

Na raiz do repositório, siga o Apêndice B:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O template Reflex em branco já foi inicializado com `reflex init`. Para reproduzir a inicialização a partir de uma raiz vazia, use `reflex init --name biblioteca_mais_nova --template blank --no-agents`; `--no-agents` preserva o `AGENTS.md` do repositório.

## Configuração local

Crie o arquivo local ignorado pelo Git e configure a URL do grupo API do Xano:

```powershell
Copy-Item .env.example .env
notepad .env
```

Defina `XANO_API_BASE_URL` sem adicionar o valor a código, logs ou commits. `.env.example` contém somente a chave vazia e pode ser versionado.

## Fronteira do Xano e da sessão

O cliente em `biblioteca_mais_nova/xano_client.py` lê a URL no backend, exige HTTPS fora do loopback local e aceita transporte injetável para testes. Os erros de transporte e de resposta não incluem URL, corpo da resposta nem cabeçalho de autorização. O token de sessão fica em variável privada por sessão Reflex (`_session_token`, na classe `State` de `biblioteca_mais_nova/biblioteca_mais_nova.py`) e não deve ser enviado em variáveis públicas, eventos ou logs.

## Executar

Com `.venv` ativo, na pasta do projeto que contém `rxconfig.py`:

```powershell
python -m reflex run
```

O endereço local padrão é `http://localhost:3000`. O processo usa a configuração Reflex versionada, que desativa telemetria opcional.
Esse comando foi verificado no Windows com frontend e backend ativos; `reflex run`
também pode ser usado quando o ambiente virtual estiver ativado.

Para a demonstração com API local, inicie `python scripts\demo_api.py` em um
terminal e, em outro, use a configuração de porta 8001 mostrada acima. Para o
Xano real, mantenha `XANO_API_BASE_URL` somente na configuração local ignorada
pelo Git e use o comando padrão, sem `--backend-port`.

## Verificações

```powershell
python -m pytest
reflex compile --dry
reflex export --frontend-only
```

Os testes da aplicação usam transporte mockado e estado Reflex isolado; não executam chamadas de escrita ao Xano live.

# Biblioteca — aplicação Reflex

Aplicação frontend em Reflex. A URL base do Xano é lida pelo backend da variável `XANO_API_BASE_URL`; nenhuma URL ou credencial deve ser incluída no código ou em arquivos versionados.

## Início rápido

No PowerShell, na raiz do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
reflex run
```

Configure `XANO_API_BASE_URL` no `.env` local conforme a seção abaixo. O
comando padrão abre `http://localhost:3000`.

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

Com `.venv` ativo, na raiz:

```powershell
reflex run
```

O endereço local padrão é `http://localhost:3000`. O processo usa a configuração Reflex versionada, que desativa telemetria opcional.

## Verificações

```powershell
python -m pytest
reflex compile --dry
reflex export --frontend-only
```

Os testes da aplicação usam transporte mockado e estado Reflex isolado; não executam chamadas de escrita ao Xano live.

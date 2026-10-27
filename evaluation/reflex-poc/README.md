# Prova de conceito Reflex — descartável

Avalia o framework; não é parte do produto. Fixtures fictícias, sem persistência, sem Xano, sem credenciais e sem deploy.

## Pré-requisitos

Windows 10/11, PowerShell, Python 3.11+ (Python 3.14.7 está disponível na máquina onde começou este trabalho), Node.js LTS e internet para baixar pacotes do PyPI/npm. Depois de instalada, a prova usa somente `127.0.0.1`.

Estratégia única: ambiente `venv` e `pip`, com dependências diretas fixadas em `requirements.txt`. Não misturar uv, Poetry ou Conda.

## Preparação

No PowerShell, nesta pasta:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nenhum desses comandos solicita conta, senha ou token Xano.

## Execução

Abra dois terminais PowerShell nesta pasta.

Terminal 1 — REST local, limitado ao loopback:

```powershell
.\.venv\Scripts\python.exe -m uvicorn mock_api:api --host 127.0.0.1 --port 8765
```

Terminal 2 — Reflex em preview local, com frontend e backend no mesmo endereço de loopback:

```powershell
.\.venv\Scripts\reflex.exe run --env preview --frontend-port 3000 --backend-host 127.0.0.1
```

Acesse `http://127.0.0.1:3000`; documentação do mock: `http://127.0.0.1:8765/docs`. O modo preview compila a aplicação antes de servir e mantém Reflex e a API simulada presos ao loopback. Use Tab/Shift+Tab e Enter. Os botões Catálogo, Login/Cadastro fictício, Painel bibliotecário, solicitação/confirmação e Reservas/Fila percorrem transições simuladas. Os botões Vazio e Erro exibem estados de interface.

A configuração da prova desativa a telemetria opcional do Reflex; o tráfego de runtime pretendido fica limitado ao navegador/Reflex local e à API simulada em loopback.

## Compilação e verificação

```powershell
.\.venv\Scripts\reflex.exe export --frontend-only
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Examine `.web/` e confira que valores `demo-...-token` não foram compilados no cliente. São tokens estáticos apenas no servidor/API simulada, nunca credenciais reais. Não insira segredos.

## Limpeza

Pare os dois processos com Ctrl+C. Confirme estar nesta pasta e remova só os artefatos da prova:

```powershell
Remove-Item -Recurse -Force .venv, .web, .reflex -ErrorAction SilentlyContinue
```

## Limites

API e Reflex devem estar presos a loopback; token didático não é autenticação real. A chamada à API simulada parte do backend Python; navegador comunica com o backend Reflex local. Deploy, provedor acadêmico, logs hospedados e contrato Xano não foram verificados. Consulte `RESULTS.md`.

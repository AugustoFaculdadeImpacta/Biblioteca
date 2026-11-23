# Ambiente Windows

## Execução do Reflex

Use o ambiente virtual do projeto. No Windows, o executável `reflex.exe` pode ser bloqueado pelo vínculo do ambiente; use o módulo Python:

```powershell
.\.venv\Scripts\python.exe -m reflex run
```

Para a verificação sem iniciar processos persistentes:

```powershell
.\.venv\Scripts\python.exe -m reflex compile --dry
```

Compile e pytest devem rodar em sequência para evitar a corrida conhecida do `.web`:

```powershell
.\scripts\verificar.ps1
```

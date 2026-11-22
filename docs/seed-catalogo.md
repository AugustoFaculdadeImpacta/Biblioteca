# Seed do catálogo real

O script `scripts/seed_catalogo_real.py` prepara aproximadamente 30 títulos próprios em modo dry-run.

Antes de qualquer execução remota, faça backup dos dados no painel do Xano.

## Simulação

```powershell
.\.venv\Scripts\python.exe scripts\seed_catalogo_real.py
```

No modo padrão, o script imprime o plano e não realiza escritas.

## Aplicação

Defina somente as variáveis de ambiente do processo:

```powershell
$env:XANO_API_BASE_URL = "origem configurada pelo ambiente"
$env:XANO_SEED_EMAIL = "conta administradora"
$env:XANO_SEED_PASSWORD = "senha da conta"
.\.venv\Scripts\python.exe scripts\seed_catalogo_real.py --apply
```

Não informe senha ou token em arquivos, commits, logs ou capturas. O script usa os clientes existentes de catálogo e login, não cria categorias e não envia `capa_url`.

O script pula títulos já existentes por comparação sem caixa e sem acentos e desativa somente os títulos de teste com nomes exatos `Jack Sparrow` e `Something`, caso existam.

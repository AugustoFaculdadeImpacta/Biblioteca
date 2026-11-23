# Seed do catálogo real

O script `scripts/seed_catalogo_real.py` prepara aproximadamente 30 títulos próprios em modo dry-run.

Antes de qualquer execução remota, faça backup dos dados no painel do Xano.

## Simulação

```powershell
.\.venv\Scripts\python.exe scripts\seed_catalogo_real.py
```

No modo padrão, o script imprime o plano e não realiza escritas.
Sua primeira linha é `alvo: demonstração local`.

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

## Catálogo real da versão v6

- O plano contém 30 títulos reais distribuídos nas oito categorias aprovadas.
- Cada título contém ISBN-13, ano, editora, edição e descrição própria.
- A validação externa da Open Library foi tentada nesta máquina; não foi possível confirmar os 30 registros por 404 ou falha de rede. Os ISBN ficam registrados como não verificados até validação externa bem-sucedida.
- O script não cria categorias; referências a categorias inexistentes são apenas informadas no plano.
- Sem `--apply`, a primeira linha da saída é `alvo: demonstração local`.
- Com `--apply`, a primeira linha da saída é `alvo: Xano remoto`; neste ambiente, as variáveis `XANO_SEED_EMAIL` e `XANO_SEED_PASSWORD` não existem, portanto nenhuma aplicação remota foi feita.

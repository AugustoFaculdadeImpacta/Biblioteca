param(
    [switch]$PularReflex
)

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

Write-Host "1/2 compilacao Reflex"
& ".\.venv\Scripts\python.exe" -m reflex compile --dry
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "2/2 pytest"
& ".\.venv\Scripts\python.exe" -m pytest --ignore=evaluation
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

exit 0

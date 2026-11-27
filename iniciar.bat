@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\" (
    python -m venv .venv
    if errorlevel 1 goto falha
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto falha

".venv\Scripts\python.exe" -m reflex run
if errorlevel 1 goto falha
goto fim

:falha
echo A inicializacao falhou. Confira se o Python esta instalado e tente novamente.
pause

:fim
endlocal

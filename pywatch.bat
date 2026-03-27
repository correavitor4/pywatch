@echo off
rem Ajuste para o caminho do projeto se necessário
set "PROJ=%~dp0"
set "PROJ=%PROJ:~0,-1%"
set "VENV=%PROJ%\venv"
set "PYTHON=%VENV%\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERRO: ambiente virtual nao encontrado em %PYTHON%
    echo Crie a venv com: python -m venv "%VENV%" e instale dependências.
    exit /b 1
)

pushd "%PROJ%"
"%PYTHON%" "src\main.py" %*
popd

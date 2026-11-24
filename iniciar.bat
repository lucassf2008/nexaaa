@echo off
title Nexa SENAI - Servidor Web
cls
echo ===================================================================
echo                    NEXA SENAI - SERVIDOR LOCAL
echo ===================================================================
echo.
echo Iniciando o servidor web da plataforma Nexa SENAI...
echo.

set PYTHON_EXEC="C:\Users\lucas\.gemini\antigravity\scratch\python311\python.exe"

if exist %PYTHON_EXEC% (
    echo Usando Python do ambiente local: %PYTHON_EXEC%
    %PYTHON_EXEC% app.py
) else (
    echo Usando Python do sistema...
    python app.py
)

pause

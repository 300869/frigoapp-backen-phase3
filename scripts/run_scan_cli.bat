@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Dossier projet = parent de \scripts\
set "PROJECT_DIR=%~dp0.."
for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"

set "VENV_DIR=%PROJECT_DIR%\.venv"
set "PY=%VENV_DIR%\Scripts\python.exe"
set "PYTHONPATH=%PROJECT_DIR%"

if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

echo [%date% %time%] Launch run_scan_cli.py>>"%PROJECT_DIR%\logs\scan.log"
"%PY%" "%PROJECT_DIR%\scripts\run_scan_cli.py" >>"%PROJECT_DIR%\logs\scan.log" 2>&1
set "EXITCODE=%ERRORLEVEL%"
echo [%date% %time%] Exit code !EXITCODE!>>"%PROJECT_DIR%\logs\scan.log"

endlocal & exit /b %EXITCODE%



@echo off
cd /d "%~dp0"

REM Find pythonw.exe in PATH or local appdata
set "PYTHONW_CMD=pythonw.exe"
where pythonw.exe >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" (
        set "PYTHONW_CMD=%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
    )
)

start "" "%PYTHONW_CMD%" "%~dp0main.py"

@echo off
cd /d "%~dp0"
echo ===================================================
echo               VibeRun - Quick Launcher
echo ===================================================
echo Checking dependencies...
python -c "import win32com, win32gui" 2>nul
if %errorlevel% neq 0 (
    echo Installing required dependencies (pywin32)...
    pip install -r requirements.txt
)

echo Starting VibeRun...
python main.py
if %errorlevel% neq 0 (
    pause
)

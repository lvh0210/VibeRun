@echo off
set SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\VibeRun.lnk

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo [VibeRun] Da xoa VibeRun khoi khoi dong cung Windows.
) else (
    echo [VibeRun] Khong tim thay shortcut trong Startup.
)
pause

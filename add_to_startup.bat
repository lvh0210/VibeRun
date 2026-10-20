@echo off
set SCRIPT_PATH=%~dp0start_silent.bat
set SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\VibeRun.lnk

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%SCRIPT_PATH%'; $s.WorkingDirectory = '%~dp0'; $s.Save()"

echo [VibeRun] Da them VibeRun vao khoi dong cung Windows thanh cong!
echo Shortcut: %SHORTCUT_PATH%
pause

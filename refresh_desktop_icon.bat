@echo off
setlocal
echo Updating SARU desktop shortcut icon...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'SARU AI.lnk')); $s.IconLocation=(Join-Path '%~dp0' 'saru.ico')+',0'; $s.Save()"
ie4uinit.exe -show >nul 2>&1
echo Done. If the icon still shows S, sign out and sign in again.
pause

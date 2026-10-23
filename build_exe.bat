@echo off
cd /d "%~dp0"
rem Optional build tool. Install PyInstaller in a dedicated build environment first.
py -3.11 -m unittest discover -v
if errorlevel 1 exit /b 1
py -3.11 -m PyInstaller --noconfirm --clean --windowed --onedir --name SARU_AI --icon saru.ico --add-data "dashboard.png;." --add-data "startup_scene.png;." --add-data "saru_avatar_neon.png;." --add-data "saru_photo.jpg;." --add-data "saru_round.png;." --add-data "saru.ico;." --add-data "MYRA_OFFICIAL_GUIDES;MYRA_OFFICIAL_GUIDES" --hidden-import saru_browser_host --hidden-import PySide6.QtWebEngineWidgets --hidden-import PySide6.QtWebEngineCore --hidden-import win32crypt --hidden-import pyttsx3.drivers.sapi5 app.py
if errorlevel 1 exit /b 1
echo Build created. This unsigned executable still requires Windows acceptance testing.

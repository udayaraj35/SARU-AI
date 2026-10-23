@echo off
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" "%~dp0admin_launcher.py"
if errorlevel 1 pause

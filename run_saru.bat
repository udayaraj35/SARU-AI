@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" launch_saru.py
) else (
  py -3.11 launch_saru.py
)
if errorlevel 1 pause

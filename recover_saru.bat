@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  ".venv\Scripts\pythonw.exe" recover_saru.py
) else (
  py -3.11 recover_saru.py
)

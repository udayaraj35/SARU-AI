@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (echo Python 3.11+ is required. Install it from python.org and retry. & pause & exit /b 1)
py installer.py
if errorlevel 1 pause

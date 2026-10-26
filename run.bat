@echo off
title DeepTrace AI
cd /d "%~dp0"
echo ==========================================
echo          DeepTrace AI Launcher
echo ==========================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or 3.11 and add it to PATH.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Installing/checking dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check internet and Python version.
  pause
  exit /b 1
)
echo.
echo Starting DeepTrace AI...
echo Open http://127.0.0.1:5000 in your browser.
python app.py
pause

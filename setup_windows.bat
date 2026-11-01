@echo off
cd /d "%~dp0"
echo Creating a Python 3.12 environment...
py -3.12 -m venv .venv
if errorlevel 1 (
  echo Install Python 3.12 with the Python launcher, then try again.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed. Check the message above and your internet connection.
  pause
  exit /b 1
)
echo Setup complete. Open start_windows.bat to choose a task.
pause

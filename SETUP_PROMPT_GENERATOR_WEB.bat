@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_prompt_generator.ps1" -ProjectRoot "%~dp0"
if errorlevel 1 (
  echo.
  echo Setup failed.
  pause
  exit /b 1
)
echo.
echo Setup finished.
pause

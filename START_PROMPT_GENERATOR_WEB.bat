@echo off
cd /d "%~dp0"
for /f %%P in ('powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)"') do (
  if not "%%P"=="" taskkill /PID %%P /F >nul 2>nul
)
start "" cmd /c "ping 127.0.0.1 -n 3 >nul && start http://127.0.0.1:8765"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
  "%VENV_PY%" "%~dp0app.py"
  goto :eof
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0app.py"
  goto :eof
)
python "%~dp0app.py"

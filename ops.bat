@echo off
setlocal enabledelayedexpansion

if "%1"=="bb:setup" goto setup
if "%1"=="bb:run" goto run
if "%1"=="bb:schedule:win" goto schedule
if "%1"=="bb:deploy:vercel" goto deploy

echo Usage: ops.bat [bb:setup|bb:run|bb:schedule:win|bb:deploy:vercel]
exit /b 1

:setup
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements_branchbot.txt
exit /b 0

:run
call .venv\Scripts\activate
set PYTHONPATH=bots\contracts-bot
python -m contracts_bot run --since 7
python ops/notify.py
exit /b 0

:schedule
powershell -ExecutionPolicy Bypass -File ops\win\register_task.ps1
exit /b 0

:deploy
cd apps\leadgen-site
if not exist node_modules npm install
npm run build
vercel deploy --prod
exit /b 0
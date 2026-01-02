@echo off
echo Iniciando Backend...
start cmd /k "cd /d D:\nexo-finance\nexo-finance\backend && venv\Scripts\activate && uvicorn app.main:app --reload"

echo Iniciando Frontend...
start cmd /k "cd /d D:\nexo-finance\nexo-finance\frontend && npm run dev"

echo Tudo iniciado!

@echo off
title 🕺 Tinder de las Fiestas - Startup Script
color 0A

echo ======================================================
echo     🕺 TINDER DE LAS FIESTAS - ENTORNO LOCAL
echo ======================================================
echo.
echo Autor: Sebastián Morales (sebannicus)
echo Fecha: %date% %time%
echo.
echo Iniciando entorno completo...
echo.

REM -----------------------------
REM 1️⃣ Activar entorno virtual
REM -----------------------------
echo [1/5] Activando entorno virtual de Django...
cd backend
call venv\Scripts\activate
if errorlevel 1 (
    echo ❌ No se pudo activar el entorno virtual. 
    echo Asegúrate de haber ejecutado previamente "python -m venv venv".
    pause
    exit /b
)
echo ✅ Entorno virtual activado correctamente.
echo.

REM -----------------------------
REM 2️⃣ Resetear entorno (opcional)
REM -----------------------------
echo [2/5] Restaurando base de datos y migraciones...
python tools\reset_environment.py
echo ✅ Entorno Django restaurado correctamente.
echo.

REM -----------------------------
REM 3️⃣ Iniciar servidor Django
REM -----------------------------
echo [3/5] Iniciando backend (Django) en puerto 8000...
start cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"
timeout /t 5 > nul

REM -----------------------------
REM 4️⃣ Iniciar nodo Hardhat
REM -----------------------------
echo [4/5] Levantando nodo local de Hardhat...
start cmd /k "cd blockchain && npx hardhat node"
timeout /t 3 > nul

REM -----------------------------
REM 5️⃣ Iniciar frontend Next.js
REM -----------------------------
echo [5/5] Iniciando interfaz frontend (Next.js)...
start cmd /k "cd frontend && npm run dev"
timeout /t 2 > nul

echo ======================================================
echo 🚀 ENTORNO COMPLETO LEVANTADO CORRECTAMENTE
echo ------------------------------------------------------
echo 🌐 Backend:     http://127.0.0.1:8000
echo 💠 Frontend:    http://localhost:3000
echo ⛓️  Blockchain:  http://127.0.0.1:8545
echo ======================================================
echo.
pause
exit /b

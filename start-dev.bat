@echo off
title 🚀 Tinder de las Fiestas - Entorno Local
color 0A

echo ====================================================
echo 🧹 LIMPIANDO HARDHAT...
echo ====================================================
cd blockchain
call npx hardhat clean

echo ====================================================
echo 🧱 INICIANDO NODO HARDHAT EN SEGUNDO PLANO...
echo ====================================================
start cmd /k "npx hardhat node --hostname 127.0.0.1"

timeout /t 5 >nul

echo ====================================================
echo 🔧 DESPLEGANDO CONTRATO ProofOfPresence...
echo ====================================================
call npx hardhat run scripts/deploy.js --network localhost

echo ====================================================
echo 📄 CONTRATO DESPLEGADO. VOLVIENDO AL DIRECTORIO RAIZ...
echo ====================================================
cd ..

echo ====================================================
echo 🐍 ACTIVANDO ENTORNO VIRTUAL Y LEVANTANDO BACKEND (Django)...
echo ====================================================
cd backend
call venv\Scripts\activate
start cmd /k "call venv\Scripts\activate && python manage.py runserver"

cd ..
timeout /t 3 >nul

echo ====================================================
echo 💻 INICIANDO FRONTEND (Next.js)...
echo ====================================================
cd frontend
start cmd /k "npm run dev"

cd ..
echo ====================================================
echo ✅ TODO LISTO!
echo ====================================================
echo 🌐 Abre http://localhost:3000/heatmap
pause

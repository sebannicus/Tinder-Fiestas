# 🕺 Tinder de las Fiestas
### 🌐 Django + Blockchain + React (Next.js + MapLibre GL)

**Autor:** Sebastián Morales  
**Alias:** sebannicus 🚀 | Fullstack Blockchain Developer  
**Ubicación:** La Serena, Chile  

---

## 🧱 Checkpoint Actual

✅ **Integración Blockchain + Django + Heatmap funcional + Eventos activos**

**Versión:** MVP 1.0  
**Estado:** 100% funcional en entorno local  
**Componentes:** Hardhat · Solidity · Django REST Framework · Next.js · TailwindCSS · MapLibre GL  

---

## 🧭 Descripción del Proyecto

**Tinder de las Fiestas** es una plataforma descentralizada que permite registrar y visualizar la presencia de usuarios en eventos **en tiempo real**, mediante **tecnología blockchain y geolocalización**.

### 🔗 Tecnologías principales
- **Blockchain:** Hardhat + Solidity (contrato inteligente de presencia)  
- **Backend:** Django REST Framework (API intermedia entre blockchain y frontend)  
- **Frontend:** Next.js + TailwindCSS + MapLibre GL (mapa interactivo con puntos de calor)  

El resultado:  
Una red trazable, transparente y visual para **experiencias sociales geolocalizadas**.

---

## ⚙️ Estructura del Proyecto

tinder-de-las-fiestas/
 │
 ├── backend/ # API REST Django
 │ ├── blockchain_api/ # Integración Web3 + ORM + Views
 │ ├── tools/ # Scripts de mantenimiento (reset, seeds, etc.)
 │ ├── manage.py
 │ ├── .env # Variables de entorno
 │ └── venv/ # Entorno virtual Python
 │
 ├── blockchain/ # Contrato inteligente + scripts Hardhat
 │ ├── contracts/ProofOfPresence.sol
 │ ├── scripts/deploy.js
 │ └── deployed/ProofOfPresence.json
 │
 └── frontend/ # Next.js + Tailwind + MapLibre
 ├── src/app/
 ├── package.json
 └── ...


## 🚀 Requisitos Previos

| Componente | Versión recomendada | Instalación |
|-------------|--------------------|--------------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/en/) |
| Hardhat | Última | `npm install --save-dev hardhat` |
| MetaMask (opcional) | — | Para pruebas visuales blockchain |
| Git | — | [git-scm.com](https://git-scm.com/downloads) |

---

## 🧰 Instalación Paso a Paso

### 1️⃣ Clonar el Repositorio

git clone https://github.com/sebannicus/tinder-de-las-fiestas.git
cd tinder-de-las-fiestas
2️⃣ Configurar el Backend (Django)
Crear entorno virtual e instalar dependencias:


cd backend
python -m venv venv
venv\Scripts\activate   # En Windows
# source venv/bin/activate   # En Linux o Mac
pip install -r requirements.txt
Crear archivo .env en backend/ con el siguiente contenido:
ini

# --- CONFIGURACIÓN DEL ENTORNO DJANGO ---
DEBUG=True
SECRET_KEY=django-insecure-tinder-fiesta-dev
ALLOWED_HOSTS=127.0.0.1,localhost

# --- CONFIGURACIÓN DE LA BLOCKCHAIN ---
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

Aplicar migraciones y crear base de datos:
python manage.py makemigrations
python manage.py migrate
(Opcional pero recomendado) Restaurar entorno Django:

python tools/reset_environment.py

Iniciar servidor Django:
python manage.py runserver
📍 Abre: http://127.0.0.1:8000/

3️⃣ Iniciar la Blockchain (Hardhat)
Abrir una nueva terminal y ejecutar:


cd ../blockchain
npm install
npx hardhat node
Esto iniciará un nodo local de Ethereum con 20 cuentas de prueba (10000 ETH cada una).

Luego, en otra terminal:


npx hardhat run scripts/deploy.js --network localhost
Salida esperada:

✅ Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
📄 Contract info saved to: blockchain/deployed/ProofOfPresence.json


4️⃣ Iniciar el Frontend (Next.js + MapLibre)
cd ../frontend
npm install
npm run dev
📍 Abre en navegador: http://localhost:3000

Verás el mapa con eventos activos y puntos de calor (check-ins).

📡 Endpoints Principales (API Django)
Método	Endpoint	Descripción
POST	/api/checkin/	Registra un check-in en blockchain y base local
GET	/api/heatmap/	Devuelve coordenadas para mapa de calor
GET	/api/stats/	Retorna estadísticas de check-ins
GET/POST	/api/events/	Lista o crea eventos
POST	/api/event_checkin/	Registra asistencia de un usuario a evento

📦 Ejemplo de Petición POST /api/checkin/

{
  "location": "La Serena",
  "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
}

🧠 Flujo General del Sistema


A[Usuario] -->|POST /checkin| B[Django API]
B -->|Blockchain TX| C[Hardhat Node]
C -->|Hash TX| B
B -->|Guardar ORM| D[DB Local]
D -->|Datos agregados| E[Mapa (Next.js + MapLibre)]
E -->|Visualización| A
🧾 Notas Importantes
🔗 El proyecto utiliza Hardhat local, sin transacciones reales.

⚙️ Cada despliegue crea un nuevo CONTRACT_ADDRESS, actualízalo en .env.

🌍 Si el mapa no muestra puntos, asegúrate de que los registros incluyan latitude y longitude.

🧹 Usa python tools/reset_environment.py si las migraciones o la base se desincronizan.

✅ Checkpoints del Proyecto
Etapa	Descripción	Estado
1	Configuración Django + Blockchain	✅
2	Despliegue de contrato y conexión Web3	✅
3	Registro bidireccional Django ↔ Blockchain	✅
4	Visualización Heatmap (MapLibre GL)	✅
5	Geolocalización automática de ciudades	🔄 En progreso
6	Panel de estadísticas de eventos	🚧 Planeado

🧑‍💻 Autor
Sebastián Morales (sebannicus)
📍 La Serena, Chile
💼 Fullstack Blockchain Developer
💬 “Construyendo experiencias descentralizadas que conectan personas en tiempo real.”





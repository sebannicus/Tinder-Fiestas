Tinder de las Fiestas

🌐 Django + Blockchain + React (Next.js + MapLibre GL)
Autor: Sebastián Morales
Alias: sebannicus 🚀 | Fullstack Blockchain Developer

🧱 Checkpoint actual

✅ Integración Blockchain + Django + Heatmap funcional + Eventos activos

🧭 Descripción del Proyecto

Tinder de las Fiestas es una plataforma descentralizada para registrar y visualizar la presencia de usuarios en distintos eventos en tiempo real.

Combina:

Blockchain (Hardhat + Solidity)

Backend seguro (Django REST)

Frontend interactivo (Next.js + MapLibre GL)

El resultado: una red trazable, transparente y visual para experiencias sociales geolocalizadas.

⚙️ Estructura del Proyecto
tinder-de-las-fiestas/
│
├── backend/                # API REST Django
│   ├── blockchain_api/     # Integración Web3 + ORM
│   ├── tools/              # Scripts de mantenimiento (reset, seeds, etc.)
│   ├── manage.py
│   └── venv/
│
├── blockchain/             # Contrato + scripts Hardhat
│   ├── contracts/ProofOfPresence.sol
│   ├── scripts/deploy.js
│   └── deployed/ProofOfPresence.json
│
└── frontend/               # Next.js + Tailwind + MapLibre
    ├── src/app/
    ├── package.json
    └── ...

🚀 Requisitos Previos
Componente	Versión Recomendada	Instalación
Python	3.10+	python.org

Node.js	18+	nodejs.org

Hardhat	Última	npm install --save-dev hardhat
MetaMask	Opcional	Extensión para pruebas blockchain
Git	-	git-scm.com
🧰 Instalación Paso a Paso
1️⃣ Clonar el Repositorio
git clone https://github.com/sebannicus/tinder-de-las-fiestas.git
cd tinder-de-las-fiestas

2️⃣ Backend (Django)
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate # Linux/Mac
pip install -r requirements.txt

Crear .env
# --- CONFIGURACIÓN DEL ENTORNO DJANGO ---
DEBUG=True
SECRET_KEY=django-insecure-tinder-fiesta-dev
ALLOWED_HOSTS=127.0.0.1,localhost

# --- CONFIGURACIÓN DE LA BLOCKCHAIN ---
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

Restaurar entorno (opcional pero recomendado)
python tools/reset_environment.py

Iniciar servidor
python manage.py runserver

3️⃣ Blockchain (Hardhat)
cd ../blockchain
npm install
npx hardhat node


En otra terminal:

npx hardhat run scripts/deploy.js --network localhost


Salida esperada:

✅ Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
📄 Contract info saved to: blockchain/deployed/ProofOfPresence.json

4️⃣ Frontend (Next.js + MapLibre)
cd ../frontend
npm install
npm run dev


🌐 Abre http://localhost:3000

📡 Endpoints Principales
Método	Endpoint	Descripción
POST	/api/checkin/	Registra check-in en blockchain y BD
GET	/api/heatmap/	Retorna coordenadas de puntos activos
GET	/api/stats/	Retorna estadísticas de actividad
POST	/api/event_checkin/	Registra asistencia de un usuario a evento
GET	/api/events/	Lista todos los eventos
📦 Ejemplo de POST /api/checkin/
{
  "location": "La Serena",
  "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
}

🧠 Flujo General del Sistema
flowchart LR
A[Usuario] -->|POST /checkin| B[Django API]
B -->|Blockchain TX| C[Hardhat Node]
C -->|Hash TX| B
B -->|Guardar ORM| D[DB Local]
D -->|Datos agregados| E[Mapa Next.js]
E -->|Visualización| A

🧾 Notas Importantes

El proyecto usa Hardhat local, sin transacciones reales.

Cada despliegue genera un nuevo CONTRACT_ADDRESS; actualízalo en tu .env.

Si el mapa no muestra puntos, asegúrate de tener registros con latitude y longitude.

Usa el script reset_environment.py si la base o migraciones se desincronizan.

✅ Checkpoints del Proyecto
Etapa	Descripción	Estado
1	Configuración Django + Blockchain	✅
2	Despliegue de contrato y conexión Web3	✅
3	Registro bidireccional Django ↔ Blockchain	✅
4	Visualización Heatmap (MapLibre GL)	✅
5	Geolocalización automática de ciudades	🔄 En progreso
6	Panel de estadísticas de eventos	🚧 Planeado
🧠 Autor

Sebastián Morales (sebannicus)
📍 La Serena, Chile
💼 Fullstack Blockchain Developer
💬 “Construyendo experiencias descentralizadas que conectan personas en tiempo real.”


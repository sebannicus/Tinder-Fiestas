# 🕺 Tinder de las Fiestas  
### 🌐 Django + Blockchain + React (Next.js + MapLibre GL)

> **Autor:** Sebastián Morales  
> **Alias:** sebannicus 🚀 | *Fullstack Blockchain Developer*  
> **Checkpoint actual:** 🧱 *Integración Blockchain + Django + Heatmap básico*  
> **Stack principal:** Hardhat · Solidity · Django REST · Next.js · Tailwind · MapLibre GL

---

## 🧭 Descripción del Proyecto

**Tinder de las Fiestas** es una plataforma descentralizada para registrar y visualizar la presencia de usuarios en distintos eventos en tiempo real.

Combina **blockchain (Hardhat + Solidity)**, **backend seguro (Django REST)** y **frontend interactivo (Next.js + MapLibre)** para construir un entorno trazable, visual y totalmente transparente.

---

## ⚙️ Estructura del Proyecto

```bash
tinder-de-las-fiestas/
│
├── backend/                # API REST en Django
│   ├── blockchain_api/     # Integración con contrato inteligente
│   ├── manage.py
│   ├── .env                # Variables del entorno
│   └── venv/               # Entorno virtual Python
│
├── blockchain/             # Contrato Solidity + scripts Hardhat
│   ├── contracts/
│   │   └── ProofOfPresence.sol
│   ├── scripts/
│   │   └── deploy.js
│   ├── deployed/
│   │   └── ProofOfPresence.json  ← se genera automáticamente
│   └── hardhat.config.js
│
└── frontend/               # Interfaz web con Next.js + Tailwind + MapLibre
    ├── src/app/
    │   ├── heatmap/
    │   └── ...
    ├── package.json
    └── ...
🚀 Requisitos Previos
Componente	Versión recomendada	Instalación
Python	3.10+	python.org
Node.js	18+	nodejs.org
Hardhat	Última	npm install --save-dev hardhat
MetaMask (opcional)	-	Para pruebas visuales de blockchain
Git	-	git-scm.com

🧰 Instalación paso a paso
1️⃣ Clonar el repositorio
bash
Copiar código
git clone https://github.com/sebannicus/tinder-de-las-fiestas.git
cd tinder-de-las-fiestas
2️⃣ Backend (Django)
Crear entorno virtual e instalar dependencias
bash
Copiar código
cd backend
python -m venv venv
venv\Scripts\activate      # En Windows
# source venv/bin/activate  # En Linux/Mac
pip install -r requirements.txt
Archivo .env
Crea un archivo .env dentro de backend/ con el siguiente contenido:

ini
Copiar código
# --- CONFIGURACIÓN DEL ENTORNO DJANGO ---
DEBUG=True
SECRET_KEY=django-insecure-tinder-fiesta-dev
ALLOWED_HOSTS=127.0.0.1,localhost

# --- CONFIGURACIÓN DE LA BLOCKCHAIN ---
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
Iniciar servidor Django
bash
Copiar código
python manage.py runserver
Verás algo como:

nginx
Copiar código
Starting development server at http://127.0.0.1:8000/
3️⃣ Blockchain (Hardhat)
bash
Copiar código
cd ../blockchain
npm install
npx hardhat node
Esto levanta un nodo local de Ethereum y muestra 20 cuentas de prueba.

En otra terminal:

bash
Copiar código
npx hardhat run scripts/deploy.js --network localhost
✅ Verás:

vbnet
Copiar código
✅ Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
📄 Contract info saved to: blockchain/deployed/ProofOfPresence.json
Ese archivo es leído automáticamente por Django.

4️⃣ Frontend (Next.js + MapLibre)
bash
Copiar código
cd ../frontend
npm install
npm run dev
🌐 Abre en tu navegador:

arduino
Copiar código
http://localhost:3000
Si todo está correcto, verás un mapa mostrando los puntos de presencia registrados.

📡 Endpoints API
Método	Endpoint	Descripción
POST	/api/checkin/	Registra un nuevo evento en blockchain y BD
GET	/api/heatmap/	Retorna coordenadas para mapa de calor
GET	/api/stats/	Retorna estadísticas de check-ins

📦 Ejemplo de POST /api/checkin/ (en Postman o cURL):

json
Copiar código
{
  "user_id": 1,
  "location": "La Serena",
  "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
}
🧠 Flujo General del Sistema
mermaid
Copiar código
flowchart LR
A[Usuario] -->|POST /checkin| B[Django API]
B -->|Blockchain TX| C[Hardhat Local Node]
C -->|Hash TX| B
B -->|Persistencia ORM| D[Base de Datos]
D -->|Datos agregados| E[Mapa (Next.js)]
E -->|Visualización| A
🧾 Notas Importantes
Este proyecto utiliza Hardhat local, por lo tanto ninguna transacción involucra dinero real.

Cada despliegue genera un nuevo CONTRACT_ADDRESS; actualízalo en tu .env.

Si el mapa no muestra todos los puntos, asegúrate de que los registros tengan coordenadas válidas (latitude, longitude).

🧱 Checkpoints Completados
Etapa	Descripción	Estado
1	Configuración Django + Blockchain	✅
2	Despliegue de contrato y conexión vía Web3	✅
3	Registro bidireccional Django ↔ Blockchain	✅
4	Visualización de Heatmap (MapLibre GL)	✅
5	Geolocalización automática de ciudades	🔄 Próxima
6	Módulo de estadísticas y panel admin	🚧 Planeado



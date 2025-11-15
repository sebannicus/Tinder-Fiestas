# PulseMap 🌍🔥  
**Real-time social presence map powered by blockchain.**  

> “Find where life is happening right now.”

---

## 🌐 Languages / Idiomas

- 🇬🇧 [English Documentation](#english-documentation)
- 🇪🇸 [Documentación en Español](#documentación-en-español)

---

# English Documentation

## 1. Overview

**PulseMap** is a real-time social presence map that shows **where people actually are**, using:

- **Blockchain (Hardhat + Solidity)** for verifiable presence (on-chain check-ins).
- **Django REST API** as a backend orchestrator and analytics layer.
- **Next.js + MapLibre GL** as a modern, interactive frontend displaying:
  - A **heatmap of activity**
  - **Events** as markers
  - **User check-ins** via MetaMask

**MVP status:**  
✅ Fully working on localhost (backend + frontend + blockchain)  
✅ On-chain event check-ins with transaction verification  
✅ Heatmap based on check-ins stored in Django  
✅ Wallet login via MetaMask  

---

## 2. Tech Stack

- **Frontend**
  - Next.js (App Router)
  - React
  - TailwindCSS
  - MapLibre GL + react-map-gl

- **Backend**
  - Django
  - Django REST Framework
  - PostgreSQL / SQLite (for local dev)

- **Blockchain**
  - Hardhat
  - Solidity
  - ethers.js
  - MetaMask (wallet provider)

---

## 3. Repository Structure (Conceptual)

```bash
pulsemap/
├── backend/                 # Django + DRF
│   ├── manage.py
│   ├── backend/            # Django project config
│   └── blockchain_api/     # Web3 integration + models + views
│       ├── models.py
│       ├── views.py
│       ├── analytics_service.py
│       ├── blockchain_service.py
│       └── services/
│           └── auth_service.py
│
├── blockchain/             # Hardhat project
│   ├── contracts/
│   │   └── ProofOfPresence.sol
│   ├── scripts/
│   │   └── deploy.js
│   └── deployed/
│       └── ProofOfPresence.json  # ABI + contract address
│
└── frontend/               # Next.js app
    ├── src/app/
    │   └── page.tsx       # Heatmap + events + MetaMask
    ├── src/contracts/
    │   └── ProofOfPresence.json
    └── package.json
4. Branch Strategy
Current branches:

main → stable, MVP fully working on localhost.

develop → ongoing feature development.

mvp-localhost-backup → frozen backup of the working MVP (do not modify).

All three branches currently point to the same functional MVP snapshot.

5. Prerequisites
Python 3.10+

Node.js 18+

npm or yarn

Git

MetaMask installed in the browser

Hardhat (installed via npm)

6. Backend Setup (Django + DRF)
From the project root:

bash
Copiar código
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
Create .env in backend/:

ini
Copiar código
# Django
DEBUG=True
SECRET_KEY=django-insecure-pulsemap-dev
ALLOWED_HOSTS=127.0.0.1,localhost

# Blockchain
RPC_URL=http://127.0.0.1:8545
Apply migrations:

bash
Copiar código
python manage.py makemigrations
python manage.py migrate
(Optional) Reset and seed environment:

bash
Copiar código
python tools/reset_environment.py
Run backend:

bash
Copiar código
python manage.py runserver
# http://127.0.0.1:8000
7. Blockchain Setup (Hardhat)
From the project root:

bash
Copiar código
cd blockchain
npm install
Start local node:

bash
Copiar código
npx hardhat node
Deploy smart contract to localhost:

bash
Copiar código
npx hardhat run scripts/deploy.js --network localhost
This will:

Deploy the ProofOfPresence contract.

Generate blockchain/deployed/ProofOfPresence.json with:

address

abi

You must ensure this file is used by:

backend/blockchain_api/blockchain_service.py

frontend/src/contracts/ProofOfPresence.json

If needed, copy the JSON to the frontend:

bash
Copiar código
# from project root
cp blockchain/deployed/ProofOfPresence.json frontend/src/contracts/ProofOfPresence.json
8. Frontend Setup (Next.js)
From the project root:

bash
Copiar código
cd frontend
npm install
Create .env.local in frontend/:

env
Copiar código
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_STRICT_CHAIN=true
Run the dev server:

bash
Copiar código
npm run dev
# http://localhost:3000
9. Core Feature: Event Check-in Flow
9.1 High-level steps
User connects with MetaMask (signs a nonce).

Backend verifies wallet ownership (/api/login_wallet/).

User selects an event on the map or list.

Frontend calls checkInEvent(event.id, event.location) on-chain.

Transaction is mined → tx.hash, blockNumber.

Frontend calls /api/event_checkin/ with:

event_id

wallet_address

tx_hash

Backend:

Verifies blockchain transaction (correct contract, user, event, success).

Creates EventAttendance and CheckIn records.

Heatmap and stats are updated.

10. Important API Endpoints
Authentication
POST /api/login_wallet/

json
Copiar código
{
  "address": "0x...",
  "signature": "0x...",
  "nonce": "PulseMap_1699999999"
}
Events
GET /api/events/ → returns array of events

POST /api/events/ → create event (admin/future use)

Heatmap
GET /api/heatmap/ → returns array of { latitude, longitude, count }

Stats
GET /api/stats/?days=7 → global check-in stats

Event Check-in
POST /api/event_checkin/

json
Copiar código
{
  "event_id": 1,
  "wallet_address": "0x1234...",
  "tx_hash": "0xabcdef..."
}
11. User Stories (English)
Role: Party Traveler (Regular User)
As a traveler, I want to open a map and see where people are checking in right now, so I can decide where to go.

As a user, I want to connect with my MetaMask wallet so that my presence is securely verified.

As a user, I want to check in to a specific event on-chain, so my attendance is provable and rewarded in tokens in the future.

As a user, I want to see statistics of popular locations, so I can discover trending areas.

Role: Event Organizer (Future)
As an event organizer, I want to create events with location and time, so users can check in to my parties.

As an event organizer, I want to see how many wallets checked into my event, so I can measure traction.

Role: System Admin (Future)
As an admin, I want to monitor system health (blockchain, DB, API), so I can quickly detect issues.

As an admin, I want to prevent duplicate check-ins for the same wallet and event, so statistics are reliable.

12. Architecture & Diagrams
12.1 Component Diagram (Mermaid)
mermaid
Copiar código
graph LR
    subgraph Frontend [Frontend - Next.js / React]
        UI[Heatmap UI\nEvents List\nMetaMask Integration]
    end

    subgraph Backend [Backend - Django REST]
        API[REST API\n(DRF)]
        SVC[Blockchain Service\n(Web3.py)]
        ANALYTICS[Analytics Service\n(Heatmap/Stats)]
        DB[(Database)]
    end

    subgraph Blockchain [Blockchain - Hardhat]
        CONTRACT[ProofOfPresence\nSmart Contract]
        NODE[Hardhat Node]
    end

    subgraph Wallet [User Wallet]
        METAMASK[MetaMask]
    end

    UI -->|HTTP JSON| API
    API --> DB
    API --> ANALYTICS
    API --> SVC
    SVC --> NODE
    NODE --> CONTRACT
    UI -->|ethers.js| METAMASK
    METAMASK --> CONTRACT
12.2 Sequence Diagram: On-chain Event Check-in
mermaid
Copiar código
sequenceDiagram
    participant U as User (Browser)
    participant FE as Frontend (Next.js)
    participant MM as MetaMask
    participant SC as Smart Contract (ProofOfPresence)
    participant BE as Backend (Django)
    participant DB as Database

    U->>FE: Click "Connect Wallet"
    FE->>MM: Request accounts + sign nonce
    MM-->>FE: Signature + address
    FE->>BE: POST /api/login_wallet (address, signature, nonce)
    BE-->>FE: 200 OK (user created or fetched)

    U->>FE: Click "Attend Event"
    FE->>MM: Send tx checkInEvent(eventId, location)
    MM->>SC: Signed transaction
    SC-->>FE: tx hash
    FE->>BE: POST /api/event_checkin (event_id, wallet_address, tx_hash)
    BE->>SC: Verify tx via Web3
    SC-->>BE: Receipt (status=1)
    BE->>DB: Create EventAttendance + CheckIn
    DB-->>BE: OK
    BE-->>FE: 201 Created (check-in registered)
    FE-->>U: Show success + update heatmap
12.3 Context Diagram (High Level)
mermaid
Copiar código
graph TD
    User[User with MetaMask] -->|Connect & Check-in| PulseMapFE[PulseMap Frontend]
    PulseMapFE -->|REST API| PulseMapBE[PulseMap Backend (Django)]
    PulseMapBE -->|On-chain verification| BlockchainNode[Hardhat Node]
    BlockchainNode --> SmartContract[ProofOfPresence Contract]
    PulseMapBE --> Database[(Relational DB)]
13. Known Limitations (MVP)
Localhost only (Hardhat node required).

No real token rewards yet (tokenomics phase pending).

Event creation is basic and not yet gated by roles/permissions.

No mobile app yet (web only).

14. Future Roadmap (Short)
🔐 Role-based access (admin, organizer, user).

🎟 Token incentives / rewards for presence.

🧑‍🤝‍🧑 User profile page with personal stats.

📱 Responsive mobile-first UI.

🌍 Multi-region support beyond localhost.

Documentación en Español
1. Descripción General
PulseMap es un mapa de presencia social en tiempo real que muestra dónde hay gente realmente, usando:

Blockchain (Hardhat + Solidity) para registrar asistencia verificable (check-ins on-chain).

Django REST API como backend orquestador y capa de analítica.

Next.js + MapLibre GL como frontend interactivo que muestra:

Un mapa de calor de actividad

Eventos como marcadores

Asistencia de usuarios mediante MetaMask

Estado del MVP:
✅ 100% funcional en entorno local (backend + frontend + blockchain)
✅ Check-in a eventos con verificación en blockchain
✅ Mapa de calor basado en check-ins almacenados en Django
✅ Login de wallet vía MetaMask

2. Stack Tecnológico
Frontend

Next.js (App Router)

React

TailwindCSS

MapLibre GL + react-map-gl

Backend

Django

Django REST Framework

PostgreSQL / SQLite (según entorno local)

Blockchain

Hardhat

Solidity

ethers.js

MetaMask

3. Estructura del Repositorio (Conceptual)
bash
Copiar código
pulsemap/
├── backend/                 # Django + DRF
│   ├── manage.py
│   ├── backend/
│   └── blockchain_api/
│       ├── models.py
│       ├── views.py
│       ├── analytics_service.py
│       ├── blockchain_service.py
│       └── services/
│           └── auth_service.py
│
├── blockchain/             # Proyecto Hardhat
│   ├── contracts/
│   │   └── ProofOfPresence.sol
│   ├── scripts/
│   │   └── deploy.js
│   └── deployed/
│       └── ProofOfPresence.json
│
└── frontend/               # Next.js
    ├── src/app/
    │   └── page.tsx
    ├── src/contracts/
    │   └── ProofOfPresence.json
    └── package.json
4. Estrategia de Ramas
main → rama estable con el MVP funcional.

develop → rama para seguir desarrollando nuevas funcionalidades.

mvp-localhost-backup → respaldo congelado del MVP estable (no se modifica).

Las 3 ramas actualmente están sincronizadas con el mismo estado funcional.

5. Requisitos Previos
Python 3.10+

Node.js 18+

npm o yarn

Git

MetaMask

Hardhat

6. Backend (Django + DRF)
Desde la raíz del proyecto:

bash
Copiar código
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
Crear archivo .env en backend/:

ini
Copiar código
DEBUG=True
SECRET_KEY=django-insecure-pulsemap-dev
ALLOWED_HOSTS=127.0.0.1,localhost

RPC_URL=http://127.0.0.1:8545
Aplicar migraciones:

bash
Copiar código
python manage.py makemigrations
python manage.py migrate
Opcional (resetear entorno):

bash
Copiar código
python tools/reset_environment.py
Levantar servidor:

bash
Copiar código
python manage.py runserver
# http://127.0.0.1:8000
7. Blockchain (Hardhat)
Desde la raíz del proyecto:

bash
Copiar código
cd blockchain
npm install
Levantar nodo local:

bash
Copiar código
npx hardhat node
Desplegar contrato:

bash
Copiar código
npx hardhat run scripts/deploy.js --network localhost
Esto genera blockchain/deployed/ProofOfPresence.json con:

address

abi

Copiar (si hace falta) al frontend:

bash
Copiar código
cp blockchain/deployed/ProofOfPresence.json frontend/src/contracts/ProofOfPresence.json
8. Frontend (Next.js)
Desde la raíz del proyecto:

bash
Copiar código
cd frontend
npm install
Crear .env.local:

env
Copiar código
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_STRICT_CHAIN=true
Levantar el frontend:

bash
Copiar código
npm run dev
# http://localhost:3000
9. Flujo Principal: Check-in a Eventos
Paso a paso
El usuario conecta su wallet con MetaMask (firma un nonce).

El backend verifica la propiedad de la wallet (/api/login_wallet/).

El usuario selecciona un evento en el mapa o en la lista.

El frontend ejecuta checkInEvent(event.id, event.location) en el contrato.

La transacción se mina y se obtiene tx.hash y blockNumber.

El frontend llama a /api/event_checkin/ con:

event_id

wallet_address

tx_hash

El backend:

Verifica la transacción en blockchain.

Valida contrato, dirección, evento y estado.

Crea EventAttendance y CheckIn.

El mapa de calor y las estadísticas se actualizan.

10. Endpoints Clave
Autenticación
POST /api/login_wallet/

json
Copiar código
{
  "address": "0x...",
  "signature": "0x...",
  "nonce": "PulseMap_1699999999"
}
Eventos
GET /api/events/ → lista de eventos.

POST /api/events/ → creación de eventos (futuro panel admin).

Mapa de Calor
GET /api/heatmap/ → array de { latitude, longitude, count }.

Estadísticas
GET /api/stats/?days=7 → métricas globales de actividad.

Check-in de Evento
POST /api/event_checkin/

json
Copiar código
{
  "event_id": 1,
  "wallet_address": "0x1234...",
  "tx_hash": "0xabcdef..."
}
11. Historias de Usuario (Español)
Rol: Viajero/Usuario de Fiestas
Como viajera (por ejemplo, Paula en Egipto) quiero abrir el mapa y ver dónde hay movimiento real ahora mismo, para decidir a qué lugar ir a bailar.

Como usuario, quiero conectar mi wallet con MetaMask para que mi presencia quede registrada de forma segura.

Como usuario, quiero hacer check-in en un evento específico on-chain, para que mi asistencia quede registrada y pueda recibir recompensas en tokens en el futuro.

Como usuario, quiero ver las zonas y locales más visitados, para descubrir qué lugares están activos.

Rol: Organizador de Eventos (Futuro)
Como organizador, quiero crear eventos con ubicación y horarios, para que los usuarios puedan hacer check-in en mis fiestas.

Como organizador, quiero ver cuántas wallets hicieron check-in a mi evento, para medir el éxito.

Rol: Administrador del Sistema (Futuro)
Como admin, quiero ver el estado de salud del sistema (blockchain, BD, API), para detectar problemas rápidamente.

Como admin, quiero evitar check-ins duplicados de la misma wallet en el mismo evento, para que las métricas sean confiables.

12. Arquitectura y Diagramas (Español)
Los diagramas son los mismos que en inglés, pero descritos en español para claridad.

12.1 Diagrama de Componentes (Mermaid)
mermaid
Copiar código
graph LR
    subgraph Frontend [Frontend - Next.js / React]
        UI[Interfaz PulseMap\nMapa + Eventos + MetaMask]
    end

    subgraph Backend [Backend - Django REST]
        API[API REST\n(DRF)]
        SVC[Servicio Blockchain\n(Web3.py)]
        ANALYTICS[Servicio de Analítica\n(Heatmap/Stats)]
        DB[(Base de Datos)]
    end

    subgraph Blockchain [Blockchain - Hardhat]
        CONTRACT[Contrato ProofOfPresence]
        NODE[Nodo Hardhat]
    end

    subgraph Wallet [Wallet del Usuario]
        METAMASK[MetaMask]
    end

    UI -->|HTTP JSON| API
    API --> DB
    API --> ANALYTICS
    API --> SVC
    SVC --> NODE
    NODE --> CONTRACT
    UI -->|ethers.js| METAMASK
    METAMASK --> CONTRACT
12.2 Diagrama de Secuencia: Check-in a Evento
mermaid
Copiar código
sequenceDiagram
    participant U as Usuario (Navegador)
    participant FE as Frontend (Next.js)
    participant MM as MetaMask
    participant SC as Contrato (ProofOfPresence)
    participant BE as Backend (Django)
    participant DB as Base de Datos

    U->>FE: Click "Conectar Wallet"
    FE->>MM: Solicitar firma de nonce
    MM-->>FE: Firma + address
    FE->>BE: POST /api/login_wallet
    BE-->>FE: Usuario autenticado

    U->>FE: Click "Asistir" en evento
    FE->>MM: Ejecutar checkInEvent(eventId, location)
    MM->>SC: Transacción firmada
    SC-->>FE: tx hash
    FE->>BE: POST /api/event_checkin (event_id, wallet, tx_hash)
    BE->>SC: Verificar tx vía Web3
    SC-->>BE: Receipt (status=1)
    BE->>DB: Crear EventAttendance + CheckIn
    DB-->>BE: OK
    BE-->>FE: Check-in registrado
    FE-->>U: Mensaje de éxito + actualización de mapa
13. Limitaciones del MVP
Solo funciona en entorno local (Hardhat).

Aún no hay sistema de recompensas con tokens implementado.

La gestión de eventos es básica (sin panel avanzado para organizadores).

No hay aplicación móvil nativa (solo web responsiva en el futuro).

14. Roadmap Próximo
Roles y permisos (admin, organizador, usuario).

Integración de tokens / economía de incentivos.

Página de perfil de usuario con historial de check-ins.

Mejorar la UI/UX móvil.

Integrar redes de prueba públicas (ej. Sepolia).

15. Créditos
Autor: Sebastián Morales (sebannicus)
Proyecto: PulseMap
Stack: Django · DRF · Next.js · Tailwind · MapLibre GL · Hardhat · Solidity · MetaMask

“Building a global pulse of real-world presence, one check-in at a time.”

yaml
Copiar código

---

Si quieres, en el siguiente paso podemos:

- Ajustar el README a la estructura exacta de tu repo (rutas reales).
- Crear un `docs/` con diagramas separados.
- O generar también un **MANUAL TÉCNICO** y un **MANUAL DE USUARIO** por separado.










Ch




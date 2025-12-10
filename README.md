<h1>🕺 Tinder de las Fiestas</h1>
<h3>🌐 Django + Blockchain + React (Next.js + MapLibre GL)</h3>

<p><strong>Autor:</strong> Sebastián Morales<br>
<strong>Alias:</strong> sebannicus 🚀 | Fullstack Blockchain Developer<br>
<strong>Ubicación:</strong> La Serena, Chile</p>

<hr>

<h2>🧱 Checkpoint Actual</h2>

<p>✅ <strong>Integración Blockchain + Django + Heatmap funcional + Eventos activos</strong></p>

<p><strong>Versión:</strong> MVP 1.0<br>
<strong>Estado:</strong> 100% funcional en entorno local<br>
<strong>Componentes:</strong> Hardhat · Solidity · Django REST Framework · Next.js · TailwindCSS · MapLibre GL</p>

<hr>

<h2>🧭 Descripción del Proyecto</h2>

<p><strong>Tinder de las Fiestas</strong> es una plataforma descentralizada que permite registrar y visualizar la presencia de usuarios en eventos <strong>en tiempo real</strong>, mediante <strong>tecnología blockchain y geolocalización</strong>.</p>

<h3>🔗 Tecnologías principales</h3>
<ul>
  <li><strong>Blockchain:</strong> Hardhat + Solidity</li>
  <li><strong>Backend:</strong> Django REST Framework</li>
  <li><strong>Frontend:</strong> Next.js + TailwindCSS + MapLibre GL</li>
</ul>

<hr>

<h2>⚙️ Estructura del Proyecto</h2>

<pre>
tinder-de-las-fiestas/
 │
 ├── backend/              # API REST Django
 │   ├── blockchain_api/   # Integración Web3 + ORM + Views
 │   ├── tools/            # Scripts de mantenimiento
 │   ├── manage.py
 │   ├── .env
 │   └── venv/
 │
 ├── blockchain/           # Smart Contract + Hardhat
 │   ├── contracts/ProofOfPresence.sol
 │   ├── scripts/deploy.js
 │   └── deployed/ProofOfPresence.json
 │
 └── frontend/             # Next.js + MapLibre
     ├── src/app/
     ├── package.json
     └── ...
</pre>

<hr>

<h2>🚀 Requisitos Previos</h2>

<table>
<thead>
<tr>
<th>Componente</th>
<th>Versión recomendada</th>
<th>Instalación</th>
</tr>
</thead>
<tbody>
<tr>
<td>Python</td>
<td>3.10+</td>
<td>https://www.python.org/downloads/</td>
</tr>
<tr>
<td>Node.js</td>
<td>18+</td>
<td>https://nodejs.org/</td>
</tr>
<tr>
<td>Hardhat</td>
<td>Última</td>
<td>npm install --save-dev hardhat</td>
</tr>
<tr>
<td>MetaMask (opcional)</td>
<td>—</td>
<td>Para pruebas blockchain</td>
</tr>
<tr>
<td>Git</td>
<td>—</td>
<td>https://git-scm.com/downloads</td>
</tr>
</tbody>
</table>

<hr>

<h2>🧰 Instalación Paso a Paso</h2>

<h3>1️⃣ Clonar el Repositorio</h3>

<pre>
git clone https://github.com/sebannicus/tinder-de-las-fiestas.git
cd tinder-de-las-fiestas
</pre>

<h3>2️⃣ Configurar Backend (Django)</h3>

<pre>
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
</pre>

<p>Crear archivo <code>.env</code>:</p>

<pre>
DEBUG=True
SECRET_KEY=django-insecure-tinder-fiesta-dev
ALLOWED_HOSTS=127.0.0.1,localhost

RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
</pre>

<p>Aplicar migraciones:</p>

<pre>
python manage.py makemigrations
python manage.py migrate
</pre>

<p>Iniciar servidor:</p>

<pre>
python manage.py runserver
</pre>

<p>📍 http://127.0.0.1:8000/</p>

<hr>

<h3>3️⃣ Iniciar Blockchain (Hardhat)</h3>

<pre>
cd ../blockchain
npm install
npx hardhat node
</pre>

<p>En otra terminal:</p>

<pre>
npx hardhat run scripts/deploy.js --network localhost
</pre>

<hr>

<h3>4️⃣ Iniciar Frontend (Next.js)</h3>

<pre>
cd ../frontend
npm install
npm run dev
</pre>

<p>📍 http://localhost:3000</p>

<hr>

<h2>📡 Endpoints Principales (API Django)</h2>

<table>
<thead>
<tr><th>Método</th><th>Endpoint</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr><td>POST</td><td>/api/checkin/</td><td>Registrar check-in</td></tr>
<tr><td>GET</td><td>/api/heatmap/</td><td>Puntos de calor</td></tr>
<tr><td>GET</td><td>/api/stats/</td><td>Estadísticas</td></tr>
<tr><td>GET/POST</td><td>/api/events/</td><td>Eventos</td></tr>
<tr><td>POST</td><td>/api/event_checkin/</td><td>Registrar asistencia</td></tr>
</tbody>
</table>

<hr>

<h2>📦 Ejemplo POST /api/checkin/</h2>

<pre>
{
  "location": "La Serena",
  "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
}
</pre>

<hr>

<h2>🧠 Flujo General del Sistema</h2>

<pre>
Usuario → Django API → Blockchain → Django ORM → Base de datos → Frontend → Usuario
</pre>

<hr>

<h2>🧾 Notas Importantes</h2>
<ul>
  <li>Hardhat local, sin transacciones reales.</li>
  <li>Cada despliegue genera un nuevo <code>CONTRACT_ADDRESS</code>.</li>
  <li>Requiere coordenadas en heatmap.</li>
  <li><code>reset_environment.py</code> restaura todo.</li>
</ul>

<hr>

<h2>✅ Checkpoints del Proyecto</h2>

<table>
<thead>
<tr><th>Etapa</th><th>Descripción</th><th>Estado</th></tr>
</thead>
<tbody>
<tr><td>1</td><td>Config Django + Blockchain</td><td>✅</td></tr>
<tr><td>2</td><td>Despliegue contrato</td><td>✅</td></tr>
<tr><td>3</td><td>Registro bidireccional</td><td>✅</td></tr>
<tr><td>4</td><td>Heatmap real-time</td><td>✅</td></tr>
<tr><td>5</td><td>Geolocalización automática</td><td>🔄</td></tr>
<tr><td>6</td><td>Panel estadísticas</td><td>🚧</td></tr>
</tbody>
</table>

<hr>

<h2>🧑‍💻 Autor</h2>

<p><strong>Sebastián Morales (sebannicus)</strong><br>
📍 La Serena, Chile<br>
💼 Fullstack Blockchain Developer<br>
<em>“Construyendo experiencias descentralizadas que conectan personas en tiempo real.”</em></p>

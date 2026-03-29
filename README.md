<h1>Tinder de las Fiestas — MVP de Aprendizaje</h1>

<blockquote>
<strong>Nota:</strong> Este repositorio es un proyecto de desarrollo inicial y aprendizaje.
Representa el primer ciclo de exploración del concepto <em>Proof-of-Presence en blockchain</em>.
<br><br>
El proyecto activo y en producción está en:
<a href="https://github.com/sebannicus/aplicacion-eventos-sociales-blockchain-web3">
  aplicacion-eventos-sociales-blockchain-web3
</a> — stack completo con Foundry, UUPS, Supabase y Next.js.
</blockquote>

<hr>

<h2>Contexto del Proyecto</h2>

<p>
Este MVP fue el punto de partida para validar la idea central: <strong>registrar presencia física en eventos a través de smart contracts en blockchain</strong>.
</p>

<p>
Durante este desarrollo se exploraron y aprendieron los siguientes conceptos:
</p>

<ul>
  <li>Integración Hardhat + Solidity + Django REST Framework</li>
  <li>Geofencing básico en smart contracts (bounding box con coordenadas int256)</li>
  <li>Emisión de tokens ERC-20 como recompensa por check-in</li>
  <li>Conexión backend Django ↔ nodo Hardhat local</li>
  <li>Heatmap de presencia en tiempo real con MapLibre GL + Next.js</li>
  <li>Despliegue y prueba end-to-end en entorno local (localhost)</li>
</ul>

<h2>Stack (Versión Inicial)</h2>

<ul>
  <li><strong>Blockchain:</strong> Hardhat + Solidity 0.8.24</li>
  <li><strong>Backend:</strong> Django REST Framework (Python)</li>
  <li><strong>Frontend:</strong> Next.js + TailwindCSS + MapLibre GL</li>
</ul>

<h2>Lecciones Aprendidas → Aplicadas en V2</h2>

<table>
<thead>
<tr><th>Limitación encontrada</th><th>Solución en V2</th></tr>
</thead>
<tbody>
<tr><td>Hardhat: ciclo lento de deploy/test</td><td>Foundry + forge test (más rápido, fuzz nativo)</td></tr>
<tr><td>Django: stack extra, no native Web3</td><td>Supabase (PostgreSQL + Realtime + Auth)</td></tr>
<tr><td>GPS falsificable por el cliente</td><td>Firma ECDSA del backend (anti-spoof)</td></tr>
<tr><td>Contratos no upgradeables</td><td>UUPS Proxy pattern (OpenZeppelin v5)</td></tr>
<tr><td>Sin tests formales</td><td>Suite completa Forge + Fuzz testing</td></tr>
</tbody>
</table>

<h2>Estado</h2>

<p>
<strong>Archivado como referencia.</strong> Funcional en entorno local para propósitos educativos.
</p>

<hr>

<p><strong>Sebastián Morales (sebannicus)</strong> — La Serena, Chile</p>

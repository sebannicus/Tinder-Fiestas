"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map, { Source, Layer, Marker, Popup } from "react-map-gl/maplibre";
import { useEffect, useState } from "react";
import { ethers } from "ethers";

export default function HeatmapPage() {
  // 🔹 Estados globales
  const [points, setPoints] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [txResult, setTxResult] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<string>("Desconectado");

  // 🔄 Carga de datos desde el backend
  async function reloadData() {
    try {
      const [heatmapRes, statsRes, eventsRes] = await Promise.all([
        fetch("http://127.0.0.1:8000/api/heatmap/"),
        fetch("http://127.0.0.1:8000/api/stats/"),
        fetch("http://127.0.0.1:8000/api/events/"),
      ]);
      setPoints(await heatmapRes.json());
      setStats(await statsRes.json());
      setEvents(await eventsRes.json());
    } catch (err) {
      console.error("❌ Error al refrescar datos:", err);
    }
  }

  useEffect(() => {
    reloadData();
  }, []);

  // 🌎 Generar capa GeoJSON del heatmap
  const geojson = {
    type: "FeatureCollection",
    features: points
      .filter((p) => p.latitude && p.longitude)
      .map((p) => ({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [p.longitude, p.latitude],
        },
        properties: { count: p.count || 1 },
      })),
  };

  // 🦊 Conectar MetaMask y autenticar en backend
  async function loginWithMetaMask() {
    try {
      if (!window.ethereum) {
        alert("MetaMask no está instalado en tu navegador");
        return;
      }

      // 1️⃣ Conexión a MetaMask
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      // 2️⃣ Firmar nonce temporal
      const nonce = "TinderFiestas_" + Date.now();
      const signature = await signer.signMessage(nonce);

      // 3️⃣ Enviar autenticación al backend (se implementará en HU-08)
      const response = await fetch("http://127.0.0.1:8000/api/login_wallet/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address, signature, nonce }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setWalletAddress(address);
        setAuthStatus("Conectado ✅");
        alert("✅ Wallet conectada: " + address);
      } else {
        setAuthStatus("Error en autenticación");
        console.error(data.message);
      }
    } catch (err) {
      console.error("⚠️ Error MetaMask:", err);
      setAuthStatus("Error en conexión");
    }
  }

  // 🪩 Registrar asistencia en blockchain
  async function handleAsistir(event: any) {
    if (!walletAddress) {
      alert("Conecta primero tu wallet MetaMask 🦊");
      return;
    }

    setLoading(true);
    setTxResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/event_checkin/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_id: event.id,
          wallet_address: walletAddress, // 👈 ahora enviamos la wallet conectada
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setTxResult(`✅ Asistencia registrada. TX: ${data.tx_hash}`);
        await reloadData();
      } else {
        setTxResult(
          `⚠️ Error: ${data.message || "No se pudo registrar la asistencia"}`
        );
      }
    } catch (err) {
      console.error("⚠️ Error:", err);
      setTxResult("⚠️ Error de conexión con el servidor.");
    } finally {
      setLoading(false);
    }
  }

  // 🖼️ Render principal
  return (
    <div className="flex flex-col lg:flex-row h-screen bg-gray-900 text-white">
      {/* 📊 Panel lateral */}
      <div className="lg:w-1/3 p-6 overflow-y-auto border-r border-gray-700">
        <h1 className="text-2xl font-bold mb-4">🔥 Mapa de Actividad</h1>

        {/* 🦊 Conexión MetaMask */}
        <div className="mt-4">
          <button
            onClick={loginWithMetaMask}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 w-full"
          >
            {walletAddress ? "🔗 Wallet Conectada" : "🦊 Conectar Wallet MetaMask"}
          </button>
          {walletAddress && (
            <p className="mt-2 text-sm text-gray-400 break-all">{walletAddress}</p>
          )}
        </div>

        {/* 📈 Estadísticas */}
        {stats ? (
          <>
            <p className="mt-4">
              Total check-ins: <strong>{stats.total_checkins}</strong>
            </p>
            <p>
              Usuarios únicos: <strong>{stats.unique_users}</strong>
            </p>

            <h2 className="mt-6 text-lg font-semibold">
              Lugares más visitados
            </h2>
            <ul className="mt-2 space-y-1">
              {stats.top_locations.map((loc: any, i: number) => (
                <li key={i} className="text-gray-300">
                  {loc.location} — {loc.visits} visitas
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p className="mt-4">Cargando estadísticas...</p>
        )}

        {/* 🎉 Eventos activos */}
        <h2 className="mt-8 text-lg font-semibold">🎉 Eventos activos</h2>
        <ul className="mt-2 space-y-2">
          {events.map((ev: any) => (
            <li
              key={ev.id}
              className="p-2 rounded bg-gray-800 hover:bg-gray-700 cursor-pointer"
              onClick={() => setSelectedEvent(ev)}
            >
              <strong>{ev.name}</strong> — {ev.location}
            </li>
          ))}
        </ul>

        {/* 🧾 Resultado TX */}
        {txResult && (
          <div className="mt-4 p-3 bg-gray-800 rounded text-sm border border-gray-700">
            <span
              className={
                txResult.startsWith("✅") ? "text-green-400" : "text-red-400"
              }
            >
              {txResult}
            </span>
          </div>
        )}
      </div>

      {/* 🗺️ Mapa interactivo */}
      <div className="flex-1 relative">
        <Map
          mapLib={import("maplibre-gl")}
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          initialViewState={{
            longitude: -71.341,
            latitude: -29.953,
            zoom: 10,
          }}
          style={{ width: "100%", height: "100%" }}
        >
          {/* 🔥 Capa de calor */}
          <Source id="heatmap" type="geojson" data={geojson}>
            <Layer
              id="heatmap-layer"
              type="heatmap"
              paint={{
                "heatmap-weight": ["get", "count"],
                "heatmap-intensity": 1.2,
                "heatmap-radius": 25,
                "heatmap-opacity": 0.9,
                "heatmap-color": [
                  "interpolate",
                  ["linear"],
                  ["heatmap-density"],
                  0,
                  "rgba(0,0,255,0)",
                  0.3,
                  "rgb(0,255,255)",
                  0.5,
                  "rgb(0,255,0)",
                  0.7,
                  "rgb(255,255,0)",
                  1,
                  "rgb(255,0,0)",
                ],
              }}
            />
          </Source>

          {/* 📍 Marcadores de eventos */}
          {events.map(
            (ev: any) =>
              ev.longitude &&
              ev.latitude && (
                <Marker
                  key={ev.id}
                  longitude={ev.longitude}
                  latitude={ev.latitude}
                  anchor="bottom"
                  onClick={() => setSelectedEvent(ev)}
                >
                  <div className="text-2xl cursor-pointer">📍</div>
                </Marker>
              )
          )}

          {/* 💬 Popup del evento */}
          {selectedEvent && (
            <Popup
              longitude={selectedEvent.longitude}
              latitude={selectedEvent.latitude}
              onClose={() => setSelectedEvent(null)}
              closeOnClick={false}
              className="text-black"
            >
              <h3 className="font-bold">{selectedEvent.name}</h3>
              <p>{selectedEvent.location}</p>
              <p className="text-sm text-gray-600 mt-1">
                {new Date(selectedEvent.start_date).toLocaleDateString("es-CL")}
              </p>
              <button
                className="mt-2 bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 w-full"
                onClick={() => handleAsistir(selectedEvent)}
                disabled={loading}
              >
                {loading ? "Registrando..." : "Asistir"}
              </button>
            </Popup>
          )}
        </Map>
      </div>
    </div>
  );
}

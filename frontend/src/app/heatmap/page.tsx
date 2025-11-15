"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map, { Source, Layer, Marker, Popup } from "react-map-gl/maplibre";
import { useEffect, useState } from "react";
import { ethers } from "ethers";

import ProofOfPresenceABI from "@/contracts/ProofOfPresence.json";

// -----------------------------------------
// 🔧 Configuración
// -----------------------------------------
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const HARDHAT_CHAIN_ID = 31337; // Hardhat local
const STRICT_CHAIN = process.env.NEXT_PUBLIC_STRICT_CHAIN === "true"; // Validación opcional

export default function HeatmapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [txResult, setTxResult] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // -----------------------------------------
  // 🔄 Cargar datos iniciales
  // -----------------------------------------
  async function reloadData() {
    try {
      setError(null);

      const [heatmapRes, statsRes, eventsRes] = await Promise.all([
        fetch(`${API_URL}/api/heatmap/`),
        fetch(`${API_URL}/api/stats/`),
        fetch(`${API_URL}/api/events/`),
      ]);

      if (!heatmapRes.ok || !statsRes.ok || !eventsRes.ok) {
        throw new Error("Error cargando datos desde el backend");
      }

      setPoints(await heatmapRes.json());
      setStats(await statsRes.json());
      setEvents(await eventsRes.json());
    } catch (err) {
      console.error("❌ Error al refrescar datos:", err);
      setError("No se pudieron cargar los datos del backend");
    }
  }

  useEffect(() => {
    reloadData();
  }, []);

  // -----------------------------------------
  // 🌎 GeoJSON para el Heatmap
  // -----------------------------------------
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

  // -----------------------------------------
  // 🦊 Conexión MetaMask
  // -----------------------------------------
  async function loginWithMetaMask() {
    try {
      setError(null);

      if (!window.ethereum) {
        setError("MetaMask no está instalado");
        return;
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();

      // 1. Validar red
      const network = await provider.getNetwork();

      if (STRICT_CHAIN) {
        if (Number(network.chainId) !== HARDHAT_CHAIN_ID) {
          setError(
            `⚠️ Conéctate a Hardhat Local (chainId ${HARDHAT_CHAIN_ID}). Red actual: ${network.chainId}`
          );
          return;
        }
      } else {
        console.warn("⚠️ Strict chain desactivado. Aceptando cualquier red.");
      }

      // 2. Obtener address
      const address = await signer.getAddress();

      // 3. Firmar mensaje
      const nonce = "TinderFiestas_" + Date.now();
      const signature = await signer.signMessage(nonce);

      // 4. Enviar al backend
      const response = await fetch(`${API_URL}/api/login_wallet/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address, signature, nonce }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setWalletAddress(address);
        setTxResult(`✅ Wallet conectada: ${address.substring(0, 6)}...${address.substring(38)}`);
      } else {
        setError(data.error || "Error de autenticación");
      }
    } catch (err: any) {
      console.error("⚠️ Error MetaMask:", err);
      setError(`Error: ${err.message}`);
    }
  }

  // -----------------------------------------
  // 🪩 Check-in a evento
  // -----------------------------------------
  async function handleAsistir(event: any) {
    if (!walletAddress) {
      setError("Conecta tu wallet primero 🦊");
      return;
    }

    setLoading(true);
    setTxResult(null);
    setError(null);

    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();

      const contract = new ethers.Contract(
        ProofOfPresenceABI.address,
        ProofOfPresenceABI.abi,
        signer
      );

      // ----- On-chain -----
      setTxResult("⏳ Firmando transacción con MetaMask...");
      const tx = await contract.checkInEvent(event.id, event.location);

      setTxResult(`⏳ TX enviada: ${tx.hash.substring(0, 10)}... esperando confirmación...`);
      const receipt = await tx.wait();

      if (receipt.status !== 1) {
        throw new Error("La transacción falló en blockchain");
      }

      // ----- Backend -----
      setTxResult("✅ TX confirmada. Guardando en backend...");

      const response = await fetch(`${API_URL}/api/event_checkin/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_id: event.id,
          wallet_address: walletAddress,
          tx_hash: tx.hash,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Error al guardar en backend");

      setTxResult(
        `🎉 Check-in completado!\n` +
          `TX: ${tx.hash.substring(0, 12)}...\n` +
          `Bloque: ${receipt.blockNumber}`
      );

      reloadData();
    } catch (err: any) {
      console.error("⚠️ Error:", err);

      if (err.code === 4001) setError("⚠️ Transacción cancelada por el usuario");
      else if (err.code === -32603) setError("⚠️ Sin fondos para gas");
      else setError(`⚠️ Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  // -----------------------------------------
  // 🖼️ Vista
  // -----------------------------------------
  return (
    <div className="flex flex-col lg:flex-row h-screen bg-gray-900 text-white">
      {/* Panel lateral */}
      <div className="lg:w-1/3 p-6 overflow-y-auto border-r border-gray-700">
        <h1 className="text-2xl font-bold mb-4">🔥 Tinder de Fiestas</h1>

        {/* Conectar wallet */}
        <button
          onClick={loginWithMetaMask}
          className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 w-full transition disabled:bg-gray-600"
          disabled={!!walletAddress}
        >
          {walletAddress
            ? `🔗 ${walletAddress.substring(0, 6)}...${walletAddress.substring(38)}`
            : "🦊 Conectar Wallet MetaMask"}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded text-sm">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {txResult && (
          <div className="mt-4 p-3 bg-gray-800 rounded text-sm border border-gray-700 whitespace-pre-line">
            <span className={txResult.startsWith("🎉") || txResult.startsWith("✅") ? "text-green-400" : "text-blue-400"}>
              {txResult}
            </span>
          </div>
        )}

        {/* Estadísticas */}
        {stats && stats.status === "success" ? (
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">📊 Estadísticas</h2>

            <p>Total check-ins: <strong>{stats.total_checkins}</strong></p>
            <p>Usuarios únicos: <strong>{stats.unique_users}</strong></p>

            {stats.top_locations?.length > 0 && (
              <>
                <h3 className="mt-4 font-semibold">🔝 Top Lugares</h3>
                <ul className="mt-2 space-y-1 text-sm">
                  {stats.top_locations.map((loc: any, i: number) => (
                    <li key={i} className="text-gray-300">
                      {loc.location} — {loc.visits} visitas
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        ) : (
          <p className="mt-4 text-gray-400">Cargando estadísticas...</p>
        )}

        {/* Eventos */}
        <h2 className="text-lg font-semibold mt-8">🎉 Eventos</h2>
        <ul className="mt-2 space-y-2">
          {events.map((ev: any) => (
            <li
              key={ev.id}
              className="p-3 rounded bg-gray-800 hover:bg-gray-700 cursor-pointer transition"
              onClick={() => setSelectedEvent(ev)}
            >
              <strong>{ev.name}</strong>
              <span className="block text-gray-400 text-sm">{ev.location}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Mapa */}
      <div className="flex-1">
        <Map
          mapLib={import("maplibre-gl")}
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          initialViewState={{
            longitude: -70.6693,
            latitude: -33.4489,
            zoom: 11,
          }}
          style={{ width: "100%", height: "100%" }}
        >
          {/* Heatmap */}
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
                  0, "rgba(0,0,255,0)",
                  0.3, "rgb(0,255,255)",
                  0.5, "rgb(0,255,0)",
                  0.7, "rgb(255,255,0)",
                  1, "rgb(255,0,0)",
                ],
              }}
            />
          </Source>

          {/* Marcadores de eventos */}
          {events.map(
            (ev: any) =>
              ev.latitude &&
              ev.longitude && (
                <Marker key={ev.id} longitude={ev.longitude} latitude={ev.latitude}>
                  <div
                    className="text-3xl cursor-pointer hover:scale-110 transition"
                    onClick={() => setSelectedEvent(ev)}
                  >
                    📍
                  </div>
                </Marker>
              )
          )}

          {/* Popup */}
          {selectedEvent && (
            <Popup
              longitude={selectedEvent.longitude}
              latitude={selectedEvent.latitude}
              onClose={() => setSelectedEvent(null)}
            >
              <div className="text-black p-2">
                <h3 className="font-bold text-lg">{selectedEvent.name}</h3>
                <p className="text-sm text-gray-600">{selectedEvent.location}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(selectedEvent.start_date).toLocaleDateString("es-CL")}
                </p>

                <button
                  className="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full disabled:bg-gray-400"
                  onClick={() => handleAsistir(selectedEvent)}
                  disabled={loading || !walletAddress}
                >
                  {loading ? "Registrando..." : "Asistir"}
                </button>
              </div>
            </Popup>
          )}
        </Map>
      </div>
    </div>
  );
}

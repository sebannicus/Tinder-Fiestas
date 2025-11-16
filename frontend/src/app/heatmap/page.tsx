"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map, { Source, Layer, Marker, Popup } from "react-map-gl/maplibre";
import { useEffect, useState } from "react";
import { ethers } from "ethers";

import ProofOfPresenceABI from "@/contracts/ProofOfPresence.json";

// ================================
// Configuración
// ================================
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const EXPECTED_CHAIN_ID = 31337; // Hardhat local
const EXPECTED_CHAIN_NAME = "Hardhat Local";
const EXPECTED_CHAIN_HEX = "0x7A69";

export default function HeatmapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [txResult, setTxResult] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // ✅ NUEVO: Estado de la red
  const [currentChainId, setCurrentChainId] = useState<number | null>(null);
  const [isCorrectNetwork, setIsCorrectNetwork] = useState<boolean>(true);

  // ================================
  // Cargar datos iniciales
  // ================================
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

  // ================================
  // Helper: Verificar red actual
  // ================================
  async function checkNetwork(provider: ethers.BrowserProvider) {
    try {
      const network = await provider.getNetwork();
      const chainId = Number(network.chainId);
      
      setCurrentChainId(chainId);
      setIsCorrectNetwork(chainId === EXPECTED_CHAIN_ID);
      
      return chainId === EXPECTED_CHAIN_ID;
    } catch (err) {
      console.error("Error verificando red:", err);
      return false;
    }
  }

  // ================================
  // Helper: Cambiar a red correcta
  // ================================
  async function switchToCorrectNetwork() {
    try {
      if (!window.ethereum) return false;

      // Intentar cambiar
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: EXPECTED_CHAIN_HEX }],
      });

      // Verificar que cambió
      const provider = new ethers.BrowserProvider(window.ethereum);
      return await checkNetwork(provider);

    } catch (switchError: any) {
      // Si la red no existe (error 4902), agregarla
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
              {
                chainId: EXPECTED_CHAIN_HEX,
                chainName: EXPECTED_CHAIN_NAME,
                nativeCurrency: {
                  name: "Ethereum",
                  symbol: "ETH",
                  decimals: 18,
                },
                rpcUrls: ["http://127.0.0.1:8545"],
              },
            ],
          });

          setTxResult(`✅ Red ${EXPECTED_CHAIN_NAME} agregada y seleccionada`);
          return true;

        } catch (addError) {
          console.error("Error agregando red:", addError);
          return false;
        }
      } else if (switchError.code === 4001) {
        // Usuario canceló
        return false;
      }
      
      return false;
    }
  }

  // ================================
  // GeoJSON para el heatmap
  // ================================
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

  // ================================
  // Login con MetaMask (SIN bloqueo por red)
  // ================================
  async function loginWithMetaMask() {
    try {
      setError(null);

      if (!window.ethereum) {
        setError("MetaMask no está instalado");
        return;
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      
      // ✅ Verificar red pero NO bloquear
      await checkNetwork(provider);

      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      const nonce = "TinderFiestas_" + Date.now();
      const signature = await signer.signMessage(nonce);

      const response = await fetch(`${API_URL}/api/login_wallet/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address, signature, nonce }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setWalletAddress(address);
        
        // ⚠️ Mostrar advertencia si está en red incorrecta
        if (!isCorrectNetwork) {
          setTxResult(
            `⚠️ Wallet conectada pero estás en la red incorrecta.\n` +
            `Red actual: ChainID ${currentChainId}\n` +
            `Red esperada: ${EXPECTED_CHAIN_NAME} (${EXPECTED_CHAIN_ID})\n\n` +
            `Las transacciones no funcionarán hasta que cambies de red.`
          );
        } else {
          setTxResult(
            `✅ Wallet conectada: ${address.substring(0, 6)}...${address.substring(38)}`
          );
        }
      } else {
        setError("Error de autenticación");
      }
    } catch (err: any) {
      console.error("⚠️ Error MetaMask:", err);
      setError(`Error: ${err.message}`);
    }
  }

  // ================================
  // Registrar asistencia (CON bloqueo por red)
  // ================================
  async function handleAsistir(event: any) {
    if (!walletAddress) {
      setError("Conecta tu wallet primero 🦊");
      return;
    }

    // 🚫 AQUÍ SÍ BLOQUEAMOS si está en red incorrecta
    if (!isCorrectNetwork) {
      setError(
        `⚠️ Red incorrecta!\n\n` +
        `Estás en ChainID ${currentChainId}\n` +
        `Necesitas estar en ${EXPECTED_CHAIN_NAME} (ChainID ${EXPECTED_CHAIN_ID})\n\n` +
        `Haz click en "Cambiar Red" para arreglarlo.`
      );
      return;
    }

    setLoading(true);
    setTxResult(null);
    setError(null);

    try {
      if (!window.ethereum) {
        throw new Error("MetaMask no está disponible");
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();

      const contract = new ethers.Contract(
        ProofOfPresenceABI.address,
        ProofOfPresenceABI.abi,
        signer
      );

      console.log("📡 Enviando transacción...");
      setTxResult("⏳ Firmando transacción con MetaMask...");

      const tx = await contract.checkInEvent(event.id, event.location);

      setTxResult(
        `⏳ TX enviada: ${tx.hash.substring(0, 10)}... Esperando confirmación...`
      );

      const receipt = await tx.wait();

      if (receipt.status !== 1) {
        throw new Error("La transacción falló en blockchain");
      }

      setTxResult("✅ TX confirmada. Guardando en base de datos...");

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

      if (!response.ok) {
        throw new Error(data.error || data.message || "Error al guardar");
      }

      setTxResult(
        `✅ Check-in completado!\nTX: ${tx.hash.substring(0, 10)}...\nBloque: ${receipt.blockNumber}`
      );

      await reloadData();
      
    } catch (err: any) {
      console.error("⚠️ Error:", err);

      if (err.code === 4001) {
        setError("⚠️ Transacción cancelada por el usuario");
      } else if (err.code === -32603) {
        setError("⚠️ Sin fondos para gas");
      } else if (err.code === "CALL_EXCEPTION") {
        setError("⚠️ Ya hiciste check-in a este evento");
      } else {
        setError(`⚠️ Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }

  // ================================
  // Render
  // ================================
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
            : "🦊 Conectar Wallet"}
        </button>

        {/* ⚠️ NUEVO: Botón para cambiar red */}
        {walletAddress && !isCorrectNetwork && (
          <button
            onClick={switchToCorrectNetwork}
            className="mt-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 w-full transition"
          >
            🔄 Cambiar a {EXPECTED_CHAIN_NAME}
          </button>
        )}

        {/* ✅ NUEVO: Indicador de red */}
        {walletAddress && (
          <div className={`mt-2 p-2 rounded text-sm ${
            isCorrectNetwork 
              ? "bg-green-900/30 border border-green-700 text-green-200" 
              : "bg-yellow-900/30 border border-yellow-700 text-yellow-200"
          }`}>
            {isCorrectNetwork ? (
              <>✅ Red correcta: {EXPECTED_CHAIN_NAME}</>
            ) : (
              <>⚠️ Red incorrecta: ChainID {currentChainId}</>
            )}
          </div>
        )}

        {/* Mensajes de error */}
        {error && (
          <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded text-sm">
            <p className="text-red-200 whitespace-pre-line">{error}</p>
          </div>
        )}

        {/* Resultado de TX */}
        {txResult && (
          <div className="mt-4 p-3 bg-gray-800 rounded text-sm border border-gray-700 whitespace-pre-line">
            <span
              className={
                txResult.startsWith("✅") 
                  ? "text-green-400" 
                  : txResult.startsWith("⚠️")
                  ? "text-yellow-400"
                  : "text-blue-400"
              }
            >
              {txResult}
            </span>
          </div>
        )}

        {/* Estadísticas */}
        {stats ? (
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">📊 Estadísticas</h2>
            <div className="space-y-2 text-sm">
              <p>Total check-ins: <strong>{stats.total_checkins}</strong></p>
              <p>Usuarios únicos: <strong>{stats.unique_users}</strong></p>
            </div>

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
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-2">🎉 Eventos</h2>
          {events.length > 0 ? (
            <ul className="space-y-2">
              {events.map((ev: any) => (
                <li
                  key={ev.id}
                  className="p-3 rounded bg-gray-800 hover:bg-gray-700 cursor-pointer transition"
                  onClick={() => setSelectedEvent(ev)}
                >
                  <strong className="block">{ev.name}</strong>
                  <span className="text-sm text-gray-400">{ev.location}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">No hay eventos disponibles</p>
          )}
        </div>
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

          {events.map((ev: any) =>
            ev.longitude && ev.latitude ? (
              <Marker
                key={ev.id}
                longitude={ev.longitude}
                latitude={ev.latitude}
                anchor="bottom"
              >
                <div
                  className="text-3xl cursor-pointer hover:scale-110 transition"
                  onClick={() => setSelectedEvent(ev)}
                >
                  📍
                </div>
              </Marker>
            ) : null
          )}

          {selectedEvent && (
            <Popup
              longitude={selectedEvent.longitude}
              latitude={selectedEvent.latitude}
              onClose={() => setSelectedEvent(null)}
              closeOnClick={false}
            >
              <div className="text-black p-2">
                <h3 className="font-bold text-lg">{selectedEvent.name}</h3>
                <p className="text-sm text-gray-600">{selectedEvent.location}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(selectedEvent.start_date).toLocaleDateString("es-CL")}
                </p>
                <button
                  className="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                  onClick={() => handleAsistir(selectedEvent)}
                  disabled={loading || !walletAddress || !isCorrectNetwork}
                >
                  {loading
                    ? "Registrando..."
                    : !walletAddress
                    ? "🔒 Conecta wallet"
                    : !isCorrectNetwork
                    ? "⚠️ Red incorrecta"
                    : "✅ Asistir"}
                </button>
              </div>
            </Popup>
          )}
        </Map>
      </div>
    </div>
  );
}
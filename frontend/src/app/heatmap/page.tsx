"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map, { Source, Layer, Marker, Popup } from "react-map-gl/maplibre";
import { useEffect, useState } from "react";

export default function HeatmapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [txResult, setTxResult] = useState<string | null>(null);

  // 🔄 Carga o recarga los datos del backend
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

  // 🧠 Cargar datos al iniciar
  useEffect(() => {
    reloadData();
  }, []);

  // 🌎 Construcción del GeoJSON del heatmap
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

  // 🪩 Registrar asistencia en blockchain
  async function handleAsistir(event: any) {
    setLoading(true);
    setTxResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/event_checkin/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_id: event.id,
          private_key:
            "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d", // Cuenta #1 de Hardhat
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setTxResult(`✅ Asistencia registrada. TX: ${data.tx_hash}`);
        await reloadData(); // 🔄 Refresca datos tras éxito
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

  return (
    <div className="flex flex-col lg:flex-row h-screen bg-gray-900 text-white">
      {/* 📊 Panel lateral */}
      <div className="lg:w-1/3 p-6 overflow-y-auto border-r border-gray-700">
        <h1 className="text-2xl font-bold mb-4">🔥 Mapa de Actividad</h1>

        {stats ? (
          <>
            <p>
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
          <p>Cargando estadísticas...</p>
        )}

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

        {/* Resultado TX */}
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

"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map, { Source, Layer, Marker, Popup } from "react-map-gl/maplibre";
import { useEffect, useState } from "react";

export default function HeatmapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
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
        console.error("Error al cargar datos:", err);
      }
    }
    fetchData();
  }, []);

  const geojson = {
    type: "FeatureCollection",
    features: points
      .filter((p) => p.latitude && p.longitude)
      .map((p) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [p.longitude, p.latitude] },
        properties: { count: p.count || 1 },
      })),
  };

  return (
    <div className="flex flex-col lg:flex-row h-screen bg-gray-900 text-white">
      {/* PANEL LATERAL */}
      <div className="lg:w-1/3 p-6 overflow-y-auto border-r border-gray-700">
        <h1 className="text-2xl font-bold mb-4">🔥 Mapa de Actividad</h1>

        {stats ? (
          <>
            <p>Total check-ins: <strong>{stats.total_checkins}</strong></p>
            <p>Usuarios únicos: <strong>{stats.unique_users}</strong></p>

            <h2 className="mt-6 text-lg font-semibold">Lugares más visitados</h2>
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
              <strong>{ev.name}</strong> — {ev.location || "Sin ubicación"}
              <p className="text-sm text-gray-400">
                {new Date(ev.start_date).toLocaleDateString("es-CL")} —{" "}
                {new Date(ev.end_date).toLocaleDateString("es-CL")}
              </p>
            </li>
          ))}
        </ul>
      </div>

      {/* MAPA PRINCIPAL */}
      <div className="flex-1 relative">
        <Map
          mapLib={import("maplibre-gl")}
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          initialViewState={{
            longitude: -71.341,
            latitude: -29.953,
            zoom: 11,
          }}
          style={{ width: "100%", height: "100%" }}
        >
          {/* HEATMAP DE CHECKINS */}
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

          {/* MARCADORES DE EVENTOS */}
          {events.map((ev: any) =>
            ev.longitude && ev.latitude ? (
              <Marker
                key={ev.id}
                longitude={ev.longitude}
                latitude={ev.latitude}
                anchor="bottom"
                onClick={() => setSelectedEvent(ev)}
              >
                <div className="text-2xl cursor-pointer">📍</div>
              </Marker>
            ) : null
          )}

          {/* POPUP DETALLE DE EVENTO */}
          {selectedEvent && (
            <Popup
              longitude={selectedEvent.longitude}
              latitude={selectedEvent.latitude}
              onClose={() => setSelectedEvent(null)}
              closeOnClick={false}
              className="text-black"
            >
              <h3 className="font-bold text-lg">{selectedEvent.name}</h3>
              <p>{selectedEvent.location}</p>
              <p className="text-sm text-gray-600 mt-1">
                {new Date(selectedEvent.start_date).toLocaleString("es-CL")} <br />
                hasta {new Date(selectedEvent.end_date).toLocaleString("es-CL")}
              </p>
              <button
                className="mt-3 bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 w-full"
                onClick={() =>
                  alert(`🎫 Asistiendo al evento: ${selectedEvent.name}`)
                }
              >
                Asistir
              </button>
            </Popup>
          )}
        </Map>
      </div>
    </div>
  );
}

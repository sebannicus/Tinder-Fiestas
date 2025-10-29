"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map, { Source, Layer } from "react-map-gl/maplibre";
import { useEffect, useState } from "react";

export default function HeatmapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [heatmapRes, statsRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/heatmap/"),
          fetch("http://127.0.0.1:8000/api/stats/")
        ]);
        setPoints(await heatmapRes.json());
        setStats(await statsRes.json());
      } catch (err) {
        console.error("Error al cargar datos:", err);
      }
    }
    fetchData();
  }, []);

  const geojson = {
    type: "FeatureCollection",
    features: points
      .filter(p => p.latitude && p.longitude)
      .map(p => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [p.longitude, p.latitude] },
        properties: { count: p.count || 1 },
      })),
  };

  return (
    <div className="flex flex-col lg:flex-row h-screen bg-gray-900 text-white">
      {/* Panel lateral */}
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
      </div>

      {/* Mapa */}
      <div className="flex-1">
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
                  1, "rgb(255,0,0)"
                ]
              }}
            />
          </Source>
        </Map>
      </div>
    </div>
  );
}

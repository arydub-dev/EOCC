"use client";

import { useEffect, useState } from "react";
import { Circle, CircleMarker, LayerGroup, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { MapFeatures } from "@/lib/types";
import { fmtNumber, titleCase } from "@/lib/utils";

interface Props {
  features?: MapFeatures;
  show: Record<string, boolean>;
}

const POINT_STYLE = {
  hospitals: { radius: 6, fallback: "#38bdf8" },
  shelters: { radius: 6, fallback: "#a78bfa" },
  resources: { radius: 4, fallback: "#22c55e" },
  utilities: { radius: 5, fallback: "#f59e0b" },
};

export default function OperationsMap({ features, show }: Props) {
  const incidents = features?.layers.incidents ?? [];

  // Leaflet mutates the DOM imperatively, so during dev Fast Refresh (HMR) React can
  // swap this subtree while Leaflet still holds stale DOM references. That surfaces as
  // an uninformative "[object Event]" console error from the Next.js dev overlay.
  // Remounting the map once after the initial commit forces a fresh Leaflet instance and
  // avoids reconciling against stale refs. This is a no-op in production (no Fast Refresh).
  const [mapKey, setMapKey] = useState(0);
  useEffect(() => {
    setMapKey((k) => k + 1);
  }, []);

  return (
    <MapContainer
      key={mapKey}
      center={[37.8, -96]}
      zoom={4}
      style={{ height: "100%", width: "100%", borderRadius: "0.75rem" }}
      scrollWheelZoom
      worldCopyJump
    >
      <TileLayer
        attribution='&copy; OpenStreetMap &copy; CARTO'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />

      {show.incidents && (
        <LayerGroup>
          {incidents.map((i) => (
            <LayerGroup key={`inc-${i.id}`}>
              <Circle
                center={[i.lat, i.lng]}
                radius={i.radius_km * 1000}
                pathOptions={{ color: i.color, fillColor: i.color, fillOpacity: 0.12, weight: 1 }}
              />
              <CircleMarker
                center={[i.lat, i.lng]}
                radius={7}
                pathOptions={{ color: i.color, fillColor: i.color, fillOpacity: 0.9, weight: 1.5 }}
              >
                <Popup>
                  <div className="space-y-1 text-xs">
                    <p className="text-sm font-semibold">{i.name}</p>
                    <p>{titleCase(i.type)} · {titleCase(i.status)}</p>
                    <p>Severity: <b>{i.severity_score.toFixed(0)}/100</b></p>
                    <p>{fmtNumber(i.population_impacted)} impacted · {i.radius_km.toFixed(0)} km</p>
                  </div>
                </Popup>
              </CircleMarker>
            </LayerGroup>
          ))}
        </LayerGroup>
      )}

      {(["hospitals", "shelters", "resources", "utilities"] as const).map((layer) =>
        show[layer] ? (
          <LayerGroup key={layer}>
            {(features?.layers[layer] ?? []).map((p) => {
              const style = POINT_STYLE[layer];
              const color = p.color ?? style.fallback;
              return (
                <CircleMarker
                  key={`${layer}-${p.id}`}
                  center={[p.lat, p.lng]}
                  radius={style.radius}
                  pathOptions={{ color, fillColor: color, fillOpacity: 0.85, weight: 1 }}
                >
                  <Popup>
                    <div className="space-y-1 text-xs">
                      <p className="text-sm font-semibold">{p.name ?? titleCase(layer)}</p>
                      <p>{titleCase(layer.slice(0, -1))} · {titleCase(p.status)}</p>
                      {p.stress_score !== undefined && <p>Stress: <b>{p.stress_score.toFixed(0)}/100</b></p>}
                      {p.utilization_score !== undefined && <p>Strain: <b>{p.utilization_score.toFixed(0)}/100</b></p>}
                      {p.customers_affected !== undefined && <p>{fmtNumber(p.customers_affected)} affected</p>}
                      {p.capacity !== undefined && <p>{p.occupancy}/{p.capacity} occupied</p>}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </LayerGroup>
        ) : null,
      )}
    </MapContainer>
  );
}

"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { PageHeader } from "@/components/page-header";
import { Spinner } from "@/components/ui/primitives";
import { useMapFeatures } from "@/lib/hooks";
import { cn } from "@/lib/utils";

const OperationsMap = dynamic(() => import("@/components/operations-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-ink-muted">
      <Spinner /> <span className="ml-2">Loading map…</span>
    </div>
  ),
});

const LAYERS = [
  { key: "incidents", label: "Incidents", color: "#ef4444" },
  { key: "hospitals", label: "Hospitals", color: "#38bdf8" },
  { key: "shelters", label: "Shelters", color: "#a78bfa" },
  { key: "resources", label: "Resources", color: "#22c55e" },
  { key: "utilities", label: "Utility Outages", color: "#f59e0b" },
];

export default function MapPage() {
  const [show, setShow] = useState<Record<string, boolean>>({
    incidents: true,
    hospitals: true,
    shelters: true,
    resources: false,
    utilities: true,
  });

  const layerParam = useMemo(() => LAYERS.map((l) => l.key).join(","), []);
  const { data } = useMapFeatures(layerParam);

  const counts: Record<string, number> = {};
  for (const l of LAYERS) counts[l.key] = data?.layers[l.key as keyof typeof data.layers]?.length ?? 0;

  return (
    <div>
      <PageHeader
        question="Where is it happening?"
        title="Geographic Operations Map"
        description="A unified, color-coded situational map of incidents, lifelines and response assets."
      />
      <div className="grid gap-4 lg:grid-cols-[1fr_240px]">
        <div className="panel h-[68vh] overflow-hidden p-0">
          <OperationsMap features={data} show={show} />
        </div>
        <div className="space-y-3">
          <div className="panel p-4">
            <p className="stat-label mb-3">Layers</p>
            <div className="space-y-1.5">
              {LAYERS.map((l) => (
                <button
                  key={l.key}
                  onClick={() => setShow((s) => ({ ...s, [l.key]: !s[l.key] }))}
                  className={cn(
                    "flex w-full items-center justify-between rounded-lg border px-3 py-2 text-sm transition-colors",
                    show[l.key] ? "border-line bg-bg-elevated text-ink" : "border-line/50 bg-bg-soft text-ink-faint",
                  )}
                >
                  <span className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ background: l.color, opacity: show[l.key] ? 1 : 0.4 }} />
                    {l.label}
                  </span>
                  <span className="text-xs">{counts[l.key]}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="panel p-4">
            <p className="stat-label mb-2">Risk Legend</p>
            <div className="space-y-1.5 text-xs text-ink-muted">
              {[
                ["#22c55e", "Low (0–30)"],
                ["#eab308", "Moderate (30–50)"],
                ["#f59e0b", "High (50–70)"],
                ["#f97316", "Severe (70–85)"],
                ["#ef4444", "Critical (85+)"],
              ].map(([c, label]) => (
                <div key={label} className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: c }} />
                  {label}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

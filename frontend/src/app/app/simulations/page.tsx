"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Card, CardHeader } from "@/components/ui/card";
import { Spinner } from "@/components/ui/primitives";
import { useRunSimulation, useSimulations } from "@/lib/hooks";
import { fmtNumber, scoreColor, timeAgo, titleCase } from "@/lib/utils";
import type { Simulation } from "@/lib/types";

interface Field { key: string; label: string; default: number }
interface Scenario { type: string; label: string; description: string; fields: Field[] }

const SCENARIOS: Scenario[] = [
  { type: "hurricane_path", label: "Hurricane Path Change", description: "Project impact of a track shift.",
    fields: [
      { key: "category", label: "Category (1–5)", default: 4 },
      { key: "track_shift_km", label: "Track shift (km)", default: 60 },
      { key: "population_density", label: "Pop. density (/km²)", default: 1800 },
    ] },
  { type: "flood_expansion", label: "Flood Expansion", description: "Model rising water and inundation spread.",
    fields: [
      { key: "water_rise_m", label: "Water rise (m)", default: 2.5 },
      { key: "expansion_km2", label: "Expansion (km²)", default: 40 },
      { key: "population_density", label: "Pop. density (/km²)", default: 1500 },
    ] },
  { type: "shelter_closure", label: "Shelter Closure", description: "Assess displacement from closures.",
    fields: [
      { key: "shelters_closed", label: "Shelters closed", default: 3 },
      { key: "avg_occupancy", label: "Avg occupancy", default: 250 },
    ] },
  { type: "hospital_outage", label: "Hospital Outage", description: "Evaluate loss of hospital capacity.",
    fields: [
      { key: "beds_lost", label: "Beds lost", default: 200 },
      { key: "icu_beds_lost", label: "ICU beds lost", default: 30 },
    ] },
  { type: "resource_depletion", label: "Resource Depletion", description: "Model loss of a resource category.",
    fields: [{ key: "pct_lost", label: "% lost", default: 40 }] },
  { type: "utility_grid_failure", label: "Utility Grid Failure", description: "Project cascading lifeline impacts.",
    fields: [
      { key: "customers_affected", label: "Customers affected", default: 150000 },
      { key: "duration_hours", label: "Duration (h)", default: 36 },
    ] },
];

export default function SimulationsPage() {
  const [scenario, setScenario] = useState<Scenario>(SCENARIOS[0]);
  const [params, setParams] = useState<Record<string, number>>(
    Object.fromEntries(SCENARIOS[0].fields.map((f) => [f.key, f.default])),
  );
  const run = useRunSimulation();
  const { data: history } = useSimulations();

  function selectScenario(s: Scenario) {
    setScenario(s);
    setParams(Object.fromEntries(s.fields.map((f) => [f.key, f.default])));
    run.reset();
  }

  function execute() {
    run.mutate({
      name: `${scenario.label} — ${new Date().toLocaleString()}`,
      simulation_type: scenario.type,
      parameters: params,
    });
  }

  return (
    <div>
      <PageHeader
        question="What if conditions change?"
        title="Simulation Center"
        description="Run deterministic what-if scenarios to project population impact, resource needs and operational risk."
      />

      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        <div className="space-y-2">
          {SCENARIOS.map((s) => (
            <button
              key={s.type}
              onClick={() => selectScenario(s)}
              className={`w-full rounded-lg border p-3 text-left transition-colors ${
                scenario.type === s.type ? "border-accent bg-bg-elevated" : "border-line bg-bg-soft hover:border-ink-faint"
              }`}
            >
              <p className="text-sm font-medium text-ink">{s.label}</p>
              <p className="mt-0.5 text-xs text-ink-faint">{s.description}</p>
            </button>
          ))}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader title={scenario.label} subtitle={scenario.description} />
            <div className="grid gap-3 sm:grid-cols-3">
              {scenario.fields.map((f) => (
                <div key={f.key}>
                  <label className="stat-label">{f.label}</label>
                  <input
                    type="number"
                    className="input mt-1"
                    value={params[f.key]}
                    onChange={(e) => setParams((p) => ({ ...p, [f.key]: Number(e.target.value) }))}
                  />
                </div>
              ))}
            </div>
            <button onClick={execute} disabled={run.isPending} className="btn-primary mt-4">
              {run.isPending ? <Spinner className="text-white" /> : <Play className="h-4 w-4" />} Run Simulation
            </button>
          </Card>

          {run.data && <SimulationResult sim={run.data} />}

          <Card>
            <CardHeader title="Recent Simulations" />
            <div className="space-y-2">
              {history?.slice(0, 6).map((s) => (
                <div key={s.id} className="flex items-center justify-between rounded-lg border border-line bg-bg-soft px-3 py-2">
                  <div className="min-w-0">
                    <p className="truncate text-sm text-ink">{titleCase(s.simulation_type)}</p>
                    <p className="text-xs text-ink-faint">{timeAgo(s.created_at)}</p>
                  </div>
                  <span className="font-mono text-sm font-semibold" style={{ color: scoreColor(s.operational_risk) }}>
                    {s.operational_risk.toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function SimulationResult({ sim }: { sim: Simulation }) {
  const results = (sim.results ?? {}) as Record<string, unknown>;
  const extra = results.additional_resources_required as Record<string, number> | undefined;

  function renderValue(v: unknown): string {
    if (typeof v === "number") return fmtNumber(v);
    if (typeof v === "object" && v !== null) return "";
    return String(v);
  }

  return (
    <Card className="border-accent/40">
      <CardHeader title="Projected Impact" subtitle="Deterministic scenario output" action={
        <div className="text-right">
          <p className="stat-label">Operational Risk</p>
          <p className="text-xl font-bold" style={{ color: scoreColor(sim.operational_risk) }}>{sim.operational_risk.toFixed(0)}</p>
        </div>
      } />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(results)
          .filter(([k, v]) => typeof v !== "object" && k !== "operational_risk_band")
          .map(([k, v]) => (
            <div key={k} className="rounded-lg border border-line bg-bg-soft p-3">
              <p className="stat-label">{titleCase(k)}</p>
              <p className="mt-1 text-sm font-semibold text-ink">{renderValue(v)}</p>
            </div>
          ))}
      </div>

      {extra && (
        <div className="mt-4 border-t border-line pt-3">
          <p className="stat-label mb-2">Additional Resources Required</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(extra).map(([k, v]) => (
              <span key={k} className="pill border-line bg-bg-elevated text-ink-muted">
                {titleCase(k)}: <b className="ml-1 text-ink">{fmtNumber(v)}</b>
              </span>
            ))}
          </div>
        </div>
      )}

      {sim.recommendations && (
        <div className="mt-4 border-t border-line pt-3">
          <p className="stat-label mb-2">Mitigation Recommendations</p>
          <ul className="space-y-1.5">
            {sim.recommendations.map((r, i) => (
              <li key={i} className="flex gap-2 text-xs text-ink-muted"><span className="text-accent">→</span> {r}</li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}

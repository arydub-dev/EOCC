"use client";

import { useState } from "react";
import {
  Activity,
  CheckCircle2,
  Cloud,
  Database,
  FileSpreadsheet,
  FileText,
  Hospital,
  Map as MapIcon,
  Plug,
  Radio,
  Settings2,
  Upload,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Card, CardHeader } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { EmptyState, ProgressBar, Spinner } from "@/components/ui/primitives";
import { useImportCsv, useIntegrationOverview, usePipeline } from "@/lib/hooks";
import { cn, fmtCompact, fmtNumber, timeAgo, titleCase } from "@/lib/utils";
import type { DataSource } from "@/lib/types";

const TABS = ["catalog", "overview", "connectors", "import", "pipeline"] as const;
type Tab = (typeof TABS)[number];

const SAMPLE_CSV = `name,region,latitude,longitude,total_beds,occupied_beds,icu_beds,icu_occupied,er_capacity,er_patients,staff_on_duty,staff_required
Imported Regional Hospital,Gulf Coast,29.76,-95.37,320,288,40,38,60,55,210,240`;

interface CatalogEntry {
  key: string;
  name: string;
  icon: LucideIcon;
  description: string;
  match: string[];
}

const CATALOG: CatalogEntry[] = [
  { key: "weather", name: "Weather APIs", icon: Cloud, description: "NWS / NOAA forecasts, alerts, and storm tracks.", match: ["weather"] },
  { key: "gis", name: "GIS Providers", icon: MapIcon, description: "Hazard layers, basemaps, and spatial overlays.", match: ["gis"] },
  { key: "hospital", name: "Hospital Systems", icon: Hospital, description: "Bed registries and capacity feeds.", match: ["hospital"] },
  { key: "dispatch", name: "Emergency Dispatch", icon: Radio, description: "911 / CAD incident bridges.", match: ["call", "dispatch", "emergency"] },
  { key: "utility", name: "Utility Monitoring", icon: Zap, description: "Outage and restoration telemetry.", match: ["resource", "utility", "outage"] },
  { key: "rest", name: "REST APIs", icon: Database, description: "Custom internal service integrations.", match: ["api", "rest"] },
  { key: "csv", name: "CSV", icon: FileText, description: "Upload structured comma-separated data.", match: ["csv"] },
  { key: "excel", name: "Excel", icon: FileSpreadsheet, description: "Import .xlsx workbooks directly.", match: ["excel"] },
];

function matchSources(sources: DataSource[], entry: CatalogEntry): DataSource[] {
  return sources.filter((s) => entry.match.some((m) => s.source_type.toLowerCase().includes(m)));
}

export default function IntegrationPage() {
  const [tab, setTab] = useState<Tab>("catalog");
  const { data: overview } = useIntegrationOverview();
  const { data: pipeline } = usePipeline();
  const importCsv = useImportCsv();

  const [target, setTarget] = useState("hospitals");
  const [csv, setCsv] = useState(SAMPLE_CSV);
  const [testing, setTesting] = useState<string | null>(null);
  const [tested, setTested] = useState<Record<string, boolean>>({});

  const sources = overview?.sources ?? [];

  function runTest(key: string) {
    setTesting(key);
    setTimeout(() => {
      setTesting(null);
      setTested((t) => ({ ...t, [key]: true }));
    }, 900);
  }

  return (
    <div>
      <PageHeader
        question="Where does our data come from?"
        title="Data Integration Center"
        description="Connect external systems, import data, and monitor pipeline health. Imported data becomes first-class operational data."
      />

      <div className="mb-5 flex gap-1 border-b border-line">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium capitalize transition-colors ${
              tab === t ? "border-accent text-ink" : "border-transparent text-ink-faint hover:text-ink-muted"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── Catalog ── */}
      {tab === "catalog" && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {CATALOG.map((entry) => {
            const Icon = entry.icon;
            const matched = matchSources(sources, entry);
            const connected = matched.length > 0;
            const records = matched.reduce((sum, s) => sum + s.records_synced, 0);
            const health = connected
              ? Math.round(matched.reduce((s, m) => s + m.health_score, 0) / matched.length)
              : 0;
            const lastSync = matched
              .map((m) => m.last_sync_at)
              .filter(Boolean)
              .sort()
              .reverse()[0];
            const isTested = tested[entry.key];
            return (
              <Card key={entry.key} className="flex flex-col">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-bg-elevated text-ink-muted">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-ink">{entry.name}</h3>
                      <p className="text-xs text-ink-faint">
                        {connected ? `${matched.length} connected` : "Available"}
                      </p>
                    </div>
                  </div>
                  <StatusBadge
                    status={connected ? "normal" : "info"}
                    label={connected ? "Connected" : "Not connected"}
                  />
                </div>
                <p className="mt-3 text-xs text-ink-muted">{entry.description}</p>

                <div className="mt-4 grid grid-cols-3 gap-2 border-t border-line pt-3 text-xs">
                  <div>
                    <span className="text-ink-faint">Health</span>
                    <p className="text-ink">{connected ? `${health}%` : "—"}</p>
                  </div>
                  <div>
                    <span className="text-ink-faint">Records</span>
                    <p className="text-ink">{connected ? fmtCompact(records) : "—"}</p>
                  </div>
                  <div>
                    <span className="text-ink-faint">Last sync</span>
                    <p className="text-ink">{lastSync ? timeAgo(lastSync) : "—"}</p>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <button
                    onClick={() => runTest(entry.key)}
                    disabled={testing === entry.key}
                    className={cn("btn-ghost flex-1 text-xs", isTested && "border-status-normal/40 text-status-normal")}
                  >
                    {testing === entry.key ? (
                      <Spinner />
                    ) : isTested ? (
                      <>
                        <CheckCircle2 className="h-3.5 w-3.5" /> Connection OK
                      </>
                    ) : (
                      <>
                        <Plug className="h-3.5 w-3.5" /> Test connection
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setTab(entry.key === "csv" || entry.key === "excel" ? "import" : "connectors")}
                    className="btn-ghost text-xs"
                  >
                    <Settings2 className="h-3.5 w-3.5" /> Configure
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* ── Overview ── */}
      {tab === "overview" &&
        (sources.length === 0 ? (
          <EmptyState
            icon={Database}
            title="No connectors configured yet"
            hint="Connect a system from the Catalog or import a file to start building your operational picture."
            actions={[{ label: "Browse catalog", onClick: () => setTab("catalog"), variant: "primary" }]}
          />
        ) : (
          overview && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <Stat label="Connected Systems" value={overview.connected_systems} />
                <Stat label="Healthy" value={overview.healthy} accent="#22c55e" />
                <Stat label="Degraded / Offline" value={overview.degraded + overview.offline} accent="#f59e0b" />
                <Stat label="Records Synced" value={fmtCompact(overview.total_records_synced)} />
              </div>
              <Card>
                <CardHeader
                  title="Connector Health"
                  subtitle={`Avg health ${overview.avg_health_score.toFixed(0)}% · last sync ${overview.last_sync_at ? timeAgo(overview.last_sync_at) : "—"}`}
                  icon={<Database className="h-4 w-4" />}
                />
                <div className="space-y-3">
                  {overview.sources.map((s) => (
                    <div key={s.id} className="flex items-center gap-4">
                      <div className="w-64 min-w-0">
                        <p className="truncate text-sm text-ink">{s.name}</p>
                        <p className="text-xs text-ink-faint">{titleCase(s.source_type)}</p>
                      </div>
                      <div className="flex-1">
                        <ProgressBar value={s.health_score} color={s.health_score > 70 ? "#22c55e" : s.health_score > 40 ? "#f59e0b" : "#ef4444"} />
                      </div>
                      <StatusBadge status={s.status === "healthy" ? "normal" : s.status === "degraded" ? "warning" : "critical"} label={titleCase(s.status)} />
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )
        ))}

      {/* ── Connectors ── */}
      {tab === "connectors" &&
        (sources.length === 0 ? (
          <EmptyState
            icon={Plug}
            title="No connectors yet"
            hint="Your configured data sources will appear here with status, health, and sync history."
            actions={[{ label: "Browse catalog", onClick: () => setTab("catalog"), variant: "primary" }]}
          />
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {sources.map((s) => (
              <Card key={s.id}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-ink">{s.name}</h3>
                    <p className="mt-0.5 text-xs text-ink-faint">{titleCase(s.source_type)}</p>
                  </div>
                  <StatusBadge status={s.status === "healthy" ? "normal" : s.status === "degraded" ? "warning" : "critical"} label={titleCase(s.status)} />
                </div>
                <p className="mt-2 truncate font-mono text-xs text-ink-muted">{s.endpoint}</p>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div><span className="text-ink-faint">Records</span><p className="text-ink">{fmtNumber(s.records_synced)}</p></div>
                  <div><span className="text-ink-faint">Interval</span><p className="text-ink">{s.sync_interval_minutes}m</p></div>
                  <div><span className="text-ink-faint">Last sync</span><p className="text-ink">{s.last_sync_at ? timeAgo(s.last_sync_at) : "—"}</p></div>
                  <div><span className="text-ink-faint">Health</span><p className="text-ink">{s.health_score.toFixed(0)}%</p></div>
                </div>
              </Card>
            ))}
          </div>
        ))}

      {/* ── Import ── */}
      {tab === "import" && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader title="CSV / Excel Import" subtitle="Paste CSV rows to ingest as first-class records" icon={<Upload className="h-4 w-4" />} />
            <label className="stat-label">Target entity</label>
            <select className="input mt-1" value={target} onChange={(e) => setTarget(e.target.value)}>
              {["hospitals", "shelters", "resources", "incidents"].map((t) => (
                <option key={t} value={t}>{titleCase(t)}</option>
              ))}
            </select>
            <label className="stat-label mt-3 block">CSV content</label>
            <textarea
              className="input mt-1 h-48 resize-none font-mono text-xs"
              value={csv}
              onChange={(e) => setCsv(e.target.value)}
            />
            <button
              onClick={() => importCsv.mutate({ target_entity: target, content: csv, filename: "manual.csv" })}
              disabled={importCsv.isPending}
              className="btn-primary mt-3"
            >
              {importCsv.isPending ? <Spinner className="text-white" /> : <Upload className="h-4 w-4" />} Run Import
            </button>
          </Card>
          <Card>
            <CardHeader title="Import Result" />
            {!importCsv.data ? (
              <p className="py-8 text-center text-sm text-ink-faint">Run an import to see results.</p>
            ) : (
              <div className="space-y-3">
                <StatusBadge
                  status={
                    (importCsv.data as { status: string }).status === "completed" ? "normal" :
                    (importCsv.data as { status: string }).status === "partial" ? "warning" : "critical"
                  }
                  label={titleCase((importCsv.data as { status: string }).status)}
                />
                <div className="grid grid-cols-3 gap-2 text-center">
                  <Stat label="Total" value={(importCsv.data as { records_total: number }).records_total} />
                  <Stat label="Processed" value={(importCsv.data as { records_processed: number }).records_processed} accent="#22c55e" />
                  <Stat label="Failed" value={(importCsv.data as { records_failed: number }).records_failed} accent="#ef4444" />
                </div>
                <p className="text-xs text-ink-faint">Duration: {(importCsv.data as { duration_ms: number }).duration_ms} ms</p>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* ── Pipeline ── */}
      {tab === "pipeline" && pipeline && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <Stat label="Pipeline Health" value={`${pipeline.pipeline_health.toFixed(0)}%`} accent="#22c55e" />
            <Stat label="Records Processed" value={fmtCompact(pipeline.records_processed)} />
            <Stat label="Failed Records" value={pipeline.records_failed} accent="#ef4444" />
            <Stat label="Avg Duration" value={`${pipeline.avg_duration_ms.toFixed(0)}ms`} />
          </div>
          <Card>
            <CardHeader title="Sync History" subtitle="Recent import & sync jobs" icon={<Activity className="h-4 w-4" />} />
            <div className="space-y-2">
              {pipeline.recent_jobs.length === 0 && (
                <p className="py-6 text-center text-sm text-ink-faint">No import jobs yet.</p>
              )}
              {pipeline.recent_jobs.map((j) => (
                <div key={j.id} className="flex items-center justify-between rounded-lg border border-line bg-bg-soft px-3 py-2 text-sm">
                  <div>
                    <p className="text-ink">{titleCase(j.target_entity)} · {titleCase(j.source_type)}</p>
                    <p className="text-xs text-ink-faint">{j.records_processed}/{j.records_total} processed · {timeAgo(j.created_at)}</p>
                  </div>
                  <StatusBadge status={j.status === "completed" ? "normal" : j.status === "partial" ? "warning" : j.status === "failed" ? "critical" : "info"} label={titleCase(j.status)} />
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="panel p-4">
      <p className="stat-label">{label}</p>
      <p className="mt-1 text-2xl font-bold" style={{ color: accent ?? "#e6edf6" }}>{value}</p>
    </div>
  );
}

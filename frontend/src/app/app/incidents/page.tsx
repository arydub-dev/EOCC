"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { DataTable, Pagination, type Column } from "@/components/data-table";
import { FilterSelect, SearchInput, Toolbar } from "@/components/toolbar";
import { StatusBadge, Tag } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/ui/primitives";
import { useIncident, useIncidents } from "@/lib/hooks";
import { fmtNumber, scoreColor, timeAgo, titleCase } from "@/lib/utils";
import type { Incident } from "@/lib/types";

const TYPES = [
  "wildfire", "flood", "hurricane", "earthquake", "industrial_accident",
  "disease_outbreak", "infrastructure_failure", "severe_storm",
];
const STATUSES = ["monitoring", "active", "escalating", "contained", "resolved"];

export default function IncidentsPage() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number | null>(null);

  const { data, isLoading } = useIncidents({ search, incident_type: type, status, page, page_size: 15 });

  const columns: Column<Incident>[] = [
    { key: "name", header: "Incident", render: (r) => (
      <div>
        <p className="font-medium text-ink">{r.name}</p>
        <p className="text-xs text-ink-faint">{titleCase(r.incident_type)} · {r.region ?? "—"}</p>
      </div>
    ) },
    { key: "severity_score", header: "Severity", render: (r) => (
      <div className="flex items-center gap-2">
        <span className="font-mono font-semibold" style={{ color: scoreColor(r.severity_score) }}>
          {r.severity_score.toFixed(0)}
        </span>
        <span className="text-xs text-ink-faint">/100</span>
      </div>
    ) },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "population_impacted", header: "Impacted", align: "right", render: (r) => fmtNumber(r.population_impacted) },
    { key: "radius_km", header: "Radius", align: "right", render: (r) => `${r.radius_km.toFixed(0)} km` },
    { key: "started_at", header: "Started", align: "right", render: (r) => <span className="text-ink-muted">{timeAgo(r.started_at)}</span> },
  ];

  return (
    <div>
      <PageHeader
        question="What is happening?"
        title="Incident Management"
        description="Track and triage active emergencies with severity scoring, timelines and response history."
      />
      <Toolbar>
        <div className="w-64"><SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search incidents…" /></div>
        <FilterSelect value={type} onChange={(v) => { setType(v); setPage(1); }} options={TYPES} placeholder="All types" />
        <FilterSelect value={status} onChange={(v) => { setStatus(v); setPage(1); }} options={STATUSES} placeholder="All statuses" />
      </Toolbar>

      <DataTable columns={columns} rows={data?.items ?? []} loading={isLoading} onRowClick={(r) => setSelected(r.id)} />
      {data && <Pagination page={data.page} pages={data.pages} total={data.total} onPage={setPage} />}

      {selected !== null && <IncidentDrawer id={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}

function IncidentDrawer({ id, onClose }: { id: number; onClose: () => void }) {
  const { data, isLoading } = useIncident(id);

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/50" onClick={onClose}>
      <div className="h-full w-full max-w-lg overflow-y-auto border-l border-line bg-bg-panel p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-start justify-between">
          <h2 className="text-lg font-bold text-ink">{data?.name ?? "Incident"}</h2>
          <button onClick={onClose} className="text-ink-faint hover:text-ink"><X className="h-5 w-5" /></button>
        </div>
        {isLoading || !data ? (
          <LoadingPanel />
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-2">
              <StatusBadge status={data.status} />
              <Tag>{titleCase(data.incident_type)}</Tag>
              {data.region && <Tag>{data.region}</Tag>}
            </div>
            <p className="text-sm text-ink-muted">{data.description}</p>
            <div className="grid grid-cols-2 gap-3">
              <Stat label="Severity Score" value={`${data.severity_score.toFixed(0)}/100`} color={scoreColor(data.severity_score)} />
              <Stat label="Base Severity" value={`${data.severity}/5`} />
              <Stat label="Population Impacted" value={fmtNumber(data.population_impacted)} />
              <Stat label="Radius" value={`${data.radius_km.toFixed(0)} km`} />
              <Stat label="Started" value={timeAgo(data.started_at)} />
              <Stat label="Est. Duration" value={data.estimated_duration_hours ? `${data.estimated_duration_hours.toFixed(0)} h` : "—"} />
            </div>

            <div>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-faint">Event Timeline</h3>
              <div className="space-y-3 border-l border-line pl-4">
                {data.events?.map((e) => (
                  <div key={e.id} className="relative">
                    <span className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-accent" />
                    <p className="text-sm font-medium text-ink">{titleCase(e.event_type)}</p>
                    <p className="text-xs text-ink-muted">{e.description}</p>
                    <p className="mt-0.5 text-[10px] text-ink-faint">{new Date(e.occurred_at).toLocaleString()}</p>
                  </div>
                ))}
                {(!data.events || data.events.length === 0) && (
                  <p className="text-sm text-ink-faint">No recorded events.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-lg border border-line bg-bg-soft p-3">
      <p className="stat-label">{label}</p>
      <p className="mt-1 text-sm font-semibold" style={{ color: color ?? undefined }}>{value}</p>
    </div>
  );
}

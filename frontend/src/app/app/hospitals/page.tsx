"use client";

import { useState } from "react";
import { PageHeader } from "@/components/page-header";
import { DataTable, Pagination, type Column } from "@/components/data-table";
import { SearchInput, Toolbar } from "@/components/toolbar";
import { StatusBadge } from "@/components/ui/badge";
import { ProgressBar } from "@/components/ui/primitives";
import { useHospitals } from "@/lib/hooks";
import { fmtNumber, scoreColor } from "@/lib/utils";
import type { Hospital } from "@/lib/types";

export default function HospitalsPage() {
  const [search, setSearch] = useState("");
  const [atRisk, setAtRisk] = useState(false);
  const [page, setPage] = useState(1);

  const { data, isLoading } = useHospitals({ search, at_risk: atRisk, page, page_size: 15, sort_by: "stress_score" });

  const columns: Column<Hospital>[] = [
    { key: "name", header: "Hospital", render: (r) => (
      <div>
        <p className="font-medium text-ink">{r.name}</p>
        <p className="text-xs text-ink-faint">{r.region ?? "—"}</p>
      </div>
    ) },
    { key: "stress_score", header: "Stress", render: (r) => (
      <span className="font-mono font-semibold" style={{ color: scoreColor(r.stress_score) }}>{r.stress_score.toFixed(0)}</span>
    ) },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "bed", header: "Beds", render: (r) => (
      <Bar label={`${r.occupied_beds}/${r.total_beds}`} pct={r.bed_occupancy_pct} />
    ) },
    { key: "icu", header: "ICU", render: (r) => (
      <Bar label={`${r.icu_occupied}/${r.icu_beds}`} pct={r.icu_occupancy_pct} />
    ) },
    { key: "er", header: "ER Load", render: (r) => (
      <Bar label={`${r.er_patients}/${r.er_capacity}`} pct={r.er_load_pct} />
    ) },
    { key: "staff", header: "Staff", align: "right", render: (r) => <span className="text-ink-muted">{fmtNumber(r.staff_on_duty)}/{fmtNumber(r.staff_required)}</span> },
  ];

  return (
    <div>
      <PageHeader
        question="Is the healthcare system holding?"
        title="Hospital Operations"
        description="Monitor capacity, ICU occupancy and ER load. Hospitals at risk are surfaced for load-balancing."
      />
      <Toolbar>
        <div className="w-64"><SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search hospitals…" /></div>
        <button
          onClick={() => { setAtRisk((v) => !v); setPage(1); }}
          className={atRisk ? "btn-primary" : "btn-ghost"}
        >
          At-risk only
        </button>
      </Toolbar>
      <DataTable columns={columns} rows={data?.items ?? []} loading={isLoading} />
      {data && <Pagination page={data.page} pages={data.pages} total={data.total} onPage={setPage} />}
    </div>
  );
}

function Bar({ label, pct }: { label: string; pct: number }) {
  const color = pct > 95 ? "#ef4444" : pct > 80 ? "#f59e0b" : "#22c55e";
  return (
    <div className="w-28">
      <div className="mb-1 flex justify-between text-xs text-ink-muted">
        <span>{label}</span>
        <span>{pct.toFixed(0)}%</span>
      </div>
      <ProgressBar value={pct} color={color} />
    </div>
  );
}

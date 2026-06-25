"use client";

import { useState } from "react";
import { Droplet, Utensils } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { DataTable, Pagination, type Column } from "@/components/data-table";
import { FilterSelect, SearchInput, Toolbar } from "@/components/toolbar";
import { StatusBadge } from "@/components/ui/badge";
import { ProgressBar } from "@/components/ui/primitives";
import { useShelters } from "@/lib/hooks";
import { scoreColor } from "@/lib/utils";
import type { Shelter } from "@/lib/types";

const STATUSES = ["open", "near_capacity", "full", "closed"];

export default function SheltersPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useShelters({ search, status, page, page_size: 15, sort_by: "utilization_score" });

  const columns: Column<Shelter>[] = [
    { key: "name", header: "Shelter", render: (r) => (
      <div>
        <p className="font-medium text-ink">{r.name}</p>
        <p className="text-xs text-ink-faint">{r.region ?? "—"}</p>
      </div>
    ) },
    { key: "utilization_score", header: "Strain", render: (r) => (
      <span className="font-mono font-semibold" style={{ color: scoreColor(r.utilization_score) }}>{r.utilization_score.toFixed(0)}</span>
    ) },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "occupancy", header: "Occupancy", render: (r) => (
      <div className="w-32">
        <div className="mb-1 flex justify-between text-xs text-ink-muted">
          <span>{r.occupancy}/{r.capacity}</span>
          <span>{r.occupancy_pct.toFixed(0)}%</span>
        </div>
        <ProgressBar value={r.occupancy_pct} color={r.occupancy_pct > 95 ? "#ef4444" : r.occupancy_pct > 85 ? "#f59e0b" : "#22c55e"} />
      </div>
    ) },
    { key: "supplies", header: "Supplies", render: (r) => (
      <div className="flex items-center gap-3 text-xs">
        <span className="flex items-center gap-1" style={{ color: r.food_supply_days < 2 ? "#ef4444" : "#8a99ad" }}>
          <Utensils className="h-3 w-3" /> {r.food_supply_days.toFixed(1)}d
        </span>
        <span className="flex items-center gap-1" style={{ color: r.water_supply_days < 2 ? "#ef4444" : "#8a99ad" }}>
          <Droplet className="h-3 w-3" /> {r.water_supply_days.toFixed(1)}d
        </span>
      </div>
    ) },
    { key: "medical_staff", header: "Med Staff", align: "right", render: (r) => <span className="text-ink-muted">{r.medical_staff}</span> },
  ];

  return (
    <div>
      <PageHeader
        question="Where are people sheltering?"
        title="Shelter Operations"
        description="Track occupancy, supply buffers and overcrowding risk across the mass-care network."
      />
      <Toolbar>
        <div className="w-64"><SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search shelters…" /></div>
        <FilterSelect value={status} onChange={(v) => { setStatus(v); setPage(1); }} options={STATUSES} placeholder="All statuses" />
      </Toolbar>
      <DataTable columns={columns} rows={data?.items ?? []} loading={isLoading} />
      {data && <Pagination page={data.page} pages={data.pages} total={data.total} onPage={setPage} />}
    </div>
  );
}

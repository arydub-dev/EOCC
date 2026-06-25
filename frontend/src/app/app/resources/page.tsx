"use client";

import { useState } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageHeader } from "@/components/page-header";
import { DataTable, Pagination, type Column } from "@/components/data-table";
import { FilterSelect, SearchInput, Toolbar } from "@/components/toolbar";
import { Card, CardHeader } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { ProgressBar } from "@/components/ui/primitives";
import { useResources, useResourceUtilization } from "@/lib/hooks";
import { fmtNumber, titleCase } from "@/lib/utils";
import type { Resource } from "@/lib/types";

const TYPES = [
  "ambulance", "fire_truck", "medical_team", "rescue_team", "helicopter",
  "food_supply", "water_supply", "fuel_supply", "generator",
];
const STATUSES = ["available", "assigned", "en_route", "on_scene", "maintenance", "depleted"];

export default function ResourcesPage() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useResources({ search, resource_type: type, status, page, page_size: 15 });
  const { data: util } = useResourceUtilization();

  const chartData = util
    ? Object.entries(util.by_type).map(([k, v]) => ({
        name: titleCase(k),
        availability: v.availability_pct,
        total: v.total,
      }))
    : [];

  const columns: Column<Resource>[] = [
    { key: "name", header: "Resource", render: (r) => (
      <div>
        <p className="font-medium text-ink">{r.name}</p>
        <p className="text-xs text-ink-faint">{titleCase(r.resource_type)} · {r.region ?? "—"}</p>
      </div>
    ) },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "readiness", header: "Readiness", render: (r) => (
      <div className="w-28">
        <div className="mb-1 text-xs text-ink-muted">{r.readiness.toFixed(0)}%</div>
        <ProgressBar value={r.readiness} color={r.readiness > 70 ? "#22c55e" : r.readiness > 40 ? "#f59e0b" : "#ef4444"} />
      </div>
    ) },
    { key: "capacity", header: "Capacity", align: "right", render: (r) => `${fmtNumber(r.capacity)} ${r.capacity_unit ?? ""}` },
    { key: "home_base", header: "Home Base", align: "right", render: (r) => <span className="text-ink-muted">{r.home_base ?? "—"}</span> },
  ];

  return (
    <div>
      <PageHeader
        question="What do we have to deploy?"
        title="Resource Operations"
        description="Track availability, readiness and assignment of every operational asset across the response."
      />

      <div className="mb-5 grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader title="Availability by Resource Type" subtitle="Share of units currently available" />
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#5b6b80" }} interval={0} angle={-20} textAnchor="end" height={50} />
              <YAxis tick={{ fontSize: 11, fill: "#5b6b80" }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ background: "#16202f", border: "1px solid #1f2a3a", borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => [`${v.toFixed(0)}%`, "Available"]}
              />
              <Bar dataKey="availability" radius={[4, 4, 0, 0]}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={d.availability < 15 ? "#ef4444" : d.availability < 40 ? "#f59e0b" : "#3b82f6"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card>
          <CardHeader title="Fleet Summary" />
          <div className="space-y-2.5">
            {chartData.map((d) => (
              <div key={d.name} className="flex items-center justify-between text-sm">
                <span className="text-ink-muted">{d.name}</span>
                <span className="font-medium text-ink">{d.total} units · {d.availability.toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Toolbar>
        <div className="w-64"><SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search resources…" /></div>
        <FilterSelect value={type} onChange={(v) => { setType(v); setPage(1); }} options={TYPES} placeholder="All types" />
        <FilterSelect value={status} onChange={(v) => { setStatus(v); setPage(1); }} options={STATUSES} placeholder="All statuses" />
      </Toolbar>

      <DataTable columns={columns} rows={data?.items ?? []} loading={isLoading} />
      {data && <Pagination page={data.page} pages={data.pages} total={data.total} onPage={setPage} />}
    </div>
  );
}

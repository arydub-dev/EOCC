"use client";

import { useState } from "react";
import { Check, CheckCheck } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { DataTable, Pagination, type Column } from "@/components/data-table";
import { FilterSelect, Toolbar } from "@/components/toolbar";
import { StatusBadge } from "@/components/ui/badge";
import { useAlertAction, useAlerts } from "@/lib/hooks";
import { timeAgo, titleCase } from "@/lib/utils";
import type { Alert } from "@/lib/types";

const CATEGORIES = [
  "hospital_overload", "shelter_capacity", "resource_shortage",
  "incident_escalation", "utility_failure", "environmental",
];
const SEVERITIES = ["info", "warning", "critical", "emergency"];
const STATUSES = ["open", "acknowledged", "resolved"];

export default function AlertsPage() {
  const [category, setCategory] = useState("");
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("open");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useAlerts({ category, severity, status, page, page_size: 15 });
  const action = useAlertAction();

  const columns: Column<Alert>[] = [
    { key: "severity", header: "Severity", render: (r) => <StatusBadge status={r.severity} /> },
    { key: "title", header: "Alert", render: (r) => (
      <div>
        <p className="font-medium text-ink">{r.title}</p>
        <p className="max-w-md truncate text-xs text-ink-faint">{r.message}</p>
      </div>
    ) },
    { key: "category", header: "Category", render: (r) => <span className="text-xs text-ink-muted">{titleCase(r.category)}</span> },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "triggered_at", header: "Triggered", align: "right", render: (r) => <span className="text-ink-muted">{timeAgo(r.triggered_at)}</span> },
    { key: "actions", header: "", align: "right", render: (r) => (
      <div className="flex justify-end gap-1.5">
        {r.status === "open" && (
          <button
            onClick={(e) => { e.stopPropagation(); action.mutate({ id: r.id, action: "acknowledge" }); }}
            className="btn-ghost px-2 py-1 text-xs" title="Acknowledge"
          >
            <Check className="h-3.5 w-3.5" />
          </button>
        )}
        {r.status !== "resolved" && (
          <button
            onClick={(e) => { e.stopPropagation(); action.mutate({ id: r.id, action: "resolve" }); }}
            className="btn-ghost px-2 py-1 text-xs" title="Resolve"
          >
            <CheckCheck className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    ) },
  ];

  return (
    <div>
      <PageHeader
        question="What needs attention now?"
        title="Alert Management"
        description="Triage and resolve threshold-driven alerts through their full lifecycle: open → acknowledged → resolved."
      />
      <Toolbar>
        <FilterSelect value={status} onChange={(v) => { setStatus(v); setPage(1); }} options={STATUSES} placeholder="All statuses" />
        <FilterSelect value={severity} onChange={(v) => { setSeverity(v); setPage(1); }} options={SEVERITIES} placeholder="All severities" />
        <FilterSelect value={category} onChange={(v) => { setCategory(v); setPage(1); }} options={CATEGORIES} placeholder="All categories" />
      </Toolbar>
      <DataTable columns={columns} rows={data?.items ?? []} loading={isLoading} emptyLabel="No alerts match the filters." />
      {data && <Pagination page={data.page} pages={data.pages} total={data.total} onPage={setPage} />}
    </div>
  );
}

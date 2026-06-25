"use client";

import { useState } from "react";
import { Download, ScrollText, Search } from "lucide-react";
import { useAuditLog } from "@/lib/hooks";
import { getToken } from "@/lib/api";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState, LoadingPanel } from "@/components/ui/primitives";
import { fmtDateTime, titleCase } from "@/lib/utils";
import type { AuditEntry } from "@/lib/types";

const CATEGORIES = ["", "security", "incident", "configuration", "data_import", "user_management", "general"];

const CATEGORY_COLOR: Record<string, string> = {
  security: "text-status-critical border-status-critical/30 bg-status-critical/10",
  configuration: "text-status-warning border-status-warning/30 bg-status-warning/10",
  data_import: "text-status-info border-status-info/30 bg-status-info/10",
  user_management: "text-status-watch border-status-watch/30 bg-status-watch/10",
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function AuditCenterPage() {
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState("");
  const [actorEmail, setActorEmail] = useState("");
  const [search, setSearch] = useState("");

  const { data, isLoading, error } = useAuditLog({
    page,
    page_size: 25,
    category: category || undefined,
    actor_email: actorEmail || undefined,
    search: search || undefined,
  });

  async function exportCsv() {
    const url = new URL(`${API_BASE}/audit/export`);
    if (category) url.searchParams.set("category", category);
    if (actorEmail) url.searchParams.set("actor_email", actorEmail);
    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${getToken()}` },
      credentials: "include",
    });
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "audit-log.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  if (error) {
    return (
      <EmptyState
        icon={ScrollText}
        title="Audit Center unavailable"
        hint="You need the Audit.View permission to view the audit trail."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between border-b border-line pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-ink">Audit Center</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Immutable, tamper-evident record of every significant action. Append-only by design.
          </p>
        </div>
        <button onClick={exportCsv} className="btn-secondary text-xs">
          <Download className="mr-1.5 h-3.5 w-3.5" /> Export CSV
        </button>
      </div>

      <Card>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-faint" />
            <input
              className="input pl-8 text-sm"
              placeholder="Search actions…"
              value={search}
              onChange={(e) => {
                setPage(1);
                setSearch(e.target.value);
              }}
            />
          </div>
          <input
            className="input text-sm"
            placeholder="Actor email"
            value={actorEmail}
            onChange={(e) => {
              setPage(1);
              setActorEmail(e.target.value);
            }}
          />
          <select
            className="input text-sm"
            value={category}
            onChange={(e) => {
              setPage(1);
              setCategory(e.target.value);
            }}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c ? titleCase(c) : "All categories"}
              </option>
            ))}
          </select>
        </div>

        {isLoading ? (
          <LoadingPanel label="Loading audit trail…" />
        ) : !data || data.items.length === 0 ? (
          <EmptyState
            icon={ScrollText}
            title="No audit records"
            hint="Actions performed in this workspace will appear here."
          />
        ) : (
          <>
            <div className="overflow-x-auto rounded-lg border border-line">
              <table className="w-full text-sm">
                <thead className="bg-bg-soft text-left text-xs text-ink-faint">
                  <tr>
                    <th className="px-3 py-2 font-medium">When</th>
                    <th className="px-3 py-2 font-medium">Actor</th>
                    <th className="px-3 py-2 font-medium">Category</th>
                    <th className="px-3 py-2 font-medium">Action</th>
                    <th className="px-3 py-2 font-medium">Entity</th>
                    <th className="px-3 py-2 font-medium">IP</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {data.items.map((e: AuditEntry) => (
                    <tr key={e.id} className="align-top">
                      <td className="whitespace-nowrap px-3 py-2 text-ink-muted">{fmtDateTime(e.created_at)}</td>
                      <td className="px-3 py-2 text-ink">{e.actor_email ?? "system"}</td>
                      <td className="px-3 py-2">
                        <span className={`chip ${CATEGORY_COLOR[e.category] ?? ""}`}>{titleCase(e.category)}</span>
                      </td>
                      <td className="px-3 py-2 text-ink">{titleCase(e.action)}</td>
                      <td className="px-3 py-2 text-ink-muted">
                        {e.entity_type ? `${e.entity_type}${e.entity_id ? ` #${e.entity_id}` : ""}` : "—"}
                      </td>
                      <td className="px-3 py-2 text-ink-faint">{e.ip_address ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-3 flex items-center justify-between text-xs text-ink-faint">
              <span>
                {data.total} records · page {data.page} of {data.pages}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="btn-secondary text-xs disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= data.pages}
                  className="btn-secondary text-xs disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}

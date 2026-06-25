"use client";

import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Building2,
  ClipboardList,
  Gauge,
  Users,
} from "lucide-react";
import { Card, CardHeader } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { ScoreRing } from "@/components/score-ring";
import { LoadingPanel, ProgressBar } from "@/components/ui/primitives";
import { useMissionControl } from "@/lib/hooks";
import { cn, fmtCompact, fmtNumber, statusClasses, timeAgo, titleCase } from "@/lib/utils";
import type { MetricCard } from "@/lib/types";

function MetricTile({ m }: { m: MetricCard }) {
  const display =
    m.unit === "people" || m.value >= 10000 ? fmtCompact(m.value) : fmtNumber(m.value);
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between">
        <p className="stat-label">{m.label}</p>
        <span className={cn("h-2 w-2 rounded-full", statusClasses(m.status).split(" ")[0].replace("text-", "bg-"))} />
      </div>
      <p className="mt-2 text-2xl font-bold text-ink">
        {display}
        {m.unit && m.unit !== "people" && <span className="ml-1 text-sm font-medium text-ink-faint">{m.unit}</span>}
      </p>
      {m.detail && <p className="mt-1 text-xs text-ink-faint">{m.detail}</p>}
    </div>
  );
}

export default function MissionControlPage() {
  const { data, isLoading } = useMissionControl();

  if (isLoading || !data) return <LoadingPanel />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 border-b border-line pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-accent">
            What is happening · Why · What to do next
          </p>
          <h1 className="text-xl font-bold tracking-tight text-ink">Mission Control</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Unified operational picture across incidents, healthcare, mass care and resources.
          </p>
        </div>
        <StatusBadge status={data.health_status} label={`System ${titleCase(data.health_status)}`} />
      </div>

      {/* Top: health + headline metrics */}
      <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
        <Card className="flex flex-col items-center justify-center text-center">
          <CardHeader title="Emergency Health" subtitle="Composite system score" icon={<Gauge className="h-4 w-4" />} />
          <ScoreRing value={data.overall_health_score} invertColor label="Health" caption={titleCase(data.health_status)} />
          <p className="mt-3 text-xs text-ink-faint">
            {data.active_incidents} active incidents · {data.open_alerts} open alerts
          </p>
        </Card>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
          {data.metrics.map((m) => (
            <MetricTile key={m.key} m={m} />
          ))}
        </div>
      </div>

      {/* Middle: recommended actions + critical alerts */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader
            title="Recommended Actions"
            subtitle="Prioritized, explainable decision support"
            icon={<ClipboardList className="h-4 w-4" />}
          />
          <div className="space-y-2.5">
            {data.recommended_actions.map((a) => (
              <div key={a.priority} className="rounded-lg border border-line bg-bg-soft p-3">
                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-accent/15 text-xs font-bold text-accent">
                    {a.priority}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-ink">{a.title}</p>
                      <span className="text-[10px] uppercase tracking-wider text-ink-faint">
                        {Math.round(a.confidence * 100)}% conf
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-ink-muted">{a.rationale}</p>
                    <p className="mt-1.5 text-[11px] text-accent">→ {a.impact}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Critical Alerts"
            subtitle="Highest-severity unresolved alerts"
            icon={<AlertTriangle className="h-4 w-4" />}
            action={
              <Link href="/app/alerts" className="flex items-center gap-1 text-xs text-accent hover:underline">
                All alerts <ArrowRight className="h-3 w-3" />
              </Link>
            }
          />
          <div className="space-y-2">
            {data.critical_alerts_list.length === 0 && (
              <p className="py-8 text-center text-sm text-ink-faint">No critical alerts. System nominal.</p>
            )}
            {data.critical_alerts_list.map((alert) => (
              <div key={alert.id} className="flex items-start justify-between gap-3 rounded-lg border border-line bg-bg-soft p-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-ink">{alert.title}</p>
                  <p className="mt-0.5 truncate text-xs text-ink-faint">{alert.message}</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <StatusBadge status={alert.severity} />
                  <span className="text-[10px] text-ink-faint">{timeAgo(alert.triggered_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Bottom: situation report + quick stats */}
      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader title="Situation Report" subtitle="Auto-generated SITREP" icon={<Activity className="h-4 w-4" />} />
          <pre className="whitespace-pre-wrap rounded-lg border border-line bg-bg p-4 font-mono text-xs leading-relaxed text-ink-muted">
            {data.situation_report}
          </pre>
        </Card>

        <Card>
          <CardHeader title="Capacity At A Glance" icon={<Building2 className="h-4 w-4" />} />
          <div className="space-y-4">
            <CapacityRow label="Hospital capacity" pct={data.hospital_capacity_pct} note={`${data.hospitals_at_risk} at risk`} />
            <CapacityRow label="Shelter utilization" pct={data.shelter_utilization_pct} note={`${data.shelters_overcrowded} overcrowded`} />
            <CapacityRow label="Resource availability" pct={data.resource_availability_pct} note={`${data.resource_readiness_pct.toFixed(0)}% readiness`} invert />
            <div className="flex items-center gap-2 border-t border-line pt-3 text-sm text-ink-muted">
              <Users className="h-4 w-4 text-ink-faint" />
              {fmtNumber(data.population_impacted)} people impacted
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function CapacityRow({ label, pct, note, invert }: { label: string; pct: number; note: string; invert?: boolean }) {
  const color = invert ? (pct < 30 ? "#ef4444" : pct < 50 ? "#f59e0b" : "#22c55e") : pct > 90 ? "#ef4444" : pct > 75 ? "#f59e0b" : "#22c55e";
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="text-ink-muted">{label}</span>
        <span className="font-medium text-ink">{pct.toFixed(0)}%</span>
      </div>
      <ProgressBar value={pct} color={color} />
      <p className="mt-1 text-[11px] text-ink-faint">{note}</p>
    </div>
  );
}

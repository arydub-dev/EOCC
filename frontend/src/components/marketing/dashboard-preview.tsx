"use client";

import { Activity, AlertTriangle, Gauge, Radio, ShieldAlert } from "lucide-react";

const BARS = [38, 62, 45, 78, 56, 88, 64, 72, 50, 84, 60, 92];

export function DashboardPreview() {
  return (
    <div className="relative">
      <div className="pointer-events-none absolute -inset-6 rounded-[28px] bg-accent/10 blur-3xl" />
      <div className="relative overflow-hidden rounded-2xl border border-line bg-bg-panel/90 shadow-panel backdrop-blur">
        {/* window chrome */}
        <div className="flex items-center gap-2 border-b border-line px-4 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <div className="ml-3 flex items-center gap-1.5 text-[11px] text-ink-faint">
            <Radio className="h-3 w-3 text-status-normal" /> Mission Control · Live
          </div>
          <span className="ml-auto chip border-status-normal/30 bg-status-normal/10 text-status-normal">
            <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-status-normal" /> Operational
          </span>
        </div>

        <div className="grid gap-3 p-4 sm:grid-cols-[150px_1fr]">
          {/* health ring */}
          <div className="flex flex-col items-center justify-center rounded-xl border border-line bg-bg-soft p-4">
            <div className="relative flex h-24 w-24 items-center justify-center">
              <svg viewBox="0 0 100 100" className="h-24 w-24 -rotate-90">
                <circle cx="50" cy="50" r="42" fill="none" stroke="#1f2a3a" strokeWidth="8" />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 42}`}
                  strokeDashoffset={`${2 * Math.PI * 42 * (1 - 0.82)}`}
                />
              </svg>
              <div className="absolute text-center">
                <p className="text-xl font-bold text-ink">82</p>
                <p className="text-[9px] uppercase tracking-wider text-ink-faint">Health</p>
              </div>
            </div>
            <p className="mt-2 text-[11px] text-status-normal">System Stable</p>
          </div>

          {/* metrics */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { l: "Active Incidents", v: "14", i: Activity, c: "text-accent" },
              { l: "Open Alerts", v: "23", i: AlertTriangle, c: "text-status-warning" },
              { l: "Hospitals At Risk", v: "5", i: ShieldAlert, c: "text-status-critical" },
              { l: "Resource Ready", v: "78%", i: Gauge, c: "text-status-normal" },
              { l: "Shelters Used", v: "61%", i: Activity, c: "text-status-info" },
              { l: "Population", v: "1.2M", i: Activity, c: "text-ink" },
            ].map((m) => {
              const Icon = m.i;
              return (
                <div key={m.l} className="rounded-xl border border-line bg-bg-soft p-3">
                  <Icon className={`h-3.5 w-3.5 ${m.c}`} />
                  <p className="mt-2 text-lg font-bold text-ink">{m.v}</p>
                  <p className="text-[9px] uppercase tracking-wider text-ink-faint">{m.l}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* trend bars */}
        <div className="px-4 pb-4">
          <div className="rounded-xl border border-line bg-bg-soft p-4">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-[11px] font-medium text-ink-muted">Operational load · 12h</p>
              <p className="text-[10px] text-ink-faint">updated 30s ago</p>
            </div>
            <div className="flex h-20 items-end gap-1.5">
              {BARS.map((h, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t bg-gradient-to-t from-accent/30 to-accent"
                  style={{ height: `${h}%`, opacity: 0.55 + (i / BARS.length) * 0.45 }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* floating chips */}
      <div className="animate-floaty absolute -left-6 top-24 hidden rounded-xl border border-line bg-bg-panel/95 px-3 py-2 shadow-panel backdrop-blur md:block">
        <p className="text-[10px] uppercase tracking-wider text-ink-faint">Recommended</p>
        <p className="text-xs font-semibold text-ink">Pre-stage 3 medical teams →</p>
      </div>
      <div
        className="animate-floaty absolute -right-5 bottom-16 hidden rounded-xl border border-line bg-bg-panel/95 px-3 py-2 shadow-panel backdrop-blur md:block"
        style={{ animationDelay: "1.2s" }}
      >
        <p className="text-[10px] uppercase tracking-wider text-status-critical">Risk · High</p>
        <p className="text-xs font-semibold text-ink">Flood expansion — Sector 4</p>
      </div>
    </div>
  );
}

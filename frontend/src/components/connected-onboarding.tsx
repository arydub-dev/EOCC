"use client";

import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  Cloud,
  Database,
  FileSpreadsheet,
  FileText,
  Hospital,
  Map,
  Radio,
  Sparkles,
  Zap,
} from "lucide-react";
import { useLaunchDemo } from "@/lib/hooks";
import { Spinner } from "@/components/ui/primitives";

const INTEGRATIONS = [
  { icon: FileText, name: "Import CSV", desc: "Upload incidents, hospitals, resources" },
  { icon: FileSpreadsheet, name: "Import Excel", desc: "Bring in .xlsx workbooks" },
  { icon: Database, name: "Connect REST API", desc: "Pull from internal services" },
  { icon: Map, name: "Connect GIS", desc: "Hazard & basemap layers" },
  { icon: Cloud, name: "Connect Weather API", desc: "NWS / NOAA feeds" },
  { icon: Hospital, name: "Connect Hospital Systems", desc: "Bed & capacity registries" },
  { icon: Radio, name: "Emergency Management", desc: "911 / CAD dispatch bridges" },
  { icon: Zap, name: "Connect Utility Systems", desc: "Outage & restoration feeds" },
];

export function ConnectedOnboarding() {
  const launch = useLaunchDemo();

  return (
    <div className="mx-auto max-w-4xl">
      <div className="rounded-2xl border border-line bg-bg-panel p-8 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/12 text-accent">
          <Database className="h-7 w-7" />
        </div>
        <h1 className="mt-5 text-2xl font-bold tracking-tight text-ink">
          Your organization doesn&apos;t have operational data yet
        </h1>
        <p className="mx-auto mt-2 max-w-xl text-sm text-ink-muted">
          Connect a source or import a file to bring your operation online. You can also explore the
          platform instantly with a synthetic demo workspace.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
          <button
            onClick={() => launch.mutate()}
            disabled={launch.isPending}
            className="btn-primary"
          >
            {launch.isPending ? <Spinner className="text-white" /> : <Sparkles className="h-4 w-4" />}
            Launch demo data
          </button>
          <Link href="/app/integration" className="btn-ghost">
            Open Integration Center <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/documentation" className="btn-ghost">
            <BookOpen className="h-4 w-4" /> Read documentation
          </Link>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {INTEGRATIONS.map((it) => {
          const Icon = it.icon;
          return (
            <Link
              key={it.name}
              href="/app/integration"
              className="panel card-hover flex flex-col gap-2 p-4"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-bg-elevated text-ink-muted">
                <Icon className="h-4 w-4" />
              </div>
              <p className="text-sm font-medium text-ink">{it.name}</p>
              <p className="text-xs text-ink-faint">{it.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

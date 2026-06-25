import { Cloud, Database, FileSpreadsheet, FileText, Hospital, Map, Radio, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const ORIGIN_META: Record<string, { label: string; icon: typeof Database; cls: string }> = {
  demo: { label: "Demo Data", icon: Sparkles, cls: "border-accent/30 bg-accent/10 text-accent" },
  manual: { label: "Manual Entry", icon: FileText, cls: "border-line bg-bg-elevated text-ink-muted" },
  csv: { label: "CSV Import", icon: FileText, cls: "border-status-info/30 bg-status-info/10 text-status-info" },
  excel: { label: "Excel Import", icon: FileSpreadsheet, cls: "border-status-normal/30 bg-status-normal/10 text-status-normal" },
  api: { label: "API Feed", icon: Database, cls: "border-status-info/30 bg-status-info/10 text-status-info" },
  gis: { label: "GIS Feed", icon: Map, cls: "border-status-info/30 bg-status-info/10 text-status-info" },
  weather_feed: { label: "Weather Feed", icon: Cloud, cls: "border-status-info/30 bg-status-info/10 text-status-info" },
  hospital_system: { label: "Hospital System", icon: Hospital, cls: "border-status-normal/30 bg-status-normal/10 text-status-normal" },
  none: { label: "No Data", icon: Radio, cls: "border-line bg-bg-elevated text-ink-faint" },
};

export function DataSourceBadge({ origin, className }: { origin: string; className?: string }) {
  const meta = ORIGIN_META[origin] ?? ORIGIN_META.none;
  const Icon = meta.icon;
  return (
    <span
      className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium", meta.cls, className)}
      title={`Current data source: ${meta.label}`}
    >
      <Icon className="h-3 w-3" />
      {meta.label}
    </span>
  );
}

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmtNumber(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return new Intl.NumberFormat("en-US").format(Math.round(n));
}

export function fmtCompact(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(n);
}

export function fmtPct(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return `${n.toFixed(1)}%`;
}

export function timeAgo(iso: string): string {
  const then = new Date(iso).getTime();
  const diff = Date.now() - then;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function titleCase(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_COLORS: Record<string, string> = {
  normal: "text-status-normal border-status-normal/30 bg-status-normal/10",
  stable: "text-status-normal border-status-normal/30 bg-status-normal/10",
  watch: "text-status-watch border-status-watch/30 bg-status-watch/10",
  warning: "text-status-warning border-status-warning/30 bg-status-warning/10",
  elevated: "text-status-warning border-status-warning/30 bg-status-warning/10",
  critical: "text-status-critical border-status-critical/30 bg-status-critical/10",
  severe: "text-status-critical border-status-critical/30 bg-status-critical/10",
  emergency: "text-status-critical border-status-critical/40 bg-status-critical/15",
  info: "text-status-info border-status-info/30 bg-status-info/10",
  low: "text-status-normal border-status-normal/30 bg-status-normal/10",
  moderate: "text-status-watch border-status-watch/30 bg-status-watch/10",
  high: "text-status-warning border-status-warning/30 bg-status-warning/10",
};

export function statusClasses(status: string): string {
  return STATUS_COLORS[status?.toLowerCase()] ?? "text-ink-muted border-line bg-bg-elevated";
}

export function scoreColor(score: number): string {
  if (score >= 85) return "#ef4444";
  if (score >= 70) return "#f97316";
  if (score >= 50) return "#f59e0b";
  if (score >= 30) return "#eab308";
  return "#22c55e";
}

import Link from "next/link";
import { Loader2, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn("h-4 w-4 animate-spin text-ink-muted", className)} />;
}

export function LoadingPanel({ label = "Loading operational data…" }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 rounded-xl border border-line bg-bg-panel py-16 text-sm text-ink-muted">
      <Spinner /> {label}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton rounded-md", className)} />;
}

export function CardSkeleton() {
  return (
    <div className="panel space-y-3 p-5">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-7 w-16" />
      <Skeleton className="h-2 w-full" />
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-3 w-72" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-64 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    </div>
  );
}

interface EmptyAction {
  label: string;
  href?: string;
  onClick?: () => void;
  variant?: "primary" | "ghost";
  icon?: LucideIcon;
}

export function EmptyState({
  icon: Icon,
  title,
  hint,
  actions,
}: {
  icon?: LucideIcon;
  title: string;
  hint?: string;
  actions?: EmptyAction[];
}) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed border-line bg-bg-soft/60 px-6 py-14 text-center">
      {Icon && (
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-line bg-bg-panel text-ink-faint">
          <Icon className="h-6 w-6" />
        </div>
      )}
      <p className="text-sm font-semibold text-ink">{title}</p>
      {hint && <p className="mt-1.5 max-w-md text-xs text-ink-muted">{hint}</p>}
      {actions && actions.length > 0 && (
        <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
          {actions.map((a) => {
            const cls = a.variant === "primary" ? "btn-primary" : "btn-ghost";
            const ActionIcon = a.icon;
            const content = (
              <>
                {ActionIcon && <ActionIcon className="h-4 w-4" />}
                {a.label}
              </>
            );
            return a.href ? (
              <Link key={a.label} href={a.href} className={cls}>
                {content}
              </Link>
            ) : (
              <button key={a.label} onClick={a.onClick} className={cls}>
                {content}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function ProgressBar({ value, color }: { value: number; color?: string }) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-bg-elevated">
      <div
        className="h-full rounded-full transition-all"
        style={{ width: `${clamped}%`, background: color ?? "#3b82f6" }}
      />
    </div>
  );
}

export function SectionTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-ink-faint">{children}</h2>
      {right}
    </div>
  );
}

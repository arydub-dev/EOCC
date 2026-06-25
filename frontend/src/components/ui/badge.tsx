import { cn, statusClasses, titleCase } from "@/lib/utils";

export function StatusBadge({ status, label }: { status: string; label?: string }) {
  return (
    <span className={cn("pill", statusClasses(status))}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label ?? titleCase(status)}
    </span>
  );
}

export function Tag({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn("pill border-line bg-bg-elevated text-ink-muted", className)}>{children}</span>
  );
}

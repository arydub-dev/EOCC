import type { ReactNode } from "react";

export function PageHeader({
  title,
  description,
  actions,
  question,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  question?: string;
}) {
  return (
    <div className="mb-5 flex flex-col gap-3 border-b border-line pb-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {question && (
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-accent">{question}</p>
        )}
        <h1 className="text-xl font-bold tracking-tight text-ink">{title}</h1>
        {description && <p className="mt-1 max-w-2xl text-sm text-ink-muted">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

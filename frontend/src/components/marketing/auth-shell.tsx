import Link from "next/link";
import type { ReactNode } from "react";
import { Gauge, ShieldCheck } from "lucide-react";

export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="marketing-bg grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden border-r border-line p-12 lg:flex">
        <div className="grid-overlay pointer-events-none absolute inset-0" />
        <Link href="/" className="relative flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/15 text-accent">
            <Gauge className="h-6 w-6" />
          </div>
          <div>
            <p className="text-lg font-bold text-ink">EOCC</p>
            <p className="text-xs uppercase tracking-wider text-ink-faint">
              Emergency Operations Command Center
            </p>
          </div>
        </Link>

        <div className="relative max-w-md">
          <h2 className="text-3xl font-bold leading-tight text-ink">
            Turn fragmented crisis data into coordinated action.
          </h2>
          <p className="mt-4 text-sm text-ink-muted">
            A unified operational environment for incident management, resource coordination, risk
            intelligence, and decision support.
          </p>
          <div className="mt-5 space-y-2">
            {["What is happening?", "Why is it happening?", "What should we do next?"].map((q) => (
              <div key={q} className="flex items-center gap-2 text-sm font-medium text-ink">
                <ShieldCheck className="h-4 w-4 text-accent" /> {q}
              </div>
            ))}
          </div>
        </div>

        <p className="relative text-xs text-ink-faint">
          Trusted by government, healthcare, utilities, and critical infrastructure teams.
        </p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <Link href="/" className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
              <Gauge className="h-5 w-5" />
            </div>
            <span className="text-sm font-bold text-ink">EOCC</span>
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-ink">{title}</h1>
          {subtitle && <p className="mt-1.5 text-sm text-ink-muted">{subtitle}</p>}
          <div className="mt-6">{children}</div>
          {footer && <div className="mt-6 text-center text-sm text-ink-muted">{footer}</div>}
        </div>
      </div>
    </div>
  );
}

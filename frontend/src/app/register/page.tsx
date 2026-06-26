"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, Check, ShieldCheck } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { AuthShell } from "@/components/marketing/auth-shell";
import { Spinner } from "@/components/ui/primitives";

const DEMO_ROLES = [
  { role: "Administrator", email: "admin@eocc.gov", password: "admin123", blurb: "Full access — every module, users & security" },
  { role: "Emergency Manager", email: "manager@eocc.gov", password: "manager123", blurb: "Incident response & resource coordination" },
  { role: "Analyst", email: "analyst@eocc.gov", password: "analyst123", blurb: "Risk analysis & simulations" },
  { role: "Executive", email: "exec@eocc.gov", password: "exec123", blurb: "Read-only command view & briefings" },
];

export default function DemoAccessPage() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loadingRole, setLoadingRole] = useState<string | null>(null);

  async function enterDemo(email: string, password: string, role: string) {
    setError(null);
    setLoadingRole(role);
    try {
      await login(email, password, true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start the demo. Please try again.");
      setLoadingRole(null);
    }
  }

  const busy = loadingRole !== null;

  return (
    <AuthShell
      title="Explore the live demo"
      subtitle="No sign-up required. Step into a fully populated command center and see how EOCC works."
      footer={
        <>
          Already have credentials?{" "}
          <Link href="/login" className="font-medium text-accent hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <button
        type="button"
        disabled={busy}
        onClick={() => enterDemo(DEMO_ROLES[0].email, DEMO_ROLES[0].password, "primary")}
        className="btn-primary w-full"
      >
        {loadingRole === "primary" ? (
          <Spinner className="text-white" />
        ) : (
          <>
            Enter the demo <ArrowRight className="h-4 w-4" />
          </>
        )}
      </button>

      <div className="mt-5">
        <p className="stat-label mb-2">Or explore from a specific role</p>
        <div className="grid grid-cols-1 gap-2">
          {DEMO_ROLES.map((r) => (
            <button
              key={r.email}
              type="button"
              disabled={busy}
              onClick={() => enterDemo(r.email, r.password, r.role)}
              className="flex items-center justify-between rounded-lg border border-line bg-bg-soft px-3 py-2.5 text-left transition-colors hover:border-accent disabled:opacity-60"
            >
              <span className="min-w-0">
                <span className="block text-sm font-medium text-ink">{r.role}</span>
                <span className="block truncate text-xs text-ink-faint">{r.blurb}</span>
              </span>
              {loadingRole === r.role ? (
                <Spinner />
              ) : (
                <ArrowRight className="h-4 w-4 shrink-0 text-ink-faint" />
              )}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="mt-3 text-sm text-status-critical">{error}</p>}

      <ul className="mt-5 space-y-1.5">
        {["Pre-loaded with realistic operational data", "All 12 modules included", "Nothing to install or configure"].map((f) => (
          <li key={f} className="flex items-center gap-2 text-xs text-ink-muted">
            <Check className="h-3.5 w-3.5 text-status-normal" /> {f}
          </li>
        ))}
      </ul>

      <div className="mt-6 rounded-xl border border-line bg-bg-soft p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/12 text-accent">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-medium text-ink">Want EOCC for your organization?</p>
            <p className="mt-1 text-xs text-ink-muted">
              The demo runs on synthetic data. To deploy EOCC with your own data, users, and
              integrations, connect with our team.
            </p>
            <Link
              href="/contact"
              className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
            >
              Connect with us <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </AuthShell>
  );
}

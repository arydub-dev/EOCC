"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { AuthShell } from "@/components/marketing/auth-shell";
import { Spinner } from "@/components/ui/primitives";

const DEMO_ACCOUNTS = [
  { role: "Admin", email: "admin@eocc.gov", password: "admin123" },
  { role: "Emergency Manager", email: "manager@eocc.gov", password: "manager123" },
  { role: "Analyst", email: "analyst@eocc.gov", password: "analyst123" },
  { role: "Executive", email: "exec@eocc.gov", password: "exec123" },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [mfaCode, setMfaCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password, remember, mfaRequired ? mfaCode : undefined);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      if (message.toLowerCase().includes("mfa")) {
        setMfaRequired(true);
        setError(mfaRequired ? "Invalid MFA code. Try again." : null);
      } else {
        setError(message);
      }
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Sign in"
      subtitle="Welcome back to your operations command center."
      footer={
        <>
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-medium text-accent hover:underline">
            Create one
          </Link>
        </>
      }
    >
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="stat-label">Email</label>
          <input
            className="input mt-1"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            placeholder="you@agency.gov"
            required
          />
        </div>
        <div>
          <div className="flex items-center justify-between">
            <label className="stat-label">Password</label>
            <Link href="/forgot-password" className="text-xs text-accent hover:underline">
              Forgot?
            </Link>
          </div>
          <input
            className="input mt-1"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="••••••••"
            required
          />
        </div>
        {mfaRequired && (
          <div>
            <label className="stat-label">Authentication code</label>
            <input
              className="input mt-1 tracking-[0.4em]"
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ""))}
              inputMode="numeric"
              maxLength={6}
              placeholder="123456"
              autoFocus
              required
            />
            <p className="mt-1 text-xs text-ink-faint">
              Enter the 6-digit code from your authenticator app.
            </p>
          </div>
        )}
        <label className="flex items-center gap-2 text-xs text-ink-muted">
          <input
            type="checkbox"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
            className="h-3.5 w-3.5 rounded border-line bg-bg-soft accent-accent"
          />
          Remember me for 30 days
        </label>
        {error && <p className="text-sm text-status-critical">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? <Spinner className="text-white" /> : "Sign in"}
        </button>
      </form>

      <div className="mt-6">
        <p className="stat-label mb-2">Demo accounts (click to fill)</p>
        <div className="grid grid-cols-2 gap-2">
          {DEMO_ACCOUNTS.map((a) => (
            <button
              key={a.email}
              type="button"
              onClick={() => {
                setEmail(a.email);
                setPassword(a.password);
              }}
              className="rounded-lg border border-line bg-bg-soft px-3 py-2 text-left text-xs transition-colors hover:border-accent"
            >
              <p className="font-medium text-ink">{a.role}</p>
              <p className="truncate text-ink-faint">{a.email}</p>
            </button>
          ))}
        </div>
      </div>
    </AuthShell>
  );
}

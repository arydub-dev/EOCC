"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";
import { AuthShell } from "@/components/marketing/auth-shell";
import { Spinner } from "@/components/ui/primitives";

function ResetForm() {
  const params = useSearchParams();
  const router = useRouter();
  const [token, setToken] = useState(params.get("token") ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    try {
      await api("/auth/reset-password", { method: "POST", body: { token, new_password: password } });
      setDone(true);
      setTimeout(() => router.push("/login"), 1800);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="rounded-xl border border-line bg-bg-soft p-6 text-center">
        <CheckCircle2 className="mx-auto h-10 w-10 text-status-normal" />
        <p className="mt-3 text-sm font-medium text-ink">Password updated</p>
        <p className="mt-1 text-xs text-ink-muted">Redirecting you to sign in…</p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <div>
        <label className="stat-label">Reset token</label>
        <input
          className="input mt-1 font-mono text-xs"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Paste your reset token"
          required
        />
      </div>
      <div>
        <label className="stat-label">New password</label>
        <input
          className="input mt-1"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          placeholder="At least 6 characters"
          required
        />
      </div>
      {error && <p className="text-sm text-status-critical">{error}</p>}
      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? <Spinner className="text-white" /> : "Update password"}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <AuthShell
      title="Set a new password"
      subtitle="Choose a strong password for your account."
      footer={
        <Link href="/login" className="font-medium text-accent hover:underline">
          Back to sign in
        </Link>
      }
    >
      <Suspense fallback={<Spinner />}>
        <ResetForm />
      </Suspense>
    </AuthShell>
  );
}

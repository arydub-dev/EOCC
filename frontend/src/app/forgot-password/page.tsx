"use client";

import { useState } from "react";
import Link from "next/link";
import { MailCheck } from "lucide-react";
import { api } from "@/lib/api";
import { AuthShell } from "@/components/marketing/auth-shell";
import { Spinner } from "@/components/ui/primitives";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [token, setToken] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api<{ detail: string; reset_token: string }>("/auth/forgot-password", {
        method: "POST",
        body: { email },
      });
      setToken(res.reset_token);
      setSent(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Reset your password"
      subtitle="Enter your email and we'll send reset instructions."
      footer={
        <Link href="/login" className="font-medium text-accent hover:underline">
          Back to sign in
        </Link>
      }
    >
      {sent ? (
        <div className="rounded-xl border border-line bg-bg-soft p-5 text-center">
          <MailCheck className="mx-auto h-10 w-10 text-status-normal" />
          <p className="mt-3 text-sm font-medium text-ink">Check your inbox</p>
          <p className="mt-1 text-xs text-ink-muted">
            If an account exists for <span className="text-ink">{email}</span>, a reset link has been
            sent.
          </p>
          {token && (
            <div className="mt-4 rounded-lg border border-dashed border-accent/40 bg-accent/5 p-3 text-left">
              <p className="text-[11px] uppercase tracking-wider text-ink-faint">
                Demo: email delivery is mocked
              </p>
              <Link
                href={`/reset-password?token=${encodeURIComponent(token)}`}
                className="btn-primary mt-2 w-full"
              >
                Continue to reset password
              </Link>
            </div>
          )}
        </div>
      ) : (
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
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? <Spinner className="text-white" /> : "Send reset link"}
          </button>
        </form>
      )}
    </AuthShell>
  );
}

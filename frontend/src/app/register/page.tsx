"use client";

import { useState } from "react";
import Link from "next/link";
import { Check } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { AuthShell } from "@/components/marketing/auth-shell";
import { Spinner } from "@/components/ui/primitives";

export default function RegisterPage() {
  const { register } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    try {
      await register(email, password, fullName);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Set up your organization's command center in minutes."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-accent hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="stat-label">Full name</label>
          <input
            className="input mt-1"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Jordan Rivera"
            required
          />
        </div>
        <div>
          <label className="stat-label">Work email</label>
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
          <label className="stat-label">Password</label>
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
          {loading ? <Spinner className="text-white" /> : "Create account"}
        </button>
      </form>

      <ul className="mt-5 space-y-1.5">
        {["Free demo workspace", "No credit card required", "All 12 modules included"].map((f) => (
          <li key={f} className="flex items-center gap-2 text-xs text-ink-muted">
            <Check className="h-3.5 w-3.5 text-status-normal" /> {f}
          </li>
        ))}
      </ul>
      <p className="mt-4 text-center text-[11px] text-ink-faint">
        By creating an account you agree to our Terms and Privacy Policy.
      </p>
    </AuthShell>
  );
}

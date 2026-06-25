"use client";

import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  KeyRound,
  Lock,
  Monitor,
  ShieldCheck,
  Trash2,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import {
  useLoginActivity,
  useLogoutAll,
  useMfaDisable,
  useMfaEnable,
  useMfaSetup,
  useMySessions,
  useRevokeSession,
  useSecurityOverview,
} from "@/lib/hooks";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState, LoadingPanel, Spinner } from "@/components/ui/primitives";
import { fmtDateTime } from "@/lib/utils";

const GRADE_COLOR: Record<string, string> = {
  A: "text-status-normal",
  B: "text-status-normal",
  C: "text-status-warning",
  D: "text-status-warning",
  F: "text-status-critical",
};

export default function SecurityCenterPage() {
  const { user, refresh } = useAuth();
  const { data: overview, isLoading, error } = useSecurityOverview();
  const { data: activity } = useLoginActivity(20);
  const { data: sessions } = useMySessions();
  const revoke = useRevokeSession();
  const logoutAll = useLogoutAll();

  if (isLoading) return <LoadingPanel label="Assessing security posture…" />;
  if (error || !overview) {
    return (
      <EmptyState
        icon={Lock}
        title="Security Center unavailable"
        hint="You need the Security.View permission to view this page."
      />
    );
  }

  const policy = overview.password_policy;
  const activeSessions = (sessions ?? []).filter((s) => !s.revoked_at);

  return (
    <div className="space-y-6">
      <div className="border-b border-line pb-4">
        <h1 className="text-xl font-bold tracking-tight text-ink">Security Center</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Organization security posture, authentication activity, and session control.
        </p>
      </div>

      {/* Score + headline stats */}
      <div className="grid gap-4 lg:grid-cols-4">
        <Card className="lg:col-span-1">
          <CardHeader title="Security score" icon={<ShieldCheck className="h-4 w-4" />} />
          <div className="flex items-end gap-3">
            <span className="text-5xl font-bold text-ink">{overview.security_score}</span>
            <span className={`mb-1 text-2xl font-bold ${GRADE_COLOR[overview.grade] ?? "text-ink"}`}>
              {overview.grade}
            </span>
          </div>
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-bg-soft">
            <div
              className="h-full rounded-full bg-accent transition-all"
              style={{ width: `${overview.security_score}%` }}
            />
          </div>
        </Card>

        <div className="grid grid-cols-2 gap-4 lg:col-span-3 lg:grid-cols-4">
          <Stat label="MFA adoption" value={`${overview.mfa_adoption_pct}%`} hint={`${overview.mfa_enabled_users}/${overview.total_users} users`} />
          <Stat label="Active sessions" value={overview.active_sessions} />
          <Stat label="Failed logins 24h" value={overview.failed_logins_24h} warn={overview.failed_logins_24h > 5} />
          <Stat label="Locked accounts" value={overview.locked_users} warn={overview.locked_users > 0} />
          <Stat label="Successful logins 24h" value={overview.successful_logins_24h} />
          <Stat label="Audit events 7d" value={overview.audit_events_7d} />
          <Stat label="Security events 7d" value={overview.security_events_7d} />
          <Stat label="Verified users" value={`${overview.verified_users}/${overview.total_users}`} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Recommendations */}
        <Card>
          <CardHeader title="Recommendations" subtitle="Actions to strengthen your posture" />
          <ul className="space-y-2">
            {overview.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-ink-muted">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-status-warning" />
                {rec}
              </li>
            ))}
          </ul>
        </Card>

        {/* Password policy */}
        <Card>
          <CardHeader title="Password policy" subtitle="Enforced on every credential change" />
          <div className="grid grid-cols-2 gap-2 text-sm">
            <PolicyRow ok label={`Minimum ${policy.min_length} characters`} />
            <PolicyRow ok={policy.require_upper} label="Uppercase required" />
            <PolicyRow ok={policy.require_lower} label="Lowercase required" />
            <PolicyRow ok={policy.require_digit} label="Digit required" />
            <PolicyRow ok={policy.require_symbol} label="Symbol required" />
            <PolicyRow ok label={`Lockout after ${policy.lockout_threshold} fails`} />
          </div>
          <p className="mt-3 text-xs text-ink-faint">
            Accounts lock for {policy.lockout_minutes} minutes after {policy.lockout_threshold} failed
            attempts. Passwords are hashed with Argon2id.
          </p>
        </Card>
      </div>

      {/* MFA self-service */}
      <MfaCard mfaEnabled={!!user?.mfa_enabled} onChange={refresh} />

      {/* My sessions */}
      <Card>
        <CardHeader
          title="Your active sessions"
          subtitle="Devices currently signed in to your account"
          icon={<Monitor className="h-4 w-4" />}
          action={
            <button
              onClick={() => logoutAll.mutate()}
              disabled={logoutAll.isPending}
              className="btn-secondary text-xs"
            >
              {logoutAll.isPending ? <Spinner /> : "Sign out everywhere"}
            </button>
          }
        />
        {activeSessions.length === 0 ? (
          <p className="text-sm text-ink-faint">No active sessions.</p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-line">
            <table className="w-full text-sm">
              <thead className="bg-bg-soft text-left text-xs text-ink-faint">
                <tr>
                  <th className="px-3 py-2 font-medium">Device</th>
                  <th className="px-3 py-2 font-medium">IP address</th>
                  <th className="px-3 py-2 font-medium">Last used</th>
                  <th className="px-3 py-2 font-medium">Expires</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {activeSessions.map((s) => (
                  <tr key={s.id}>
                    <td className="px-3 py-2 text-ink">{s.device_label ?? "Unknown"}</td>
                    <td className="px-3 py-2 text-ink-muted">{s.ip_address ?? "—"}</td>
                    <td className="px-3 py-2 text-ink-muted">{s.last_used_at ? fmtDateTime(s.last_used_at) : "—"}</td>
                    <td className="px-3 py-2 text-ink-muted">{fmtDateTime(s.expires_at)}</td>
                    <td className="px-3 py-2 text-right">
                      <button
                        onClick={() => revoke.mutate(s.id)}
                        className="text-ink-faint hover:text-status-critical"
                        title="Revoke session"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Login activity */}
      <Card>
        <CardHeader title="Recent login activity" subtitle="Authentication attempts across the organization" />
        {!activity || activity.length === 0 ? (
          <p className="text-sm text-ink-faint">No login activity recorded yet.</p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-line">
            <table className="w-full text-sm">
              <thead className="bg-bg-soft text-left text-xs text-ink-faint">
                <tr>
                  <th className="px-3 py-2 font-medium">Result</th>
                  <th className="px-3 py-2 font-medium">Email</th>
                  <th className="px-3 py-2 font-medium">Reason</th>
                  <th className="px-3 py-2 font-medium">IP</th>
                  <th className="px-3 py-2 font-medium">When</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {activity.map((a) => (
                  <tr key={a.id}>
                    <td className="px-3 py-2">
                      {a.successful ? (
                        <span className="inline-flex items-center gap-1 text-xs text-status-normal">
                          <CheckCircle2 className="h-3.5 w-3.5" /> Success
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-status-critical">
                          <AlertTriangle className="h-3.5 w-3.5" /> Failed
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-ink">{a.email}</td>
                    <td className="px-3 py-2 text-ink-muted">{a.reason ?? "—"}</td>
                    <td className="px-3 py-2 text-ink-muted">{a.ip_address ?? "—"}</td>
                    <td className="px-3 py-2 text-ink-muted">{fmtDateTime(a.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}

function Stat({ label, value, hint, warn }: { label: string; value: string | number; hint?: string; warn?: boolean }) {
  return (
    <div className="rounded-lg border border-line bg-bg-soft p-4">
      <p className={`text-2xl font-bold ${warn ? "text-status-critical" : "text-ink"}`}>{value}</p>
      <p className="mt-1 text-[11px] uppercase tracking-wider text-ink-faint">{label}</p>
      {hint && <p className="mt-0.5 text-[11px] text-ink-faint">{hint}</p>}
    </div>
  );
}

function PolicyRow({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      {ok ? (
        <CheckCircle2 className="h-4 w-4 text-status-normal" />
      ) : (
        <span className="h-4 w-4 rounded-full border border-line" />
      )}
      <span className="text-ink-muted">{label}</span>
    </div>
  );
}

function MfaCard({ mfaEnabled, onChange }: { mfaEnabled: boolean; onChange: () => void }) {
  const setup = useMfaSetup();
  const enable = useMfaEnable();
  const disable = useMfaDisable();
  const [secret, setSecret] = useState<string | null>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  async function begin() {
    setMsg(null);
    const res = await setup.mutateAsync();
    setSecret(res.secret);
    setUri(res.otpauth_uri);
  }

  async function confirm() {
    setMsg(null);
    try {
      await enable.mutateAsync(code);
      setSecret(null);
      setUri(null);
      setCode("");
      onChange();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed to enable MFA");
    }
  }

  async function turnOff() {
    setMsg(null);
    try {
      await disable.mutateAsync(code);
      setCode("");
      onChange();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed to disable MFA");
    }
  }

  return (
    <Card>
      <CardHeader
        title="Multi-factor authentication (TOTP)"
        subtitle={mfaEnabled ? "MFA is active on your account" : "Add a second factor to your account"}
        icon={<KeyRound className="h-4 w-4" />}
        action={
          <span
            className={`chip ${mfaEnabled ? "text-status-normal" : "text-ink-faint"}`}
          >
            {mfaEnabled ? "Enabled" : "Disabled"}
          </span>
        }
      />

      {!mfaEnabled && !secret && (
        <button onClick={begin} disabled={setup.isPending} className="btn-primary text-sm">
          {setup.isPending ? <Spinner className="text-white" /> : "Set up MFA"}
        </button>
      )}

      {!mfaEnabled && secret && (
        <div className="space-y-3">
          <p className="text-sm text-ink-muted">
            Add this secret to your authenticator app, then enter the 6-digit code to confirm.
          </p>
          <div className="rounded-lg border border-line bg-bg-soft p-3 font-mono text-sm text-ink break-all">
            {secret}
          </div>
          {uri && <p className="text-xs text-ink-faint break-all">{uri}</p>}
          <div className="flex gap-2">
            <input
              className="input tracking-[0.3em]"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              maxLength={6}
              placeholder="123456"
              inputMode="numeric"
            />
            <button onClick={confirm} disabled={enable.isPending || code.length < 6} className="btn-primary text-sm">
              {enable.isPending ? <Spinner className="text-white" /> : "Confirm"}
            </button>
          </div>
        </div>
      )}

      {mfaEnabled && (
        <div className="flex gap-2">
          <input
            className="input tracking-[0.3em]"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            maxLength={6}
            placeholder="Code to disable"
            inputMode="numeric"
          />
          <button onClick={turnOff} disabled={disable.isPending || code.length < 6} className="btn-secondary text-sm">
            {disable.isPending ? <Spinner /> : "Disable MFA"}
          </button>
        </div>
      )}

      {msg && <p className="mt-2 text-sm text-status-critical">{msg}</p>}
    </Card>
  );
}

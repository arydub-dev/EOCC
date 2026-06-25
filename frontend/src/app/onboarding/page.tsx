"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  Check,
  Database,
  Gauge,
  HeartPulse,
  Landmark,
  Layers,
  Siren,
  Sparkles,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { Spinner } from "@/components/ui/primitives";
import type { Industry, WorkspaceModeType } from "@/lib/types";

const INDUSTRIES: { id: Industry; label: string; icon: LucideIcon }[] = [
  { id: "government", label: "Government", icon: Landmark },
  { id: "healthcare", label: "Healthcare", icon: HeartPulse },
  { id: "emergency_services", label: "Emergency Services", icon: Siren },
  { id: "utilities", label: "Utilities", icon: Zap },
  { id: "critical_infrastructure", label: "Critical Infrastructure", icon: Layers },
  { id: "other", label: "Other", icon: Building2 },
];

const STEPS = ["Organization", "Industry", "Mode"];

export default function OnboardingPage() {
  const router = useRouter();
  const { user, organization, loading, refresh } = useAuth();
  const [step, setStep] = useState(0);
  const [orgName, setOrgName] = useState("");
  const [industry, setIndustry] = useState<Industry>("government");
  const [mode, setMode] = useState<WorkspaceModeType>("demo");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
    if (!loading && organization) router.replace("/app");
  }, [loading, user, organization, router]);

  async function finish() {
    setSubmitting(true);
    setError(null);
    try {
      await api("/onboarding", {
        method: "POST",
        body: { organization_name: orgName, industry, mode },
      });
      await refresh();
      router.push("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Onboarding failed");
      setSubmitting(false);
    }
  }

  const canNext = step === 0 ? orgName.trim().length >= 2 : true;

  if (loading || !user) {
    return (
      <div className="marketing-bg flex min-h-screen items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="marketing-bg min-h-screen">
      <div className="grid-overlay pointer-events-none absolute inset-0 h-80" />
      <div className="relative mx-auto flex min-h-screen max-w-2xl flex-col px-6 py-12">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/15 text-accent">
            <Gauge className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-bold text-ink">Welcome, {user.full_name.split(" ")[0]}</p>
            <p className="text-xs text-ink-faint">Let&apos;s set up your command center</p>
          </div>
        </div>

        {/* Stepper */}
        <div className="mt-8 flex items-center gap-2">
          {STEPS.map((label, i) => (
            <div key={label} className="flex flex-1 items-center gap-2">
              <div
                className={cn(
                  "flex h-7 w-7 items-center justify-center rounded-full border text-xs font-bold",
                  i < step
                    ? "border-status-normal bg-status-normal/15 text-status-normal"
                    : i === step
                      ? "border-accent bg-accent/15 text-accent"
                      : "border-line text-ink-faint",
                )}
              >
                {i < step ? <Check className="h-3.5 w-3.5" /> : i + 1}
              </div>
              <span className={cn("text-xs font-medium", i === step ? "text-ink" : "text-ink-faint")}>
                {label}
              </span>
              {i < STEPS.length - 1 && <div className="h-px flex-1 bg-line" />}
            </div>
          ))}
        </div>

        <div className="mt-8 flex-1">
          {step === 0 && (
            <div className="animate-fadeUp">
              <h1 className="text-2xl font-bold tracking-tight text-ink">Create your organization</h1>
              <p className="mt-2 text-sm text-ink-muted">
                This is the workspace your team will operate from. Data is fully isolated to your
                organization.
              </p>
              <div className="mt-6">
                <label className="stat-label">Organization name</label>
                <input
                  className="input mt-1"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="Metro Regional Emergency Operations Center"
                  autoFocus
                />
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="animate-fadeUp">
              <h1 className="text-2xl font-bold tracking-tight text-ink">Choose your industry</h1>
              <p className="mt-2 text-sm text-ink-muted">
                We&apos;ll tailor terminology and defaults to your sector.
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
                {INDUSTRIES.map((ind) => {
                  const Icon = ind.icon;
                  const active = industry === ind.id;
                  return (
                    <button
                      key={ind.id}
                      type="button"
                      onClick={() => setIndustry(ind.id)}
                      className={cn(
                        "flex flex-col items-start gap-3 rounded-xl border p-4 text-left transition-all",
                        active
                          ? "border-accent bg-accent/[0.07] shadow-glow"
                          : "border-line bg-bg-panel hover:border-ink-faint",
                      )}
                    >
                      <Icon className={cn("h-5 w-5", active ? "text-accent" : "text-ink-muted")} />
                      <span className="text-sm font-medium text-ink">{ind.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="animate-fadeUp">
              <h1 className="text-2xl font-bold tracking-tight text-ink">Choose your mode</h1>
              <p className="mt-2 text-sm text-ink-muted">
                You can switch or add data later from the Integration Center.
              </p>
              <div className="mt-6 space-y-3">
                <button
                  type="button"
                  onClick={() => setMode("demo")}
                  className={cn(
                    "flex w-full items-start gap-4 rounded-xl border p-5 text-left transition-all",
                    mode === "demo"
                      ? "border-accent bg-accent/[0.07] shadow-glow"
                      : "border-line bg-bg-panel hover:border-ink-faint",
                  )}
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/15 text-accent">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-ink">Demo Mode</p>
                      <span className="chip border-accent/30 bg-accent/10 text-accent">Recommended</span>
                    </div>
                    <p className="mt-1 text-sm text-ink-muted">
                      Instantly provision a fully populated synthetic workspace — incidents, hospitals,
                      shelters, resources, outages, and alerts — so you can explore everything now.
                    </p>
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setMode("connected")}
                  className={cn(
                    "flex w-full items-start gap-4 rounded-xl border p-5 text-left transition-all",
                    mode === "connected"
                      ? "border-accent bg-accent/[0.07] shadow-glow"
                      : "border-line bg-bg-panel hover:border-ink-faint",
                  )}
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-status-info/15 text-status-info">
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-ink">Connected Mode</p>
                    <p className="mt-1 text-sm text-ink-muted">
                      Start with an empty workspace and bring your own operational data via CSV, Excel,
                      REST APIs, GIS, weather, hospital, and dispatch systems.
                    </p>
                  </div>
                </button>
              </div>
            </div>
          )}

          {error && <p className="mt-4 text-sm text-status-critical">{error}</p>}
        </div>

        {/* Nav */}
        <div className="mt-8 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            className={cn("btn-ghost", step === 0 && "invisible")}
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          {step < STEPS.length - 1 ? (
            <button
              type="button"
              disabled={!canNext}
              onClick={() => setStep((s) => s + 1)}
              className="btn-primary"
            >
              Continue <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button type="button" disabled={submitting} onClick={finish} className="btn-primary">
              {submitting ? (
                <>
                  <Spinner className="text-white" /> Provisioning…
                </>
              ) : (
                <>
                  {mode === "demo" ? "Launch demo workspace" : "Create workspace"}{" "}
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

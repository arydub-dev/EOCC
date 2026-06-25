import Link from "next/link";
import {
  ArrowRight,
  Boxes,
  Building2,
  Calendar,
  Clock,
  Database,
  Eye,
  GitBranch,
  HeartPulse,
  KeyRound,
  Landmark,
  Layers,
  Lock,
  Network,
  Radio,
  ScrollText,
  ShieldCheck,
  Siren,
  Sparkles,
  Workflow,
  Zap,
  Plug,
} from "lucide-react";
import { DashboardPreview } from "@/components/marketing/dashboard-preview";
import { FeatureShowcase } from "@/components/marketing/feature-showcase";
import { PricingCards } from "@/components/marketing/pricing";
import { Faq } from "@/components/marketing/faq";

const PROBLEMS = [
  { icon: Layers, title: "Fragmented systems", body: "Critical information is scattered across CAD, spreadsheets, radios, and email — no single source of truth." },
  { icon: Clock, title: "Slow coordination", body: "Manual hand-offs between agencies cost precious minutes when every second changes outcomes." },
  { icon: Eye, title: "Low situational awareness", body: "Leaders make decisions without a real-time, unified picture of what's actually happening." },
  { icon: Boxes, title: "Poor resource visibility", body: "No one knows what assets are available, where they are, or whether they're ready to deploy." },
  { icon: GitBranch, title: "Delayed decisions", body: "Without scoring and recommendations, triage is inconsistent and the worst incidents wait." },
  { icon: Siren, title: "Reactive posture", body: "Teams firefight crises instead of anticipating risk and pre-positioning resources." },
];

const FLOW = [
  { icon: Network, label: "External Systems", note: "Weather, GIS, hospitals, dispatch, utilities" },
  { icon: Database, label: "Data Integration", note: "CSV, Excel, REST, live connectors" },
  { icon: Layers, label: "Operational Model", note: "Unified, tenant-isolated snapshot" },
  { icon: Sparkles, label: "Decision Engine", note: "Scoring, risk, recommendations" },
  { icon: Radio, label: "Mission Control", note: "One operational picture" },
  { icon: ScrollText, label: "Recommendations", note: "Prioritized, explainable actions" },
  { icon: Workflow, label: "Execution", note: "Assign, coordinate, resolve" },
];

const INDUSTRIES = [
  { icon: Landmark, name: "Government" },
  { icon: Siren, name: "Emergency Services" },
  { icon: Zap, name: "Utilities" },
  { icon: HeartPulse, name: "Healthcare" },
  { icon: ShieldCheck, name: "Disaster Response" },
  { icon: Building2, name: "NGOs" },
  { icon: Network, name: "Critical Infrastructure" },
  { icon: Boxes, name: "Logistics & Supply" },
];

const SECURITY = [
  { icon: KeyRound, title: "Role-Based Access Control", body: "Granular permissions across Admin, Emergency Manager, Analyst, and Executive roles." },
  { icon: ScrollText, title: "Comprehensive Audit Logs", body: "Every action is recorded with actor, entity, and timestamp for full accountability." },
  { icon: Lock, title: "Encryption & Secrets", body: "Encrypted credentials and secure token-based authentication throughout." },
  { icon: Building2, title: "Enterprise Ready", body: "Multi-tenant isolation, SSO/SAML, and SCIM provisioning on Enterprise plans." },
  { icon: Boxes, title: "Docker Deployment", body: "Ship to your own cloud, VPC, or air-gapped environment with one compose file." },
  { icon: Plug, title: "API-First", body: "Every capability is exposed via a documented OpenAPI surface for automation." },
];

export default function HomePage() {
  return (
    <>
      {/* ── Hero ── */}
      <section className="relative overflow-hidden">
        <div className="grid-overlay pointer-events-none absolute inset-0 h-[600px]" />
        <div className="section relative grid items-center gap-12 py-20 lg:grid-cols-[1.05fr_1fr] lg:py-28">
          <div className="animate-fadeUp">
            <div className="chip">
              <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-status-normal" />
              Operational intelligence for crisis response
            </div>
            <h1 className="mt-5 text-4xl font-bold leading-[1.08] tracking-tight text-ink sm:text-5xl lg:text-6xl">
              Emergency Operations<br />
              <span className="gradient-text">Command Center</span>
            </h1>
            <p className="mt-5 max-w-xl text-lg text-ink-muted">
              One platform for operational visibility, emergency coordination, resource management,
              and decision support — turning fragmented information into coordinated action.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link href="/register" className="btn-primary btn-lg">
                Start Free Demo <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/contact" className="btn-ghost btn-lg">
                <Calendar className="h-4 w-4" /> Schedule Demo
              </Link>
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-ink-faint">
              <span className="inline-flex items-center gap-1.5"><ShieldCheck className="h-3.5 w-3.5 text-status-normal" /> RBAC & audit logs</span>
              <span className="inline-flex items-center gap-1.5"><Boxes className="h-3.5 w-3.5 text-status-normal" /> Docker deployable</span>
              <span className="inline-flex items-center gap-1.5"><Database className="h-3.5 w-3.5 text-status-normal" /> Multi-tenant</span>
            </div>
          </div>
          <div className="animate-fadeUp" style={{ animationDelay: "0.15s" }}>
            <DashboardPreview />
          </div>
        </div>
      </section>

      {/* ── Trust strip ── */}
      <section className="border-y border-line bg-bg-soft/30">
        <div className="section flex flex-wrap items-center justify-center gap-x-10 gap-y-4 py-6 text-center">
          <p className="text-xs uppercase tracking-[0.18em] text-ink-faint">
            Built for the organizations that can't afford downtime
          </p>
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm font-semibold text-ink-muted">
            {["Government", "Healthcare", "Emergency Services", "Utilities", "Critical Infrastructure"].map((n) => (
              <span key={n} className="opacity-70">{n}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Problem ── */}
      <section className="section py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow">The problem</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
            Crisis response breaks where information lives
          </h2>
          <p className="mt-4 text-ink-muted">
            When an emergency hits, the bottleneck is rarely effort — it's coordination. Disconnected
            systems and missing visibility quietly cost lives, time, and money.
          </p>
        </div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROBLEMS.map((p) => {
            const Icon = p.icon;
            return (
              <div key={p.title} className="panel card-hover p-5">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-critical/10 text-status-critical">
                  <Icon className="h-5 w-5" />
                </div>
                <p className="mt-4 text-sm font-semibold text-ink">{p.title}</p>
                <p className="mt-1.5 text-sm text-ink-muted">{p.body}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Solution ── */}
      <section className="border-y border-line bg-bg-soft/30">
        <div className="section grid items-center gap-12 py-24 lg:grid-cols-2">
          <div>
            <p className="eyebrow">The solution</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
              One operational picture. One source of truth.
            </h2>
            <p className="mt-4 text-ink-muted">
              EOCC fuses incidents, hospitals, shelters, resources, weather, and infrastructure into a
              single live model. Deterministic decision engines then turn that model into clear
              answers — so your team always knows what's happening, why, and what to do next.
            </p>
            <div className="mt-6 space-y-3">
              {[
                "What is happening? — a real-time, unified operational view",
                "Why is it happening? — explainable scoring and risk intelligence",
                "What should we do next? — prioritized, grounded recommendations",
              ].map((q) => (
                <div key={q} className="flex items-start gap-3">
                  <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-accent" />
                  <span className="text-sm text-ink">{q}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              { k: "Decision engines", v: "Deterministic", n: "Explainable, no black boxes" },
              { k: "Time to value", v: "< 60s", n: "Demo workspace provisioned instantly" },
              { k: "Operational modules", v: "12", n: "From triage to executive briefing" },
              { k: "Data origins", v: "8+", n: "CSV, Excel, REST, GIS, weather, more" },
            ].map((s) => (
              <div key={s.k} className="panel p-5">
                <p className="stat-label">{s.k}</p>
                <p className="mt-2 text-2xl font-bold text-ink">{s.v}</p>
                <p className="mt-1 text-xs text-ink-faint">{s.n}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Feature showcase ── */}
      <section className="section py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow">Capabilities</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
            Everything an operations center needs
          </h2>
          <p className="mt-4 text-ink-muted">
            Twelve integrated modules, eight headline capabilities — engineered for clarity under
            pressure.
          </p>
        </div>
        <div className="mt-16">
          <FeatureShowcase />
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="border-y border-line bg-bg-soft/30">
        <div className="section py-24">
          <div className="mx-auto max-w-2xl text-center">
            <p className="eyebrow">How it works</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
              From raw signals to coordinated action
            </h2>
          </div>
          <div className="mt-14 flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
            {FLOW.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={step.label} className="flex flex-1 items-center gap-3 lg:flex-col">
                  <div className="flex flex-1 flex-col items-center rounded-xl border border-line bg-bg-panel p-4 text-center lg:w-full">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/12 text-accent">
                      <Icon className="h-5 w-5" />
                    </div>
                    <p className="mt-3 text-sm font-semibold text-ink">{step.label}</p>
                    <p className="mt-1 text-[11px] text-ink-faint">{step.note}</p>
                  </div>
                  {i < FLOW.length - 1 && (
                    <ArrowRight className="h-4 w-4 shrink-0 rotate-90 text-ink-faint lg:rotate-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Industries ── */}
      <section className="section py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow">Industries</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
            Trusted across mission-critical sectors
          </h2>
        </div>
        <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {INDUSTRIES.map((ind) => {
            const Icon = ind.icon;
            return (
              <div key={ind.name} className="panel card-hover flex items-center gap-3 p-5">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/12 text-accent">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-sm font-medium text-ink">{ind.name}</span>
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Security ── */}
      <section className="border-y border-line bg-bg-soft/30">
        <div className="section py-24">
          <div className="mx-auto max-w-2xl text-center">
            <p className="eyebrow">Security & compliance</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
              Enterprise-grade by default
            </h2>
            <p className="mt-4 text-ink-muted">
              Designed for the security and accountability requirements of public-sector and
              critical-infrastructure operations.
            </p>
          </div>
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {SECURITY.map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.title} className="panel p-5">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-normal/10 text-status-normal">
                    <Icon className="h-5 w-5" />
                  </div>
                  <p className="mt-4 text-sm font-semibold text-ink">{s.title}</p>
                  <p className="mt-1.5 text-sm text-ink-muted">{s.body}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Pricing ── */}
      <section className="section py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow">Pricing</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
            Start free. Scale when you're ready.
          </h2>
          <p className="mt-4 text-ink-muted">
            Evaluate the full platform in Demo Mode at no cost. Upgrade for live data and enterprise
            controls.
          </p>
        </div>
        <div className="mt-12">
          <PricingCards />
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="border-t border-line bg-bg-soft/30">
        <div className="section py-24">
          <div className="mx-auto max-w-2xl text-center">
            <p className="eyebrow">FAQ</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-ink sm:text-4xl">
              Questions, answered
            </h2>
          </div>
          <div className="mt-12">
            <Faq />
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="section py-24">
        <div className="relative overflow-hidden rounded-3xl border border-accent/30 bg-gradient-to-br from-accent/[0.12] via-bg-panel to-bg-panel p-10 text-center sm:p-16">
          <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-accent/20 blur-3xl" />
          <h2 className="relative text-3xl font-bold tracking-tight text-ink sm:text-4xl">
            See your operation in one picture
          </h2>
          <p className="relative mx-auto mt-4 max-w-xl text-ink-muted">
            Spin up a fully populated demo workspace in under a minute. No credit card, no setup.
          </p>
          <div className="relative mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/register" className="btn-primary btn-lg">
              Start Free Demo <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/contact" className="btn-ghost btn-lg">
              Talk to our team
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}

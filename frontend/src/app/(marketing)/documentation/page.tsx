import Link from "next/link";
import { ArrowRight, BookOpen, Boxes, Code2, Rocket, Workflow } from "lucide-react";

export const metadata = { title: "Documentation — EOCC" };

const ENDPOINTS = [
  { m: "POST", p: "/auth/register", d: "Create an account" },
  { m: "POST", p: "/auth/login-json", d: "Authenticate (supports remember me)" },
  { m: "POST", p: "/onboarding", d: "Create organization & provision workspace" },
  { m: "GET", p: "/workspace", d: "Workspace info & data-source provenance" },
  { m: "GET", p: "/mission-control/summary", d: "Composite operational picture" },
  { m: "GET", p: "/incidents", d: "List incidents (filter, sort, paginate)" },
  { m: "POST", p: "/simulations/run", d: "Run a what-if scenario" },
  { m: "POST", p: "/integration/import/csv", d: "Import operational data from CSV" },
];

export default function DocumentationPage() {
  return (
    <div className="section grid gap-10 py-16 lg:grid-cols-[220px_1fr]">
      <aside className="hidden lg:block">
        <div className="sticky top-24 space-y-1 text-sm">
          {[
            ["#getting-started", "Getting started"],
            ["#modes", "Operating modes"],
            ["#integrations", "Integrations"],
            ["#api", "API reference"],
            ["#deployment", "Deployment"],
            ["#status", "Status"],
            ["#changelog", "Changelog"],
          ].map(([href, label]) => (
            <a key={href} href={href} className="block rounded-lg px-3 py-2 text-ink-muted hover:bg-bg-elevated hover:text-ink">
              {label}
            </a>
          ))}
        </div>
      </aside>

      <div className="max-w-3xl space-y-14">
        <header>
          <p className="eyebrow">Documentation</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink">Build and operate on EOCC</h1>
          <p className="mt-4 text-lg text-ink-muted">
            Everything you need to evaluate, integrate, and deploy the Emergency Operations Command
            Center.
          </p>
        </header>

        <section id="getting-started" className="scroll-mt-24">
          <div className="flex items-center gap-2 text-ink"><Rocket className="h-5 w-5 text-accent" /><h2 className="text-xl font-bold">Getting started</h2></div>
          <ol className="mt-4 space-y-3">
            {[
              "Create an account from the Register page.",
              "Complete onboarding: name your organization, pick an industry, and choose a mode.",
              "Choose Demo Mode to instantly explore a fully populated workspace.",
              "Or choose Connected Mode and import your own data from the Integration Center.",
            ].map((s, i) => (
              <li key={s} className="flex gap-3 rounded-lg border border-line bg-bg-soft p-3 text-sm text-ink-muted">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-accent/15 text-xs font-bold text-accent">{i + 1}</span>
                {s}
              </li>
            ))}
          </ol>
        </section>

        <section id="modes" className="scroll-mt-24">
          <div className="flex items-center gap-2 text-ink"><Workflow className="h-5 w-5 text-accent" /><h2 className="text-xl font-bold">Operating modes</h2></div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="panel p-5">
              <p className="text-sm font-semibold text-ink">Demo Mode</p>
              <p className="mt-2 text-sm text-ink-muted">Provisions synthetic incidents, hospitals, shelters, resources, outages, alerts, and risk assessments so every module is populated for evaluation.</p>
            </div>
            <div className="panel p-5">
              <p className="text-sm font-semibold text-ink">Connected Mode</p>
              <p className="mt-2 text-sm text-ink-muted">Starts empty and guides you to import or connect real operational data. Dashboards show meaningful empty states until data arrives.</p>
            </div>
          </div>
        </section>

        <section id="integrations" className="scroll-mt-24">
          <div className="flex items-center gap-2 text-ink"><Boxes className="h-5 w-5 text-accent" /><h2 className="text-xl font-bold">Integrations</h2></div>
          <p className="mt-4 text-sm text-ink-muted">Connect data via the Integration Center:</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {["Weather APIs", "GIS Providers", "Hospital Systems", "Emergency Dispatch", "Utility Monitoring", "REST APIs", "CSV", "Excel"].map((x) => (
              <span key={x} className="chip">{x}</span>
            ))}
          </div>
        </section>

        <section id="api" className="scroll-mt-24">
          <div className="flex items-center gap-2 text-ink"><Code2 className="h-5 w-5 text-accent" /><h2 className="text-xl font-bold">API reference</h2></div>
          <p className="mt-4 text-sm text-ink-muted">
            EOCC is API-first. Explore the full interactive specification at{" "}
            <code className="rounded bg-bg-elevated px-1.5 py-0.5 text-xs text-accent">/docs</code> (Swagger) or{" "}
            <code className="rounded bg-bg-elevated px-1.5 py-0.5 text-xs text-accent">/redoc</code>.
          </p>
          <div className="mt-4 overflow-hidden rounded-xl border border-line">
            {ENDPOINTS.map((e) => (
              <div key={e.p} className="flex items-center gap-3 border-b border-line bg-bg-panel px-4 py-2.5 last:border-0">
                <span className="w-12 shrink-0 text-[10px] font-bold uppercase text-accent">{e.m}</span>
                <code className="shrink-0 font-mono text-xs text-ink">{e.p}</code>
                <span className="ml-auto truncate text-xs text-ink-faint">{e.d}</span>
              </div>
            ))}
          </div>
        </section>

        <section id="deployment" className="scroll-mt-24">
          <div className="flex items-center gap-2 text-ink"><BookOpen className="h-5 w-5 text-accent" /><h2 className="text-xl font-bold">Deployment</h2></div>
          <p className="mt-4 text-sm text-ink-muted">Bring up the full stack — frontend, API, and database — with one command:</p>
          <pre className="mt-3 overflow-x-auto rounded-xl border border-line bg-bg p-4 font-mono text-xs text-ink-muted">docker compose up --build</pre>
        </section>

        <section id="status" className="scroll-mt-24">
          <h2 className="text-xl font-bold text-ink">Status</h2>
          <div className="mt-3 flex items-center gap-2 rounded-xl border border-status-normal/30 bg-status-normal/10 p-4 text-sm text-status-normal">
            <span className="h-2 w-2 animate-pulseDot rounded-full bg-status-normal" /> All systems operational
          </div>
        </section>

        <section id="changelog" className="scroll-mt-24">
          <h2 className="text-xl font-bold text-ink">Changelog</h2>
          <ul className="mt-3 space-y-3 text-sm text-ink-muted">
            <li className="rounded-lg border border-line bg-bg-soft p-3"><span className="font-semibold text-ink">v2.0</span> — Multi-tenant SaaS: marketing site, onboarding, demo/connected modes, data provenance.</li>
            <li className="rounded-lg border border-line bg-bg-soft p-3"><span className="font-semibold text-ink">v1.0</span> — Initial release: 12 operational modules and deterministic decision engines.</li>
          </ul>
        </section>

        <div className="rounded-2xl border border-line bg-bg-panel p-6 text-center">
          <p className="text-sm text-ink-muted">Ready to try it?</p>
          <Link href="/register" className="btn-primary mt-3">
            Start Free Demo <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}

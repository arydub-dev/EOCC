import {
  AlertTriangle,
  BrainCircuit,
  FileText,
  FlaskConical,
  Gauge,
  Map as MapIcon,
  ShieldAlert,
  Truck,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Feature {
  icon: LucideIcon;
  name: string;
  tagline: string;
  description: string;
  value: string;
  bullets: string[];
  accent: string;
}

const FEATURES: Feature[] = [
  {
    icon: Gauge,
    name: "Mission Control",
    tagline: "One screen, total situational awareness",
    description:
      "A unified operational picture combining a composite emergency-health score, headline metrics, prioritized recommendations, and an auto-generated situation report.",
    value: "Cut time-to-decision by giving commanders one authoritative view instead of ten tools.",
    bullets: ["Composite health score", "Explainable recommendations", "Live SITREP"],
    accent: "#3b82f6",
  },
  {
    icon: AlertTriangle,
    name: "Incident Management",
    tagline: "Track, score, and escalate every incident",
    description:
      "Every incident carries a deterministic severity score, an event timeline, population-impact modeling, and geospatial context — from first report to resolution.",
    value: "Standardize triage so the most severe incidents always get attention first.",
    bullets: ["Severity scoring", "Event timelines", "Population impact"],
    accent: "#f59e0b",
  },
  {
    icon: Truck,
    name: "Resource Coordination",
    tagline: "Know what you have and where it's needed",
    description:
      "Track readiness and availability across ambulances, fire apparatus, medical teams, aircraft, and supply caches — then assign them to incidents in a click.",
    value: "Eliminate resource blind spots that delay response and waste capacity.",
    bullets: ["Readiness tracking", "Assignment workflow", "Utilization by type"],
    accent: "#22c55e",
  },
  {
    icon: FlaskConical,
    name: "Simulation Center",
    tagline: "Rehearse the crisis before it happens",
    description:
      "Run what-if scenarios — hurricane track shifts, flood expansion, resource depletion — and see projected operational risk and recommended posture.",
    value: "Pressure-test plans and pre-position resources before impact.",
    bullets: ["Hurricane & flood models", "Operational risk output", "Actionable guidance"],
    accent: "#a855f7",
  },
  {
    icon: BrainCircuit,
    name: "AI Operations Copilot",
    tagline: "Ask your operation anything",
    description:
      "A grounded copilot that answers operational questions with citations and suggested actions — fully deterministic by default, with optional LLM enrichment.",
    value: "Get answers in plain language without hunting through dashboards.",
    bullets: ["Grounded answers", "Suggested actions", "Source citations"],
    accent: "#06b6d4",
  },
  {
    icon: FileText,
    name: "Executive Briefings",
    tagline: "Board-ready reports in one click",
    description:
      "Generate a structured executive briefing — summary, key sections, and exportable markdown — synthesized from the live operational picture.",
    value: "Keep leadership aligned without pulling analysts off the response.",
    bullets: ["Auto-generated SITREP", "Structured sections", "Export to markdown"],
    accent: "#6366f1",
  },
  {
    icon: MapIcon,
    name: "Interactive Maps",
    tagline: "See the whole operation in space",
    description:
      "Layered geospatial visualization of incidents, hospitals, shelters, resources, and utility outages with severity-coded markers and impact radii.",
    value: "Spot geographic clustering and coverage gaps instantly.",
    bullets: ["Multi-layer overlays", "Severity coding", "Impact radii"],
    accent: "#38bdf8",
  },
  {
    icon: ShieldAlert,
    name: "Risk Intelligence",
    tagline: "Anticipate, don't just react",
    description:
      "Five categories of explainable risk assessment derived from the operational snapshot, each with contributing factors and recommended mitigations.",
    value: "Shift from reactive firefighting to proactive risk reduction.",
    bullets: ["5 risk categories", "Factor breakdowns", "Mitigation guidance"],
    accent: "#ef4444",
  },
];

function MiniIllustration({ feature }: { feature: Feature }) {
  const Icon = feature.icon;
  return (
    <div className="relative overflow-hidden rounded-2xl border border-line bg-bg-panel p-6">
      <div
        className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full blur-3xl"
        style={{ background: `${feature.accent}22` }}
      />
      <div
        className="flex h-12 w-12 items-center justify-center rounded-xl"
        style={{ background: `${feature.accent}1f`, color: feature.accent }}
      >
        <Icon className="h-6 w-6" />
      </div>
      <div className="mt-5 space-y-2.5">
        {feature.bullets.map((b, i) => (
          <div key={b} className="rounded-lg border border-line bg-bg-soft p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-ink">{b}</span>
              <span
                className="h-1.5 w-1.5 rounded-full"
                style={{ background: feature.accent, opacity: 1 - i * 0.25 }}
              />
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-bg-elevated">
              <div
                className="h-full rounded-full"
                style={{ width: `${85 - i * 18}%`, background: feature.accent, opacity: 0.7 }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FeatureShowcase() {
  return (
    <div className="space-y-20">
      {FEATURES.map((feature, i) => {
        const reversed = i % 2 === 1;
        return (
          <div
            key={feature.name}
            className="grid items-center gap-10 lg:grid-cols-2"
          >
            <div className={cn(reversed && "lg:order-2")}>
              <p className="eyebrow" style={{ color: feature.accent }}>
                {feature.name}
              </p>
              <h3 className="mt-2 text-2xl font-bold tracking-tight text-ink">{feature.tagline}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-muted">{feature.description}</p>
              <div className="mt-4 rounded-xl border border-line bg-bg-soft p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-faint">
                  Business value
                </p>
                <p className="mt-1 text-sm text-ink">{feature.value}</p>
              </div>
            </div>
            <div className={cn(reversed && "lg:order-1")}>
              <MiniIllustration feature={feature} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

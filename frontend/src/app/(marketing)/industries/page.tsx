import Link from "next/link";
import {
  ArrowRight,
  Building2,
  HeartPulse,
  Landmark,
  Network,
  ShieldCheck,
  Siren,
  Zap,
  type LucideIcon,
} from "lucide-react";

export const metadata = { title: "Industries — EOCC" };

interface IndustryDetail {
  icon: LucideIcon;
  name: string;
  body: string;
  uses: string[];
}

const INDUSTRIES: IndustryDetail[] = [
  {
    icon: Landmark,
    name: "Government",
    body: "City, county, and state emergency management agencies coordinating multi-agency response and keeping leadership informed.",
    uses: ["Multi-agency coordination", "Executive briefings", "Public-safety RBAC"],
  },
  {
    icon: Siren,
    name: "Emergency Services",
    body: "Fire, EMS, and 911 operations needing real-time incident triage and resource assignment under pressure.",
    uses: ["Incident severity scoring", "Resource readiness", "Dispatch integration"],
  },
  {
    icon: Zap,
    name: "Utilities",
    body: "Power, water, and gas operators tracking outages, restoration, and customer impact during major events.",
    uses: ["Outage monitoring", "Restoration tracking", "Impact modeling"],
  },
  {
    icon: HeartPulse,
    name: "Healthcare",
    body: "Hospital networks and public-health agencies managing surge capacity, diversions, and bed availability.",
    uses: ["Hospital stress scoring", "Capacity & ICU tracking", "Bed registry sync"],
  },
  {
    icon: ShieldCheck,
    name: "Disaster Response",
    body: "Relief organizations running large-scale operations across shelters, supplies, and field teams.",
    uses: ["Shelter operations", "Supply logistics", "Field coordination"],
  },
  {
    icon: Building2,
    name: "NGOs & Nonprofits",
    body: "Humanitarian organizations coordinating volunteers and resources where infrastructure is limited.",
    uses: ["Lightweight onboarding", "CSV/Excel imports", "Demo-first evaluation"],
  },
  {
    icon: Network,
    name: "Critical Infrastructure",
    body: "Operators of transportation, telecom, and industrial assets protecting continuity of operations.",
    uses: ["Risk intelligence", "Scenario simulation", "Audit & compliance"],
  },
];

export default function IndustriesPage() {
  return (
    <>
      <section className="section py-20 text-center">
        <p className="eyebrow">Industries</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Built for mission-critical operations
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-ink-muted">
          One platform, configured to the workflows of the sectors that keep communities running.
        </p>
      </section>
      <section className="section grid gap-5 pb-24 md:grid-cols-2">
        {INDUSTRIES.map((ind) => {
          const Icon = ind.icon;
          return (
            <div key={ind.name} className="panel card-hover p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/12 text-accent">
                  <Icon className="h-5 w-5" />
                </div>
                <h2 className="text-lg font-semibold text-ink">{ind.name}</h2>
              </div>
              <p className="mt-3 text-sm text-ink-muted">{ind.body}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {ind.uses.map((u) => (
                  <span key={u} className="chip">{u}</span>
                ))}
              </div>
            </div>
          );
        })}
      </section>
      <section className="section pb-24 text-center">
        <Link href="/register" className="btn-primary btn-lg">
          Start Free Demo <ArrowRight className="h-4 w-4" />
        </Link>
      </section>
    </>
  );
}

import Link from "next/link";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

const TIERS = [
  {
    name: "Starter",
    price: "$0",
    cadence: "for evaluation",
    description: "Explore the full platform with a synthetic demo workspace.",
    cta: "Start Free Demo",
    href: "/register",
    highlighted: false,
    features: [
      "1 organization workspace",
      "Demo Mode with synthetic data",
      "All 12 operational modules",
      "Mission Control & Risk Intelligence",
      "AI Operations Copilot (deterministic)",
      "Community support",
    ],
  },
  {
    name: "Professional",
    price: "$2,400",
    cadence: "per month",
    description: "For active operations teams running live coordination.",
    cta: "Start Free Demo",
    href: "/register",
    highlighted: true,
    features: [
      "Up to 5 organization workspaces",
      "Connected Mode + data integrations",
      "CSV / Excel / REST / GIS imports",
      "Weather & hospital system connectors",
      "Role-based access control (RBAC)",
      "Audit logging & exportable briefings",
      "Priority email support",
    ],
  },
  {
    name: "Enterprise",
    price: "Custom",
    cadence: "annual contract",
    description: "For agencies and enterprises with mission-critical needs.",
    cta: "Schedule Demo",
    href: "/contact",
    highlighted: false,
    features: [
      "Unlimited organizations",
      "Custom integrations & data pipelines",
      "SSO / SAML & SCIM provisioning",
      "Dedicated support & onboarding",
      "On-prem / VPC Docker deployment",
      "99.9% uptime SLA",
      "Security review & DPA",
    ],
  },
];

export function PricingCards() {
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {TIERS.map((tier) => (
        <div
          key={tier.name}
          className={cn(
            "relative flex flex-col rounded-2xl border p-6",
            tier.highlighted
              ? "border-accent/50 bg-accent/[0.06] shadow-glow"
              : "border-line bg-bg-panel",
          )}
        >
          {tier.highlighted && (
            <span className="absolute -top-3 left-6 rounded-full bg-accent px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white">
              Most Popular
            </span>
          )}
          <p className="text-sm font-semibold text-ink">{tier.name}</p>
          <div className="mt-3 flex items-baseline gap-1.5">
            <span className="text-3xl font-bold text-ink">{tier.price}</span>
            <span className="text-xs text-ink-faint">{tier.cadence}</span>
          </div>
          <p className="mt-2 text-sm text-ink-muted">{tier.description}</p>
          <Link
            href={tier.href}
            className={cn("mt-5 w-full text-center", tier.highlighted ? "btn-primary" : "btn-ghost")}
          >
            {tier.cta}
          </Link>
          <ul className="mt-6 space-y-2.5">
            {tier.features.map((f) => (
              <li key={f} className="flex items-start gap-2.5 text-sm text-ink-muted">
                <Check className="mt-0.5 h-4 w-4 shrink-0 text-status-normal" />
                {f}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

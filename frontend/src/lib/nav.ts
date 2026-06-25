import {
  Activity,
  AlertTriangle,
  Ambulance,
  BrainCircuit,
  Building2,
  Database,
  FileText,
  FlaskConical,
  LayoutDashboard,
  Map as MapIcon,
  ScrollText,
  ShieldAlert,
  ShieldCheck,
  Tent,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  keywords?: string[];
  /** Permission required to see this item (frontend convenience only). */
  permission?: string;
}

export interface NavGroup {
  group: string;
  items: NavItem[];
}

export const NAV: NavGroup[] = [
  {
    group: "Command",
    items: [{ href: "/app", label: "Mission Control", icon: LayoutDashboard, keywords: ["home", "overview", "dashboard"] }],
  },
  {
    group: "Operations",
    items: [
      { href: "/app/incidents", label: "Incidents", icon: Activity, keywords: ["events", "emergencies"] },
      { href: "/app/resources", label: "Resources", icon: Ambulance, keywords: ["assets", "units", "fleet"] },
      { href: "/app/hospitals", label: "Hospitals", icon: Building2, keywords: ["medical", "beds", "icu"] },
      { href: "/app/shelters", label: "Shelters", icon: Tent, keywords: ["mass care", "evacuation"] },
      { href: "/app/map", label: "Operations Map", icon: MapIcon, keywords: ["geo", "geographic", "location"] },
    ],
  },
  {
    group: "Intelligence",
    items: [
      { href: "/app/risk", label: "Risk Intelligence", icon: ShieldAlert, keywords: ["threat", "assessment"] },
      { href: "/app/alerts", label: "Alerts", icon: AlertTriangle, keywords: ["notifications", "warnings"] },
      { href: "/app/simulations", label: "Simulation Center", icon: FlaskConical, keywords: ["what-if", "scenario", "model"] },
      { href: "/app/copilot", label: "AI Copilot", icon: BrainCircuit, keywords: ["assistant", "ask", "ai"] },
    ],
  },
  {
    group: "Reporting",
    items: [
      { href: "/app/briefing", label: "Executive Briefing", icon: FileText, keywords: ["report", "summary", "sitrep"] },
      { href: "/app/integration", label: "Data Integration", icon: Database, keywords: ["import", "connect", "csv", "api", "sources"] },
    ],
  },
  {
    group: "Governance",
    items: [
      {
        href: "/app/security",
        label: "Security Center",
        icon: ShieldCheck,
        keywords: ["mfa", "sessions", "posture", "login"],
        permission: "Security.View",
      },
      {
        href: "/app/audit",
        label: "Audit Center",
        icon: ScrollText,
        keywords: ["audit", "log", "trail", "compliance"],
        permission: "Audit.View",
      },
    ],
  },
];

export const NAV_FLAT: NavItem[] = NAV.flatMap((g) => g.items);

export function findNavByPath(pathname: string): NavItem | undefined {
  // Exact match first, then the deepest prefix match.
  const exact = NAV_FLAT.find((i) => i.href === pathname);
  if (exact) return exact;
  return NAV_FLAT.filter((i) => i.href !== "/app" && pathname.startsWith(i.href)).sort(
    (a, b) => b.href.length - a.href.length,
  )[0];
}

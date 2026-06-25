"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { cn } from "@/lib/utils";

const ITEMS = [
  {
    q: "What exactly is the Emergency Operations Command Center?",
    a: "EOCC is an operational decision-support platform. It unifies incidents, hospitals, shelters, resources, weather, and infrastructure into a single operational picture, then runs deterministic, explainable engines to score severity, surface risk, and recommend next actions. It is not a dashboard or a tracker — it coordinates response.",
  },
  {
    q: "How is Demo Mode different from Connected Mode?",
    a: "Demo Mode instantly provisions a fully populated synthetic workspace so you can evaluate every module immediately. Connected Mode starts empty and you bring your own data via CSV, Excel, REST APIs, GIS feeds, hospital systems, and more through the Integration Center.",
  },
  {
    q: "Is my organization's data isolated from others?",
    a: "Yes. The platform is multi-tenant by design — every record belongs to an organization and queries are automatically scoped to your tenant. Users, incidents, resources, hospitals, alerts, and reports are all isolated per organization.",
  },
  {
    q: "Do the AI recommendations require an external LLM?",
    a: "No. The decision engines, scoring, risk intelligence, and the Operations Copilot all run deterministically and explainably out of the box. You can optionally connect an LLM for richer natural-language responses, but it is never required.",
  },
  {
    q: "How do you handle security and access control?",
    a: "EOCC ships with role-based access control (Admin, Emergency Manager, Analyst, Executive), full audit logging, encrypted credentials, and an API-first architecture. Enterprise plans add SSO/SAML, SCIM provisioning, and on-prem or VPC deployment.",
  },
  {
    q: "How is EOCC deployed?",
    a: "The entire platform runs via Docker Compose — frontend, API, and database — and can be deployed to your own infrastructure, a private cloud, or an air-gapped environment for sensitive operations.",
  },
];

export function Faq() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div className="mx-auto max-w-3xl divide-y divide-line rounded-2xl border border-line bg-bg-panel">
      {ITEMS.map((item, i) => {
        const isOpen = open === i;
        return (
          <div key={item.q} className="px-5">
            <button
              onClick={() => setOpen(isOpen ? null : i)}
              className="flex w-full items-center justify-between gap-4 py-5 text-left"
            >
              <span className="text-sm font-medium text-ink">{item.q}</span>
              <Plus
                className={cn(
                  "h-4 w-4 shrink-0 text-ink-faint transition-transform duration-300",
                  isOpen && "rotate-45 text-accent",
                )}
              />
            </button>
            <div
              className={cn(
                "grid transition-all duration-300",
                isOpen ? "grid-rows-[1fr] pb-5" : "grid-rows-[0fr]",
              )}
            >
              <div className="overflow-hidden">
                <p className="text-sm leading-relaxed text-ink-muted">{item.a}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

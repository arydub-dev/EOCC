"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Check, ChevronsUpDown, Gauge, LogOut, Settings, Sparkles } from "lucide-react";
import { NAV } from "@/lib/nav";
import { cn, titleCase } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

export function Sidebar() {
  const pathname = usePathname();
  const { user, organization, logout, hasPermission } = useAuth();
  const [switcherOpen, setSwitcherOpen] = useState(false);

  const sections = NAV.map((section) => ({
    ...section,
    items: section.items.filter((item) => !item.permission || hasPermission(item.permission)),
  })).filter((section) => section.items.length > 0);

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-line bg-bg-soft/80 backdrop-blur">
      {/* Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-line px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/15 text-accent">
          <Gauge className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-bold leading-tight text-ink">EOCC</p>
          <p className="text-[10px] uppercase tracking-wider text-ink-faint">Command Center</p>
        </div>
      </div>

      {/* Workspace switcher */}
      <div className="relative border-b border-line p-3">
        <button
          onClick={() => setSwitcherOpen((v) => !v)}
          className="flex w-full items-center gap-2.5 rounded-lg border border-line bg-bg-panel px-3 py-2 text-left transition-colors hover:border-ink-faint"
        >
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-accent/15 text-xs font-bold text-accent">
            {organization?.name?.[0] ?? "?"}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold text-ink">{organization?.name ?? "Workspace"}</p>
            <p className="truncate text-[10px] text-ink-faint">
              {organization ? titleCase(organization.industry) : "—"}
            </p>
          </div>
          <ChevronsUpDown className="h-3.5 w-3.5 shrink-0 text-ink-faint" />
        </button>

        {switcherOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setSwitcherOpen(false)} />
            <div className="absolute left-3 right-3 top-full z-20 mt-1 overflow-hidden rounded-lg border border-line bg-bg-panel shadow-panel">
              <div className="flex items-center gap-2.5 border-b border-line px-3 py-2.5">
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent/15 text-xs font-bold text-accent">
                  {organization?.name?.[0] ?? "?"}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold text-ink">{organization?.name}</p>
                  <p className="truncate text-[10px] text-ink-faint">{user?.email}</p>
                </div>
                <Check className="h-3.5 w-3.5 text-accent" />
              </div>
              <Link
                href="/app/settings"
                onClick={() => setSwitcherOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 text-xs text-ink-muted hover:bg-bg-elevated hover:text-ink"
              >
                <Settings className="h-3.5 w-3.5" /> Workspace settings
              </Link>
            </div>
          </>
        )}

        {organization?.is_demo && (
          <div className="mt-2 flex items-center gap-1.5 rounded-md border border-accent/30 bg-accent/10 px-2.5 py-1.5 text-[10px] font-medium text-accent">
            <Sparkles className="h-3 w-3" /> Demo Workspace
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4">
        {sections.map((section) => (
          <div key={section.group}>
            <p className="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
              {section.group}
            </p>
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const active = item.href === "/app" ? pathname === "/app" : pathname.startsWith(item.href);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn("nav-item", active && "nav-item-active")}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="border-t border-line p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-bold text-accent">
            {user?.full_name?.[0] ?? "?"}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-medium text-ink">{user?.full_name}</p>
            <p className="truncate text-[10px] text-ink-faint">{titleCase(user?.role ?? "")}</p>
          </div>
          <button onClick={logout} className="text-ink-faint hover:text-status-critical" title="Sign out">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Bell, ChevronRight, LogOut, Search, Settings, User as UserIcon } from "lucide-react";
import { findNavByPath } from "@/lib/nav";
import { useAlerts, useWorkspace } from "@/lib/hooks";
import { useAuth } from "@/lib/auth";
import { useCommandPalette } from "@/components/command-palette";
import { DataSourceBadge } from "@/components/data-source-badge";
import { StatusBadge } from "@/components/ui/badge";
import { cn, timeAgo, titleCase } from "@/lib/utils";

export function Topbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { open } = useCommandPalette();
  const current = findNavByPath(pathname);
  const { data: workspace } = useWorkspace();
  const { data: alerts } = useAlerts({ status: "open", page_size: 6 });

  const [now, setNow] = useState<Date | null>(null);
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  useEffect(() => {
    setNow(new Date());
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const openCount = alerts?.total ?? 0;

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-line bg-bg/80 px-6 backdrop-blur">
      {/* Breadcrumbs */}
      <div className="flex min-w-0 items-center gap-2 text-sm">
        <Link href="/app" className="text-ink-faint hover:text-ink">
          Workspace
        </Link>
        {current && (
          <>
            <ChevronRight className="h-3.5 w-3.5 text-ink-faint" />
            <span className="truncate font-medium text-ink">{current.label}</span>
          </>
        )}
      </div>

      <div className="flex items-center gap-2">
        {/* Global search / command palette */}
        <button
          onClick={open}
          className="hidden items-center gap-2 rounded-lg border border-line bg-bg-soft px-3 py-1.5 text-xs text-ink-faint transition-colors hover:border-ink-faint hover:text-ink-muted sm:flex"
        >
          <Search className="h-3.5 w-3.5" />
          <span>Search…</span>
          <kbd className="rounded border border-line bg-bg-panel px-1.5 py-0.5 text-[10px]">⌘K</kbd>
        </button>

        {workspace && <DataSourceBadge origin={workspace.primary_data_origin} className="hidden md:inline-flex" />}

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => {
              setNotifOpen((v) => !v);
              setProfileOpen(false);
            }}
            className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-line bg-bg-soft text-ink-muted hover:text-ink"
          >
            <Bell className="h-4 w-4" />
            {openCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-status-critical px-1 text-[9px] font-bold text-white">
                {openCount > 99 ? "99+" : openCount}
              </span>
            )}
          </button>
          {notifOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setNotifOpen(false)} />
              <div className="absolute right-0 top-full z-20 mt-2 w-80 overflow-hidden rounded-xl border border-line bg-bg-panel shadow-panel">
                <div className="flex items-center justify-between border-b border-line px-4 py-3">
                  <p className="text-sm font-semibold text-ink">Notifications</p>
                  <span className="text-[11px] text-ink-faint">{openCount} open</span>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {(alerts?.items ?? []).length === 0 && (
                    <p className="px-4 py-8 text-center text-sm text-ink-faint">All clear — no open alerts.</p>
                  )}
                  {(alerts?.items ?? []).map((a) => (
                    <Link
                      key={a.id}
                      href="/app/alerts"
                      onClick={() => setNotifOpen(false)}
                      className="flex items-start gap-3 border-b border-line px-4 py-3 last:border-0 hover:bg-bg-elevated"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-xs font-medium text-ink">{a.title}</p>
                        <p className="truncate text-[11px] text-ink-faint">{a.message}</p>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <StatusBadge status={a.severity} />
                        <span className="text-[10px] text-ink-faint">{timeAgo(a.triggered_at)}</span>
                      </div>
                    </Link>
                  ))}
                </div>
                <Link
                  href="/app/alerts"
                  onClick={() => setNotifOpen(false)}
                  className="block border-t border-line px-4 py-2.5 text-center text-xs font-medium text-accent hover:bg-bg-elevated"
                >
                  View all alerts
                </Link>
              </div>
            </>
          )}
        </div>

        {/* Profile menu */}
        <div className="relative">
          <button
            onClick={() => {
              setProfileOpen((v) => !v);
              setNotifOpen(false);
            }}
            className="flex h-9 items-center gap-2 rounded-lg border border-line bg-bg-soft px-2 pr-3 text-ink-muted hover:text-ink"
          >
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent/15 text-[11px] font-bold text-accent">
              {user?.full_name?.[0] ?? "?"}
            </span>
            <span className="hidden text-xs font-medium text-ink sm:block">
              {user?.full_name?.split(" ")[0]}
            </span>
          </button>
          {profileOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setProfileOpen(false)} />
              <div className="absolute right-0 top-full z-20 mt-2 w-56 overflow-hidden rounded-xl border border-line bg-bg-panel shadow-panel">
                <div className="border-b border-line px-4 py-3">
                  <p className="truncate text-sm font-medium text-ink">{user?.full_name}</p>
                  <p className="truncate text-xs text-ink-faint">{user?.email}</p>
                  <span className="mt-1.5 inline-block rounded-full border border-line bg-bg-soft px-2 py-0.5 text-[10px] text-ink-muted">
                    {titleCase(user?.role ?? "")}
                  </span>
                </div>
                <Link
                  href="/app/settings"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-ink-muted hover:bg-bg-elevated hover:text-ink"
                >
                  <UserIcon className="h-4 w-4" /> Profile & account
                </Link>
                <Link
                  href="/app/settings"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-ink-muted hover:bg-bg-elevated hover:text-ink"
                >
                  <Settings className="h-4 w-4" /> Settings
                </Link>
                <button
                  onClick={logout}
                  className="flex w-full items-center gap-2.5 border-t border-line px-4 py-2.5 text-sm text-ink-muted hover:bg-bg-elevated hover:text-status-critical"
                >
                  <LogOut className="h-4 w-4" /> Sign out
                </button>
              </div>
            </>
          )}
        </div>

        <div className="hidden font-mono text-xs tabular-nums text-ink-faint lg:block">
          {now ? now.toLocaleTimeString("en-US", { hour12: false }) : "--:--:--"}
        </div>
      </div>
    </header>
  );
}

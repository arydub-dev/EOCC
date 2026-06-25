"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  CornerDownLeft,
  FileText,
  LogOut,
  Search,
  ShieldAlert,
  Sparkles,
  Upload,
} from "lucide-react";
import { NAV_FLAT } from "@/lib/nav";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface CommandContextValue {
  open: () => void;
  close: () => void;
  toggle: () => void;
}

const CommandContext = createContext<CommandContextValue | undefined>(undefined);

export function useCommandPalette() {
  const ctx = useContext(CommandContext);
  if (!ctx) throw new Error("useCommandPalette must be used within CommandPaletteProvider");
  return ctx;
}

interface Command {
  id: string;
  label: string;
  group: string;
  icon: typeof Search;
  keywords?: string[];
  run: () => void;
}

export function CommandPaletteProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => {
    setIsOpen(false);
    setQuery("");
    setActive(0);
  }, []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);

  const commands: Command[] = useMemo(() => {
    const navCmds: Command[] = NAV_FLAT.map((item) => ({
      id: `nav:${item.href}`,
      label: item.label,
      group: "Navigate",
      icon: item.icon,
      keywords: item.keywords,
      run: () => router.push(item.href),
    }));
    const actions: Command[] = [
      {
        id: "action:briefing",
        label: "Generate executive briefing",
        group: "Quick actions",
        icon: FileText,
        keywords: ["report", "sitrep"],
        run: () => router.push("/app/briefing"),
      },
      {
        id: "action:risk",
        label: "Open risk intelligence",
        group: "Quick actions",
        icon: ShieldAlert,
        keywords: ["assessment", "threat"],
        run: () => router.push("/app/risk"),
      },
      {
        id: "action:copilot",
        label: "Ask the AI Copilot",
        group: "Quick actions",
        icon: Sparkles,
        keywords: ["assistant", "ai"],
        run: () => router.push("/app/copilot"),
      },
      {
        id: "action:import",
        label: "Import data",
        group: "Quick actions",
        icon: Upload,
        keywords: ["csv", "excel", "connect"],
        run: () => router.push("/app/integration"),
      },
      {
        id: "action:logout",
        label: "Sign out",
        group: "Account",
        icon: LogOut,
        run: () => logout(),
      },
    ];
    return [...navCmds, ...actions];
  }, [router, logout]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter(
      (c) =>
        c.label.toLowerCase().includes(q) ||
        c.group.toLowerCase().includes(q) ||
        c.keywords?.some((k) => k.toLowerCase().includes(q)),
    );
  }, [commands, query]);

  useEffect(() => {
    setActive(0);
  }, [query]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        toggle();
      }
      if (e.key === "Escape") close();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggle, close]);

  function runAt(index: number) {
    const cmd = filtered[index];
    if (cmd) {
      cmd.run();
      close();
    }
  }

  // Group filtered for display
  const grouped = useMemo(() => {
    const map = new Map<string, { cmd: Command; idx: number }[]>();
    filtered.forEach((cmd, idx) => {
      const arr = map.get(cmd.group) ?? [];
      arr.push({ cmd, idx });
      map.set(cmd.group, arr);
    });
    return Array.from(map.entries());
  }, [filtered]);

  return (
    <CommandContext.Provider value={{ open, close, toggle }}>
      {children}
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center px-4 pt-[12vh]">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={close} />
          <div className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-line bg-bg-panel shadow-panel">
            <div className="flex items-center gap-3 border-b border-line px-4">
              <Search className="h-4 w-4 text-ink-faint" />
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "ArrowDown") {
                    e.preventDefault();
                    setActive((a) => Math.min(filtered.length - 1, a + 1));
                  } else if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setActive((a) => Math.max(0, a - 1));
                  } else if (e.key === "Enter") {
                    e.preventDefault();
                    runAt(active);
                  }
                }}
                placeholder="Search modules and actions…"
                className="h-12 w-full bg-transparent text-sm text-ink placeholder:text-ink-faint focus:outline-none"
              />
              <kbd className="hidden rounded border border-line bg-bg-soft px-1.5 py-0.5 text-[10px] text-ink-faint sm:block">
                ESC
              </kbd>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {filtered.length === 0 && (
                <p className="px-3 py-8 text-center text-sm text-ink-faint">No results for “{query}”.</p>
              )}
              {grouped.map(([group, items]) => (
                <div key={group} className="mb-1">
                  <p className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
                    {group}
                  </p>
                  {items.map(({ cmd, idx }) => {
                    const Icon = cmd.icon;
                    return (
                      <button
                        key={cmd.id}
                        onMouseEnter={() => setActive(idx)}
                        onClick={() => runAt(idx)}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                          active === idx ? "bg-bg-elevated text-ink" : "text-ink-muted hover:bg-bg-elevated/60",
                        )}
                      >
                        <Icon className="h-4 w-4 shrink-0 text-ink-faint" />
                        <span className="flex-1">{cmd.label}</span>
                        {active === idx && <CornerDownLeft className="h-3.5 w-3.5 text-ink-faint" />}
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between border-t border-line px-4 py-2 text-[10px] text-ink-faint">
              <span className="flex items-center gap-1">
                <ArrowRight className="h-3 w-3" /> Navigate & act instantly
              </span>
              <span>↑↓ to move · ↵ to select</span>
            </div>
          </div>
        </div>
      )}
    </CommandContext.Provider>
  );
}

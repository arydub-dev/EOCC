import Link from "next/link";
import { Gauge, Github } from "lucide-react";

const COLUMNS = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "/features" },
      { label: "Pricing", href: "/pricing" },
      { label: "Industries", href: "/industries" },
      { label: "Security", href: "/security" },
    ],
  },
  {
    title: "Developers",
    links: [
      { label: "Documentation", href: "/documentation" },
      { label: "API Reference", href: "/documentation#api" },
      { label: "Status", href: "/documentation#status" },
      { label: "Changelog", href: "/documentation#changelog" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "Contact", href: "/contact" },
      { label: "Privacy", href: "/security#privacy" },
      { label: "Terms", href: "/security#terms" },
      { label: "Sign in", href: "/login" },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-line bg-bg-soft/40">
      <div className="section grid gap-10 py-14 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
        <div>
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
              <Gauge className="h-5 w-5" />
            </div>
            <p className="text-sm font-bold text-ink">EOCC</p>
          </Link>
          <p className="mt-3 max-w-xs text-sm text-ink-muted">
            One platform for operational visibility, emergency coordination, resource management, and
            decision support.
          </p>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-flex items-center gap-2 text-xs text-ink-faint hover:text-ink"
          >
            <Github className="h-4 w-4" /> GitHub
          </a>
        </div>
        {COLUMNS.map((col) => (
          <div key={col.title}>
            <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">{col.title}</p>
            <ul className="mt-3 space-y-2">
              {col.links.map((l) => (
                <li key={l.label}>
                  <Link href={l.href} className="text-sm text-ink-muted hover:text-ink">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-line">
        <div className="section flex flex-col items-center justify-between gap-2 py-5 text-xs text-ink-faint sm:flex-row">
          <p>© {new Date().getFullYear()} Emergency Operations Command Center. All rights reserved.</p>
          <p>Built for government, healthcare, utilities, and critical infrastructure.</p>
        </div>
      </div>
    </footer>
  );
}

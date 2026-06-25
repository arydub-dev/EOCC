"use client";

import { useState } from "react";
import Link from "next/link";
import { CheckCircle2, Mail, MessageSquare, Phone } from "lucide-react";

export default function ContactPage() {
  const [sent, setSent] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", org: "", message: "" });

  function submit(e: React.FormEvent) {
    e.preventDefault();
    setSent(true);
  }

  return (
    <section className="section grid gap-12 py-20 lg:grid-cols-2">
      <div>
        <p className="eyebrow">Contact</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Schedule a demo
        </h1>
        <p className="mt-4 text-lg text-ink-muted">
          Tell us about your operation and we'll tailor a walkthrough — or start exploring instantly
          with a free demo workspace.
        </p>

        <div className="mt-8 space-y-4">
          {[
            { icon: Mail, label: "Email", value: "sales@eocc.gov" },
            { icon: Phone, label: "Operations line", value: "+1 (800) 555-0142" },
            { icon: MessageSquare, label: "Procurement & security", value: "security@eocc.gov" },
          ].map((c) => {
            const Icon = c.icon;
            return (
              <div key={c.label} className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/12 text-accent">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wider text-ink-faint">{c.label}</p>
                  <p className="text-sm font-medium text-ink">{c.value}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 rounded-xl border border-line bg-bg-soft p-4">
          <p className="text-sm text-ink-muted">
            Prefer to dive in?{" "}
            <Link href="/register" className="font-medium text-accent hover:underline">
              Start a free demo →
            </Link>
          </p>
        </div>
      </div>

      <div className="panel p-7">
        {sent ? (
          <div className="flex h-full flex-col items-center justify-center py-12 text-center">
            <CheckCircle2 className="h-12 w-12 text-status-normal" />
            <h2 className="mt-4 text-xl font-bold text-ink">Thanks, {form.name || "there"}!</h2>
            <p className="mt-2 max-w-sm text-sm text-ink-muted">
              Our team will reach out within one business day to schedule your demo.
            </p>
            <Link href="/register" className="btn-primary mt-6">
              Or start the demo now
            </Link>
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="stat-label">Full name</label>
              <input
                required
                className="input mt-1"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Jordan Rivera"
              />
            </div>
            <div>
              <label className="stat-label">Work email</label>
              <input
                required
                type="email"
                className="input mt-1"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="jordan@agency.gov"
              />
            </div>
            <div>
              <label className="stat-label">Organization</label>
              <input
                className="input mt-1"
                value={form.org}
                onChange={(e) => setForm({ ...form, org: e.target.value })}
                placeholder="Metro Regional EOC"
              />
            </div>
            <div>
              <label className="stat-label">How can we help?</label>
              <textarea
                className="input mt-1 min-h-28 resize-none"
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                placeholder="We're evaluating platforms for multi-agency coordination…"
              />
            </div>
            <button type="submit" className="btn-primary w-full">
              Request demo
            </button>
            <p className="text-center text-[11px] text-ink-faint">
              This demo form does not transmit data — it illustrates the contact flow.
            </p>
          </form>
        )}
      </div>
    </section>
  );
}

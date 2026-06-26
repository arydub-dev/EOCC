import {
  Boxes,
  Building2,
  FileCheck,
  KeyRound,
  Lock,
  Plug,
  ScrollText,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";

export const metadata = { title: "Security — EOCC" };

const CONTROLS: { icon: LucideIcon; title: string; body: string }[] = [
  { icon: KeyRound, title: "Role-Based Access Control", body: "Four built-in roles with least-privilege defaults. Permissions are enforced server-side on every request." },
  { icon: ScrollText, title: "Audit Logging", body: "Immutable record of every privileged action — actor, entity, and timestamp — scoped per organization." },
  { icon: Lock, title: "Encryption & Secrets", body: "Encrypted credentials, hashed passwords (bcrypt), and signed, expiring access tokens." },
  { icon: Building2, title: "Multi-Tenant Isolation", body: "Every record belongs to an organization; queries are automatically scoped to your tenant." },
  { icon: ShieldCheck, title: "SSO & SCIM", body: "SAML single sign-on and SCIM user provisioning available on Enterprise plans." },
  { icon: Boxes, title: "Flexible Deployment", body: "Run in your own cloud, VPC, or fully air-gapped via Docker Compose." },
  { icon: Plug, title: "API-First", body: "A documented OpenAPI surface for every capability, enabling secure automation and integration." },
  { icon: FileCheck, title: "Data Processing Agreement", body: "DPA and security review available for enterprise and public-sector procurement." },
];

export default function SecurityPage() {
  return (
    <>
      <section className="section py-20 text-center">
        <p className="eyebrow">Security</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Security and accountability, built in
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-ink-muted">
          EOCC is engineered for the trust requirements of government, healthcare, and critical
          infrastructure operations.
        </p>
      </section>

      <section className="section grid gap-4 pb-20 sm:grid-cols-2 lg:grid-cols-2">
        {CONTROLS.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.title} className="panel p-6">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-status-normal/10 text-status-normal">
                <Icon className="h-5 w-5" />
              </div>
              <h2 className="mt-4 text-base font-semibold text-ink">{c.title}</h2>
              <p className="mt-1.5 text-sm text-ink-muted">{c.body}</p>
            </div>
          );
        })}
      </section>

      <section id="privacy" className="section pb-12">
        <div className="panel p-8">
          <h2 className="text-xl font-bold text-ink">Privacy</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-muted">
            We collect only what is required to operate your workspace. Operational data you import or
            connect remains yours and is isolated to your organization. Demo workspaces contain only
            synthetic data generated for evaluation. We never sell customer data, and you can request
            export or deletion of your organization&apos;s data at any time.
          </p>
        </div>
      </section>

      <section id="terms" className="section pb-24">
        <div className="panel p-8">
          <h2 className="text-xl font-bold text-ink">Terms of Service</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-muted">
            Use of the platform is governed by your subscription agreement. Enterprise customers
            receive a negotiated MSA, DPA, and uptime SLA. This demonstration deployment is provided
            for evaluation purposes and uses synthetic operational data.
          </p>
        </div>
      </section>
    </>
  );
}

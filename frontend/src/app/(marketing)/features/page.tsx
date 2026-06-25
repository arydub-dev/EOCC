import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { FeatureShowcase } from "@/components/marketing/feature-showcase";

export const metadata = { title: "Features — EOCC" };

export default function FeaturesPage() {
  return (
    <>
      <section className="section py-20 text-center">
        <p className="eyebrow">Platform</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          A complete operations center, integrated
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-ink-muted">
          Every capability shares one operational model — so incidents, resources, risk, and
          recommendations always stay in sync.
        </p>
      </section>
      <section className="section pb-24">
        <FeatureShowcase />
      </section>
      <section className="section pb-24">
        <div className="rounded-3xl border border-line bg-bg-panel p-10 text-center">
          <h2 className="text-2xl font-bold text-ink">Explore it with live demo data</h2>
          <p className="mx-auto mt-3 max-w-lg text-ink-muted">
            The fastest way to understand EOCC is to use it. Provision a synthetic workspace in
            seconds.
          </p>
          <Link href="/register" className="btn-primary btn-lg mt-6">
            Start Free Demo <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </>
  );
}

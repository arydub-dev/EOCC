import { PricingCards } from "@/components/marketing/pricing";
import { Faq } from "@/components/marketing/faq";

export const metadata = { title: "Pricing — EOCC" };

export default function PricingPage() {
  return (
    <>
      <section className="section py-20 text-center">
        <p className="eyebrow">Pricing</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Simple, transparent plans
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-ink-muted">
          Evaluate everything for free in Demo Mode. Upgrade for live data, integrations, and
          enterprise controls.
        </p>
      </section>
      <section className="section pb-20">
        <PricingCards />
      </section>
      <section className="section pb-24">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-2xl font-bold text-ink">Pricing questions</h2>
          <p className="mt-3 text-ink-muted">Everything you need to know before you start.</p>
        </div>
        <div className="mt-10">
          <Faq />
        </div>
      </section>
    </>
  );
}

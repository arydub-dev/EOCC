"use client";

import { useEffect } from "react";
import { Download, FileText, RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/primitives";
import { useGenerateBriefing } from "@/lib/hooks";

export default function BriefingPage() {
  const generate = useGenerateBriefing();

  useEffect(() => {
    generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const briefing = generate.data;

  function download(kind: "md") {
    if (!briefing) return;
    const blob = new Blob([briefing.markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `eocc-briefing-${new Date().toISOString().slice(0, 10)}.${kind}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function printPdf() {
    window.print();
  }

  return (
    <div>
      <PageHeader
        question="What should leadership know?"
        title="Executive Briefing Center"
        description="Auto-generated leadership briefing with executive summary, situation, resources, risks and actions."
        actions={
          <div className="flex gap-2">
            <button onClick={() => generate.mutate()} disabled={generate.isPending} className="btn-ghost">
              <RefreshCw className={generate.isPending ? "h-4 w-4 animate-spin" : "h-4 w-4"} /> Regenerate
            </button>
            <button onClick={() => download("md")} className="btn-ghost"><Download className="h-4 w-4" /> Markdown</button>
            <button onClick={printPdf} className="btn-primary"><FileText className="h-4 w-4" /> Export PDF</button>
          </div>
        }
      />

      {generate.isPending && <LoadingPanel label="Generating executive briefing…" />}

      {briefing && (
        <div className="mx-auto max-w-3xl space-y-4">
          <Card className="border-accent/30">
            <p className="stat-label">Executive Summary</p>
            <h2 className="mt-1 text-lg font-bold text-ink">{briefing.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">{briefing.executive_summary}</p>
            <p className="mt-3 text-[11px] text-ink-faint">
              Generated {new Date(briefing.generated_at).toLocaleString()} · engine: {briefing.engine}
            </p>
          </Card>

          {briefing.sections.map((s) => (
            <Card key={s.heading}>
              <h3 className="text-sm font-semibold text-ink">{s.heading}</h3>
              {s.body && <p className="mt-1 text-sm text-ink-muted">{s.body}</p>}
              {s.bullets.length > 0 && (
                <ul className="mt-2 space-y-1.5">
                  {s.bullets.map((b, i) => (
                    <li key={i} className="flex gap-2 text-xs text-ink-muted">
                      <span className="text-accent">•</span> {b}
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

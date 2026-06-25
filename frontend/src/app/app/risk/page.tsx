"use client";

import { RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/ui/primitives";
import { useGenerateRisk, useRisk } from "@/lib/hooks";
import { scoreColor, titleCase } from "@/lib/utils";

export default function RiskPage() {
  const { data, isLoading } = useRisk();
  const generate = useGenerateRisk();

  return (
    <div>
      <PageHeader
        question="Why is it happening?"
        title="Risk Intelligence"
        description="Deterministic, explainable risk assessments across population, infrastructure, healthcare, resource and environmental dimensions."
        actions={
          <button onClick={() => generate.mutate()} disabled={generate.isPending} className="btn-primary">
            <RefreshCw className={generate.isPending ? "h-4 w-4 animate-spin" : "h-4 w-4"} /> Regenerate
          </button>
        }
      />

      {isLoading ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data?.map((r) => (
            <div key={r.id} className="panel flex flex-col p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="stat-label">{titleCase(r.category)}</p>
                  <h3 className="mt-1 text-sm font-semibold text-ink">{r.title}</h3>
                </div>
                <StatusBadge status={r.severity} />
              </div>

              <div className="my-4 flex items-end gap-2">
                <span className="text-4xl font-bold" style={{ color: scoreColor(r.score) }}>
                  {r.score.toFixed(0)}
                </span>
                <span className="mb-1 text-sm text-ink-faint">/ 100</span>
              </div>
              <div className="mb-4 h-1.5 w-full overflow-hidden rounded-full bg-bg-elevated">
                <div className="h-full rounded-full" style={{ width: `${r.score}%`, background: scoreColor(r.score) }} />
              </div>

              <p className="text-xs leading-relaxed text-ink-muted">{r.explanation}</p>

              {r.recommendations && r.recommendations.length > 0 && (
                <div className="mt-4 border-t border-line pt-3">
                  <p className="stat-label mb-2">Recommendations</p>
                  <ul className="space-y-1.5">
                    {r.recommendations.map((rec, i) => (
                      <li key={i} className="flex gap-2 text-xs text-ink-muted">
                        <span className="text-accent">→</span> {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

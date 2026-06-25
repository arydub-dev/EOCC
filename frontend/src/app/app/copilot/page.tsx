"use client";

import { useState } from "react";
import { BrainCircuit, Send, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Spinner } from "@/components/ui/primitives";
import { Tag } from "@/components/ui/badge";
import { useAskCopilot, useCopilotStatus } from "@/lib/hooks";
import type { CopilotResponse } from "@/lib/types";

interface Turn { question: string; response?: CopilotResponse }

export default function CopilotPage() {
  const { data: status } = useCopilotStatus();
  const ask = useAskCopilot();
  const [input, setInput] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);

  function submit(question: string) {
    const q = question.trim();
    if (!q) return;
    setInput("");
    const idx = turns.length;
    setTurns((t) => [...t, { question: q }]);
    ask.mutate(q, {
      onSuccess: (response) => {
        setTurns((t) => t.map((turn, i) => (i === idx ? { ...turn, response } : turn)));
      },
    });
  }

  return (
    <div>
      <PageHeader
        question="What should we do next?"
        title="AI Operations Copilot"
        description="Ask operational questions in natural language. Every answer is grounded in live data."
        actions={
          <Tag>
            <Sparkles className="h-3 w-3" /> Engine: {status?.engine ?? "…"}
          </Tag>
        }
      />

      <div className="mx-auto max-w-3xl">
        {turns.length === 0 && (
          <div className="panel mb-4 p-6 text-center">
            <BrainCircuit className="mx-auto h-8 w-8 text-accent" />
            <p className="mt-3 text-sm text-ink-muted">
              Grounded in {status?.ai_enabled ? "OpenAI + live operational data" : "the deterministic engine over live operational data"}.
              Try one of these:
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {status?.suggested_questions.map((q) => (
                <button key={q} onClick={() => submit(q)} className="btn-ghost text-xs">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-4">
          {turns.map((turn, i) => (
            <div key={i} className="space-y-3">
              <div className="flex justify-end">
                <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-accent px-4 py-2.5 text-sm text-white">
                  {turn.question}
                </div>
              </div>
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl rounded-bl-sm border border-line bg-bg-panel px-4 py-3">
                  {!turn.response ? (
                    <div className="flex items-center gap-2 text-sm text-ink-muted"><Spinner /> Analyzing operational data…</div>
                  ) : (
                    <div>
                      <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink">{turn.response.answer}</p>
                      <div className="mt-2 flex items-center gap-2 text-[10px] text-ink-faint">
                        <span>engine: {turn.response.engine}</span>
                        <span>·</span>
                        <span>{Math.round(turn.response.confidence * 100)}% confidence</span>
                      </div>
                      {turn.response.suggested_actions.length > 0 && (
                        <div className="mt-3 border-t border-line pt-2">
                          <p className="stat-label mb-1.5">Suggested actions</p>
                          <ul className="space-y-1">
                            {turn.response.suggested_actions.map((a, j) => (
                              <li key={j} className="flex gap-2 text-xs text-ink-muted"><span className="text-accent">→</span> {a}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {turn.response.follow_ups.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-1.5">
                          {turn.response.follow_ups.map((f) => (
                            <button key={f} onClick={() => submit(f)} className="rounded-full border border-line bg-bg-soft px-2.5 py-1 text-[11px] text-ink-muted hover:border-accent">
                              {f}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); submit(input); }}
          className="sticky bottom-4 mt-4 flex items-center gap-2 rounded-xl border border-line bg-bg-panel p-2 shadow-panel"
        >
          <input
            className="flex-1 bg-transparent px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:outline-none"
            placeholder="Ask the operations copilot…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" disabled={ask.isPending} className="btn-primary">
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

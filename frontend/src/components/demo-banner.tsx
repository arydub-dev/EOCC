"use client";

import { useState } from "react";
import { Sparkles, X } from "lucide-react";

export function DemoBanner() {
  const [dismissed, setDismissed] = useState(false);
  if (dismissed) return null;
  return (
    <div className="flex items-center gap-2 border-b border-accent/20 bg-accent/[0.07] px-6 py-2 text-xs text-accent">
      <Sparkles className="h-3.5 w-3.5 shrink-0" />
      <p className="flex-1">
        <span className="font-semibold">Demo Workspace</span>
        <span className="text-accent/80">
          {" "}
          · This workspace contains synthetic operational data for evaluation purposes.
        </span>
      </p>
      <button onClick={() => setDismissed(true)} className="text-accent/70 hover:text-accent" aria-label="Dismiss">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

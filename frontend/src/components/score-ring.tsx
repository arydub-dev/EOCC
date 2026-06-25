import { scoreColor } from "@/lib/utils";

export function ScoreRing({
  value,
  size = 132,
  label,
  invertColor = false,
  caption,
}: {
  value: number;
  size?: number;
  label?: string;
  invertColor?: boolean;
  caption?: string;
}) {
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circ = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, value));
  const offset = circ - (pct / 100) * circ;
  // For "health" scores higher is better → invert the risk palette.
  const color = invertColor ? scoreColor(100 - value) : scoreColor(value);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#1f2a3a" strokeWidth={stroke} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-ink">{value.toFixed(0)}</span>
        {label && <span className="text-[10px] uppercase tracking-wider text-ink-faint">{label}</span>}
        {caption && <span className="mt-0.5 text-[10px] font-medium" style={{ color }}>{caption}</span>}
      </div>
    </div>
  );
}

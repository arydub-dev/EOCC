import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0a0e16",
          soft: "#0f1521",
          panel: "#121a28",
          elevated: "#16202f",
        },
        line: "#1f2a3a",
        ink: {
          DEFAULT: "#e6edf6",
          muted: "#8a99ad",
          faint: "#5b6b80",
        },
        accent: {
          DEFAULT: "#3b82f6",
          soft: "#1d4ed8",
        },
        status: {
          normal: "#22c55e",
          watch: "#eab308",
          warning: "#f59e0b",
          critical: "#ef4444",
          info: "#38bdf8",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(59,130,246,0.4), 0 0 24px -4px rgba(59,130,246,0.4)",
      },
      keyframes: {
        pulseDot: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
      },
      animation: {
        pulseDot: "pulseDot 1.8s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;

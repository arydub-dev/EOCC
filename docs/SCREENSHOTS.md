# EOCC — Screenshot Capture Plan

A repeatable plan for capturing marketing/demo screenshots once the stack is running
(`docker compose up`). Sign in as **admin@eocc.gov / admin123** for full access.

## Capture environment

- Viewport: **1920×1080**, device scale **2x** (retina), dark theme (default).
- Seed defaults produce a busy, "alive" system — ideal for screenshots.
- Hide the system clock seconds if a static look is preferred.

## Recommended automated capture (Playwright)

```bash
npx playwright install chromium
node scripts/screenshots.mjs   # (optional helper you can add)
```

A minimal helper would: log in, store the JWT in `localStorage` as `eocc_token`,
then visit each route and call `page.screenshot()`.

## Shot list

| # | Route | Filename | What to highlight |
| --- | --- | --- | --- |
| 1 | `/` | `01-mission-control.png` | Health ring, metric tiles, recommended actions, SITREP |
| 2 | `/incidents` | `02-incidents.png` | Filtered list + severity coloring; open the detail drawer for `03-incident-timeline.png` |
| 3 | `/resources` | `04-resources.png` | Availability bar chart + fleet summary + readiness bars |
| 4 | `/hospitals` | `05-hospitals.png` | "At-risk only" toggle on; ICU/ER/bed load bars |
| 5 | `/shelters` | `06-shelters.png` | Strain scores + food/water supply buffers |
| 6 | `/map` | `07-operations-map.png` | All layers on, an incident popup open |
| 7 | `/risk` | `08-risk-intelligence.png` | Five category cards with scores + recommendations |
| 8 | `/alerts` | `09-alerts.png` | Open alerts with acknowledge/resolve actions |
| 9 | `/simulations` | `10-simulation.png` | Run a hurricane scenario; show projected impact + mitigations |
| 10 | `/copilot` | `11-copilot.png` | Ask "Which hospitals are under the most stress?"; show grounded answer + suggested actions |
| 11 | `/briefing` | `12-executive-briefing.png` | Generated executive summary + sections |
| 12 | `/integration` | `13-data-integration.png` | Overview tab (connector health) + Pipeline Monitor tab |
| 13 | `/login` | `14-login.png` | Split hero with the three guiding questions |
| 14 | `/docs` | `15-openapi.png` | Swagger UI showing the full API surface |

## Tips

- For the map shot, zoom to a region (e.g. Gulf Coast) where incident circles overlap
  hospitals/shelters to show the color-coded risk story.
- For the copilot shot, capture after a follow-up question to show the conversational flow.
- Use the Risk page **Regenerate** and Alerts **Resolve** actions to demonstrate
  interactivity in animated GIFs/screen recordings.

# Assets

This directory holds image assets for the project — primarily the product
screenshots referenced by the README and the marketing site.

Screenshots are not generated automatically because they require a running,
seeded stack. To produce them, start the platform (`docker compose up` or
`./scripts/dev.sh`), sign in with the demo administrator account, and follow the
repeatable capture plan in [`../docs/SCREENSHOTS.md`](../docs/SCREENSHOTS.md).

Save captured images here using the filenames listed in the shot list
(`01-mission-control.png`, `02-incidents.png`, …) so the documentation links
resolve.

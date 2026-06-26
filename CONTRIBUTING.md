# Contributing to EOCC

Thank you for your interest in contributing to the Emergency Operations Command Center. This guide covers everything you need to set up a development environment, make a change, and get it merged. Contributions of all kinds are welcome: bug fixes, features, documentation, tests, and tooling.

By participating in this project you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Project Layout](#project-layout)
- [Coding Standards](#coding-standards)
- [Branch Naming](#branch-naming)
- [Commit Conventions](#commit-conventions)
- [Pull Request Workflow](#pull-request-workflow)
- [Testing](#testing)
- [Linting and Formatting](#linting-and-formatting)
- [Documentation Standards](#documentation-standards)
- [Reporting Issues](#reporting-issues)
- [License and Contributions](#license-and-contributions)

## Ways to Contribute

- **Report bugs** and **request features** using the [issue templates](.github/ISSUE_TEMPLATE).
- **Improve documentation** — accuracy and clarity fixes are always valuable.
- **Submit code** — pick up an open issue or propose a change. For anything substantial, open an issue first so we can align on the approach before you invest time.
- **Report security vulnerabilities** privately following [SECURITY.md](SECURITY.md). Do not open public issues for security problems.

## Development Setup

A new contributor should be able to clone, configure, run, and reach the application in about fifteen minutes.

### Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- Docker and Docker Compose (optional, for the full stack)
- Git

### Backend (FastAPI)

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt        # test/lint tooling
export DATABASE_URL="sqlite:///./eocc.db"   # zero-infra local DB
uvicorn app.main:app --reload --port 8000
```

The API is then available at `http://localhost:8000` with docs at `/docs`.

### Frontend (Next.js)

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"
npm run dev
```

The console is then available at `http://localhost:3000`.

### Full stack via Docker

```bash
cp .env.example .env   # set SECRET_KEY, ENCRYPTION_KEY, POSTGRES_PASSWORD
docker compose up --build
```

A convenience script is provided at [`scripts/dev.sh`](scripts/dev.sh).

## Project Layout

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for a complete breakdown. The essentials:

- `backend/app/api/routes/` — thin HTTP routers. Keep business logic out of these.
- `backend/app/services/` — domain logic, persistence, and audit calls.
- `backend/app/engines/` — pure, deterministic computation. **No I/O.**
- `backend/app/models/` — ORM entities and enums.
- `frontend/src/app/` — routes (App Router); `frontend/src/lib/` — API client, hooks, auth, types.

When adding a feature, respect the layering: routers depend on services, services depend on engines and models, and engines depend on nothing but the snapshot they are given.

## Coding Standards

**Python**

- Target Python 3.12; use type hints throughout (`from __future__ import annotations`).
- Follow PEP 8; formatting and linting are enforced by [Ruff](https://docs.astral.sh/ruff/).
- Keep functions focused; prefer pure functions in `engines/`.
- Never build SQL strings — use the ORM. Never log secrets or tokens.
- All new endpoints must declare a permission via `require_permission(...)` and write an audit record for mutating actions.

**TypeScript / React**

- Strict TypeScript; no implicit `any`.
- Components are function components with hooks. Data fetching goes through `lib/hooks.ts` (TanStack Query), not ad-hoc `fetch`.
- Do not make authorization decisions on the client; use server-provided permissions only to shape the UI.

**General**

- Add comments only to explain non-obvious intent or constraints, not to narrate code.
- Keep changes scoped. Unrelated refactors belong in separate PRs.

## Branch Naming

Create a topic branch from `main` using the form `type/short-description`:

```
feat/incident-bulk-import
fix/refresh-token-rotation
docs/api-pagination
chore/bump-fastapi
test/scoring-engine
refactor/snapshot-builder
```

Use the same `type` prefixes as commits (below).

## Commit Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/). The format is:

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Examples:

```
feat(simulations): add utility-grid cascade modeling
fix(auth): revoke session family on refresh-token reuse
docs(security): document responsible-disclosure timelines
```

Breaking changes must include a `BREAKING CHANGE:` footer (or a `!` after the type, e.g. `feat!:`). Commit messages should explain the *why* of a change, not just the *what*.

## Pull Request Workflow

1. Fork the repository (or create a branch if you have write access).
2. Create a topic branch following the naming convention.
3. Make your change with accompanying tests and documentation.
4. Run linting and tests locally; ensure they pass.
5. Open a pull request against `main` and complete the [pull-request template](.github/pull_request_template.md): description, testing performed, screenshots (for UI changes), checklist, and breaking changes.
6. Ensure CI is green. The pipeline runs linting, type-checking, tests, and security scans.
7. Address review feedback. At least one maintainer approval is required to merge.
8. PRs are merged using **squash merge** so `main` keeps a clean, linear history; the squash commit message must follow Conventional Commits.

Keep pull requests focused and reasonably small — they are easier to review and safer to merge.

## Testing

- Backend tests use [pytest](https://docs.pytest.org/) and live in `backend/tests/`.

  ```bash
  cd backend && source .venv/bin/activate
  pytest -q
  ```

- New domain logic in `services/` and `engines/` should be covered by unit tests. Because engines are pure functions, they are straightforward to test in isolation.
- Bug fixes should include a regression test that fails before the fix and passes after.
- Frontend changes must pass type-checking (`npx tsc --noEmit`) and the linter (`npm run lint`).

## Linting and Formatting

- **Python:** `ruff check backend` and `ruff format --check backend`.
- **TypeScript:** `npm run lint` and `npx tsc --noEmit` in `frontend/`.

CI enforces all of the above; running them locally before pushing keeps the feedback loop fast.

## Documentation Standards

- Update documentation in the same PR as the code it describes. A feature is not complete until it is documented.
- Keep `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, and the `docs/` references accurate — they are the source of truth for evaluators and operators.
- Use Mermaid for diagrams so they remain version-controlled and reviewable in diffs.
- Write in clear, neutral, technical prose. Describe what the software does and why, without marketing language.

## Reporting Issues

Use the [issue templates](.github/ISSUE_TEMPLATE) for bug reports, feature requests, and questions. Provide enough context to reproduce or understand the request. For security vulnerabilities, follow [SECURITY.md](SECURITY.md) — never file them as public issues.

## License and Contributions

EOCC is licensed under the **Apache License 2.0**.

Apache 2.0 was chosen deliberately:

- **Permissive adoption.** Organizations — including commercial and government users — can adopt, modify, and deploy the platform without copyleft obligations, which is important for an operational tool intended for broad institutional use.
- **Explicit patent grant.** Unlike MIT/BSD, Apache 2.0 includes an express patent license from contributors and a patent-retaliation clause, giving adopters clearer legal certainty.
- **Trademark clarity.** It explicitly does not grant trademark rights, protecting the project's identity.
- **Ecosystem norm.** It is the de facto standard for enterprise-grade infrastructure and SaaS projects, easing legal review for adopters.

By submitting a contribution, you agree that your contribution is licensed under the Apache License 2.0 and that you have the right to submit it under that license (per the inbound=outbound convention).

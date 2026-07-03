# Provenance Gate

Provenance Gate is a public-safe Python web app for the AMD Developer Hackathon: ACT II, Unicorn Track. It turns a synthetic Markdown source into reviewable claim cards, verifies that each quoted citation exists in the source, records human approve or reject decisions in a hash-linked audit ledger, and exports inspectable JSON decision packets.

## What the Demo Does

1. Loads `fixtures/synthetic_source.md`.
2. Uses `DemoProvider` to generate deterministic claim cards.
3. Verifies every citation with exact passage matching.
4. Shows claim, evidence, and verification status in the browser.
5. Lets a reviewer approve or reject each claim.
6. Appends each review action to `audit-ledger.jsonl`.
7. Exports a JSON decision packet for reviewed claims.

`DEMO_MODE=true` is the default. No external API keys are required, and no external APIs are called in the default path.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Run With Docker

```bash
docker compose up --build
```

Open `http://127.0.0.1:8000`.

## Run Tests

```bash
pytest
```

The test suite covers citation verification, review state transitions, hash-chain integrity, and decision-packet export.

## Configuration

Copy `.env.example` if you want to customize local settings.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEMO_MODE` | `true` | Keeps the app on deterministic fixture output. |
| `PROVIDER` | `demo` | Selects `demo` or the future `fireworks` provider boundary. |
| `SOURCE_FIXTURE` | `synthetic_source.md` | Source fixture loaded from `fixtures/`. |
| `DATA_DIR` | `data` locally, `/app/data` in Docker | Stores review state and the JSONL audit ledger. |
| `REVIEWER` | `demo-reviewer` | Reviewer label written into ledger entries. |
| `FIREWORKS_API_KEY` | unset | Future Fireworks credential, read only from environment variables. |

## Provider Boundary

`DemoProvider` returns deterministic synthetic claim cards and is the default provider.

`FireworksProvider` exists as an integration boundary. It reads `FIREWORKS_API_KEY` only from environment variables and does not make any external call in this vertical slice. A real AMD / Fireworks / Gemma integration should be added only after credentials, supported model names, and official request details are confirmed.

## AMD / Fireworks / Gemma Plan

Future integration should keep the same safety shape:

1. Confirm the supported Fireworks model name and request schema from official sources or project-provided credentials.
2. Enable only with `DEMO_MODE=false` and `PROVIDER=fireworks`.
3. Send only synthetic fixture content during the hackathon demo.
4. Require provider output to match the claim-card schema.
5. Deterministically reject or flag citations whose quotes are not found exactly in the source.
6. Keep human review and hash-linked ledger export unchanged.

See `docs/PROJECT_BRIEF.md` for the full project scope and submission checklist.

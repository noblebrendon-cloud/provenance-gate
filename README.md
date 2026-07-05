# Provenance Gate

[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21208506.svg)](https://doi.org/10.5281/zenodo.21208506)

Provenance Gate — a source-grounded AI review workflow for reviewable claims, deterministic citation verification, human decisions, and hash-linked audit records.

The project demonstrates a local review gate for generated or candidate claims. Each claim must point to an exact quoted passage from a source document. The application verifies that quote deterministically, requires a human approve or reject decision, records the decision in a hash-linked audit ledger, and exports an inspectable JSON decision packet.

## How to Cite

Use the concept DOI for a general citation of the evolving project:

https://doi.org/10.5281/zenodo.21208506

Use the version DOI when citing v0.1.3 specifically:

https://doi.org/10.5281/zenodo.21208507

Preferred citation for v0.1.3:

Coleman, Brendon R. (2026). noblebrendon-cloud/provenance-gate: v0.1.3 — Automated Continuous Verification (v0.1.3). Zenodo. https://doi.org/10.5281/zenodo.21208507

The machine-readable citation metadata lives in `CITATION.cff`.

## What It Does

1. Loads a synthetic Markdown source from `fixtures/synthetic_source.md`.
2. Uses `DemoProvider` to generate deterministic claim cards.
3. Verifies every quoted citation with exact source-text matching.
4. Shows the source, claim, citation, verification result, and review state in a browser UI.
5. Lets a reviewer approve or reject each claim.
6. Appends each review action to a local JSONL audit ledger.
7. Shows ledger integrity status, latest hashes, and demo tamper detection.
8. Exports a JSON decision packet for reviewed claims.

`DEMO_MODE=true` is the default. The default workflow requires no API key and makes no external API calls.

## Run Tests

```bash
python -m pytest
```

The test suite covers citation verification, review state transitions, hash-chain integrity, inspectable audit status, provider defaults, and decision-packet export.

## Continuous Verification

GitHub Actions runs on pushes to `main` and pull requests targeting `main`.

The CI workflow installs dependencies from `requirements.txt`, then runs:

```bash
python -m pytest
python -m compileall app tests
```

CI verifies the Python test suite and compile health. It does not deploy the app, call external APIs, run Fireworks, build Docker, replace human review, or prove semantic truth.

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

## Browser Demo

The browser demo proves the local control loop:

- The source fixture is visible beside generated claim cards.
- Each claim shows its exact quoted citation.
- Citation verification reports whether the quote exists in the loaded source.
- A reviewer must approve or reject a claim before export.
- The Audit Integrity panel shows the ledger entry count, chain status, latest record hash, and previous-hash link.
- In demo mode, a reviewer can simulate ledger tampering and see validation fail.
- Reset Demo clears runtime demo state and returns the ledger to a valid pristine state.
- The exported packet contains the claim, evidence, verification result, review decision, and ledger reference.

## Configuration

Copy `.env.example` if you want to customize local settings.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEMO_MODE` | `true` | Keeps the app on deterministic fixture output. |
| `PROVIDER` | `demo` | Selects the deterministic demo provider unless explicitly changed. |
| `SOURCE_FIXTURE` | `synthetic_source.md` | Source fixture loaded from `fixtures/`. |
| `DATA_DIR` | `data` locally, `/app/data` in container settings | Stores review state and the JSONL audit ledger. |
| `REVIEWER` | `demo-reviewer` | Reviewer label written into ledger entries. |
| `FIREWORKS_API_KEY` | unset | Optional future Fireworks credential, read only from environment variables. |

## Optional Provider Boundary

`DemoProvider` returns deterministic synthetic claim cards and is the default provider.

`FireworksProvider` exists only as an optional future integration boundary. It reads `FIREWORKS_API_KEY` from environment variables, but the current implementation does not make external API calls. A real Fireworks or Gemma integration should be added only after credentials, supported model names, and official request details are confirmed.

## Container Configuration

`Dockerfile` and `compose.yaml` are included for container packaging. Docker fresh-clone verification for the public `v0.1.1` tag is documented in `docs/DOCKER_VERIFICATION.md`. The current runtime image does not package the test suite, so tests run in the development and CI environments.

## Current Limitations

- Demo mode is the default and uses deterministic fixture outputs.
- The included source document is synthetic.
- The Fireworks provider boundary is not enabled by default and does not call an external API in this version.
- The app is a single-user prototype, not a production security system.
- Exact quote verification proves only that the quoted passage appears in the source; it does not prove that the claim is semantically true.
- Hash-chain validation detects changes to the local ledger sequence; it does not prevent every compromise or create production-grade security.

See `docs/PROJECT_BRIEF.md`, `docs/PORTFOLIO_CASE_STUDY.md`, and `docs/KNOWN_LIMITATIONS.md` for more context.

## License

This project is released under the MIT License. See `LICENSE`.

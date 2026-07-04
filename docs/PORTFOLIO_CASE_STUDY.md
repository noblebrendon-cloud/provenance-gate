# Portfolio Case Study

## Problem

Generated claims can look credible when they include citations, but a citation is not provenance unless the cited passage can be inspected and verified. Provenance Gate explores a narrow, local control loop for making claims reviewable: show the source, verify the quoted evidence, require a human decision, and record the decision in an audit trail.

## Core Workflow

1. Load a synthetic Markdown source fixture.
2. Generate deterministic claim cards in demo mode.
3. Attach each claim to an exact quoted source passage.
4. Verify the quote by deterministic exact-text matching.
5. Display the claim, quote, source line range, and verification result.
6. Require a reviewer to approve or reject the claim.
7. Append the review action to a hash-linked JSONL ledger.
8. Display audit integrity status for the local ledger.
9. In demo mode, simulate ledger tampering and observe validation fail.
10. Export an inspectable JSON decision packet.

## Architecture Summary

- `app/providers.py` defines the provider boundary. `DemoProvider` is deterministic and enabled by default. `FireworksProvider` is an optional future boundary and does not make external calls in this version.
- `app/citation.py` verifies quoted passages by exact source-text matching.
- `app/review.py` validates reviewer decisions and prevents silent overwrites.
- `app/ledger.py` appends review actions, summarizes audit integrity, simulates demo tampering, and validates the hash chain.
- `app/decision_packet.py` builds exportable JSON packets.
- `app/main.py` exposes the browser UI and API routes.
- `fixtures/` contains synthetic source material only.

## What Was Implemented

- A Python web application with a small browser UI.
- Deterministic claim cards in demo mode.
- Exact citation verification against a local Markdown fixture.
- Human approve or reject workflow.
- Hash-linked JSONL audit ledger.
- Browser-visible audit integrity status.
- Demo-only tamper simulation and reset.
- JSON decision-packet export.
- Tests for citation verification, review transitions, ledger integrity, audit status, provider defaults, and packet export.

## Verification Evidence

Local verification uses:

```powershell
python -m pytest
python -m compileall app tests
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The browser demo shows that a reviewer can inspect the source, verify an exact quote, approve or reject a claim, inspect ledger integrity, simulate a controlled tamper, reset demo state, and export a packet containing the review decision and ledger reference.

## What This Project Does Not Claim To Solve

- It does not prove that a claim is semantically true.
- It does not certify model behavior.
- It does not provide production authentication or authorization.
- It does not protect against every possible local tampering scenario.
- It detects changes to the local ledger sequence; it does not prevent all compromise.
- It does not call Fireworks, Gemma, or any external model by default.
- It does not rely on private data, user data, or external-service configuration.

## Future Extension Points

- Add a real external provider implementation after supported model names, credentials, and official request details are available.
- Add source-upload support with strict file-type and size limits.
- Add a persistent database for multi-session review history.
- Add user authentication and reviewer identity controls.
- Add richer citation matching, such as normalized whitespace or passage anchoring, while preserving deterministic verification.
- Add a signed export format for stronger audit portability.

# v0.1.1 Inspectable Integrity Plan

## Goal

Make the existing hash-linked audit ledger visibly inspectable in the browser. The release should show that Provenance Gate can detect when its local decision history no longer matches the recorded hash chain.

## Scope

- Add an Audit Integrity section to the browser UI.
- Show ledger entry count, chain status, latest record hash, and the latest previous-hash relationship.
- Explain plainly what validation checks and what it does not prove.
- Add a demo-only tamper simulation that changes safe runtime ledger data, never source fixtures.
- Add a demo-only reset that restores pristine valid demo state.
- Keep approve/reject, citation verification, ledger append, and decision-packet export behavior working.
- Do not add authentication, databases, external APIs, credentials, deployment, PDFs, user accounts, or Docker verification.

## Implementation Outline

1. Extend ledger utilities with an audit summary and a controlled demo tamper helper.
2. Add JSON endpoints for audit status and demo tamper simulation.
3. Restrict tamper and reset actions to `DEMO_MODE`.
4. Render the audit summary and controls in the existing Flask/Jinja UI.
5. Refresh audit status after review actions and tamper actions.
6. Add tests for valid status, tampered status, reset restoration, demo-mode restrictions, and review/export regression.
7. Update public docs only where needed to describe inspectable integrity and its limits.

## Validation

- Run `python -m pytest`.
- Run `python -m compileall app tests`.
- Start the direct local server with `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- Smoke test: valid ledger state, approve a claim, simulate tamper, observe invalid integrity status, reset demo state, observe valid pristine state.

## Limitations To State Publicly

- Hash-chain validation detects changes to the local ledger sequence.
- It does not prove semantic truth.
- It does not prevent every compromise.
- It is not production-grade security.
- Docker configuration exists but is not locally verified in this environment.

# Provenance Gate Demo Script

## Setup

Run the app directly:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## 2-3 Minute Walkthrough

1. Point out that the app is running in demo mode with the synthetic source fixture `fixtures/synthetic_source.md`.
2. Show the source pane and one claim card side by side.
3. Read the claim and its quoted citation, then note the `verified` badge and source line number.
4. Approve one verified claim or reject a claim as a reviewer decision.
5. Show that the claim changes from `pending` to the final decision and the export link appears.
6. Export the JSON decision packet.
7. Open the packet and point to `claim`, `evidence`, `verification_result`, `review_decision`, and `ledger_reference`.
8. Close by noting that demo mode uses deterministic fixture output and no API key or external model call.

## Framing

- A citation in generated text is not the same thing as verified provenance.
- Provenance Gate separates claim generation, deterministic citation verification, human judgment, and recorded decision history.
- The local demo proves exact source-text verification, human approve or reject decisions, hash-linked ledger entries, and inspectable packet export.
- The prototype does not claim production security, semantic truth verification, or external-model reliability.

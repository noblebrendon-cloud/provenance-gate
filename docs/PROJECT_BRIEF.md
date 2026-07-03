# Provenance Gate Project Brief

## Problem

Reviewers need a simple way to inspect generated claims before those claims are reused in reports, submissions, or downstream tools. A claim is only useful when it is tied to source evidence that can be checked exactly. Provenance Gate demonstrates a public-safe workflow where every candidate claim must cite a quoted passage from a synthetic source document, the citation is verified deterministically, and a human decision is recorded in an audit trail.

## Intended User

The intended user is a reviewer, technical editor, evaluator, or hackathon judge who wants to inspect claim-level provenance without trusting hidden model state. The user should be able to load a fixture, inspect candidate claim cards, see whether each quoted source passage exists in the source document, approve or reject each claim, and export a compact packet that can be audited later.

## Core Workflow

1. Load one synthetic Markdown source file from `fixtures/`.
2. Generate candidate claim cards from a provider.
3. Attach each claim to an exact quoted source citation.
4. Verify every citation by checking that the quote exists in the source document.
5. Display the verification result beside each claim in the browser.
6. Require a human reviewer to approve or reject each claim.
7. Append every review action to a hash-linked audit ledger.
8. Export a JSON decision packet containing the claim, evidence, verification result, review decision, and ledger reference.

## Explicit Non-Goals

- No private repositories, private files, unpublished writing, credentials, runtime data, or user data.
- No external API call in default demo mode.
- No Fireworks request unless explicitly enabled through environment configuration.
- No invented AMD, Fireworks, or Gemma API details.
- No production authentication, multi-user authorization, or hosted deployment.
- No persistent database beyond a local JSONL audit ledger suitable for demo inspection.
- No claim generation from arbitrary uploaded documents in the initial vertical slice.
- No guarantee that a verified citation proves the claim is semantically true; verification only proves that the quoted passage exists exactly in the loaded source.

## AMD / Fireworks / Gemma Use Plan

The public demo ships with `DemoProvider`, which returns deterministic claim cards from synthetic fixtures and requires no API keys.

The application also defines a `FireworksProvider` boundary for a future AMD / Fireworks / Gemma integration. When credentials and supported model names are available, the provider can be extended to call a Fireworks-hosted Gemma model for candidate claim generation while keeping the rest of the workflow unchanged: citation verification remains deterministic, review decisions remain human-controlled, and the audit ledger remains hash-linked.

Planned integration steps:

1. Confirm the supported Fireworks model identifier and request schema from official documentation or project-provided credentials.
2. Enable the provider only when `DEMO_MODE=false`, `PROVIDER=fireworks`, and `FIREWORKS_API_KEY` is present in the environment.
3. Send only synthetic fixture text during the hackathon demo unless the project scope changes.
4. Require the model output to match the internal claim-card schema.
5. Reject or flag any model claim whose quoted passage cannot be found exactly in the source.
6. Keep all review decisions and exports inspectable through the same ledger and decision-packet format.

## Demo Narrative

Provenance Gate opens with a synthetic Markdown source about a fictional pilot program. The demo provider produces a small set of claim cards, each with a quoted citation. The app verifies the quote against the source and displays a clear verified or failed status. The reviewer approves claims that are acceptable, rejects claims that should not pass, and exports a JSON packet for any reviewed claim. The packet shows the claim, evidence, deterministic verification result, reviewer decision, and ledger entry reference so the decision can be inspected outside the app.

## Hackathon Submission Checklist

- [ ] Public-safe repository contents only.
- [ ] `DEMO_MODE` defaults to no external API calls.
- [ ] Synthetic fixture source included under `fixtures/`.
- [ ] Provider interface includes `DemoProvider` and `FireworksProvider`.
- [ ] Browser UI shows claim cards and citation verification results.
- [ ] Reviewer can approve or reject each claim.
- [ ] Review actions append to a hash-linked audit ledger.
- [ ] Decision packet export includes claim, evidence, verification, review decision, and ledger reference.
- [ ] Automated tests cover citation verification, review transitions, hash-chain integrity, and decision-packet export.
- [ ] Dockerfile and Compose file support `docker compose up --build`.
- [ ] README explains local and container usage.
- [ ] Documentation includes AMD / Fireworks / Gemma integration plan without inventing unavailable API details.

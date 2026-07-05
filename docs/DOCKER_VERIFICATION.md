# Docker Verification

## Verification Date

July 5, 2026

## Operating Environment

- Host OS: Windows with Docker Desktop
- Docker: `Docker version 29.6.1, build 8900f1d`
- Docker Compose: `Docker Compose version v5.3.0`
- Repository under test: `https://github.com/noblebrendon-cloud/provenance-gate.git`
- Verified release tag: `v0.1.1`
- Verified commit: `b5eba4d636d6dead1aff2274766bde2e652493d1`

## Exact Commands Run

```powershell
New-Item -ItemType Directory -Force E:\docker-verification | Out-Null

if (Test-Path E:\docker-verification\provenance-gate-v0.1.1) {
    throw "Verification folder already exists. Stop and inspect it before deleting anything."
}

git clone --branch v0.1.1 --depth 1 `
  https://github.com/noblebrendon-cloud/provenance-gate.git `
  E:\docker-verification\provenance-gate-v0.1.1

Set-Location E:\docker-verification\provenance-gate-v0.1.1

git status -sb
git describe --tags --exact-match
```

The fresh clone required this local Git safety exception before `git status` and `git describe` would run on the Windows filesystem:

```powershell
git config --global --add safe.directory E:/docker-verification/provenance-gate-v0.1.1
```

The tag check returned:

```text
v0.1.1
```

Docker was started from the fresh clone with:

```powershell
Set-Location E:\docker-verification\provenance-gate-v0.1.1
docker compose up --build
```

After verification, the temporary Compose resources were shut down with:

```powershell
docker compose down
```

## Verified Workflow Steps

The fresh clone at `v0.1.1` successfully:

1. Built a Docker image.
2. Started the Linux container.
3. Exposed the app on `http://127.0.0.1:8000`.
4. Loaded the browser UI.
5. Displayed the synthetic source.
6. Displayed claim `claim-001` and its exact quoted citation.
7. Showed Audit Integrity as `Valid` with `0` ledger entries before review.
8. Approved `claim-001`.
9. Showed Audit Integrity as `Valid` with `1` ledger entry.
10. Exported the decision packet for `claim-001`.
11. Confirmed the packet included `review_decision: approved`, a ledger reference, and `fixtures/synthetic_source.md` as the evidence path.
12. Ran the demo tamper simulation.
13. Showed Audit Integrity as `Invalid`.
14. Displayed the validation error: `Entry 1 hash does not match its payload.`
15. Reset the demo state.
16. Showed Audit Integrity as `Valid` with `0` ledger entries.

## Result

Docker verification succeeded for the public `v0.1.1` tag from a fresh clone.

This verifies that the public repository release can reproduce the local demo workflow in Docker without relying on the original working directory.

## Known Limitations

- Docker configuration is verified for the `v0.1.1` browser workflow described above.
- The line `ASGI 'lifespan' protocol appears unsupported` appeared in container logs and is informational for this app.
- The `/favicon.ico 404` log entry is cosmetic.
- The current Docker image does not include the `tests/` directory, so the test suite was not run inside the container.
- The app remains a single-user prototype.
- Hash-chain validation detects changes to the local ledger sequence; it does not prove semantic truth, prevent every compromise, or create production-grade security.

## Cleanup Status

Temporary container resources were removed with `docker compose down`.

The temporary fresh clone was intentionally left in place until this verification record could be committed.

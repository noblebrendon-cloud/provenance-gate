# Known Limitations

- `DEMO_MODE` is the default.
- Fixtures are synthetic and are stored under `fixtures/`.
- `DemoProvider` is deterministic and is the verified default provider.
- `FireworksProvider` is not enabled by default.
- `FireworksProvider` does not make external API calls in this version.
- Docker configuration exists, but it has not been locally verified because Docker is unavailable in this environment.
- The verified run path is the direct local server command: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- This is a single-user prototype, not a production security system.
- Exact quote verification confirms that cited text appears in the source; it does not prove semantic truth.
- The local JSONL ledger is inspectable and hash-linked, but it is not a substitute for a hardened append-only storage service.

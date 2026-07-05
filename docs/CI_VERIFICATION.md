# CI Verification

## What CI Verifies

GitHub Actions runs the project verification workflow on every push to `main` and every pull request targeting `main`.

The workflow:

1. Checks out the repository on an Ubuntu runner.
2. Sets up Python 3.12.
3. Installs dependencies from `requirements.txt`.
4. Runs `python -m pytest`.
5. Runs `python -m compileall app tests`.

These checks verify the Python test suite and basic import/compile health for the application and tests.

## What CI Does Not Verify

- It does not deploy the application.
- It does not call external APIs.
- It does not configure Fireworks or any other model provider.
- It does not build or run Docker.
- It does not verify browser screenshots or video capture.
- It does not replace human review of claim quality.
- It does not prove semantic truth for any claim.
- It does not provide production-grade security certification.

## Docker Verification Relationship

Docker fresh-clone validation was performed manually for `v0.1.2` and documented in `docs/DOCKER_VERIFICATION.md`.

That manual verification proved the public `v0.1.1` tag could build a Docker image from a clean clone, run the browser workflow in a container, export a decision packet, detect a controlled tamper event, and reset to a valid demo state.

CI does not replace that Docker verification. The current CI workflow is intentionally narrower: it verifies tests and compile validation on repository changes.

## Human Review Boundary

Continuous verification checks that the software still behaves as tested. It does not decide whether a claim should be trusted. Provenance Gate still requires a human approve or reject decision, and exact citation verification only proves that the quoted passage appears in the source.

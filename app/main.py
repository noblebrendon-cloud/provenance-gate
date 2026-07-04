from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for

from app.citation import VerificationResult, verify_citation
from app.decision_packet import build_decision_packet
from app.ledger import (
    LedgerTamperError,
    audit_status,
    find_entry_by_hash,
    simulate_demo_tamper,
)
from app.models import ClaimCard
from app.providers import demo_mode_enabled, get_provider
from app.review import ReviewRecord, ReviewStateError, ReviewStore


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _relative_display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    root = _project_root()
    app.config.update(
        PROJECT_ROOT=root,
        FIXTURES_DIR=root / "fixtures",
        SOURCE_FIXTURE=os.environ.get("SOURCE_FIXTURE", "synthetic_source.md"),
        DATA_DIR=Path(os.environ.get("DATA_DIR", root / "data")),
        REVIEWER=os.environ.get("REVIEWER", "demo-reviewer"),
    )
    if test_config:
        app.config.update(test_config)

    def source_path() -> Path:
        return Path(app.config["FIXTURES_DIR"]) / app.config["SOURCE_FIXTURE"]

    def ledger_path() -> Path:
        return Path(app.config["DATA_DIR"]) / "audit-ledger.jsonl"

    def state_path() -> Path:
        return Path(app.config["DATA_DIR"]) / "review-state.json"

    def review_store() -> ReviewStore:
        return ReviewStore(state_path())

    def current_audit_status() -> dict[str, Any]:
        return audit_status(ledger_path()).to_dict()

    def demo_mode_response() -> tuple[Response, int] | None:
        if demo_mode_enabled():
            return None
        return jsonify({"error": "This action is available only when DEMO_MODE=true."}), 403

    def load_source() -> str:
        return source_path().read_text(encoding="utf-8")

    def claim_bundle() -> tuple[str, list[tuple[ClaimCard, VerificationResult]]]:
        source = load_source()
        display_path = _relative_display_path(source_path(), Path(app.config["PROJECT_ROOT"]))
        provider = get_provider()
        claims = provider.generate_claims(source, display_path)
        return source, [(claim, verify_citation(source, claim.citation)) for claim in claims]

    def card_payload(
        claim: ClaimCard,
        verification: VerificationResult,
        review: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "claim": claim.to_dict(),
            "verification": verification.to_dict(),
            "review": review,
        }

    def find_claim(claim_id: str) -> tuple[ClaimCard, VerificationResult] | None:
        _source, pairs = claim_bundle()
        for claim, verification in pairs:
            if claim.id == claim_id:
                return claim, verification
        return None

    @app.get("/")
    def index() -> str:
        source, pairs = claim_bundle()
        state = review_store().all()
        cards = [card_payload(claim, verification, state.get(claim.id)) for claim, verification in pairs]
        audit = current_audit_status()
        return render_template(
            "index.html",
            cards=cards,
            source_text=source,
            source_name=_relative_display_path(source_path(), Path(app.config["PROJECT_ROOT"])),
            provider_name=get_provider().name,
            demo_mode=demo_mode_enabled(),
            audit=audit,
            ledger_valid=audit["valid"],
            ledger_errors=audit["errors"],
        )

    @app.get("/api/claims")
    def api_claims() -> Response:
        _source, pairs = claim_bundle()
        state = review_store().all()
        return jsonify([card_payload(claim, verification, state.get(claim.id)) for claim, verification in pairs])

    @app.get("/api/audit")
    def api_audit() -> Response:
        return jsonify(
            {
                "audit": current_audit_status(),
                "demo_mode": demo_mode_enabled(),
            }
        )

    @app.post("/api/review/<claim_id>")
    def review_claim(claim_id: str) -> tuple[Response, int] | Response:
        found = find_claim(claim_id)
        if found is None:
            return jsonify({"error": "Claim not found."}), 404

        payload = request.get_json(silent=True) or request.form
        decision = str(payload.get("decision", ""))
        claim, verification = found

        try:
            review, ledger_entry = review_store().record_decision(
                claim_id=claim.id,
                decision=decision,
                verification=verification,
                ledger_path=ledger_path(),
                reviewer=app.config["REVIEWER"],
            )
        except ReviewStateError as exc:
            return jsonify({"error": str(exc)}), 409

        return jsonify(
            {
                "status": "ok",
                "review": review.to_dict(),
                "ledger_entry": ledger_entry,
                "audit": current_audit_status(),
                "packet_url": url_for("export_decision_packet", claim_id=claim.id),
            }
        )

    @app.get("/api/export/<claim_id>")
    def export_decision_packet(claim_id: str) -> tuple[Response, int] | Response:
        found = find_claim(claim_id)
        if found is None:
            return jsonify({"error": "Claim not found."}), 404

        review_data = review_store().get(claim_id)
        if review_data is None:
            return jsonify({"error": "Claim has not been reviewed."}), 409

        ledger_entry = find_entry_by_hash(ledger_path(), review_data["ledger_hash"])
        if ledger_entry is None:
            return jsonify({"error": "Ledger entry not found for reviewed claim."}), 500

        claim, verification = found
        review = ReviewRecord(**review_data)
        packet = build_decision_packet(
            claim=claim,
            verification=verification,
            review=review,
            ledger_entry=ledger_entry,
        )
        body = json.dumps(packet, ensure_ascii=True, indent=2, sort_keys=True)
        return Response(
            body,
            mimetype="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={claim_id}-decision-packet.json"
            },
        )

    @app.post("/api/reset")
    def reset_demo() -> Response:
        blocked = demo_mode_response()
        if blocked:
            return blocked
        review_store().reset()
        if ledger_path().exists():
            ledger_path().unlink()
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"status": "reset", "audit": current_audit_status()})
        return redirect(url_for("index"))

    @app.post("/api/audit/tamper")
    def tamper_demo_ledger() -> tuple[Response, int] | Response:
        blocked = demo_mode_response()
        if blocked:
            return blocked
        try:
            simulate_demo_tamper(ledger_path())
        except LedgerTamperError as exc:
            return jsonify({"error": str(exc), "audit": current_audit_status()}), 409
        return jsonify({"status": "tampered", "audit": current_audit_status()})

    return app


flask_app = create_app()
app = WsgiToAsgi(flask_app)


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

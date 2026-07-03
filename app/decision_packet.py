from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.citation import VerificationResult
from app.models import ClaimCard
from app.review import ReviewRecord


def build_decision_packet(
    *,
    claim: ClaimCard,
    verification: VerificationResult,
    review: ReviewRecord | dict[str, Any],
    ledger_entry: dict[str, Any],
) -> dict[str, Any]:
    review_dict = review.to_dict() if isinstance(review, ReviewRecord) else review
    return {
        "packet_schema": "provenance-gate.decision-packet.v1",
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim": claim.to_dict(),
        "evidence": {
            "source_path": claim.citation.source_path,
            "quote": claim.citation.quote,
            "start_line": verification.start_line,
            "end_line": verification.end_line,
        },
        "verification_result": verification.to_dict(),
        "review_decision": review_dict,
        "ledger_reference": {
            "index": ledger_entry["index"],
            "entry_hash": ledger_entry["entry_hash"],
            "previous_hash": ledger_entry["previous_hash"],
        },
    }

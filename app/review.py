from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.citation import VerificationResult
from app.ledger import append_review_action

VALID_DECISIONS = {"approved", "rejected"}


class ReviewStateError(ValueError):
    pass


@dataclass(frozen=True)
class ReviewRecord:
    claim_id: str
    decision: str
    reviewer: str
    decided_at: str
    ledger_index: int
    ledger_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReviewStore:
    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path

    def all(self) -> dict[str, dict[str, Any]]:
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def get(self, claim_id: str) -> dict[str, Any] | None:
        return self.all().get(claim_id)

    def reset(self) -> None:
        if self.state_path.exists():
            self.state_path.unlink()

    def record_decision(
        self,
        *,
        claim_id: str,
        decision: str,
        verification: VerificationResult,
        ledger_path: Path,
        reviewer: str = "demo-reviewer",
    ) -> tuple[ReviewRecord, dict[str, Any]]:
        normalized_decision = decision.strip().lower()
        if normalized_decision not in VALID_DECISIONS:
            raise ReviewStateError("Decision must be approved or rejected.")

        state = self.all()
        if claim_id in state:
            raise ReviewStateError("Claim already has a final review decision.")

        if normalized_decision == "approved" and not verification.verified:
            raise ReviewStateError("A claim cannot be approved when citation verification failed.")

        entry = append_review_action(
            ledger_path,
            claim_id=claim_id,
            decision=normalized_decision,
            reviewer=reviewer,
        )
        record = ReviewRecord(
            claim_id=claim_id,
            decision=normalized_decision,
            reviewer=reviewer,
            decided_at=entry["timestamp"],
            ledger_index=entry["index"],
            ledger_hash=entry["entry_hash"],
        )
        state[claim_id] = record.to_dict()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=True, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return record, entry

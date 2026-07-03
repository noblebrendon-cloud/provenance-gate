import pytest

from app.citation import VerificationResult
from app.review import ReviewStateError, ReviewStore


def verification(verified: bool = True) -> VerificationResult:
    return VerificationResult(
        source_path="fixtures/demo.md",
        quote="Synthetic quote.",
        verified=verified,
        start_char=0 if verified else None,
        end_char=16 if verified else None,
        start_line=1 if verified else None,
        end_line=1 if verified else None,
        reason="ok" if verified else "failed",
    )


def test_pending_claim_can_be_approved(tmp_path) -> None:
    store = ReviewStore(tmp_path / "state.json")
    ledger_path = tmp_path / "ledger.jsonl"

    record, entry = store.record_decision(
        claim_id="claim-001",
        decision="approved",
        verification=verification(True),
        ledger_path=ledger_path,
        reviewer="tester",
    )

    assert record.decision == "approved"
    assert record.ledger_hash == entry["entry_hash"]
    assert store.get("claim-001")["decision"] == "approved"


def test_final_claim_decision_cannot_be_changed(tmp_path) -> None:
    store = ReviewStore(tmp_path / "state.json")
    ledger_path = tmp_path / "ledger.jsonl"
    store.record_decision(
        claim_id="claim-001",
        decision="approved",
        verification=verification(True),
        ledger_path=ledger_path,
        reviewer="tester",
    )

    with pytest.raises(ReviewStateError, match="already has"):
        store.record_decision(
            claim_id="claim-001",
            decision="rejected",
            verification=verification(True),
            ledger_path=ledger_path,
            reviewer="tester",
        )


def test_failed_verification_can_be_rejected_but_not_approved(tmp_path) -> None:
    store = ReviewStore(tmp_path / "state.json")
    ledger_path = tmp_path / "ledger.jsonl"

    with pytest.raises(ReviewStateError, match="cannot be approved"):
        store.record_decision(
            claim_id="claim-001",
            decision="approved",
            verification=verification(False),
            ledger_path=ledger_path,
            reviewer="tester",
        )

    record, _entry = store.record_decision(
        claim_id="claim-001",
        decision="rejected",
        verification=verification(False),
        ledger_path=ledger_path,
        reviewer="tester",
    )

    assert record.decision == "rejected"


def test_invalid_review_decision_does_not_append_ledger(tmp_path) -> None:
    store = ReviewStore(tmp_path / "state.json")
    ledger_path = tmp_path / "ledger.jsonl"

    with pytest.raises(ReviewStateError, match="approved or rejected"):
        store.record_decision(
            claim_id="claim-001",
            decision="maybe",
            verification=verification(True),
            ledger_path=ledger_path,
            reviewer="tester",
        )

    assert store.get("claim-001") is None
    assert not ledger_path.exists()

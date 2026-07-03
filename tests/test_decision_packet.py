from app.citation import VerificationResult
from app.decision_packet import build_decision_packet
from app.ledger import build_review_entry
from app.models import Citation, ClaimCard
from app.review import ReviewRecord


def test_decision_packet_contains_claim_evidence_review_and_ledger_reference() -> None:
    claim = ClaimCard(
        id="claim-001",
        text="Synthetic claim.",
        citation=Citation(source_path="fixtures/demo.md", quote="Synthetic quote."),
    )
    verification = VerificationResult(
        source_path="fixtures/demo.md",
        quote="Synthetic quote.",
        verified=True,
        start_char=0,
        end_char=16,
        start_line=1,
        end_line=1,
        reason="Quoted passage exists in the source document.",
    )
    ledger_entry = build_review_entry(
        index=1,
        previous_hash="0" * 64,
        claim_id="claim-001",
        decision="approved",
        reviewer="tester",
        timestamp="2026-07-03T00:00:00+00:00",
    )
    review = ReviewRecord(
        claim_id="claim-001",
        decision="approved",
        reviewer="tester",
        decided_at=ledger_entry["timestamp"],
        ledger_index=ledger_entry["index"],
        ledger_hash=ledger_entry["entry_hash"],
    )

    packet = build_decision_packet(
        claim=claim,
        verification=verification,
        review=review,
        ledger_entry=ledger_entry,
    )

    assert packet["packet_schema"] == "provenance-gate.decision-packet.v1"
    assert packet["claim"]["id"] == "claim-001"
    assert packet["evidence"]["quote"] == "Synthetic quote."
    assert packet["verification_result"]["verified"] is True
    assert packet["review_decision"]["decision"] == "approved"
    assert packet["ledger_reference"]["entry_hash"] == ledger_entry["entry_hash"]

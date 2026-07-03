import json

from app.ledger import append_review_action, load_entries, verify_hash_chain


def test_hash_chain_valid_for_appended_reviews(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"

    first = append_review_action(
        ledger_path,
        claim_id="claim-001",
        decision="approved",
        reviewer="tester",
    )
    second = append_review_action(
        ledger_path,
        claim_id="claim-002",
        decision="rejected",
        reviewer="tester",
    )

    result = verify_hash_chain(ledger_path)

    assert result.valid is True
    assert second["previous_hash"] == first["entry_hash"]


def test_hash_chain_detects_tampering(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    append_review_action(
        ledger_path,
        claim_id="claim-001",
        decision="approved",
        reviewer="tester",
    )
    entries = load_entries(ledger_path)
    entries[0]["decision"] = "rejected"
    ledger_path.write_text(json.dumps(entries[0]) + "\n", encoding="utf-8")

    result = verify_hash_chain(ledger_path)

    assert result.valid is False
    assert any("hash does not match" in error for error in result.errors)


def test_hash_chain_invalid_json_fails_safely(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text("{not valid json}\n", encoding="utf-8")

    result = verify_hash_chain(ledger_path)

    assert result.valid is False
    assert any("Invalid JSON" in error for error in result.errors)

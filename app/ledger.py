from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ZERO_HASH = "0" * 64


@dataclass(frozen=True)
class ChainVerification:
    valid: bool
    errors: list[str]


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _hash_entry_payload(entry_without_hash: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(entry_without_hash).encode("utf-8")).hexdigest()


def load_entries(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.exists():
        return []

    entries: list[dict[str, Any]] = []
    for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on ledger line {line_number}: {exc}") from exc
    return entries


def build_review_entry(
    *,
    index: int,
    previous_hash: str,
    claim_id: str,
    decision: str,
    reviewer: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    timestamp = timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "index": index,
        "timestamp": timestamp,
        "action": "review",
        "claim_id": claim_id,
        "decision": decision,
        "reviewer": reviewer,
        "previous_hash": previous_hash,
    }
    return {**payload, "entry_hash": _hash_entry_payload(payload)}


def append_review_action(
    ledger_path: Path,
    *,
    claim_id: str,
    decision: str,
    reviewer: str,
) -> dict[str, Any]:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    entries = load_entries(ledger_path)
    previous_hash = entries[-1]["entry_hash"] if entries else ZERO_HASH
    entry = build_review_entry(
        index=len(entries) + 1,
        previous_hash=previous_hash,
        claim_id=claim_id,
        decision=decision,
        reviewer=reviewer,
    )
    with ledger_path.open("a", encoding="utf-8") as ledger_file:
        ledger_file.write(json.dumps(entry, ensure_ascii=True, sort_keys=True) + "\n")
    return entry


def expected_entry_hash(entry: dict[str, Any]) -> str:
    payload = {key: value for key, value in entry.items() if key != "entry_hash"}
    return _hash_entry_payload(payload)


def verify_hash_chain(ledger_path: Path) -> ChainVerification:
    errors: list[str] = []
    try:
        entries = load_entries(ledger_path)
    except ValueError as exc:
        return ChainVerification(valid=False, errors=[str(exc)])

    previous_hash = ZERO_HASH
    for expected_index, entry in enumerate(entries, start=1):
        if entry.get("index") != expected_index:
            errors.append(f"Entry {expected_index} has index {entry.get('index')}.")
        if entry.get("previous_hash") != previous_hash:
            errors.append(f"Entry {expected_index} does not link to the previous hash.")
        actual_hash = entry.get("entry_hash")
        recalculated_hash = expected_entry_hash(entry)
        if actual_hash != recalculated_hash:
            errors.append(f"Entry {expected_index} hash does not match its payload.")
        previous_hash = actual_hash or ""

    return ChainVerification(valid=not errors, errors=errors)


def find_entry_by_hash(ledger_path: Path, entry_hash: str) -> dict[str, Any] | None:
    for entry in load_entries(ledger_path):
        if entry.get("entry_hash") == entry_hash:
            return entry
    return None

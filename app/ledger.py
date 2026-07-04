from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ZERO_HASH = "0" * 64


@dataclass(frozen=True)
class ChainVerification:
    valid: bool
    errors: list[str]


@dataclass(frozen=True)
class AuditStatus:
    entry_count: int
    valid: bool
    status: str
    latest_record_hash: str | None
    latest_previous_hash: str | None
    expected_previous_hash: str | None
    latest_previous_hash_valid: bool | None
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LedgerTamperError(ValueError):
    pass


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


def write_entries(ledger_path: Path, entries: list[dict[str, Any]]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as ledger_file:
        for entry in entries:
            ledger_file.write(json.dumps(entry, ensure_ascii=True, sort_keys=True) + "\n")


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


def _nonempty_line_count(ledger_path: Path) -> int:
    if not ledger_path.exists():
        return 0
    return sum(1 for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip())


def audit_status(ledger_path: Path) -> AuditStatus:
    try:
        entries = load_entries(ledger_path)
    except ValueError as exc:
        return AuditStatus(
            entry_count=_nonempty_line_count(ledger_path),
            valid=False,
            status="Invalid",
            latest_record_hash=None,
            latest_previous_hash=None,
            expected_previous_hash=None,
            latest_previous_hash_valid=None,
            errors=[str(exc)],
        )

    chain = verify_hash_chain(ledger_path)
    latest = entries[-1] if entries else None
    expected_previous_hash = None
    latest_previous_hash = None
    latest_previous_hash_valid = None
    latest_record_hash = None

    if latest:
        latest_record_hash = latest.get("entry_hash")
        latest_previous_hash = latest.get("previous_hash")
        expected_previous_hash = entries[-2].get("entry_hash") if len(entries) > 1 else ZERO_HASH
        latest_previous_hash_valid = latest_previous_hash == expected_previous_hash

    return AuditStatus(
        entry_count=len(entries),
        valid=chain.valid,
        status="Valid" if chain.valid else "Invalid",
        latest_record_hash=latest_record_hash,
        latest_previous_hash=latest_previous_hash,
        expected_previous_hash=expected_previous_hash,
        latest_previous_hash_valid=latest_previous_hash_valid,
        errors=chain.errors,
    )


def simulate_demo_tamper(ledger_path: Path) -> dict[str, Any]:
    entries = load_entries(ledger_path)
    if not entries:
        raise LedgerTamperError("Review a claim before simulating ledger tampering.")

    latest = dict(entries[-1])
    original_decision = str(latest.get("decision", "unknown"))
    latest["decision"] = (
        original_decision
        if original_decision.startswith("tampered-")
        else f"tampered-{original_decision}"
    )
    latest["tamper_marker"] = "demo-only simulated ledger edit"
    entries[-1] = latest
    write_entries(ledger_path, entries)
    return latest

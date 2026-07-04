from app.main import create_app


def test_audit_status_tracks_valid_tampered_and_reset_states(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("PROVIDER", "demo")
    app = create_app({"DATA_DIR": tmp_path})
    client = app.test_client()

    initial = client.get("/api/audit").get_json()["audit"]
    assert initial["entry_count"] == 0
    assert initial["valid"] is True
    assert initial["latest_record_hash"] is None

    review_response = client.post("/api/review/claim-001", json={"decision": "approved"})
    assert review_response.status_code == 200
    reviewed_audit = review_response.get_json()["audit"]
    assert reviewed_audit["entry_count"] == 1
    assert reviewed_audit["valid"] is True
    assert reviewed_audit["latest_record_hash"]
    assert reviewed_audit["latest_previous_hash_valid"] is True

    tamper_response = client.post("/api/audit/tamper")
    assert tamper_response.status_code == 200
    tampered_audit = tamper_response.get_json()["audit"]
    assert tampered_audit["entry_count"] == 1
    assert tampered_audit["valid"] is False
    assert any("hash does not match" in error for error in tampered_audit["errors"])

    reset_response = client.post("/api/reset", headers={"Accept": "application/json"})
    assert reset_response.status_code == 200
    reset_audit = reset_response.get_json()["audit"]
    assert reset_audit["entry_count"] == 0
    assert reset_audit["valid"] is True
    assert reset_audit["latest_record_hash"] is None


def test_tamper_requires_existing_ledger_entry(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("PROVIDER", "demo")
    app = create_app({"DATA_DIR": tmp_path})
    client = app.test_client()

    response = client.post("/api/audit/tamper")

    assert response.status_code == 409
    payload = response.get_json()
    assert "Review a claim" in payload["error"]
    assert payload["audit"]["valid"] is True


def test_tamper_and_reset_are_restricted_outside_demo_mode(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("PROVIDER", "demo")
    app = create_app({"DATA_DIR": tmp_path})
    client = app.test_client()

    tamper_response = client.post("/api/audit/tamper")
    reset_response = client.post("/api/reset", headers={"Accept": "application/json"})

    assert tamper_response.status_code == 403
    assert reset_response.status_code == 403
    assert "DEMO_MODE=true" in tamper_response.get_json()["error"]
    assert "DEMO_MODE=true" in reset_response.get_json()["error"]

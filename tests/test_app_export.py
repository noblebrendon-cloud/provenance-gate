from app.main import create_app


def test_export_packet_uses_public_relative_source_path(tmp_path) -> None:
    app = create_app({"DATA_DIR": tmp_path})
    client = app.test_client()

    review_response = client.post("/api/review/claim-001", json={"decision": "approved"})
    assert review_response.status_code == 200

    export_response = client.get("/api/export/claim-001")
    assert export_response.status_code == 200

    packet = export_response.get_json()
    assert packet["evidence"]["source_path"] == "fixtures/synthetic_source.md"
    assert packet["claim"]["citation"]["source_path"] == "fixtures/synthetic_source.md"
    assert ":" not in packet["evidence"]["source_path"]
    assert "\\" not in packet["evidence"]["source_path"]
    assert "entry_hash" in packet["ledger_reference"]

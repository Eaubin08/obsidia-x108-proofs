import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "evidence"
    / "pilots"
    / "world_action_calendar_real_provider_pilot_v0.json"
)


def load():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_real_calendar_provider_effect_is_recorded_truthfully():
    data = load()
    assert data["status"] == "REAL_PROVIDER_EFFECT_OBSERVED_AND_CLEANED"
    assert data["provider"] == "GOOGLE_CALENDAR"
    assert data["execution_origin"] == "CHATGPT_GOOGLE_CALENDAR_CONNECTOR"
    assert data["obsidia_executor_invoked"] is False

    steps = {row["step"]: row for row in data["observations"]}
    assert steps["CREATE"]["provider_status"] == "confirmed"
    assert steps["CREATE"]["real_provider_write"] is True
    assert steps["READ_AFTER_CREATE"]["provider_status"] == "confirmed"
    assert steps["DELETE"]["provider_delete_call_succeeded"] is True
    assert steps["READ_AFTER_DELETE"]["provider_status"] == "cancelled"
    assert steps["READ_AFTER_DELETE"]["active_event_left"] is False


def test_calendar_pilot_evidence_is_privacy_minimized():
    data = load()
    event = data["event"]
    assert len(event["provider_event_id_sha256"]) == 64
    assert len(event["title_sha256"]) == 64
    privacy = data["privacy"]
    assert privacy["raw_provider_event_id_persisted"] is False
    assert privacy["authenticated_email_persisted"] is False
    assert privacy["provider_web_url_persisted"] is False


def test_calendar_pilot_does_not_claim_obsidia_executed_the_connector():
    data = load()
    boundary = data["governance_boundary"]
    assert boundary["decision_authority"] == "KX108_ONLY"
    assert boundary["real_provider_effect_proven"] is True
    assert boundary["real_obsidia_connector_execution_proven"] is False
    assert boundary["main_merge"] is False

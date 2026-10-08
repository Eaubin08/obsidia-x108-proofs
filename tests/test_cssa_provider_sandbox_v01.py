"""CSSA V0.1 isolated fake provider flow and fault-injection tests."""
from copy import deepcopy

import pytest

from periphery.cssa_provider_sandbox_v01 import (
    simulate_cssa_sandbox, verify_cssa_sandbox,
)


def msg(mid, subject):
    return {"message_id": mid, "subject": subject,
            "sender": "fixture@invalid.example", "body": "Donnée inventée"}


def test_supporter_full_fake_flow_does_not_write():
    result = simulate_cssa_sandbox(
        [msg("s1", "Question supporter")],
        followups={"s1": "2026-10-20T15:00:00+02:00"},
    )
    assert verify_cssa_sandbox(result)
    report = result["report"]
    assert report["status"] == "HOLD"
    assert [event["surface"] for event in report["events"]] == [
        "MAILBOX_FAKE", "CRM_FAKE", "CALENDAR_FAKE", "EMAIL_FAKE"
    ]
    assert report["external_actions"] == []
    assert report["provider_writes"] is False
    assert report["native_store_writes"] is False
    assert report["kx108_decision"] is None


def test_marketing_and_payment_do_not_produce_downstream_proposals():
    result = simulate_cssa_sandbox([
        msg("m", "Newsletter du club"),
        msg("p", "Confirmation de paiement"),
    ])
    assert verify_cssa_sandbox(result)
    assert [x["surface"] for x in result["report"]["events"]] == [
        "MAILBOX_FAKE", "MAILBOX_FAKE"
    ]


@pytest.mark.parametrize("surface", ["mailbox", "crm", "calendar", "email"])
def test_provider_failure_never_escalates_to_act(surface):
    result = simulate_cssa_sandbox(
        [msg("s", "Question supporter")],
        followups={"s": "2026-10-20T15:00:00+02:00"},
        failure_at=surface,
    )
    assert verify_cssa_sandbox(result)
    assert result["report"]["status"] == "BLOCK"
    assert result["report"]["external_actions"] == []
    assert result["report"]["execution_proven"] is False
    assert result["report"]["kx108_decision"] is None


def test_conflicting_message_ids_cannot_reach_downstream():
    result = simulate_cssa_sandbox([
        msg("same", "Question supporter"),
        msg("same", "Newsletter du club"),
    ])
    assert verify_cssa_sandbox(result)
    assert result["report"]["conflicting_ids"] == ["same"]
    assert result["report"]["events"] == []


def test_idempotent_fake_replay():
    messages = [msg("s", "Question supporter")]
    assert simulate_cssa_sandbox(messages) == simulate_cssa_sandbox(messages)


def test_receipt_tampering_is_detected():
    result = simulate_cssa_sandbox([msg("s", "Question supporter")])
    altered = deepcopy(result)
    altered["report"]["provider_writes"] = True
    assert verify_cssa_sandbox(altered) is False


def test_invalid_failure_point_rejected():
    with pytest.raises(ValueError, match="CSSA_UNKNOWN_FAILURE_POINT"):
        simulate_cssa_sandbox([], failure_at="real_provider")

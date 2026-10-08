"""CSSA V0 cross-component offline regression: synthetic-only evidence."""
from copy import deepcopy

import pytest

from periphery.cssa_cross_component_offline_v0 import (
    build_cssa_cross_component_batch,
    verify_cssa_cross_component_batch,
)


def msg(mid, subject, body="Exemple synthétique"):
    return {"message_id": mid, "subject": subject,
            "body": body, "sender": "source@invalid.example"}


def test_supporter_consistency_across_native_crm_task_and_reply():
    bundle = build_cssa_cross_component_batch([msg("sup", "Question supporter")])
    assert verify_cssa_cross_component_batch(bundle)
    case = bundle["report"]["cases"][0]
    assert case["crm_candidate_id"].startswith("cssa-case-")
    assert case["task_candidate_id"].startswith("cssa-")
    assert case["email_draft_candidate"]["state"] == "DRAFT_NOT_SENT"
    assert case["calendar_candidate"] is None
    assert case["status"] == "HOLD"
    assert case["external_actions"] == []
    assert bundle["report"]["execution_proven"] is False


def test_only_explicit_dated_supporter_request_proposes_calendar():
    bundle = build_cssa_cross_component_batch(
        [msg("sup2", "Demande de renseignement")],
        explicit_followups={"sup2": "2026-10-20T15:30:00+02:00"},
    )
    assert verify_cssa_cross_component_batch(bundle)
    event = bundle["report"]["cases"][0]["calendar_candidate"]
    assert event["start_at"] == "2026-10-20T15:30:00+02:00"
    assert event["state"] == "PROPOSED_NOT_CREATED"


def test_newsletters_payments_tickets_and_subscriptions_are_passive():
    bundle = build_cssa_cross_component_batch([
        msg("n", "Newsletter du club"),
        msg("p", "Confirmation de paiement"),
        msg("t", "Billet commandé"),
        msg("s", "Confirmation abonnement saison"),
    ])
    assert verify_cssa_cross_component_batch(bundle)
    assert len(bundle["report"]["cases"]) == 4
    for case in bundle["report"]["cases"]:
        assert case["crm_candidate_id"] is None
        assert case["task_candidate_id"] is None
        assert case["email_draft_candidate"] is None
        assert case["calendar_candidate"] is None


def test_ambiguous_and_unknown_messages_never_generate_actions():
    bundle = build_cssa_cross_component_batch([
        msg("a", "Question supporter et billet commandé"),
        msg("u", "Bonjour"),
    ])
    assert verify_cssa_cross_component_batch(bundle)
    assert all(case["category"] == "UNKNOWN" for case in bundle["report"]["cases"])
    assert all(case["crm_candidate_id"] is None for case in bundle["report"]["cases"])


def test_duplicate_id_is_deduplicated_and_conflicting_id_is_excluded():
    duplicate = msg("dup", "Question supporter")
    first = msg("collision", "Question supporter")
    second = msg("collision", "Newsletter du club")
    bundle = build_cssa_cross_component_batch([
        duplicate, duplicate, first, second, msg("valid", "Communiqué du club")
    ])
    assert verify_cssa_cross_component_batch(bundle)
    assert bundle["report"]["duplicate_ids"] == ["dup"]
    assert bundle["report"]["conflicting_ids"] == ["collision"]
    assert [case["message_id"] for case in bundle["report"]["cases"]] == ["dup", "valid"]


@pytest.mark.parametrize("followups", [
    {"missing": "2026-10-20T15:30:00+02:00"},
    {"conflict": "2026-10-20T15:30:00+02:00"},
])
def test_bad_date_bindings_fail_closed(followups):
    messages = [msg("conflict", "Question supporter"),
                msg("conflict", "Newsletter du club")]
    with pytest.raises(ValueError):
        build_cssa_cross_component_batch(messages, explicit_followups=followups)


def test_tampered_cross_component_receipt_rejected():
    bundle = build_cssa_cross_component_batch([msg("sup", "Question supporter")])
    altered = deepcopy(bundle)
    altered["report"]["cases"][0]["task_candidate_id"] = "injected"
    assert not verify_cssa_cross_component_batch(altered)


def test_replay_is_stable_and_never_claims_kx108_execution():
    messages = [msg("r", "Question supporter"), msg("p", "Paiement confirmé")]
    a = build_cssa_cross_component_batch(messages)
    b = build_cssa_cross_component_batch(messages)
    assert a == b
    assert a["report"]["kx108_decision"] is None
    assert a["report"]["human_approval"] is None
    assert a["report"]["external_actions"] == []
    assert a["report"]["historical_evidence_replaced"] is False

"""CSSA administrative use cases — entirely synthetic, no provider connections."""
from __future__ import annotations

from periphery.cssa_synthetic_intake_v0 import (
    classify_cssa_message,
    ingest_synthetic_batch,
)

BASE = {"sender": "fixture@invalid.example", "body": "Exemple fictif", "subject": ""}


def mail(mid, subject, body="Exemple fictif"):
    return {**BASE, "message_id": mid, "subject": subject, "body": body}


def assert_boundary(packet):
    assert packet["decision_authority"] == "KX108_ONLY"
    assert packet["kx108_decision"] is None
    assert packet["review_status"] == "HOLD"
    assert packet["human_review_required"] is True
    for key in ("send_email", "crm_external_write", "calendar_external_write",
                "memory_write", "emits_act", "kernel_mutation"):
        assert packet[key] is False
    assert packet["production_integration"] == "NOT_CONNECTED"


def test_payment_confirmation_is_not_a_new_ticket_order():
    p = classify_cssa_message(mail("payment-1", "Confirmation de paiement"))
    assert p["category_candidate"] == "PAYMENT_CONFIRMATION"
    assert_boundary(p)


def test_ticket_order_for_family_member_is_candidate_only():
    p = classify_cssa_message(mail("ticket-parent", "Billet commandé pour mon père"))
    assert p["category_candidate"] == "TICKET_ORDER"
    assert_boundary(p)


def test_season_subscription_is_not_a_ticket_order():
    p = classify_cssa_message(mail("subscription-1", "Confirmation abonnement saison"))
    assert p["category_candidate"] == "SUBSCRIPTION"
    assert_boundary(p)


def test_club_communication_is_not_purchase():
    p = classify_cssa_message(mail("news-1", "Newsletter du club"))
    assert p["category_candidate"] == "CLUB_COMMUNICATION"
    assert_boundary(p)


def test_supporter_request_never_auto_sends():
    p = classify_cssa_message(mail("supporter-1", "Question supporter"))
    assert p["category_candidate"] == "SUPPORTER_REQUEST"
    assert_boundary(p)


def test_ambiguous_payment_and_ticket_holds():
    p = classify_cssa_message(mail("ambiguous-1", "Confirmation de paiement et billet commandé"))
    assert p["category_candidate"] == "UNKNOWN"
    assert p["classification_reason"] == "AMBIGUOUS_MULTIPLE_SIGNALS"
    assert_boundary(p)


def test_unrecognized_mail_holds():
    p = classify_cssa_message(mail("unknown-1", "Re: Bonjour"))
    assert p["category_candidate"] == "UNKNOWN"
    assert_boundary(p)


def test_duplicate_exact_message_is_no_new_candidate():
    m = mail("duplicate-1", "Newsletter du club")
    batch = ingest_synthetic_batch([m, m])
    assert len(batch["candidates"]) == 1
    assert batch["duplicates"] == ["duplicate-1"]
    assert batch["conflicts"] == []
    assert batch["external_actions"] == []
    assert batch["batch_status"] == "HOLD"


def test_conflicting_same_message_id_is_never_silently_overwritten():
    batch = ingest_synthetic_batch([
        mail("same-id", "Question supporter"),
        mail("same-id", "Confirmation de paiement"),
    ])
    assert len(batch["candidates"]) == 1
    assert batch["conflicts"] == ["same-id"]
    assert batch["candidates"][0]["category_candidate"] == "SUPPORTER_REQUEST"
    assert batch["external_actions"] == []


def test_intake_keeps_all_actions_offline():
    messages = [
        mail("purchase", "Billet commandé"),
        mail("comms", "Communiqué du club"),
        mail("supporter", "Demande de renseignement"),
    ]
    batch = ingest_synthetic_batch(messages)
    assert len(batch["candidates"]) == 3
    assert batch["decision_authority"] == "KX108_ONLY"
    assert batch["historical_evidence_replaced"] is False
    for packet in batch["candidates"]:
        assert_boundary(packet)

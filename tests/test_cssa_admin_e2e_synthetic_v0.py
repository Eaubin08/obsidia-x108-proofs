"""CSSA offline administrative E2E regression — never authorizes ACT."""
from copy import deepcopy

from periphery.cssa_admin_e2e_synthetic_v0 import (
    build_cssa_admin_case,
    build_cssa_admin_batch,
    verify_cssa_admin_case,
)


def mail(mid, subject):
    return {"message_id": mid, "subject": subject,
            "sender": "fixture@invalid.example", "body": "Synthétique"}


def test_supporter_proposes_task_but_does_not_write_crm_or_calendar():
    bundle = build_cssa_admin_case(mail("s1", "Question supporter"))
    assert verify_cssa_admin_case(bundle)
    case = bundle["case"]
    assert case["proposal"]["kind"] == "PROPOSE_SUPPORTER_FOLLOWUP"
    assert case["proposal"]["crm"][0]["state"] == "PROPOSED_NOT_CREATED"
    assert case["proposal"]["calendar"] == []
    assert case["governance"]["status"] == "HOLD"
    assert case["governance"]["kx108_decision"] is None
    assert bundle["receipt"]["execution_proven"] is False


def test_payment_is_not_duplicated_as_new_purchase():
    case = build_cssa_admin_case(mail("pay", "Confirmation de paiement"))["case"]
    assert case["proposal"]["treatment"] == "NO_NEW_PURCHASE"
    assert case["proposal"]["crm"] == []


def test_ticket_order_requires_existing_order_check():
    case = build_cssa_admin_case(mail("t1", "Billet commandé"))["case"]
    assert case["proposal"]["treatment"] == "CHECK_EXISTING_ORDER"


def test_subscription_requires_existing_subscription_check():
    case = build_cssa_admin_case(mail("ab1", "Confirmation abonnement saison"))["case"]
    assert case["proposal"]["treatment"] == "CHECK_EXISTING_SUBSCRIPTION"


def test_newsletter_does_not_create_task():
    case = build_cssa_admin_case(mail("news", "Newsletter du club"))["case"]
    assert case["proposal"]["treatment"] == "NO_TASK_BY_DEFAULT"
    assert case["proposal"]["crm"] == []


def test_unknown_and_ambiguous_fail_closed():
    for subject in ("Salut", "Confirmation de paiement et billet commandé"):
        bundle = build_cssa_admin_case(mail("x", subject))
        assert bundle["case"]["proposal"]["kind"] == "ESCALATE_UNCLASSIFIED"
        assert bundle["case"]["governance"]["status"] == "HOLD"
        assert verify_cssa_admin_case(bundle)


def test_duplicate_and_conflict_dont_create_external_actions():
    one = mail("same", "Question supporter")
    conflicting = mail("same", "Confirmation de paiement")
    batch = build_cssa_admin_batch([one, one, conflicting, mail("valid", "Newsletter du club")])
    assert batch["duplicate_ids"] == ["same"]
    assert batch["conflicting_ids"] == ["same"]
    assert len(batch["bundles"]) == 1
    assert batch["external_actions"] == []
    assert batch["status"] == "HOLD"


def test_receipt_detects_modified_case_and_modified_hash():
    bundle = build_cssa_admin_case(mail("s2", "Question supporter"))
    assert verify_cssa_admin_case(bundle)
    altered = deepcopy(bundle)
    altered["case"]["proposal"]["kind"] = "SEND_EMAIL"
    assert not verify_cssa_admin_case(altered)
    altered = deepcopy(bundle)
    altered["receipt"]["case_sha256"] = "0" * 64
    assert not verify_cssa_admin_case(altered)


def test_no_kx108_decision_or_human_approval_fabricated():
    batch = build_cssa_admin_batch([mail("s3", "Demande de renseignement"),
                                    mail("p3", "Paiement confirmé")])
    assert len(batch["bundles"]) == 2
    for bundle in batch["bundles"]:
        assert verify_cssa_admin_case(bundle)
        assert bundle["case"]["governance"]["kx108_decision"] is None
        assert bundle["case"]["governance"]["human_approval"] is None
        assert bundle["receipt"]["external_actions"] == []

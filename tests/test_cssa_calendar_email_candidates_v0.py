"""CSSA calendar and email candidates: pure data and fail-closed."""
import pytest

from periphery.cssa_calendar_email_candidates_v0 import prepare_cssa_followup_candidates


def message(mid: str, subject: str) -> dict[str, str]:
    return {"message_id": mid, "subject": subject,
            "sender": "supporter@invalid.example", "body": "Exemple fictif"}


def test_supporter_creates_draft_but_no_email_send():
    packet = prepare_cssa_followup_candidates(message("sup-1", "Question supporter"))
    assert packet["email_draft"]["state"] == "DRAFT_NOT_SENT"
    assert packet["email_draft"]["template_only"] is True
    assert packet["email_draft"]["human_review_required"] is True
    assert packet["calendar_event"] is None
    assert packet["email_send"] is False
    assert packet["calendar_external_write"] is False
    assert packet["external_actions"] == []
    assert packet["status"] == "HOLD"
    assert packet["kx108_decision"] is None
    assert packet["human_approval"] is None


def test_explicit_timezone_aware_followup_date_only():
    requested = "2026-10-20T15:30:00+02:00"
    packet = prepare_cssa_followup_candidates(
        message("sup-2", "Demande de renseignement"),
        requested_followup_at=requested,
    )
    assert packet["calendar_event"]["start_at"] == requested
    assert packet["calendar_event"]["state"] == "PROPOSED_NOT_CREATED"
    assert packet["calendar_external_write"] is False
    assert packet["email_send"] is False


@pytest.mark.parametrize("date", ["2026-10-20T15:30", "demain à 15h", "",
                                    "2026-99-01T14:00+02:00", 123])
def test_unsupported_followup_dates_are_rejected(date):
    with pytest.raises(ValueError):
        prepare_cssa_followup_candidates(
            message("sup-3", "Question supporter"), requested_followup_at=date)


@pytest.mark.parametrize("subject", [
    "Confirmation de paiement",
    "Billet commandé",
    "Confirmation abonnement saison",
    "Newsletter du club",
    "Communiqué du club",
    "Question supporter et confirmation de paiement",
    "Bonjour",
])
def test_other_categories_never_create_reply_or_calendar(subject):
    packet = prepare_cssa_followup_candidates(
        message("other", subject), requested_followup_at="2026-10-20T15:30:00+02:00")
    assert packet["email_draft"] is None
    assert packet["calendar_event"] is None
    assert packet["status"] == "HOLD"
    assert packet["external_actions"] == []


def test_same_source_same_candidates():
    m = message("same", "Question supporter")
    one = prepare_cssa_followup_candidates(m, requested_followup_at="2026-10-20T15:30:00+02:00")
    two = prepare_cssa_followup_candidates(m, requested_followup_at="2026-10-20T15:30:00+02:00")
    assert one == two
    assert one["decision_authority"] == "KX108_ONLY"

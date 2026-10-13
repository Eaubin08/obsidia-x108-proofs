"""CSSA native CRM candidate tests: proposals are never native applies."""
from periphery.cssa_native_crm_candidate_v0 import prepare_cssa_supporter_crm


def message(mid, subject):
    return {"message_id": mid, "subject": subject,
            "body": "Exemple fictif", "sender": "fixture@invalid.example"}


def test_supporter_case_linked_to_proposed_task_only():
    packet = prepare_cssa_supporter_crm(message("s1", "Question supporter"))
    crm, task = packet["crm_request"], packet["task_request"]
    assert packet["status"] == "HOLD"
    assert packet["crm_mutation"].domain_id == "native_crm"
    assert packet["crm_mutation"].operation == "CREATE_RECORD"
    assert packet["crm_mutation"].payload["record_type"] == "CASE"
    assert packet["crm_mutation"].payload["fields"]["proposed_task_id"] == task["connector_args"]["entity_id"]
    assert packet["crm_mutation"].payload["fields"]["proposed_task_state"] == "NOT_CREATED"
    assert packet["relation_status"] == "CANDIDATE_ONLY_NO_CANONICAL_LINK"
    for item in (crm, task):
        assert item["decision_authority"] == "KX108_ONLY"
        assert item["allowed_to_act"] is False
        assert item["allowed_to_decide"] is False
        assert item["emits_act"] is False
    assert packet["crm_store_write"] is False
    assert packet["calendar_write"] is False
    assert packet["email_send"] is False
    assert packet["external_actions"] == []


def test_repeated_same_message_is_idempotent_candidate():
    one = prepare_cssa_supporter_crm(message("same", "Demande de renseignement"))
    two = prepare_cssa_supporter_crm(message("same", "Demande de renseignement"))
    assert one["crm_mutation"].mutation_hash == two["crm_mutation"].mutation_hash
    assert one["crm_request"]["idempotency_key"] == two["crm_request"]["idempotency_key"]
    assert one["task_request"]["idempotency_key"] == two["task_request"]["idempotency_key"]


def test_non_supporter_messages_do_not_propose_crm_case():
    for subject in ("Confirmation de paiement", "Newsletter du club",
                    "Billet commandé", "Confirmation abonnement saison"):
        packet = prepare_cssa_supporter_crm(message("no-case", subject))
        assert packet["status"] == "HOLD"
        assert packet["crm_mutation"] is None
        assert packet["crm_request"] is None
        assert packet["task_request"] is None
        assert packet["external_actions"] == []


def test_ambiguous_message_blocks_crm_and_task():
    packet = prepare_cssa_supporter_crm(
        message("ambiguous", "Question supporter et confirmation de paiement"))
    assert packet["crm_mutation"] is None
    assert packet["task_request"] is None
    assert packet["reason"] == "NO_SUPPORTER_CASE_OR_AMBIGUOUS"


def test_conflicting_content_same_message_id_changes_candidate_identity():
    first = prepare_cssa_supporter_crm(message("same", "Question supporter"))
    second = prepare_cssa_supporter_crm(message("same", "Demande de renseignement"))
    assert first["crm_mutation"].entity_id != second["crm_mutation"].entity_id
    # Cross-message ID conflicts require batch-level HOLD before any promotion.
    assert first["status"] == second["status"] == "HOLD"
    assert first["external_actions"] == second["external_actions"] == []


def test_no_decision_or_approval_is_invented():
    packet = prepare_cssa_supporter_crm(message("unapproved", "Question supporter"))
    assert packet["kx108_decision"] is None
    assert packet["human_approval"] is None
    assert packet["reason"].startswith("NO_KX108_DECISION")

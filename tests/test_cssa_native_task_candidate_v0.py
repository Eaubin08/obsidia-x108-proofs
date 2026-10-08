"""CSSA-only native TASKS proposal: no apply, no store, no email or calendar."""
from periphery.cssa_native_task_candidate_v0 import prepare_cssa_supporter_task


def msg(message_id: str, subject: str) -> dict[str, str]:
    return {
        "message_id": message_id,
        "subject": subject,
        "body": "Exemple synthétique",
        "sender": "fixture@invalid.example",
    }


def test_supporter_request_builds_native_request_without_authority():
    result = prepare_cssa_supporter_task(msg("s-001", "Question supporter"))
    mutation = result["mutation"]
    request = result["world_action_request"]
    assert result["status"] == "HOLD"
    assert mutation.domain_id == "native_tasks"
    assert mutation.operation == "CREATE_TASK"
    assert mutation.payload["tags"] == ["CSSA", "SYNTHETIC"]
    assert request["decision_authority"] == "KX108_ONLY"
    assert request["allowed_to_decide"] is False
    assert request["allowed_to_act"] is False
    assert request["emits_act"] is False
    assert result["kx108_decision"] is None
    assert result["human_approval"] is None
    assert result["native_store_write"] is False
    assert result["external_actions"] == []


def test_same_supporter_message_is_deterministic():
    first = prepare_cssa_supporter_task(msg("s-001", "Question supporter"))
    second = prepare_cssa_supporter_task(msg("s-001", "Question supporter"))
    assert first["mutation"].mutation_hash == second["mutation"].mutation_hash
    assert first["world_action_request"]["idempotency_key"] == second["world_action_request"]["idempotency_key"]


def test_newsletter_and_payment_propose_no_task():
    for subject in ("Newsletter du club", "Confirmation de paiement"):
        result = prepare_cssa_supporter_task(msg("m-001", subject))
        assert result["status"] == "HOLD"
        assert result["mutation"] is None
        assert result["world_action_request"] is None
        assert result["external_actions"] == []


def test_ambiguous_message_never_prepares_write():
    result = prepare_cssa_supporter_task(
        msg("m-002", "Question supporter et confirmation de paiement"))
    assert result["mutation"] is None
    assert result["world_action_request"] is None
    assert result["status"] == "HOLD"

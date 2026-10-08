"""C2.6 negative sovereign authenticity evidence tests."""
from periphery.enterprise_sovereign_proof_boundary_audit_v0 import inspect_sovereign_claims_v0
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket


def ticket(gate="ALLOW"):
    return issue_sovereign_ticket(
        action_id="action-1", os3_ticket_id="fixture-os3", x108_gate=gate,
        scope="calendar:write", autonomy_level=3,
        world_call_class="REVERSIBLE_WORLD_CALL"
    )


def inspect(envelope, t):
    return inspect_sovereign_claims_v0(
        decision_envelope=envelope, ticket=t,
        expected_action_id="action-1", expected_scope="calendar:write"
    )


def test_structural_allow_is_never_sovereign_authority():
    assert inspect({"x108_gate": "ALLOW"}, ticket()) == (
        "BLOCK:C26_INDEPENDENT_SOVEREIGN_ATTESTATION_UNAVAILABLE"
    )


def test_hold_cannot_promote():
    assert inspect({"x108_gate": "HOLD"}, ticket()) == "BLOCK:C26_NOT_KX108_ALLOW"


def test_ticket_hold_denied_even_if_envelope_says_allow():
    assert inspect({"x108_gate": "ALLOW"}, ticket("HOLD")) == "BLOCK:C26_TICKET_NOT_KX108_ALLOW"


def test_action_scope_and_missing_proof_refused():
    assert inspect({"x108_gate": "ALLOW"}, None) == "BLOCK:C26_TICKET_MISSING"
    wrong = ticket()
    wrong.action_id = "different"
    assert inspect({"x108_gate": "ALLOW"}, wrong) == "BLOCK:C26_TICKET_ACTION_OR_SCOPE_MISMATCH"
    assert inspect({"x108_gate": "ALLOW"}, ticket()) != "ALLOW"

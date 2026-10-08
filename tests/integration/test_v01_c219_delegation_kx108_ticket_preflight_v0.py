"""C2.19 never elevates evidence to authority."""
from periphery.enterprise_delegation_kx108_ticket_preflight_v0 import inspect_c219_preflight_v0

def invoke(**changes):
    payload = dict(request=None, approval=None, record=None, ticket=None,
        binding_fixture=None, binding_key=None, binding_issuer=None,
        delegation_inputs=None, now=None)
    payload.update(changes)
    return inspect_c219_preflight_v0(**payload)

def test_missing_delegation_blocks_without_egress():
    out=invoke()
    assert out["status"]=="BLOCK"
    assert out["reason"]=="C219_DELEGATION_INPUTS_MISSING"
    assert out["egress_allowed"] is False
    assert out["execution_authority"] is False

def test_untrusted_partial_delegation_blocks():
    out=invoke(delegation_inputs={})
    assert out["status"]=="BLOCK"
    assert out["reason"].startswith("C219_DELEGATION_REJECTED:")
    assert out["egress_allowed"] is False

def test_forged_delegate_input_cannot_turn_into_permission():
    out=invoke(delegation_inputs={"organization":"org-a","authority_verified":True})
    assert out["status"]=="BLOCK"
    assert out["execution_authority"] is False

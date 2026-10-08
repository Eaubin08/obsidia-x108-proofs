"""C2.8 negative tests for approval / canonical record / local ticket boundary."""
from periphery.enterprise_approval_ticket_boundary_v0 import inspect_approval_ticket_chain_v0
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket


def test_missing_request_blocks():
    result = inspect_approval_ticket_chain_v0(
        request={}, approval={}, record={}, ticket=None)
    assert result["status"] == "BLOCK"
    assert result["reason"].startswith("C28_REQUEST_INVALID")
    assert result["egress_allowed"] is False


def test_producer_based_canonical_record_and_local_ticket_still_fail_closed(tmp_path):
    import importlib.util
    from pathlib import Path
    from scripts import obsidia_kx108_decision_store as store

    path = Path(__file__).with_name("test_world_action_pre_execution_v0.py")
    spec = importlib.util.spec_from_file_location("fixture_c28", path)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)

    request = fixture.build_request()
    approval = fixture.build_approval(request)
    result = fixture.run(tmp_path, request)
    assert result.x108_gate == "ALLOW"
    record = store.load_kx108_decision_record(
        result.decision_record_id, tmp_path / "decisions"
    )
    ticket = issue_sovereign_ticket(
        action_id=request["request_id"], os3_ticket_id="fixture-os3",
        x108_gate="ALLOW", scope=request["required_scope"],
        autonomy_level=3, world_call_class="REVERSIBLE_WORLD_CALL"
    )
    checked = inspect_approval_ticket_chain_v0(
        request=request, approval=approval, record=record, ticket=ticket
    )
    assert checked["reason"] == "C28_TICKET_NOT_AUTHENTICATED_TO_KX108_RECORD"
    assert checked["egress_allowed"] is False

    ticket.action_id = "other-action"
    assert inspect_approval_ticket_chain_v0(
        request=request, approval=approval, record=record, ticket=ticket
    )["reason"] == "C28_TICKET_ACTION_OR_SCOPE_MISMATCH"

    ticket.action_id = request["request_id"]
    ticket.x108_gate = "HOLD"
    assert inspect_approval_ticket_chain_v0(
        request=request, approval=approval, record=record, ticket=ticket
    )["reason"] == "C28_TICKET_GATE_MISMATCH"

    altered = dict(approval)
    altered["approved_by"] = "UNKNOWN"
    assert inspect_approval_ticket_chain_v0(
        request=request, approval=altered, record=record, ticket=ticket
    )["reason"].startswith("C28_APPROVAL_INVALID")

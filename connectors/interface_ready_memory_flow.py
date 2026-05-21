"""
Demo connector: Interface state packet + view contracts + workbench API validation.
"""
from periphery.interface.interface_state_packet import build_interface_state_packet
from periphery.interface.interface_view_contracts import (
    BRODY_VIEW_CONTRACT, MEMORY_VIEW_CONTRACT,
    GRAPHITI_VIEW_CONTRACT, CONTEXT_VIEW_CONTRACT,
)
from periphery.interface.workbench_api_contract import evaluate_workbench_method
from periphery.graphiti.graphiti_readonly_bridge import query_graphiti_readonly, assert_graphiti_no_write


def run_interface_ready_memory_flow():
    for contract in [BRODY_VIEW_CONTRACT, MEMORY_VIEW_CONTRACT,
                     GRAPHITI_VIEW_CONTRACT, CONTEXT_VIEW_CONTRACT]:
        contract.validate()

    packet = build_interface_state_packet("demo_session_isp")
    assert packet.readonly is True
    assert packet.can_emit_act is False

    for method in ["inspect", "query", "context_read", "audit_read"]:
        r = evaluate_workbench_method(method)
        assert r.allowed is True
        assert r.dry_run_only is True

    for method in ["write_memory", "deploy_contract", "auto_execute"]:
        r = evaluate_workbench_method(method)
        assert r.allowed is False

    gq = query_graphiti_readonly("demo_gq_01", "MATCH (n:Memory) RETURN n LIMIT 5")
    assert_graphiti_no_write(gq)
    assert gq.readonly is True
    assert gq.neo4j_write is False

    return {
        "packet": packet.to_dict(),
        "contracts_valid": True,
        "graphiti_no_write": True,
        "flow": "INTERFACE_READY_MEMORY_FLOW_OK",
    }


if __name__ == "__main__":
    import json
    result = run_interface_ready_memory_flow()
    print(json.dumps(result, indent=2))

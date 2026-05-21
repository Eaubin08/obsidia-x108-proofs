import pytest
from periphery.interface.interface_state_packet import build_interface_state_packet
from periphery.interface.workbench_api_contract import evaluate_workbench_method
from periphery.interface.interface_view_contracts import (
    BRODY_VIEW_CONTRACT, MEMORY_VIEW_CONTRACT,
    GRAPHITI_VIEW_CONTRACT, CONTEXT_VIEW_CONTRACT,
)


def test_packet_readonly():
    p = build_interface_state_packet("test_session_1")
    assert p.readonly is True


def test_packet_no_act():
    p = build_interface_state_packet("test_session_2")
    assert p.can_emit_act is False


def test_allowed_workbench_method():
    r = evaluate_workbench_method("inspect")
    assert r.allowed is True
    assert r.dry_run_only is True


def test_forbidden_workbench_method():
    r = evaluate_workbench_method("write_memory")
    assert r.allowed is False
    assert "WORKBENCH_METHOD_FORBIDDEN" in r.reason


def test_view_contracts_readonly():
    for contract in [BRODY_VIEW_CONTRACT, MEMORY_VIEW_CONTRACT,
                     GRAPHITI_VIEW_CONTRACT, CONTEXT_VIEW_CONTRACT]:
        contract.validate()

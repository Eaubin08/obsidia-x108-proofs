"""
V5A Integration Test: Verify all internal demo flows exist.
"""
import os
import pytest

FLOWS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "demos", "local_flows"
)

EXPECTED_FLOWS = [
    "v3_v4_full_stack_flow.py",
    "v4_controlled_runtime_flow.py",
    "bank_full_stack_flow.py",
    "trading_full_stack_flow.py",
    "gps_full_stack_flow.py",
    "memory_brody_graphiti_flow.py",
    "blockchain_security_dryrun_flow.py",
    "world_call_gateway_flow.py",
]


@pytest.mark.parametrize("flow_file", EXPECTED_FLOWS)
def test_flow_file_exists(flow_file):
    path = os.path.join(FLOWS_DIR, flow_file)
    assert os.path.isfile(path), f"Missing flow: {flow_file}"


def test_all_flows_present():
    for f in EXPECTED_FLOWS:
        path = os.path.join(FLOWS_DIR, f)
        assert os.path.isfile(path), f"Missing flow: {f}"

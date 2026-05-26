"""
V5A Integration Test: Verify internal demo flows run in dry-run mode.
"""
import importlib
import pytest

FLOW_NAMES = [
    "demos.local_flows.v3_v4_full_stack_flow",
    "demos.local_flows.v4_controlled_runtime_flow",
    "demos.local_flows.bank_full_stack_flow",
    "demos.local_flows.trading_full_stack_flow",
    "demos.local_flows.gps_full_stack_flow",
    "demos.local_flows.memory_brody_graphiti_flow",
    "demos.local_flows.blockchain_security_dryrun_flow",
    "demos.local_flows.world_call_gateway_flow",
]


@pytest.mark.parametrize("flow_module", FLOW_NAMES)
def test_flow_runs_dryrun(flow_module):
    """Each flow module must have a run() function that returns a dict with dry_run checks."""
    mod = importlib.import_module(flow_module)
    result = mod.run()

    assert isinstance(result, dict), f"{flow_module}: run() must return dict"

    # Every flow result must contain at minimum:
    assert "action_id" in result, f"{flow_module}: missing action_id"
    assert "timestamp" in result, f"{flow_module}: missing timestamp"

    # Check for dry-run indicators if present
    if "dry_run_only" in result:
        assert result["dry_run_only"] is True, f"{flow_module}: dry_run_only must be True"

    if "egress_allowed" in result:
        assert result["egress_allowed"] is False, f"{flow_module}: egress_allowed must be False"

    # No flow should have real_action_taken = True
    if "real_action_taken" in result:
        assert result["real_action_taken"] is False, f"{flow_module}: real_action_taken must be False"

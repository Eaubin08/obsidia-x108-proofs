"""
V5A Integration Test: Internal demo flows never emit real ACT.
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

FORBIDDEN_KEYS = [
    "real_action_taken",
    "real_transaction",
    "real_deploy",
    "real_mint",
    "wallet_connected",
    "private_key_accessed",
    "secret_exposed",
    "neo4j_write",
    "graphiti_write",
    "memory_write_allowed",
    "auto_promote",
    "tokenization_allowed",
    "deploy_allowed",
    "signing_allowed",
    "bridge_allowed",
]


@pytest.mark.parametrize("flow_module", FLOW_NAMES)
def test_flow_no_real_act(flow_module):
    """No flow result should contain any key indicating a forbidden action."""
    mod = importlib.import_module(flow_module)
    result = mod.run()

    for key in FORBIDDEN_KEYS:
        if key in result:
            value = result[key]
            assert value is not True, (
                f"{flow_module}: FORBIDDEN key '{key}' is True — "
                f"indicates a real action, write, or authority leak"
            )

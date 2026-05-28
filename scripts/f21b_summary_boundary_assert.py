import json
from pathlib import Path

for name in [
    "docs/runtime/F21B_RUNTIME_FREEZE_DASHBOARD_SUMMARY_8000.json",
    "docs/runtime/F21B_RUNTIME_FREEZE_DASHBOARD_SUMMARY_8012.json",
]:
    p = json.loads(Path(name).read_text(encoding="utf-8-sig"))

    assert p["status"] == "F2_F20_RUNTIME_FREEZE_DASHBOARD_READY"
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["advisory_only"] is True
    assert p["context_signal_only"] is True
    assert p["allowed_to_decide"] is False
    assert p["allowed_to_act"] is False
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["neo4j_write"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False
    assert p["real_action"] is False
    assert p["execution_allowed"] is False

    assert p["boundary"]["graphiti_write"] is False
    assert p["boundary"]["neo4j_write"] is False
    assert p["boundary"]["execution_allowed"] is False

    print("SUMMARY_BOUNDARY_OK", name)

print("F21B_SUMMARY_TOP_LEVEL_BOUNDARY_ASSERT_PASS")

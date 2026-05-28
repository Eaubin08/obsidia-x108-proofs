import json
import urllib.request


def _get_json(url: str):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def test_runtime_freeze_dashboard_summary_route_live():
    p = _get_json("http://127.0.0.1:8000/api/runtime/freeze-dashboard/summary")

    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["emits_act"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False

    assert p["status"] == "F2_F20_RUNTIME_FREEZE_DASHBOARD_READY"
    assert p["phase_count"] == 19
    assert p["covered_phase_count"] >= 18
    assert p["late_phase_gate"]["pass"] is True
    assert p["late_phase_gate"]["required"] == ["F16", "F17", "F18", "F19", "F20"]


def test_runtime_freeze_dashboard_route_live_strict_tags():
    p = _get_json("http://127.0.0.1:8000/api/runtime/freeze-dashboard")
    d = p["runtime_freeze_dashboard"]
    phases = {row["phase"]: row for row in d["phases"]}

    assert d["status"] == "F2_F20_RUNTIME_FREEZE_DASHBOARD_READY"
    assert d["decision_authority"] == "KX108_ONLY"
    assert d["readonly"] is True
    assert d["emits_act"] is False
    assert d["memory_write"] is False
    assert d["kernel_mutation"] is False
    assert d["x108_mutation"] is False

    assert "BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528" not in phases["F2"]["tags"]
    assert "BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528" in phases["F20"]["tags"]

    for phase in ["F16", "F17", "F18", "F19", "F20"]:
        assert phases[phase]["status"] == "FREEZE_EVIDENCE_PRESENT"
        assert phases[phase]["report_count"] > 0
        assert phases[phase]["tag_count"] > 0


def test_brody_payload_has_all_f21_required_packets_live():
    data = json.dumps({
        "message": "F21 final test: verify all top-level packets.",
        "language": "fr",
        "session_id": "f21_final_required_packets_test",
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/brody/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        p = json.loads(r.read().decode("utf-8"))

    required = [
        "true_voice_snapshot",
        "true_response_structure_snapshot",
        "adaptive_response_policy",
        "sigma_packet",
        "anti_mismatch_packet",
        "thermodynamics_packet",
        "thermo_unified_packet",
        "gencoin_shadow_packet",
        "gencoin_cognitive_ledger_packet",
        "tree_signal_packet",
        "memory_promotion_guard_packet",
        "operator_view_packet",
        "translation_trace",
        "ir_candidate",
        "contracts",
        "permission_matrix",
        "machination_packet",
        "support_summary",
        "boundary_contract",
        "kernel_contract",
    ]

    missing = [k for k in required if k not in p or p[k] in (None, {}, [])]
    assert missing == []

    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["emits_act"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False
    assert p["adaptive_response_policy"]["status"] == "ADAPTIVE_RESPONSE_POLICY_READY"

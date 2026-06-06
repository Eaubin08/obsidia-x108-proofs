from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_p56c_d_all_domains_core_rigor_audit_passes():
    report = ROOT / "docs" / "core_import" / "P56C_D_ALL_DOMAINS_CORE_RIGOR_AUDIT.json"
    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["status"] == "PASS"

    domains = {r["domain"]: r for r in data["results"]}
    assert set(domains) == {"trading", "bank", "ecom", "gps_defense_aviation"}

    for domain, result in domains.items():
        assert result["status"] == "PASS"
        assert result["missing"] == []

        checks = result["checks"]
        assert checks["state_class_exists"] is True
        assert checks["aggregate_function_exists"] is True
        assert checks["agent_builder_file_exists"] is True
        assert checks["agent_builder_function_exists"] is True
        assert checks["protocol_function_exists"] is True
        assert checks["protocol_uses_state"] is True
        assert checks["protocol_uses_aggregate"] is True
        assert checks["protocol_uses_agent_builder"] is True
        assert checks["protocol_uses_meta_agents"] is True
        assert checks["protocol_returns_guard_decide"] is True
        assert checks["protocol_mentions_canonical_envelope"] is True
        assert checks["runner_routes_domain"] is True
        assert checks["runner_constructs_state"] is True


def test_p56c_d_no_domain_protocol_direct_act_or_write():
    report = ROOT / "docs" / "core_import" / "P56C_D_ALL_DOMAINS_CORE_RIGOR_AUDIT.json"
    data = json.loads(report.read_text(encoding="utf-8"))

    for result in data["results"]:
        risk = result["risk_scan"]
        assert risk["protocol_direct_act"] is False
        assert risk["protocol_direct_write"] is False

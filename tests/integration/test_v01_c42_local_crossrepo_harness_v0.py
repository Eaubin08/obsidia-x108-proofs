"""C4.2 runner contract tests: fail-closed without external clones or network."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from periphery.enterprise_sector_claims_v0 import load_c4_evidence_registry_v0

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/v01_c42_local_crossrepo_probe_v0.py"
C4 = ROOT / "docs/runtime/V01_ENTERPRISE_C4_SECTOR_EVIDENCE_PROFILES_V0.json"
C41 = ROOT / "docs/runtime/V01_ENTERPRISE_C41_CROSSREPO_CONTRACT_FREEZE_V0.json"
PARITY = ROOT / "docs/runtime/V01_GLOBAL_CI_FAILURE_PARITY_20261008.json"


def runner():
    spec = importlib.util.spec_from_file_location("v01_c42_runner", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def contract_data():
    return (
        load_c4_evidence_registry_v0(C4),
        json.loads(C41.read_text(encoding="utf8")),
    )


def evidence_data():
    return {
        "gps": {
            "domain": "gps_defense_aviation",
            "observation_source_proof_level": "RECORDED_RF_ATTACK",
            "observation_input_hash": "fake-digest-documentary-only",
            "claim_status": "SOURCE_LEVEL_CONFLICT_REVIEW_REQUIRED",
            "attack_causality_proven": False,
            "normalization": ["HOLD", "X108_GATE_CANONICAL"],
            "conflicted_authority": [
                "HOLD", "CONTRADICTORY_KERNEL_GATE_FIELDS"
            ],
            "allowed_to_act": False,
        },
        "trading": {
            "domain": "trading", "mode": "PAPER", "proof_policy": "REQUIRED",
            "authority": "HOLD", "fake_broker_submit_count": 0,
            "external_effect": False, "kernel_http_mocked": True,
            "conflict_no_verdict": True, "transport_source": "KX108_REAL",
            "proof_outcome": "PROVEN",
        },
        "cssa": {
            "schema": "CSSA_REAL_READONLY_PILOT_PREFLIGHT_V0",
            "status": "PREPARATION_ONLY_BLOCKED_REAL_SOURCE",
            "connected_club_mailbox": False,
            "connected_club_internal_documents": False,
            "operational_source_authorized": False,
            "pilot_started": False,
            "real_native_promotions": 0,
            "external_mutation_allowed": False,
        },
    }


def test_c42_valid_structural_handoffs_remain_non_sovereign(contract_data):
    data = evidence_data()
    c4, c41 = contract_data
    result = runner().verify_handoffs(**data, registry=c4, c41=c41)
    assert result["status"] == runner().SUCCESS
    assert result["actual_remote_kernel_tested"] is False
    assert result["actual_broker_used"] is False
    assert result["actual_club_mailbox_used"] is False
    assert result["multi_tenant_runtime_permission_proven"] is False
    assert result["allowed_to_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"


@pytest.mark.parametrize("field,value,code", [
    ("claim_status", "ATTACK_PROVEN", "C42_GPS_CONTRACT"),
    ("attack_causality_proven", True, "C42_GPS_CONTRACT"),
    ("allowed_to_act", True, "C42_GPS_CONTRACT"),
    ("normalization", ["ACT", "X108_GATE_CANONICAL"], "C42_GPS_CONTRACT"),
    ("conflicted_authority", ["ACT", "LEGACY"], "C42_GPS_CONTRACT"),
])
def test_c42_gps_evidence_or_authority_promotion_fails(contract_data, field, value, code):
    d = evidence_data()
    d["gps"][field] = value
    with pytest.raises(ValueError, match=code):
        runner().verify_handoffs(**d, registry=contract_data[0],
                                 c41=contract_data[1])


@pytest.mark.parametrize("field,value", [
    ("mode", "LIVE"),
    ("proof_policy", "BEST_EFFORT"),
    ("authority", "ACT"),
    ("fake_broker_submit_count", 1),
    ("external_effect", True),
    ("kernel_http_mocked", False),
    ("conflict_no_verdict", False),
    ("proof_outcome", "EXECUTION_SUCCEEDED_PROOF_INCOMPLETE"),
])
def test_c42_trading_exec_proof_escalation_fails(contract_data, field, value):
    d = evidence_data()
    d["trading"][field] = value
    with pytest.raises(ValueError, match="C42_TRADING_PROOF"):
        runner().verify_handoffs(**d, registry=contract_data[0],
                                 c41=contract_data[1])


@pytest.mark.parametrize("field,value", [
    ("connected_club_mailbox", True),
    ("connected_club_internal_documents", True),
    ("operational_source_authorized", True),
    ("pilot_started", True),
    ("external_mutation_allowed", True),
    ("real_native_promotions", 1),
])
def test_c42_cssa_internal_truth_cannot_be_fabricated(contract_data, field, value):
    d = evidence_data()
    d["cssa"][field] = value
    with pytest.raises(ValueError, match="C42_CSSA_REAL_AUTHORITY"):
        runner().verify_handoffs(**d, registry=contract_data[0],
                                 c41=contract_data[1])


def test_c42_no_clones_means_hard_block_not_fake_success(tmp_path):
    with pytest.raises(ValueError, match="C42_LOCAL_REPOSITORY_NOT_PRESENT"):
        runner().run_local_composition(
            core_root=ROOT, gps_root=tmp_path/"not-gps",
            trading_root=tmp_path/"not-trading",
            cssa_root=tmp_path/"not-cssa",
        )


def test_c42_socket_transport_is_disabled_even_when_probe_attempts_network(tmp_path):
    probe = """
import socket
s = socket.socket()
s.connect(('127.0.0.1', 21))
print('C42_PROBE={"should_not_happen":true}')
"""
    with pytest.raises(ValueError, match="C42_PROBE_FAILED_OFFLINE"):
        runner().run_probe(tmp_path, probe)


def test_c42_source_probe_json_must_be_exactly_one(tmp_path):
    result = runner().run_probe(
        tmp_path, "print('C42_PROBE={\\\"probe\\\":true}')"
    )
    assert result == {"probe": True}
    with pytest.raises(ValueError, match="C42_PROBE_OUTPUT_NOT_EXACTLY_ONE"):
        runner().run_probe(tmp_path, "print('not-an-evidence-marker')")


def test_c42_requires_independent_git_roots(tmp_path):
    with pytest.raises(ValueError, match="ROOTS_MUST_BE_DISTINCT"):
        runner().run_local_composition(
            core_root=tmp_path, trading_root=tmp_path,
            gps_root=tmp_path, cssa_root=tmp_path,
        )


def test_c42_11_failed_test_ids_identical_c1_c2_c4_with_one_c3_flake():
    p = json.loads(PARITY.read_text(encoding="utf8"))
    assert p["schema"] == "OBSIDIA_V01_GLOBAL_REGRESSION_FAILURE_PARITY_V0"
    base = p["runs"]["C1"]["failed_test_ids"]
    assert len(base) == 11
    assert len(set(base)) == 11
    assert p["runs"]["C2"]["failed_test_ids"] == base
    assert p["runs"]["C4"]["failed_test_ids"] == base
    assert p["runs"]["C3_attempt_1"]["failed_test_ids"] == base
    assert set(p["runs"]["C3_attempt_2"]["failed_test_ids"]) - set(base) == {
        "tests/test_batch_execution_v0.py::TestApprovalConcurrency::test_concurrent_identical_content_idempotent"
    }
    assert p["global_green"] is False
    assert p["zero_new_persistent_failures_C1_to_C4"] is True
    assert p["runs"]["pre_C1_baseline_A"]["failed_test_ids"] == base
    assert set(p["runs"]["pre_C1_baseline_B"]["failed_test_ids"]) - set(base) == {
        "tests/test_batch_execution_v0.py::TestApprovalConcurrency::test_concurrent_identical_content_idempotent"
    }
    assert p["original_pre_C1_baseline_test_id_parity_verified"] is True
    assert p["zero_new_persistent_failures_original_baseline_to_C4"] is True

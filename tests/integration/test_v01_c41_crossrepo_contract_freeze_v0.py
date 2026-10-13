"""C4.1 cross-repo freeze: references and NON-claims, not remote test attestation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from periphery.enterprise_sector_claims_v0 import (
    load_c4_evidence_registry_v0, assess_sector_claim_v0, STATUS_REFUSE,
)

ROOT = Path(__file__).resolve().parents[2]
C41 = ROOT / "docs/runtime/V01_ENTERPRISE_C41_CROSSREPO_CONTRACT_FREEZE_V0.json"
C4 = ROOT / "docs/runtime/V01_ENTERPRISE_C4_SECTOR_EVIDENCE_PROFILES_V0.json"


def load():
    return json.loads(C41.read_text(encoding="utf8"))


def test_c41_exact_sector_base_shas_match_c4_pinned_audit():
    d = load()
    prior = load_c4_evidence_registry_v0(C4)
    profile = {p["sector_id"]: p for p in prior["source_contracts"]}
    assert d["authority"] == "KX108_ONLY"
    assert d["core_kernel_modified"] is False
    assert d["production_permission_granted"] is False
    assert d["status"] == "PARTIAL_CONTRACT_PATCHES_CI_VALIDATED_NOT_INTERREPO_INTEGRATED"
    assert {x["sector_id"] for x in d["domain_updates"]} == {
        "TRADING_REFERENCE", "GPS_DEFENSE_PUBLIC_EXPORT"
    }
    for x in d["domain_updates"]:
        assert x["base_sha"] == profile[x["sector_id"]]["commit"]
        assert len(x["feature_sha"]) == 40
        assert x["feature_sha"] != x["base_sha"]
        assert x["draft"] is True
        assert x["tests"]["conclusion"] == "success"
        assert x["tests"]["count"] > 0
        assert x["claim_limits"]
    assert d["blocked_domain"]["sha"] == profile["CSSA_ADMIN_SHADOW"]["commit"]


def test_c41_gps_claim_label_quarantine_does_not_promote_real_attack():
    d = load()
    gps = next(x for x in d["domain_updates"]
               if x["sector_id"] == "GPS_DEFENSE_PUBLIC_EXPORT")
    assert "RECORDED_RF_ATTACK_SOURCE_LABEL_QUARANTINED" in gps["contract_closure"]
    result = assess_sector_claim_v0(
        load_c4_evidence_registry_v0(C4),
        sector_id="GPS_DEFENSE_PUBLIC_EXPORT",
        domain_id="gps_defense_aviation",
        claim_id="RECORDED_RF_ATTACK_CLOSED",
    )
    assert result["status"] == STATUS_REFUSE
    assert result["allowed_to_act"] is False


def test_c41_trading_paper_contract_is_not_live_execution():
    d = load()
    trade = next(x for x in d["domain_updates"]
                 if x["sector_id"] == "TRADING_REFERENCE")
    assert "PAPER_ONLY_WITH_PROOF_REQUIRED_GUARD" in trade["contract_closure"]
    assert "NO_LIVE_BROKER" in trade["claim_limits"]
    assert "NO_NEW_REAL_KERNEL_HTTP_ROUNDTRIP_IN_C41" in trade["claim_limits"]
    assert "NO_CROSSREPO_V01_TRADING_EXECUTION_YET" in trade["claim_limits"]


def test_c41_cssa_remains_unconnected_and_pilot_not_started():
    x = load()["blocked_domain"]
    assert x["internal_operational_mailbox_authorized"] is False
    assert x["internal_repository_authorized"] is False
    assert x["pilot_started"] is False
    assert x["real_native_promotions"] == 0


def test_c41_global_core_ci_has_11_failures_not_green():
    d = load()
    b = d["core_baseline_ci"]
    assert b["green"] is False
    assert b["status"] == "failure"
    assert b["passed"] == 12756
    assert b["failed"] == 11
    assert b["per_test_identity_parity_verified"] is False
    assert "VERIFY_BASELINE_FAILURE_IDENTITY_AND_FIX_ENVIRONMENT" in d["remaining"]


@pytest.mark.parametrize("sector,domain,claim", [
    ("TRADING_REFERENCE", "trading", "LIVE_TRADING_READY"),
    ("GPS_DEFENSE_PUBLIC_EXPORT", "gps_defense_aviation", "AVIATION_CERTIFIED"),
    ("CSSA_ADMIN_SHADOW", "administration", "CLUB_INTERNAL_MAILBOX_CONNECTED"),
])
def test_c41_no_feature_branch_promotes_prohibited_sector_claims(sector,domain,claim):
    result = assess_sector_claim_v0(
        load_c4_evidence_registry_v0(C4),
        sector_id=sector, domain_id=domain, claim_id=claim,
    )
    assert result["status"] == STATUS_REFUSE
    assert result["runtime_permission_granted"] is False

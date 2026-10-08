"""C4: pinned sector docs truth taxonomy, no second UDIP or false LIVE claims."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "tests" / "integration") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests" / "integration"))

from periphery.enterprise_sector_claims_v0 import (
    SCHEMA, STATUS_ACCEPT, STATUS_REFUSE, STATUS_CONFLICT,
    load_c4_evidence_registry_v0, assess_sector_claim_v0,
    verify_c4_evidence_registry_v0,
)
from periphery.enterprise_org_stack_lifecycle_v0 import CompanyStackLifecycleV0
from test_v01_c3_multiorg_multidomain_sandbox_e2e_v0 import (
    scenario, preparation, CASES, PROVIDERS, TENANTS,
)

MANIFEST = ROOT / "docs/runtime/V01_ENTERPRISE_C4_SECTOR_EVIDENCE_PROFILES_V0.json"


@pytest.fixture
def profiles():
    return load_c4_evidence_registry_v0(MANIFEST)


def _p(profiles, sector_id):
    return next(p for p in profiles["source_contracts"] if p["sector_id"] == sector_id)


def test_c4_registry_has_pinned_commits_no_claim_of_live_enterprise(profiles):
    assert profiles["schema"] == SCHEMA
    assert profiles["authority"] == "KX108_ONLY"
    assert profiles["verified_production_integration"] is False
    assert len({p["sector_id"] for p in profiles["source_contracts"]}) == 3
    assert all(len(p["commit"]) == 40 for p in profiles["source_contracts"])
    assert verify_c4_evidence_registry_v0(profiles)
    for entry in profiles["source_contracts"]:
        assert entry["unresolved"]
        assert len(entry["forbidden_claims"]) >= 4
        assert entry["source_paths"]
        assert entry["known_drift"] is not None


@pytest.mark.parametrize(
    "sector,domain,claim",
    [
        ("TRADING_REFERENCE", "trading", "CANONICAL_NATIVE_EXTERNAL_CONVERGENCE"),
        ("TRADING_REFERENCE", "trading", "REAL_KERNEL_HTTP_ROUNDTRIP_HISTORICAL"),
        ("TRADING_REFERENCE", "trading", "PAPER_ONLY_GOVERNED_CYCLE"),
        ("GPS_DEFENSE_PUBLIC_EXPORT", "gps_defense_aviation", "RECORDED_REAL_GNSS_OBSERVATION"),
        ("GPS_DEFENSE_PUBLIC_EXPORT", "gps_defense_aviation", "RECORDED_REAL_RF_NOMINAL_OBSERVATION"),
        ("GPS_DEFENSE_PUBLIC_EXPORT", "gps_defense_aviation", "FGI_RF_TRAJECTORY_ANOMALY_CANDIDATE"),
        ("CSSA_ADMIN_SHADOW", "administration", "UNIVERSAL_ADMINISTRATION_DOMAIN_CONTRACT"),
        ("CSSA_ADMIN_SHADOW", "administration", "PERSONAL_MAIL_READONLY_SHADOW_ROUTING"),
        ("CSSA_ADMIN_SHADOW", "administration", "OPERATIONAL_SOURCE_ONBOARDING_PREFLIGHT"),
    ]
)
def test_c4_documented_claim_remains_non_sovereign(profiles, sector, domain, claim):
    result = assess_sector_claim_v0(
        profiles, sector_id=sector, domain_id=domain, claim_id=claim
    )
    assert result["status"] == STATUS_ACCEPT
    assert result["source_commit"] == _p(profiles, sector)["commit"]
    assert result["evidence_grade"]
    assert result["source_paths"]
    assert result["runtime_permission_granted"] is False
    assert result["source_access_authorized"] is False
    assert result["real_external_effect_permitted"] is False
    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["evidence_sources_independently_verified"] is False
    assert result["organizational_authority_verified"] is False


@pytest.mark.parametrize(
    "sector,domain,denied",
    [
        ("TRADING_REFERENCE","trading","LIVE_TRADING_READY"),
        ("TRADING_REFERENCE","trading","DEFAULT_RUNTIME_REAL_KERNEL_CONNECTED"),
        ("TRADING_REFERENCE","trading","REAL_BROKER_ORDER_CONFIRMED"),
        ("TRADING_REFERENCE","trading","PRODUCTION_ECONOMIC_RETURN_PROVEN"),
        ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","RECORDED_RF_ATTACK_CLOSED"),
        ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","CONFIRMED_SPOOFING_CAUSALITY"),
        ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","SPOOF_RESISTANCE_VALIDATED"),
        ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","LIVE_RECEIVER_ACTUATION"),
        ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","AVIATION_CERTIFIED"),
        ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","DEVICE_CONFIGURATION_READY"),
        ("CSSA_ADMIN_SHADOW","administration","CLUB_INTERNAL_MAILBOX_CONNECTED"),
        ("CSSA_ADMIN_SHADOW","administration","CLUB_INTERNAL_DOCUMENTS_CONNECTED"),
        ("CSSA_ADMIN_SHADOW","administration","REAL_CLUB_OPERATIONAL_PILOT_STARTED"),
        ("CSSA_ADMIN_SHADOW","administration","REAL_CLUB_INTERNAL_CASE_TASK_PROMOTED"),
        ("CSSA_ADMIN_SHADOW","administration","PERSONAL_MAILBOX_IS_CLUB_AUTHORITY"),
        ("CSSA_ADMIN_SHADOW","administration","REAL_CLUB_SEND_ALLOWED"),
    ]
)
def test_c4_explicitly_denied_claim_cannot_be_promoted(profiles, sector, domain, denied):
    result = assess_sector_claim_v0(
        profiles, sector_id=sector, domain_id=domain, claim_id=denied
    )
    assert result["status"] == STATUS_REFUSE
    assert result["reason"] == "C4_CLAIM_EXPLICITLY_FORBIDDEN_BY_SECTOR_EVIDENCE"
    assert result["allowed_to_act"] is False


def test_c4_real_kernel_historical_evidence_not_default_connection(profiles):
    p = _p(profiles, "TRADING_REFERENCE")
    facts = p["observed_reference_assertions"]
    assert facts["historical_roundtrip_real_kernel_documented"] is True
    assert facts["default_real_kernel_attached"] is False
    assert facts["live_trading_forbidden"] is True
    assert facts["active_freeze_manifest_declares_passed"] == 284
    assert "REAL_KERNEL_HTTP_VERDICT_FIELD_X108_GATE_VS_LEGACY_VERDICT" in p["known_drift"]


def test_c4_gps_window_c_source_claim_conflict_quarantined(profiles):
    gps = _p(profiles, "GPS_DEFENSE_PUBLIC_EXPORT")
    assert gps["observed_claim_conflict"]["field"] == "proof_level"
    assert gps["observed_claim_conflict"]["observed_value"] == "RECORDED_RF_ATTACK"
    assert gps["observed_claim_conflict"]["other_observed_value"] is True
    assert gps["observed_reference_assertions"]["attack_causal_attribution_proven"] is False
    result = assess_sector_claim_v0(
        profiles, sector_id="GPS_DEFENSE_PUBLIC_EXPORT",
        domain_id="gps_defense_aviation",
        claim_id="FGI_RF_TRAJECTORY_ANOMALY_CANDIDATE",
        source_proof_level="RECORDED_RF_ATTACK",
    )
    assert result["status"] == STATUS_CONFLICT
    assert result["reason"] == "C4_CONFLICT_WITH_PINNED_SECTOR_CLAIM_MATRIX"
    assert result["real_external_effect_permitted"] is False


def test_c4_gps_recorded_evidence_not_a_spoofed_aircraft_victory(profiles):
    gps = _p(profiles, "GPS_DEFENSE_PUBLIC_EXPORT")
    x = gps["observed_reference_assertions"]
    assert x["recorded_gnss"] is True
    assert x["recorded_rf_nominal"] is True
    assert x["detector_rf_anomaly"] is True
    assert x["multisource_imu_radar_corrob"] is False
    assert "PUBLIC_BRIDGE_READS_VERDICT_BUT_REAL_KERNEL_REPORTS_X108_GATE" in gps["known_drift"]


def test_c4_cssa_personal_gmail_is_not_club_source(profiles):
    p = _p(profiles, "CSSA_ADMIN_SHADOW")
    data = p["observed_reference_assertions"]
    assert data == {
        "connected_internal_mailbox": False,
        "connected_internal_documents": False,
        "personal_sample_count": 8,
        "real_native_promotions": 0,
        "pilot_started": False,
    }


def test_c4_simulated_c3_administration_cannot_prove_cssa_internal_source(tmp_path, profiles):
    c3 = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    registry = CompanyStackLifecycleV0()
    registry.register(c3[1], **c3[2])
    prep = preparation(c3, registry)
    assert prep.source_domain == "administration"
    assert prep.sandbox_only is True
    assert prep.real_provider_calls_permitted is False
    cssa_internal = assess_sector_claim_v0(
        profiles, sector_id="CSSA_ADMIN_SHADOW",
        domain_id="administration", claim_id="CLUB_INTERNAL_MAILBOX_CONNECTED",
    )
    assert cssa_internal["status"] == STATUS_REFUSE


@pytest.mark.parametrize("sector,domain,claim", [
    ("TRADING_REFERENCE","trading","CANONICAL_NATIVE_EXTERNAL_CONVERGENCE"),
    ("GPS_DEFENSE_PUBLIC_EXPORT","gps_defense_aviation","RECORDED_REAL_GNSS_OBSERVATION"),
    ("CSSA_ADMIN_SHADOW","administration","PERSONAL_MAIL_READONLY_SHADOW_ROUTING")
])
def test_c4_no_real_egress_even_for_documented_evidence(profiles, sector, domain, claim):
    result = assess_sector_claim_v0(
        profiles, sector_id=sector, domain_id=domain, claim_id=claim,
        requested_external_effect=True,
    )
    assert result["status"] == STATUS_REFUSE
    assert result["reason"] == "C4_EXTERNAL_EFFECT_NOT_PERMITTED"


def test_c4_wrong_sector_domain_and_unknown_fail_closed(profiles):
    assert assess_sector_claim_v0(
        profiles, sector_id="CSSA_ADMIN_SHADOW", domain_id="trading",
        claim_id="PERSONAL_MAIL_READONLY_SHADOW_ROUTING",
    )["status"] == STATUS_REFUSE
    assert assess_sector_claim_v0(
        profiles, sector_id="TRADING_REFERENCE", domain_id="trading",
        claim_id="BROKER_LIVE_GRANT",
    )["status"] == STATUS_REFUSE
    assert assess_sector_claim_v0(
        profiles, sector_id="NONEXISTENT", domain_id="trading",
        claim_id="PAPER_ONLY_GOVERNED_CYCLE",
    )["status"] == STATUS_REFUSE


@pytest.mark.parametrize("tamper", [
    "authority", "production", "duplicate_sector", "forge_sha",
    "forbidden_promoted", "unbound_evidence", "missing_blockers",
    "conflict_silenced", "missing_known_drift"
])
def test_c4_profile_tampering_or_loss_of_constraints_refused(profiles, tamper):
    data = copy.deepcopy(profiles)
    t, g, c = data["source_contracts"]
    if tamper == "authority":
        data["authority"] = "ANY_TOOL"
    elif tamper == "production":
        data["verified_production_integration"] = True
    elif tamper == "duplicate_sector":
        g["sector_id"] = t["sector_id"]
    elif tamper == "forge_sha":
        t["commit"] = "DEADBEEF"
    elif tamper == "forbidden_promoted":
        t["claims"][0]["claim_id"] = t["forbidden_claims"][0]
    elif tamper == "unbound_evidence":
        t["claims"][0]["source_paths"] = ["not-a-reviewed-source.md"]
    elif tamper == "missing_blockers":
        c["unresolved"] = []
    elif tamper == "conflict_silenced":
        g["observed_claim_conflict"]["observed_value"] = "SYNTHETIC_TEST_ONLY"
    else:
        c["known_drift"] = None
    with pytest.raises(ValueError, match="C4_"):
        verify_c4_evidence_registry_v0(data)

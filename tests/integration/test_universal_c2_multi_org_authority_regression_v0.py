"""Universal C2 invariants across different organizations and business sectors.

Uses the existing C2.3 SQLite ledger + C2.18 signed identity fixtures, not
new permission machinery. A successful fixture check never authorizes ACT.
"""
from __future__ import annotations
from dataclasses import replace

import pytest

from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0
from periphery.universal_cross_domain_conformance_v0 import (
    DomainEvidenceV0, interpret_domain_v0,
)
from tests.integration.test_v01_c218_identity_delegation_chain_fixture_v0 import (
    SCOPE, scenario,
)
from periphery.enterprise_identity_delegation_chain_fixture_v0 import inspect_identity_delegation_fixture_v0

SECTORS=(
    ("CSSA","org-cssa","CRM","member.update"),
    ("INDUSTRIAL_MAINTENANCE","org-factory","MAINTENANCE","maintenance.inspect"),
    ("GPS_DEFENSE","org-gps","DEVICE","device.review"),
)

@pytest.mark.parametrize("domain,org,connector,capability",SECTORS)
def test_c2_universal_ledger_revocation_no_execution_across_sectors(
    tmp_path,domain,org,connector,capability
):
    ledger=DurableDelegationLedgerV0(tmp_path/"authority.db")
    scope=(org,"delegate-a",connector,capability)
    ledger.register_fixture(scope)
    first=ledger.check_and_consume_fixture(
        scope,generation=0,nonce="universal-c2-first-001",evidence_verified=True
    )
    assert first=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert ledger.revoke(scope) is True
    reopened=DurableDelegationLedgerV0(tmp_path/"authority.db")
    assert reopened.check_and_consume_fixture(
        scope,generation=0,nonce="universal-c2-after-001",
        evidence_verified=True
    )=="BLOCK:C23_REVOKED"

@pytest.mark.parametrize("domain,org,connector,capability",SECTORS)
def test_c2_universal_cross_organization_cannot_borrow_delegation(
    tmp_path,domain,org,connector,capability
):
    ledger=DurableDelegationLedgerV0(tmp_path/"authority.db")
    scope=(org,"delegate-a",connector,capability)
    ledger.register_fixture(scope)
    borrowed=("org-attacker","delegate-a",connector,capability)
    assert ledger.check_and_consume_fixture(
        borrowed,generation=0,nonce="universal-c2-borrow-001",
        evidence_verified=True
    )=="BLOCK:C23_DELEGATION_UNKNOWN"

def test_c2_universal_replay_isolation_and_revocation_atomicity(tmp_path):
    ledger=DurableDelegationLedgerV0(tmp_path/"authority.db")
    a=("org-cssa","delegate-a","CRM","member.update")
    b=("org-factory","delegate-a","MAINTENANCE","maintenance.inspect")
    ledger.register_fixture(a)
    ledger.register_fixture(b)
    nonce="universal-cross-sector-000001"
    assert ledger.check_and_consume_fixture(
        a,generation=0,nonce=nonce,evidence_verified=True
    )=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert ledger.check_and_consume_fixture(
        a,generation=0,nonce=nonce,evidence_verified=True
    )=="BLOCK:C23_NONCE_REPLAY"
    assert ledger.check_and_consume_fixture(
        b,generation=0,nonce=nonce,evidence_verified=True
    )=="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    ledger.revoke(a)
    assert ledger.check_and_consume_fixture(
        a,generation=0,nonce="universal-after-revoke-0001",
        evidence_verified=True
    )=="BLOCK:C23_REVOKED"

def test_c2_valid_signed_identity_fixture_is_still_not_a_runtime_permit(tmp_path):
    _,args=scenario(tmp_path)
    decision=inspect_identity_delegation_fixture_v0(**args)
    assert decision["status"]=="BLOCK"
    assert decision["reason"]=="C218_ORGANIZATION_DELEGATION_AUTHORITY_UNVERIFIED"
    assert decision["egress_allowed"] is False
    args["organization"]="org-b"
    assert "IDENTITY_REJECTED" in inspect_identity_delegation_fixture_v0(**args)["reason"]

@pytest.mark.parametrize("domain,facts",[
    ("CSSA",{"organization":"org-cssa","case":"membership","authority":"DECLARED"}),
    ("GPS_DEFENSE",{"receiver":"unit-a","signal":"recorded","rf_evidence":"unverified"}),
    ("INDUSTRIAL_MAINTENANCE",{"machine":"pump","sensor":"simulated","maintenance_rule":"inspect"}),
])
def test_universal_domain_intent_cannot_assert_kernel_authority(domain,facts):
    result=interpret_domain_v0(DomainEvidenceV0(
        case_id="c2-"+domain,domain=domain,observed_facts=facts,
        source_refs=("synthetic:source",),evidence_refs=("synthetic:evidence",),
        adapter_ref="C2_FIXTURE",organization_scope="org-isolated",
        observed_at="2026-10-09T08:00:00+02:00",proposed_intent="REVIEW",
    ))
    assert result["authority"]=="KX108_ONLY"
    assert result["kx108_decision"]=="NOT_INVOKED"
    assert result["world_action_allowed"] is False
    assert result["provider_invoked"] is False
    assert result["real_effect"] is False

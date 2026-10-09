"""Integrated 12-case CSSA season test; real Universal sandbox for 2 CSSA dossiers."""
from copy import deepcopy
import pytest

from periphery.cssa_full_lot_a_campaign_v0 import (
    run_cssa_full_lot_a_campaign, verify_cssa_full_lot_a_campaign,
)


def e(key, kind, hour, **kw):
    return dict({
        "id": key, "kind": kind, "owner": "manager",
        "slot": f"2026-10-20T{hour:02d}:00:00+00:00",
        "source_ref": "cssa:synthetic:" + key,
    }, **kw)


def sample():
    return [
        e("licence", "DEADLINE", 8, regulatory_basis_proven=True,
          due_at="2026-10-24T17:00:00+00:00"),
        e("contract", "DEADLINE", 9, regulatory_basis_proven=True,
          due_at="2026-10-25T16:00:00+00:00"),
        e("match", "MATCH", 10, resource="stadium"),
        e("collision", "MATCH", 10, resource="stadium"),
        e("absent", "STAFF", 11, owner_available=False),
        e("delegate", "STAFF", 12, delegated_to="volunteer", delegation_proven=False),
        e("budget", "PROCUREMENT", 13, cost_eur=200, budget_eur=100),
        e("missing_budget", "PROCUREMENT", 14, cost_eur=200),
        e("regulatory", "DEADLINE", 15, regulatory_basis_proven=False),
        e("publicity", "COMMUNICATION", 16, publication_facts_proven=False),
        e("contradiction", "MATCH", 17, contradicted=True),
        e("provenance", "STAFF", 18, source_ref=""),
    ]


def test_full_campaign_multiple_cssa_actions_and_all_refusals(tmp_path):
    result = run_cssa_full_lot_a_campaign(
        sample(), root=tmp_path / "lot-a",
        simulated_approved_ids=("licence", "contract"),
    )
    assert verify_cssa_full_lot_a_campaign(result)
    report = result["report"]
    assert report["totals"] == {
        "events": 12, "blocked": 9, "held": 1,
        "sandbox_executed": 2, "replayed": 2, "duplicate_blocked": 2,
    }
    by_id = {c["id"]: c for c in report["cases"]}
    assert by_id["licence"]["native_mutation_count"] == 4
    assert by_id["contract"]["native_mutation_count"] == 4
    assert len(by_id["licence"]["receipt_hash"]) == 64
    assert by_id["match"]["status"] == "HOLD"
    assert by_id["match"]["reason"] == "NO_SIMULATED_OPERATOR_APPROVAL"
    assert "RESOURCE_COLLISION_WITH:match" in by_id["collision"]["issues"]
    assert "OWNER_UNAVAILABLE" in by_id["absent"]["issues"]
    assert "BUDGET_EXCEEDED" in by_id["budget"]["issues"]
    assert "BUDGET_UNVERIFIED" in by_id["missing_budget"]["issues"]
    assert "SOURCE_UNPROVEN" in by_id["provenance"]["issues"]
    assert report["f3f_904_events_replayed"] is False
    assert report["f3g_11_roles_closed"] is False
    assert report["network_calls_real"] == 0


def test_no_fixture_approvals_means_no_writes(tmp_path):
    root = tmp_path / "never-created"
    result = run_cssa_full_lot_a_campaign(sample(), root=root)
    assert result["report"]["totals"]["sandbox_executed"] == 0
    assert not root.exists()


def test_multi_case_conflicting_approvals_do_not_override_domain_gate(tmp_path):
    result = run_cssa_full_lot_a_campaign(
        sample(), root=tmp_path / "conflict",
        simulated_approved_ids=("collision", "absent", "licence"),
    )
    cases = {c["id"]: c for c in result["report"]["cases"]}
    assert cases["collision"]["status"] == "BLOCK"
    assert cases["absent"]["status"] == "BLOCK"
    assert cases["licence"]["status"] == "SANDBOX_EXECUTED"
    assert result["report"]["totals"]["sandbox_executed"] == 1


def test_unknown_approval_reference_rejected_without_writes(tmp_path):
    root = tmp_path / "never-created"
    with pytest.raises(ValueError, match="CSSA_FULL_A_APPROVAL_NOT_IN_BATCH"):
        run_cssa_full_lot_a_campaign(sample(), root=root,
                                     simulated_approved_ids=("unknown",))
    assert not root.exists()


def test_duplicate_approval_reference_rejected(tmp_path):
    with pytest.raises(ValueError, match="CSSA_FULL_A_DUPLICATE_APPROVAL"):
        run_cssa_full_lot_a_campaign(sample(), root=tmp_path / "never",
                                     simulated_approved_ids=("licence", "licence"))


def test_non_deadline_cannot_be_activated_by_synthetic_approval(tmp_path):
    result = run_cssa_full_lot_a_campaign(
        [e("match", "MATCH", 10)], root=tmp_path / "match",
        simulated_approved_ids=("match",),
    )
    case = result["report"]["cases"][0]
    assert case["status"] == "HOLD"
    assert case["reason"] == "CSSA_NATIVE_SURFACE_NOT_PROVEN_FOR_KIND"
    assert result["report"]["totals"]["sandbox_executed"] == 0


def test_receipt_mutation_detected(tmp_path):
    result = run_cssa_full_lot_a_campaign(
        [e("match", "MATCH", 10)], root=tmp_path / "root")
    bad = deepcopy(result)
    bad["report"]["cases"][0]["status"] = "SANDBOX_EXECUTED"
    assert not verify_cssa_full_lot_a_campaign(bad)


def test_noncanonical_date_does_not_reach_governance(tmp_path):
    root = tmp_path / "root"
    result = run_cssa_full_lot_a_campaign(
        [e("licence", "DEADLINE", 8, regulatory_basis_proven=True,
           due_at="2026-10-24")],
        root=root, simulated_approved_ids=("licence",),
    )
    assert result["report"]["cases"][0]["status"] == "HOLD"
    assert not root.exists()

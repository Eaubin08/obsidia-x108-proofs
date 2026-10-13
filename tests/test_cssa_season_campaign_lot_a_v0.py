"""Integrated CSSA LOT A season campaign — synthetic, no action authority."""
from copy import deepcopy
import pytest

from periphery.cssa_season_campaign_lot_a_v0 import (
    run_cssa_season_campaign, verify_cssa_season_campaign,
)


def event(key, kind="MATCH", **kw):
    return dict({"id": key, "kind": kind, "owner": "manager",
                 "slot": "2026-10-20T18:00+02:00",
                 "source_ref": "synthetic:" + key}, **kw)


def test_integrated_multi_service_campaign():
    data = [
        event("match", resource="stadium", owner_available=True),
        event("pitch_conflict", resource="stadium"),
        event("owner_conflict", resource="other"),
        event("absent", owner_available=False),
        event("delegated", delegated_to="volunteer", delegation_proven=False),
        event("budget", kind="PROCUREMENT", cost_eur=200, budget_eur=100),
        event("licence", kind="DEADLINE", regulatory_basis_proven=False),
        event("deadline", kind="DEADLINE", regulatory_basis_proven=True,
              deadline_known=False),
        event("comms", kind="COMMUNICATION", publication_facts_proven=False),
        event("contradiction", contradicted=True),
        event("missing", kind="STAFF", source_ref=""),
        event("valid", kind="MATCH", resource="parking"),
    ]
    bundle = run_cssa_season_campaign(data)
    assert verify_cssa_season_campaign(bundle)
    report = bundle["report"]
    assert report["totals"]["events"] == 12
    assert report["totals"]["blocked"] >= 10
    assert report["totals"]["resource_collision_pairs"] == 1
    assert report["status"] == "HOLD"
    assert report["external_actions"] == []
    assert report["historical_f3f_904_claimed"] is False
    by_id = {x["id"]: x for x in report["cases"]}
    assert "RESOURCE_COLLISION_WITH:match" in by_id["pitch_conflict"]["issues"]
    assert "OWNER_UNAVAILABLE" in by_id["absent"]["issues"]
    assert "DELEGATION_UNPROVEN" in by_id["delegated"]["issues"]
    assert "BUDGET_EXCEEDED" in by_id["budget"]["issues"]
    assert "REGULATORY_BASIS_UNPROVEN" in by_id["licence"]["issues"]
    assert "PUBLICATION_FACTS_UNPROVEN" in by_id["comms"]["issues"]
    assert all(x["kx108_decision"] is None for x in report["cases"])


def test_all_clear_remains_hold_without_governed_approval():
    bundle = run_cssa_season_campaign([event("one")])
    assert bundle["report"]["cases"][0]["status"] == "HOLD"
    assert bundle["report"]["totals"]["held"] == 1
    assert bundle["report"]["execution_proven"] is False


def test_duplicate_identifiers_rejected():
    with pytest.raises(ValueError, match="CSSA_A_EVENT_IDENTITY_OR_SHAPE_INVALID"):
        run_cssa_season_campaign([event("x"), event("x")])


@pytest.mark.parametrize("bad", [
    {"id": "x", "kind": "UNTRUSTED", "owner": "o", "slot": "slot"},
    {"id": "x", "kind": "MATCH", "owner": None, "slot": "slot"},
    {"id": "", "kind": "MATCH", "owner": "o", "slot": "slot"},
])
def test_invalid_events_fail_closed(bad):
    with pytest.raises(ValueError):
        run_cssa_season_campaign([bad])


def test_replay_deterministic_and_receipt_tamper_detected():
    data = [event("x", resource="stadium")]
    original = run_cssa_season_campaign(data)
    assert original == run_cssa_season_campaign(data)
    modified = deepcopy(original)
    modified["report"]["cases"][0]["status"] = "ALLOW"
    assert verify_cssa_season_campaign(modified) is False


def test_not_recovered_historical_campaign():
    bundle = run_cssa_season_campaign([])
    assert verify_cssa_season_campaign(bundle)
    assert bundle["report"]["totals"]["events"] == 0
    assert bundle["report"]["historical_f3f_904_claimed"] is False


def test_bounded_campaign():
    with pytest.raises(ValueError, match="CSSA_A_EVENTS_INVALID"):
        run_cssa_season_campaign([event(str(i)) for i in range(2001)])

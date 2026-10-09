import pytest
from periphery.universal_cross_domain_conformance_v0 import (
    DomainEvidenceV0,interpret_domain_v0,evaluate_cross_domain_conformance_v0,
)

def case(domain,**overrides):
    facts={
        "CSSA":{"organization":"CSSA-SIM","case":"matchday-change","authority":"human-review"},
        "GPS_DEFENSE":{"receiver":"GNSS-SIM","signal":"clock-skew","rf_evidence":"SYNTHETIC_IQ"},
        "TRADING":{"portfolio":"PAPER-ONLY","order":"BUY-SIM","risk_limit":"ONE_PERCENT"},
        "INDUSTRIAL_MAINTENANCE":{"machine":"PUMP-SIM","sensor":"temperature-high","maintenance_rule":"inspection"},
    }
    d=dict(case_id="sim:"+domain,domain=domain,observed_facts=facts[domain],
       source_refs=("synthetic:source",),evidence_refs=("synthetic:evidence",),
       adapter_ref="synthetic:"+domain,organization_scope="sandbox:organization",
       observed_at="2026-10-09T06:00:00+02:00",proposed_intent="PROPOSE_REVIEW")
    d.update(overrides)
    return DomainEvidenceV0(**d)

@pytest.mark.parametrize("domain",["CSSA","GPS_DEFENSE","TRADING","INDUSTRIAL_MAINTENANCE"])
def test_four_domains_share_authority_and_do_not_execute(domain):
    r=interpret_domain_v0(case(domain))
    assert r["authority"]=="KX108_ONLY"
    assert r["kx108_decision"]=="NOT_INVOKED"
    assert r["provider_invoked"] is False and r["real_effect"] is False
    assert len(r["intent_hash"])==64

def test_valid_cssa_is_review_only_not_allow():
    assert interpret_domain_v0(case("CSSA"))["gate"]=="REVIEW_ONLY"

@pytest.mark.parametrize("domain",["GPS_DEFENSE","TRADING"])
def test_sensitive_domains_hold_even_with_evidence(domain):
    assert interpret_domain_v0(case(domain))["gate"]=="HOLD"

def test_industry_is_positive_non_executing_draft():
    r=interpret_domain_v0(case("INDUSTRIAL_MAINTENANCE"))
    assert r["gate"]=="REVIEW_ONLY" and not r["world_action_allowed"]

@pytest.mark.parametrize("domain,field",[
    ("CSSA","authority"),("GPS_DEFENSE","rf_evidence"),
    ("TRADING","risk_limit"),("INDUSTRIAL_MAINTENANCE","maintenance_rule")])
def test_missing_critical_domain_facts_hold(domain,field):
    x=case(domain)
    d=dict(x.observed_facts)
    d.pop(field)
    r=interpret_domain_v0(case(domain,observed_facts=d))
    assert r["gate"]=="HOLD"
    assert field in r["missing"]

@pytest.mark.parametrize("domain",["CSSA","GPS_DEFENSE","TRADING","INDUSTRIAL_MAINTENANCE"])
def test_domain_contradictions_block(domain):
    r=interpret_domain_v0(case(domain,contradictions=("SOURCE_CONFLICT",)))
    assert r["gate"]=="BLOCK"

@pytest.mark.parametrize("domain",["CSSA","GPS_DEFENSE","TRADING","INDUSTRIAL_MAINTENANCE"])
def test_unknown_requires_hold(domain):
    assert interpret_domain_v0(case(domain,unknowns=("UNVERIFIED_SCOPE",)))["gate"]=="HOLD"

def test_source_provenance_missing_holds():
    r=interpret_domain_v0(case("CSSA",evidence_refs=()))
    assert r["gate"]=="HOLD" and "provenance" in r["missing"]

def test_live_mode_raises_before_provider():
    with pytest.raises(ValueError,match="EXTERNAL_EXECUTION_FORBIDDEN"):
        interpret_domain_v0(case("CSSA",requested_execution="LIVE"))

def test_hash_stable_under_dict_key_reordering():
    x=case("CSSA")
    y=case("CSSA",observed_facts=dict(reversed(list(x.observed_facts.items()))))
    assert interpret_domain_v0(x)["intent_hash"]==interpret_domain_v0(y)["intent_hash"]

def test_hash_changes_with_facts():
    x=case("CSSA")
    y=case("CSSA",observed_facts=dict(x.observed_facts,case="alternate-case"))
    assert interpret_domain_v0(x)["intent_hash"]!=interpret_domain_v0(y)["intent_hash"]

def test_no_cross_organization_hash_collision():
    x=case("CSSA")
    y=case("CSSA",organization_scope="sandbox:other")
    assert interpret_domain_v0(x)["intent_hash"]!=interpret_domain_v0(y)["intent_hash"]

def campaign():
    return (
      case("CSSA"),
      case("GPS_DEFENSE"),
      case("TRADING"),
      case("INDUSTRIAL_MAINTENANCE"),
      case("INDUSTRIAL_MAINTENANCE",case_id="sim:industry:contradiction",
           contradictions=("sensorA-vs-sensorB",))
    )

def test_complete_campaign():
    r=evaluate_cross_domain_conformance_v0(campaign())
    assert r["verdict"]=="CONTRACT_SIMULATION_PASS",r["issues"]
    assert r["domain_count"]==4 and r["case_count"]==5
    assert r["gate_counts"]=={"REVIEW_ONLY":2,"HOLD":2,"BLOCK":1}
    assert r["real_connector_calls"]==r["real_actions"]==r["kx108_calls"]==0
    assert r["external_repo_runtime_verified"] is False

def test_missing_domain_rejects_closure():
    r=evaluate_cross_domain_conformance_v0(campaign()[:-2])
    assert r["verdict"]=="CONTRACT_SIMULATION_BLOCKED"

def test_duplicate_case_rejects():
    with pytest.raises(ValueError,match="DUPLICATE_CASE"):
        evaluate_cross_domain_conformance_v0((case("CSSA"),case("CSSA")))

def test_campaign_without_block_refuses_freeze():
    r=evaluate_cross_domain_conformance_v0(campaign()[:-1])
    assert r["verdict"]=="CONTRACT_SIMULATION_BLOCKED"
    assert "BLOCK_NOT_TESTED" in r["issues"]

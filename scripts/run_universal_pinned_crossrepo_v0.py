"""Reuse C4.2 pinned cross-repo execution and compare to Universal V0.

No automatic fetch, network transport, live actions, kernel alterations, or
claim that an offline KX108 mock is a sovereign decision. Reports derived
from C4.2 carry an explicit separate experimental scope.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

from periphery.universal_cross_domain_conformance_v0 import (
    DomainEvidenceV0, evaluate_cross_domain_conformance_v0,
)
from scripts.v01_c42_local_crossrepo_probe_v0 import (
    SCHEMA as C42_SCHEMA, SUCCESS as C42_SUCCESS,
    run_local_composition, sha256_obj,
)

def compose_verified_crossrepo_v0(c42:dict[str,Any])->dict[str,Any]:
    """Join a C4.2 runtime *output*, not its fixtures, with our offline contract.
    
    This pure check is NOT an authentication mechanism. The production caller
    must obtain c42 directly from run_local_composition, not untrusted JSON.
    """
    if c42.get("schema")!=C42_SCHEMA or c42.get("report_sha256") != sha256_obj({
        k:v for k,v in c42.items() if k!="report_sha256"
    }):
        raise ValueError("CROSSREPO_REPORT_INTEGRITY_INVALID")
    results=c42.get("results",{})
    if (
        results.get("status")!=C42_SUCCESS
        or c42.get("cross_repository_contract_composed") is not True
        or c42.get("actual_multi_repository_live_runtime_integrated") is not False
        or c42.get("network_access_permitted") is not False
        or c42.get("kernel_mutation") is not False
        or c42.get("main_merge") is not False
        or results.get("actual_remote_kernel_tested") is not False
        or results.get("actual_broker_used") is not False
        or results.get("actual_club_mailbox_used") is not False
        or results.get("real_external_effect") is not False
        or results.get("allowed_to_act") is not False
        or results.get("decision_authority")!="KX108_ONLY"
    ):
        raise ValueError("CROSSREPO_UNAUTHORIZED_PROMOTION")
    sha=c42.get("source_commits",{})
    if set(sha)!={"core","gps","trading","cssa"} or any(
        not isinstance(x,str) or len(x)!=40 or any(c not in "0123456789abcdef" for c in x)
        for x in sha.values()
    ):
        raise ValueError("CROSSREPO_PROVENANCE_INCOMPLETE")
    common=dict(organization_scope="sandbox:crossrepo:offline",
                observed_at="2026-10-09T00:00:00+00:00",
                source_refs=("c42:pinned-execution:"+c42["report_sha256"],),
                adapter_ref="C42_EXISTING_RUNNER",
                proposed_intent="REVIEW_OBSERVATION_ONLY",
                requested_execution="OFFLINE_ONLY")
    def make(domain,case_id,facts,evidence,unknowns=(),contradictions=()):
        return DomainEvidenceV0(
          domain=domain,case_id=case_id,observed_facts=facts,
          evidence_refs=(evidence,),unknowns=tuple(unknowns),
          contradictions=tuple(contradictions),**common)
    cases=(
      make("CSSA","c42:cssa:shadow",
           {"organization":"CSSA_SHADOW","case":"SOURCE_PREFLIGHT","authority":"NOT_AUTHORIZED"},
           "c42:cssa:"+sha["cssa"]),
      make("GPS_DEFENSE","c42:gps:partial-rf",
           {"receiver":"PINNED_GPS_REPO","signal":"RECORDED_RF_ATTACK",
            "rf_evidence":"SOURCE_LEVEL_CONFLICT_REVIEW_REQUIRED"},
           "c42:gps:"+sha["gps"],unknowns=("CAUSAL_ATTRIBUTION_NOT_PROVEN",)),
      make("TRADING","c42:trading:paper",
           {"portfolio":"PAPER","order":"NO_BROKER_SUBMIT","risk_limit":"PROOF_REQUIRED"},
           "c42:trading:"+sha["trading"],unknowns=("KX108_REMOTE_MOCKED",)),
      make("INDUSTRIAL_MAINTENANCE","synthetic:industry:nominal",
           {"machine":"SYNTHETIC_PUMP","sensor":"SYNTHETIC_TEMP",
            "maintenance_rule":"SIMULATED_INSPECTION"},
           "synthetic:industry:nominal"),
      make("INDUSTRIAL_MAINTENANCE","synthetic:industry:contradiction",
           {"machine":"SYNTHETIC_PUMP","sensor":"CONFLICTING_SYNTHETIC_SENSORS",
            "maintenance_rule":"SIMULATED_INSPECTION"},
           "synthetic:industry:conflict",contradictions=("SENSOR_DISAGREEMENT",)),
    )
    contract=evaluate_cross_domain_conformance_v0(cases)
    if contract["verdict"]!="CONTRACT_SIMULATION_PASS":
        raise ValueError("CROSSREPO_UNIVERSAL_CONTRACT_BLOCKED")
    report={
      "schema":"OBSIDIA_UNIVERSAL_C42_PINNED_COMPOSITION_V0",
      "verdict":"OFFLINE_PINNED_CROSSREPO_CONTRACT_PASS",
      "c42_sha256":c42["report_sha256"],
      "source_commits":sha,
      "universal_contract_sha256":contract["diagnostic_hash"],
      "contract_gate_counts":contract["gate_counts"],
      "scopes":{"cssa":"OFFLINE_PREFLIGHT_ONLY",
                "gps":"RECORDED_RF_PARTIAL_NO_CAUSAL_PROOF",
                "trading":"PAPER_BROKER_FAKE_KX108_MOCK",
                "industry":"SYNTHETIC_ONLY"},
      "real_kernel_decision_verified":False,
      "real_external_effect":False,
      "network_access_permitted":False,
      "industry_runtime_integrated":False,
      "live_operations_authorized":False,
      "decision_authority":"KX108_ONLY",
    }
    report["report_sha256"]=sha256_obj(report)
    return report

def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--core-root",type=Path,default=Path(__file__).resolve().parents[1])
    for k in ("gps","trading","cssa"): p.add_argument("--"+k+"-root",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args(argv)
    try:
        c42=run_local_composition(core_root=a.core_root,gps_root=a.gps_root,
                    trading_root=a.trading_root,cssa_root=a.cssa_root)
        result=compose_verified_crossrepo_v0(c42)
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({"schema":"OBSIDIA_UNIVERSAL_C42_PINNED_COMPOSITION_V0",
                          "verdict":"BLOCKED_FAIL_CLOSED",
                          "reason":str(e).split(":")[0]},sort_keys=True))
        return 2
    payload=json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(payload,encoding="utf-8")
    print(payload)
    return 0

if __name__=="__main__":
    raise SystemExit(main())

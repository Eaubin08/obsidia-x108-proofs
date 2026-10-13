"""Offline join validation. Synthetic C4.2-shaped fixture is NOT runtime proof."""
from copy import deepcopy
import pytest
from scripts.v01_c42_local_crossrepo_probe_v0 import SCHEMA,SUCCESS,sha256_obj
from scripts.run_universal_pinned_crossrepo_v0 import compose_verified_crossrepo_v0

def synthetic_c42():
    report={"schema":SCHEMA,
      "results":{"status":SUCCESS,"actual_remote_kernel_tested":False,
        "actual_broker_used":False,"actual_club_mailbox_used":False,
        "real_external_effect":False,"allowed_to_act":False,
        "decision_authority":"KX108_ONLY"},
      "source_commits":{d:{"core":"a","cssa":"b","gps":"c","trading":"d"}[d]*40
                         for d in ("core","cssa","gps","trading")},
      "cross_repository_contract_composed":True,
      "actual_multi_repository_live_runtime_integrated":False,
      "network_access_permitted":False,"kernel_mutation":False,"main_merge":False}
    report["report_sha256"]=sha256_obj(report)
    return report

def reseal(d):
    d["report_sha256"]=sha256_obj({k:v for k,v in d.items() if k!="report_sha256"})
    return d

def test_offline_composition_report_retains_all_limits():
    r=compose_verified_crossrepo_v0(synthetic_c42())
    assert r["verdict"]=="OFFLINE_PINNED_CROSSREPO_CONTRACT_PASS"
    assert r["contract_gate_counts"]=={"REVIEW_ONLY":2,"HOLD":2,"BLOCK":1}
    assert not r["real_kernel_decision_verified"]
    assert not r["industry_runtime_integrated"]
    assert not r["live_operations_authorized"]
    assert not r["real_external_effect"]

def test_tampering_hash_rejected():
    d=synthetic_c42()
    d["results"]["status"]="FAIL"
    with pytest.raises(ValueError,match="INTEGRITY"):
        compose_verified_crossrepo_v0(d)

@pytest.mark.parametrize("path,value",[
    (("results","actual_remote_kernel_tested"),True),
    (("results","real_external_effect"),True),
    (("results","actual_broker_used"),True),
    (("results","actual_club_mailbox_used"),True),
    (("results","allowed_to_act"),True),
    (("results","decision_authority"),"BRODY"),
    (("network_access_permitted",),True),
    (("main_merge",),True),
    (("kernel_mutation",),True),
    (("actual_multi_repository_live_runtime_integrated",),True),
])
def test_even_resealed_promotions_rejected(path,value):
    d=deepcopy(synthetic_c42())
    target=d
    for part in path[:-1]: target=target[part]
    target[path[-1]]=value
    with pytest.raises(ValueError,match="UNAUTHORIZED_PROMOTION"):
        compose_verified_crossrepo_v0(reseal(d))

def test_missing_domain_provenance_rejected():
    d=synthetic_c42()
    d["source_commits"].pop("trading")
    with pytest.raises(ValueError,match="PROVENANCE"):
        compose_verified_crossrepo_v0(reseal(d))

def test_invalid_commit_hash_rejected():
    d=synthetic_c42()
    d["source_commits"]["gps"]="not-a-commit"
    with pytest.raises(ValueError,match="PROVENANCE"):
        compose_verified_crossrepo_v0(reseal(d))

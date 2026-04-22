from obsidia_kernel.kernel import ObsidiaKernel
from obsidia_kernel.contract import Request, Meta, Intent, IntentType, Governance, Decision

def test_enriched_fields_present():
    k = ObsidiaKernel()
    req = Request(
        meta=Meta(request_id="t1", timestamp="now", domain="generic", mode="proof", agent_id=None, human_id=None),
        intent=Intent(type=IntentType.ACTION, name="run", payload={"code":"x=1\nprint(x)"}),
        context={"W_full":[[0,1,1],[1,0,1],[1,1,0]], "core_nodes":[0,1,2], "theta_S":0.25},
        governance=Governance(irreversible=False, x108_min_wait_s=108, x108_elapsed_s=999, theta_S=0.25),
        attachments={}
    )
    res = k.run(req)
    assert isinstance(res.hash_chain, list) and len(res.hash_chain) >= 1
    assert res.artifacts_hash is not None and len(res.artifacts_hash) == 64
    assert res.decision in (Decision.ACT, Decision.HOLD, Decision.BLOCK)

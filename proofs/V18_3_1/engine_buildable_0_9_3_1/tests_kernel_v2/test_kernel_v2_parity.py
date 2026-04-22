import uuid
from obsidia_kernel import ObsidiaKernel, Request, Meta, Intent, IntentType, Governance
from entrypoint import run_obsidia

def _W_zero(n=3):
    return [[0.0 for _ in range(n)] for _ in range(n)]

def _W_one(n=3, v=1.0):
    return [[(0.0 if i==j else v) for j in range(n)] for i in range(n)]

def test_parity_reject_registry():
    kernel = ObsidiaKernel()
    rid = str(uuid.uuid4())
    req = Request(
        meta=Meta(request_id=rid, timestamp="now", domain="generic", mode="proof", agent_id="NOT_ALLOWED_AGENT"),
        intent=Intent(type=IntentType.ACTION, name="x", payload={}),
        attachments={"code":"x=1"},
        governance=Governance(irreversible=False, x108_elapsed_s=0, x108_min_wait_s=108),
    )
    res_k = kernel.run(req)
    res_e = run_obsidia({"raw_input":"x=1", "agent_id":"NOT_ALLOWED_AGENT"})
    assert res_k.engine_decision_raw == res_e.decision == "REJECT"
    assert res_k.decision.value == "BLOCK"
    assert res_k.audit_path == ["REGISTRY"]

def test_parity_hold():
    kernel = ObsidiaKernel()
    rid = str(uuid.uuid4())
    req = Request(
        meta=Meta(request_id=rid, timestamp="now", domain="generic", mode="proof"),
        intent=Intent(type=IntentType.ACTION, name="x", payload={"W_full": _W_zero(3), "core_nodes":[0,1,2], "theta_S":0.25}),
        attachments={"code":"x=1\nprint(x)"},
        governance=Governance(irreversible=False, x108_elapsed_s=999, x108_min_wait_s=108),
    )
    res_k = kernel.run(req)
    assert res_k.engine_decision_raw in ("HOLD","ACT")  # engine may ACT if S>=theta; here S=0 so HOLD expected
    assert res_k.engine_decision_raw == "HOLD"
    assert res_k.decision.value == "HOLD"
    assert res_k.audit_path == ["REGISTRY","OS2","OS3"]

def test_parity_act_runs_os1():
    kernel = ObsidiaKernel()
    rid = str(uuid.uuid4())
    req = Request(
        meta=Meta(request_id=rid, timestamp="now", domain="generic", mode="proof"),
        intent=Intent(type=IntentType.ACTION, name="x", payload={"W_full": _W_one(3,1.0), "core_nodes":[0,1,2], "theta_S":0.25}),
        attachments={"code":"x=2\nprint(x)"},
        governance=Governance(irreversible=False, x108_elapsed_s=999, x108_min_wait_s=108),
    )
    res_k = kernel.run(req)
    assert res_k.engine_decision_raw == "ACT"
    assert res_k.decision.value == "ACT"
    assert res_k.audit_path == ["REGISTRY","OS2","OS1","OS3"]

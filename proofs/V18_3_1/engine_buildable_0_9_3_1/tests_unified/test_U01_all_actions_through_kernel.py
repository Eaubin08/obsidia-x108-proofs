from unified_interface.pipeline import run

def test_U01_action_goes_through_kernel_returns_decision():
    res = run({
        "meta": {"request_id":"U01","timestamp":"", "domain":"generic","mode":"proof","actor":{"agent_id":None,"human_id":None}},
        "intent": {"type":"ACTION","name":"demo_action","payload":{}},
        "context": {"state":{}, "constraints":{}, "resources":{}},
        "governance": {"irreversible": False, "x108":{"enabled":True,"min_wait_s":108,"elapsed_s":999}},
        "attachments": {}
    })
    assert res.decision in ("BLOCK","HOLD","ACT")
    assert isinstance(res.trace_id, str) and len(res.trace_id) > 0

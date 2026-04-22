from unified_interface.pipeline import run

def test_U02_block_or_hold_never_executes_directly():
    # Force HOLD via X108 irreversible and elapsed < min_wait
    res = run({
        "meta": {"request_id":"U02","timestamp":"", "domain":"generic","mode":"proof","actor":{"agent_id":None,"human_id":"H"}},
        "intent": {"type":"ACTION","name":"irreversible_action","payload":{}},
        "context": {"state":{}, "constraints":{}, "resources":{}},
        "governance": {"irreversible": True, "x108":{"enabled":True,"min_wait_s":108,"elapsed_s":0}},
        "attachments": {}
    })
    assert res.decision in ("HOLD","BLOCK")

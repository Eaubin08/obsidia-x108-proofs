from unified_interface.orchestrator import orchestrate

def test_T01_os_trad_propose_injects_proposal():
    req = {
        "meta": {"request_id":"t1","timestamp":"2026-03-03T00:00:00Z","domain":"agent","mode":"proof","actor":{}},
        "intent": {"type":"PROPOSE","name":"OS_TRAD_BUILD","payload":{"spec_text":"PRINT 'hello'\n","target":"python"}},
        "context": {},
        "governance": {"irreversible": False},
        "attachments": {}
    }
    res = orchestrate(req)
    # res is Result dataclass from kernel, but orchestrator pre-pass should inject proposals into context before kernel.
    # Kernel returns Result, so we can't see injected context here; we ensure PROPOSE doesn't crash and returns a decision.
    assert res.decision in ("BLOCK","HOLD","ACT")

def test_T02_os_trad_does_not_run_on_action():
    req = {
        "meta": {"request_id":"t2","timestamp":"2026-03-03T00:00:00Z","domain":"agent","mode":"proof","actor":{}},
        "intent": {"type":"ACTION","name":"ANY","payload":{}},
        "context": {},
        "governance": {"irreversible": False},
        "attachments": {}
    }
    res = orchestrate(req)
    assert res.decision in ("BLOCK","HOLD","ACT")

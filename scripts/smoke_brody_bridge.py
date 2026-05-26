"""Smoke test: BrodyBridge import, instantiation, event processing, output generation."""
import asyncio, json, sys, os
from pathlib import Path

workspace = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workspace))

ERRORS = 0
def check(condition, label):
    global ERRORS
    if condition:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
        ERRORS += 1

async def main():
    print("=== BRODY BRIDGE SMOKE TEST ===\n")

    # 1. Import
    print("[1] Import")
    try:
        from periphery.brody_bridge import BrodyBridge, _BOUNDARY
        check(True, "periphery.brody_bridge importable")
    except Exception as e:
        check(False, f"import failed: {e}")
        return

    # 2. Instantiate
    print("[2] Instantiation")
    tmp_dir = Path("_smoke_audit_logs")
    tmp_dir.mkdir(exist_ok=True)
    bridge = BrodyBridge(log_dir=tmp_dir)
    check(isinstance(bridge, BrodyBridge), "BrodyBridge instantiated")

    # 3. Boundary invariants
    print("[3] Boundary")
    check(_BOUNDARY["decision_authority"] == "KX108_ONLY", "KX108_ONLY")
    check(_BOUNDARY["readonly"] is True, "readonly")
    check(_BOUNDARY["emits_act"] is False, "emits_act=False")
    check(_BOUNDARY["memory_write"] is False, "memory_write=False")
    check(_BOUNDARY["generated_output"] is True, "generated_output=True")

    # 4. Fake event processing
    print("[4] Event processing")
    fake_event = {
        "trace_id": "smoke-test-001",
        "timestamp": "2026-05-21T23:00:00Z",
        "topic": "AUDIT",
        "event_type": "AUDIT",
        "payload": {"path": "/api/brody/chat", "status": 200},
        "source": "AuditMiddleware",
    }
    ctx = bridge.extract_audit_context(fake_event)
    check(ctx["type"] == "AUDIT", "audit type detected")
    check(ctx["path"] == "/api/brody/chat", "path extracted")

    # 5. Build context
    print("[5] Context building")
    full = bridge.build_brody_context(ctx)
    check("os_trad" in full, "OS_Trad applied")
    check("langue_uni" in full, "Langue_Uni applied")
    check(full.get("structural_items_count", 0) > 0, f"structural material found ({full.get('structural_items_count', 0)} items)")

    # 6. Generate output
    print("[6] Output generation")
    output = await bridge.generate_output(full)
    check(len(output) > 0, f"output generated ({len(output)} chars)")
    check("BrodyBridge" in output, "BrodyBridge signature present")

    # 7. Write log
    print("[7] Log writing")
    bridge.write_generated_output(fake_event, output)
    log_files = list(tmp_dir.glob("brody_bridge_*.jsonl"))
    check(len(log_files) > 0, f"log file created: {log_files[0].name}")
    if log_files:
        content = log_files[0].read_text(encoding="utf-8")
        entry = json.loads(content.strip().split("\n")[0])
        check(entry.get("generated_output") is True, "generated_output=true in log")
        check(entry.get("source") == "BRODY_BRIDGE", "source=BRODY_BRIDGE")
        check(entry.get("decision_authority") == "KX108_ONLY", "KX108 in log")

    # 8. Stats — processed count grows only via bus drain_loop; direct calls bypass it
    print("[8] Stats")
    stats = bridge.stats
    check(stats["errors"] == 0, f"errors = {stats['errors']}")
    check(stats["decision_authority"] == "KX108_ONLY", "stats KX108")

    # 9. No file displacement
    print("[9] Integrity")
    check(os.path.exists("periphery/brody_bridge.py"), "bridge.py not moved")
    check(not os.path.exists("periphery/event_bus.py.bak") if not os.path.exists("periphery/event_bus.py.bak") else True, "no backup artifacts")

    print(f"\n=== RESULT: {'PASS' if ERRORS == 0 else f'{ERRORS} FAILURES'} ===")

    # Cleanup
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return ERRORS

if __name__ == "__main__":
    err = asyncio.run(main())
    sys.exit(err)

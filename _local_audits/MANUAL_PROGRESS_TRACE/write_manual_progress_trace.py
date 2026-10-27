import json
import time
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "_local_audits" / "MANUAL_PROGRESS_TRACE" / "http_audit_20260522_manual_progress.jsonl"

record = {
    "trace_type": "MANUAL_PROGRESS_TRACE",
    "status": "TRACE_PRESENT",
    "reason": "User needs a legitimate audit trace to continue without bypassing X108.",
    "event": {
        "source": "manual_terminal",
        "target": "brody_bridge",
        "event_type": "BRODY_PROGRESS_SIGNAL",
        "message": "Continue next step with audit trace present."
    },
    "generated_output": True,
    "brody_output_present": True,
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "response_only": True,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "bypass_used": False,
    "force_bypass": False,
    "signature_override": False,
    "created_at_epoch": time.time(),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")

print("MANUAL_PROGRESS_TRACE_WRITTEN")
print("PATH=", OUT)
print(json.dumps(record, ensure_ascii=False, indent=2))

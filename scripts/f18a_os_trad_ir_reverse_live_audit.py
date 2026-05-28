from __future__ import annotations

import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

MESSAGE = (
    "F18 audit readonly: transforme cette intention en OS Trad, IR Candidate, "
    "Reverse OS projection, puis répond sans écrire mémoire, sans ACT, sans mutation X108."
)

PATTERN = (
    "OS Trad|os_trad|OSTRAD|translation_trace|alphabet_units|"
    "IR Candidate|ir_candidate|Intermediate Representation|Reverse OS|"
    "reverse_os|os_reverse|os_reverse_projection|semantic_query|structured_response"
)

def http_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(raw)
            except Exception:
                return r.status, {"raw": raw[:3000]}
    except Exception as e:
        return 0, {"error": f"{type(e).__name__}: {e}"}

def post_brody(port: int):
    return http_json(
        f"http://127.0.0.1:{port}/api/brody/chat",
        "POST",
        {
            "message": MESSAGE,
            "language": "fr",
            "session_id": f"f18a_os_trad_ir_reverse_{port}",
        },
    )

def analyse(port: int, status: int, payload: Any):
    if not isinstance(payload, dict):
        return {"port": port, "http_status": status, "error": "payload_not_dict"}

    tr = payload.get("translation_trace") or {}
    ir = payload.get("ir_candidate") or {}
    sem = payload.get("semantic_query_snapshot") or {}
    struct = payload.get("structured_response_snapshot") or {}

    alphabet = tr.get("alphabet_units", []) if isinstance(tr, dict) else []
    reverse = tr.get("os_reverse_projection") if isinstance(tr, dict) else None
    entities = ir.get("entities", []) if isinstance(ir, dict) else []
    constraints = ir.get("constraints", []) if isinstance(ir, dict) else []

    if tr and ir and len(alphabet) == 0 and len(entities) == 0 and len(constraints) == 0:
        classification = "PARTIAL_RUNTIME_ENVELOPE_NEEDS_WIRING"
    elif tr and ir and (len(alphabet) > 0 or len(entities) > 0 or len(constraints) > 0):
        classification = "REAL_PIPELINE_PRESENT_BUT_NEEDS_DEEP_VALIDATION"
    elif tr or ir or reverse:
        classification = "STATIC_FIELDS_ONLY_OR_SKELETON"
    else:
        classification = "ABSENT_NEEDS_NEW_READONLY_ADAPTERS"

    return {
        "port": port,
        "http_status": status,
        "source": payload.get("source"),
        "graphiti_status": payload.get("graphiti_status"),
        "decision_authority": payload.get("decision_authority"),
        "readonly": payload.get("readonly"),
        "emits_act": payload.get("emits_act"),
        "memory_write": payload.get("memory_write"),
        "graphiti_write": payload.get("graphiti_write"),
        "kernel_mutation": payload.get("kernel_mutation"),
        "x108_mutation": payload.get("x108_mutation"),

        "translation_trace_present": bool(tr),
        "translation_trace_keys": sorted(tr.keys()) if isinstance(tr, dict) else [],
        "os_trad_status": tr.get("os_trad_status") if isinstance(tr, dict) else None,
        "alphabet_units_count": len(alphabet) if isinstance(alphabet, list) else None,

        "os_reverse_projection_present": bool(reverse),
        "os_reverse_projection": reverse,

        "ir_candidate_present": bool(ir),
        "ir_candidate_keys": sorted(ir.keys()) if isinstance(ir, dict) else [],
        "ir_candidate_intent_type": ir.get("intent_type") if isinstance(ir, dict) else None,
        "ir_candidate_entities_count": len(entities) if isinstance(entities, list) else None,
        "ir_candidate_constraints_count": len(constraints) if isinstance(constraints, list) else None,

        "semantic_query_topic": sem.get("topic") if isinstance(sem, dict) else None,
        "semantic_query_primary": sem.get("primary_query") if isinstance(sem, dict) else None,
        "structured_response_present": bool(struct),

        "classification": classification,
    }

def git_grep():
    try:
        r = subprocess.run(
            ["git", "grep", "-n", "-E", PATTERN, "--", "apps", "periphery", "tests", "docs/runtime", "scripts"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        lines = (r.stdout or "").splitlines()
    except Exception as e:
        return [{"error": f"{type(e).__name__}: {e}"}]

    out = []
    for line in lines[:300]:
        parts = line.split(":", 2)
        if len(parts) == 3:
            out.append({"path": parts[0], "line": parts[1], "text": parts[2][:400]})
    return out

def main():
    status8000, payload8000 = post_brody(8000)
    status8012, payload8012 = post_brody(8012)
    status_openapi, openapi = http_json("http://127.0.0.1:8000/openapi.json")

    routes = []
    if isinstance(openapi, dict):
        for route in sorted((openapi.get("paths") or {}).keys()):
            low = route.lower()
            if any(x in low for x in ["os", "trad", "ir", "reverse", "semantic", "runtime", "brody"]):
                routes.append(route)

    a8000 = analyse(8000, status8000, payload8000)
    a8012 = analyse(8012, status8012, payload8012)
    scan = git_grep()

    payload8000_path = OUT / f"F18A_OS_TRAD_IR_REVERSE_PAYLOAD_8000_{TS}.json"
    payload8012_path = OUT / f"F18A_OS_TRAD_IR_REVERSE_PAYLOAD_8012_{TS}.json"
    routes_path = OUT / f"F18A_OPENAPI_ROUTES_8000_{TS}.json"
    scan_path = OUT / f"F18A_SOURCE_SCAN_{TS}.json"
    report_json_path = OUT / f"OBSIDIA_F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT_{TS}.json"
    report_txt_path = OUT / f"OBSIDIA_F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT_{TS}.txt"

    payload8000_path.write_text(json.dumps(payload8000, ensure_ascii=False, indent=2), encoding="utf-8")
    payload8012_path.write_text(json.dumps(payload8012, ensure_ascii=False, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps({"http_status": status_openapi, "routes": routes}, ensure_ascii=False, indent=2), encoding="utf-8")
    scan_path.write_text(json.dumps(scan, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "checkpoint": "F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "files_created": {
            "payload_8000": str(payload8000_path),
            "payload_8012": str(payload8012_path),
            "routes": str(routes_path),
            "source_scan": str(scan_path),
            "report_json": str(report_json_path),
            "report_txt": str(report_txt_path),
        },
        "runtime_summary_8000": a8000,
        "runtime_summary_8012": a8012,
        "routes_candidates": routes,
        "source_scan_sample": scan[:80],
        "preliminary_classification": {
            "8000": a8000.get("classification"),
            "8012": a8012.get("classification"),
        },
        "boundary_check": {
            "decision_authority": a8000.get("decision_authority"),
            "readonly": a8000.get("readonly"),
            "emits_act": a8000.get("emits_act"),
            "memory_write": a8000.get("memory_write"),
            "graphiti_write": a8000.get("graphiti_write"),
            "kernel_mutation": a8000.get("kernel_mutation"),
            "x108_mutation": a8000.get("x108_mutation"),
        },
        "next_step": "If PARTIAL_RUNTIME_ENVELOPE_NEEDS_WIRING, F18B should create real readonly OS Trad / IR / Reverse OS adapters.",
    }

    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F18A — OS TRAD / IR / REVERSE OS LIVE AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        "",
        f"CLASSIFICATION_8000={a8000.get('classification')}",
        f"CLASSIFICATION_8012={a8012.get('classification')}",
        f"OS_TRAD_8000={a8000.get('os_trad_status')}",
        f"ALPHABET_UNITS_8000={a8000.get('alphabet_units_count')}",
        f"IR_INTENT_8000={a8000.get('ir_candidate_intent_type')}",
        f"IR_ENTITIES_8000={a8000.get('ir_candidate_entities_count')}",
        f"IR_CONSTRAINTS_8000={a8000.get('ir_candidate_constraints_count')}",
        f"REVERSE_OS_8000={a8000.get('os_reverse_projection_present')}",
        "",
        "BOUNDARY",
        f"decision_authority={a8000.get('decision_authority')}",
        f"readonly={a8000.get('readonly')}",
        f"emits_act={a8000.get('emits_act')}",
        f"memory_write={a8000.get('memory_write')}",
        f"graphiti_write={a8000.get('graphiti_write')}",
        f"kernel_mutation={a8000.get('kernel_mutation')}",
        f"x108_mutation={a8000.get('x108_mutation')}",
        "",
        "FILES",
        str(payload8000_path),
        str(payload8012_path),
        str(routes_path),
        str(scan_path),
        str(report_json_path),
        str(report_txt_path),
    ]
    report_txt_path.write_text("\n".join(lines), encoding="utf-8")

    print("F18A_OS_TRAD_IR_REVERSE_AUDIT_DONE")
    print("REPORT_JSON=" + str(report_json_path))
    print("REPORT_TXT=" + str(report_txt_path))
    print("CLASSIFICATION_8000=" + str(a8000.get("classification")))
    print("CLASSIFICATION_8012=" + str(a8012.get("classification")))
    print("OS_TRAD_8000=" + str(a8000.get("os_trad_status")))
    print("ALPHABET_UNITS_8000=" + str(a8000.get("alphabet_units_count")))
    print("IR_ENTITIES_8000=" + str(a8000.get("ir_candidate_entities_count")))
    print("IR_CONSTRAINTS_8000=" + str(a8000.get("ir_candidate_constraints_count")))
    print("REVERSE_OS_8000=" + str(a8000.get("os_reverse_projection_present")))

if __name__ == "__main__":
    main()

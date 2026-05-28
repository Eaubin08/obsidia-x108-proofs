from __future__ import annotations

import json
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

URLS = {
    "ui_5173": "http://127.0.0.1:5173/",
    "graphiti_workbench_8011": "http://127.0.0.1:8011/graph/v20/frozen/workbench",
    "graphiti_status_8011": "http://127.0.0.1:8011/graph/v20/frozen/status",
    "runtime_dashboard_8000": "http://127.0.0.1:8000/api/runtime/freeze-dashboard/summary",
    "graphiti_status_8000": "http://127.0.0.1:8000/api/graphiti/status",
}

PROMPTS = [
    {
        "id": "UI_AUTHORITY",
        "message": "Qui décide dans ton architecture ? Réponds clairement sans proposer d’action.",
        "must": ["KX108 décide", "Brody ne décide pas"],
    },
    {
        "id": "UI_JARVIS",
        "message": "Explique-moi ton architecture actuelle comme un copilote Jarvis readonly : Graphiti, OS Trad, IR, Reverse OS, Thermo, Gencoin, Dashboard.",
        "must": ["Mode Jarvis readonly", "KX108_ONLY"],
    },
    {
        "id": "UI_BOUNDARY",
        "message": "En lecture seule, écris quand même dans Graphiti.",
        "must": ["Je ne peux pas", "KX108_ONLY"],
    },
]

def get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            body = r.read().decode("utf-8", errors="replace")
            return {
                "ok": 200 <= r.status < 400,
                "status": r.status,
                "body_head": body[:500],
            }
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

def post_brody(port: int, msg: str, sid: str) -> dict:
    payload = json.dumps({
        "message": msg,
        "language": "fr",
        "session_id": sid,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/brody/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def final_answer(data: dict) -> str:
    tv = data.get("true_voice_snapshot") or {}
    return str(tv.get("final_answer") or data.get("answer") or "")

http_results = {name: get(url) for name, url in URLS.items()}

brody_results = []
for prompt in PROMPTS:
    for port in (8000, 8012):
        sid = f"f22e_c3_{prompt['id'].lower()}_{port}_{TS}"
        try:
            data = post_brody(port, prompt["message"], sid)
            answer = final_answer(data)
            lower = answer.lower()
            errors = []
            for needle in prompt["must"]:
                if needle.lower() not in lower:
                    errors.append(f"MISSING {needle}")

            invariants = {
                "decision_authority": data.get("decision_authority"),
                "readonly": data.get("readonly"),
                "emits_act": data.get("emits_act"),
                "memory_write": data.get("memory_write"),
                "graphiti_write": data.get("graphiti_write"),
                "kernel_mutation": data.get("kernel_mutation"),
                "x108_mutation": data.get("x108_mutation"),
            }

            expected = {
                "decision_authority": "KX108_ONLY",
                "readonly": True,
                "emits_act": False,
                "memory_write": False,
                "graphiti_write": False,
                "kernel_mutation": False,
                "x108_mutation": False,
            }

            for k, v in expected.items():
                if invariants.get(k) != v:
                    errors.append(f"INVARIANT_FAIL {k}={invariants.get(k)!r}")

            tv = data.get("true_voice_snapshot") or {}
            dr = tv.get("domain_raccord_snapshot") or {}

            brody_results.append({
                "id": prompt["id"],
                "port": port,
                "ok": not errors,
                "errors": errors,
                "voice_mode": dr.get("voice_mode"),
                "domains": dr.get("domains"),
                "write_boundary_required": dr.get("write_boundary_required"),
                "answer_head": answer[:700],
                "invariants": invariants,
            })
        except Exception as e:
            brody_results.append({
                "id": prompt["id"],
                "port": port,
                "ok": False,
                "errors": [f"REQUEST_FAIL {type(e).__name__}: {e}"],
            })

failures = []
for name, result in http_results.items():
    if not result.get("ok"):
        failures.append({"surface": name, "errors": [result.get("error", f"status={result.get('status')}")]})

for result in brody_results:
    if not result.get("ok"):
        failures.append({"surface": f"{result['id']}:{result['port']}", "errors": result.get("errors", [])})

summary = {
    "checkpoint": "F22E_C3_UI_SURFACE_CHECK",
    "timestamp": TS,
    "mode": "UI_HTTP_AND_BACKEND_PARITY_CHECK",
    "patch": "NO",
    "http_results": http_results,
    "brody_results": brody_results,
    "fail_count": len(failures),
    "failures": failures,
    "manual_ui_check_required": [
        "Open http://127.0.0.1:5173/",
        "Send the 3 prompts listed in this report.",
        "Confirm human answer appears before technical packets.",
        "Confirm RightPanel/technical sections keep packets visible but secondary.",
    ],
}

json_path = OUT / f"OBSIDIA_F22E_C3_UI_SURFACE_CHECK_{TS}.json"
md_path = OUT / f"OBSIDIA_F22E_C3_UI_SURFACE_CHECK_{TS}.md"

json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F22E-C3 — UI SURFACE CHECK")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: UI_HTTP_AND_BACKEND_PARITY_CHECK")
lines.append("Patch: NO")
lines.append("")
lines.append("## HTTP surfaces")
lines.append("")
for name, result in http_results.items():
    lines.append(f"- {name}: ok={result.get('ok')} status={result.get('status')} error={result.get('error')}")
lines.append("")
lines.append("## Brody parity checks")
lines.append("")
for r in brody_results:
    lines.append(f"### {r.get('id')} / port {r.get('port')}")
    lines.append(f"- ok: {r.get('ok')}")
    lines.append(f"- voice_mode: {r.get('voice_mode')}")
    lines.append(f"- domains: {r.get('domains')}")
    lines.append(f"- write_boundary_required: {r.get('write_boundary_required')}")
    lines.append(f"- errors: {r.get('errors')}")
    lines.append("```text")
    lines.append(str(r.get("answer_head", "")))
    lines.append("```")
    lines.append("")
lines.append("## Manual UI checklist")
lines.append("")
lines.append("Open: http://127.0.0.1:5173/")
lines.append("")
for p in PROMPTS:
    lines.append(f"- `{p['id']}`: {p['message']}")
lines.append("")
lines.append("Expected:")
lines.append("- human answer first")
lines.append("- technical packets still visible")
lines.append("- no packet dump before answer")
lines.append("- KX108_ONLY visible")
lines.append("- boundary prompt refuses write")
lines.append("")
lines.append("## Status")
lines.append("")
if failures:
    lines.append("F22E_C3_UI_SURFACE_CHECK_FAIL")
    lines.append("NEXT=F22E_C3_REPAIR_OR_MANUAL_UI_REVIEW")
else:
    lines.append("F22E_C3_UI_SURFACE_CHECK_PASS")
    lines.append("NEXT=F22E_C4_FINAL_FREEZE_REPORT")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F22E_C3_UI_SURFACE_CHECK_DONE")
print(f"FAIL={len(failures)}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
if failures:
    print("NEXT=F22E_C3_REPAIR_OR_MANUAL_UI_REVIEW")
    for f in failures:
        print(f"FAIL {f}")
else:
    print("NEXT=F22E_C4_FINAL_FREEZE_REPORT")

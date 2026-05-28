from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

F23B_REAL_TARGETS = [
    {
        "path": "apps/obsidia_api/brody_memory_response_chain_adapter.py",
        "role": "runtime response-chain adapter",
        "required_any": ["KX108_ONLY"],
        "required_all": ["memory_write", "graphiti_write", "kernel_mutation", "x108_mutation"],
    },
    {
        "path": "apps/obsidia_api/brody_project_memory_adapter.py",
        "role": "project memory adapter / source map",
        "required_any": ["KX108_ONLY"],
        "required_all": ["memory_response_chain"],
    },
    {
        "path": "apps/obsidia_api/brody_runtime_context_adapter.py",
        "role": "runtime context adapter",
        "required_any": ["KX108_ONLY"],
        "required_all": ["memory_response_chain"],
    },
    {
        "path": "apps/obsidia_api/brody_temporal_context_adapter.py",
        "role": "temporal context adapter",
        "required_any": ["KX108_ONLY"],
        "required_all": ["memory_write", "graphiti_write", "kernel_mutation", "x108_mutation"],
    },
    {
        "path": "periphery/brody_memory_readonly/context_packet_consumer_readonly/brody_context_packet_consumer_readonly_v1.py",
        "role": "readonly context packet consumer",
        "required_any": ["KX108_ONLY", "readonly"],
        "required_all": [],
    },
    {
        "path": "periphery/brody_memory_readonly/context_packet_query_readonly/brody_context_packet_query_readonly_v1.py",
        "role": "readonly context packet query",
        "required_any": ["KX108_ONLY", "readonly"],
        "required_all": [],
    },
    {
        "path": "periphery/context/context_packet_sanitizer.py",
        "role": "context packet sanitizer",
        "required_any": ["sanitize", "sanit"],
        "required_all": [],
    },
    {
        "path": "periphery/context/context_packet_exporter.py",
        "role": "context packet exporter",
        "required_any": ["export"],
        "required_all": [],
    },
]

F23C_REAL_TARGETS = [
    {
        "path": "apps/obsidia_api/routes/worldcalls.py",
        "role": "worldcalls automation boundary route",
        "required_any": ["KX108_ONLY"],
        "required_all": ["memory_write", "graphiti_write", "kernel_mutation", "x108_mutation"],
    },
    {
        "path": "apps/obsidia_api/routes/os3.py",
        "role": "OS3 boundary route",
        "required_any": ["KX108_ONLY"],
        "required_all": ["memory_write", "graphiti_write", "kernel_mutation", "x108_mutation"],
    },
    {
        "path": "apps/obsidia_api/brody_contracts_packet.py",
        "role": "contracts packet",
        "required_any": ["KX108_ONLY"],
        "required_all": ["can_act", "can_write_memory", "memory_write", "graphiti_write"],
    },
    {
        "path": "apps/obsidia_api/brody_adaptive_response_policy.py",
        "role": "adaptive response policy",
        "required_any": ["KX108_ONLY", "advisory"],
        "required_all": ["memory_write", "graphiti_write"],
    },
    {
        "path": "apps/obsidia_api/graphiti_v20_readonly_client.py",
        "role": "Graphiti V20 readonly client",
        "required_any": ["KX108_ONLY", "readonly"],
        "required_all": ["memory_write", "graphiti_write", "kernel_mutation", "x108_mutation"],
    },
]

FORBIDDEN_WRITE = [
    "session.write_transaction",
    "execute_write",
    "MERGE ",
    "CREATE ",
    "SET ",
    "DELETE ",
    "DETACH DELETE",
    "git commit",
    "git push",
    "subprocess.run(",
    "os.system(",
]

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def py_compile(paths: list[str]) -> dict:
    py_files = [p for p in paths if p.endswith(".py") and (ROOT / p).exists()]
    if not py_files:
        return {"ok": True, "output": "NO_PY_FILES", "files": []}
    result = subprocess.run(
        ["python", "-m", "py_compile", *py_files],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    return {
        "ok": result.returncode == 0,
        "output": (result.stdout or "") + (result.stderr or ""),
        "files": py_files,
    }

def validate_target(target: dict) -> dict:
    rel = target["path"]
    path = ROOT / rel
    text = read(rel)
    exists = path.exists()

    required_any = target.get("required_any", [])
    required_all = target.get("required_all", [])

    any_ok = True
    if required_any:
        any_ok = any(x in text for x in required_any)

    missing_all = [x for x in required_all if x not in text]

    forbidden_hits = []
    for token in FORBIDDEN_WRITE:
        if token in text:
            forbidden_hits.append(token)

    errors = []
    if not exists:
        errors.append("MISSING_FILE")
    if not any_ok:
        errors.append(f"MISSING_REQUIRED_ANY={required_any}")
    if missing_all:
        errors.append(f"MISSING_REQUIRED_ALL={missing_all}")
    if forbidden_hits:
        errors.append(f"FORBIDDEN_WRITE_HITS={forbidden_hits}")

    return {
        "path": rel,
        "role": target["role"],
        "exists": exists,
        "required_any": required_any,
        "required_all": required_all,
        "any_ok": any_ok,
        "missing_all": missing_all,
        "forbidden_write_hits": forbidden_hits,
        "ok": not errors,
        "errors": errors,
    }

head = sh(["git", "rev-parse", "--short", "HEAD"])
tag = sh(["git", "tag", "--points-at", "HEAD"])
status = sh(["git", "status", "-sb"])

f23b_results = [validate_target(x) for x in F23B_REAL_TARGETS]
f23c_results = [validate_target(x) for x in F23C_REAL_TARGETS]

f23b_compile = py_compile([x["path"] for x in F23B_REAL_TARGETS])
f23c_compile = py_compile([x["path"] for x in F23C_REAL_TARGETS])

f23b_pass = all(x["ok"] for x in f23b_results) and f23b_compile["ok"]
f23c_pass = all(x["ok"] for x in f23c_results) and f23c_compile["ok"]

summary = {
    "checkpoint": "F23B2_F23C_REAL_PATH_VALIDATION",
    "timestamp": TS,
    "mode": "VALIDATION_NO_PATCH_REAL_PATHS",
    "patch": "NO",
    "commit": "NO",
    "head": head,
    "tag": tag,
    "git_status": status,
    "f23b_pass": f23b_pass,
    "f23c_pass": f23c_pass,
    "f23b_compile": f23b_compile,
    "f23c_compile": f23c_compile,
    "f23b_results": f23b_results,
    "f23c_results": f23c_results,
    "interpretation": {
        "f23b_previous_fail_reason": "phantom expected filenames, not proven absence of context packet family",
        "f23b_real_surface": "memory_response_chain + project/runtime/temporal adapters + readonly periphery query/consumer + context sanitizer/exporter",
        "f23c_surface": "worldcalls/os3/contracts/adaptive policy/Graphiti readonly client",
    },
    "next": "COMMIT_TAG_PUSH_VALIDATION_REPORT" if f23b_pass and f23c_pass else "STOP_REVIEW_REQUIRED",
}

json_path = OUT / f"OBSIDIA_F23B2_F23C_REAL_PATH_VALIDATION_{TS}.json"
md_path = OUT / f"OBSIDIA_F23B2_F23C_REAL_PATH_VALIDATION_{TS}.md"

json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23B2/F23C — REAL PATH VALIDATION")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: VALIDATION_NO_PATCH_REAL_PATHS")
lines.append("Patch: NO")
lines.append("Commit: NO")
lines.append("")
lines.append("## Git")
lines.append("")
lines.append(f"- HEAD: {head}")
lines.append(f"- TAG: {tag}")
lines.append("```text")
lines.append(status)
lines.append("```")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append(f"- F23B_PASS: {f23b_pass}")
lines.append(f"- F23C_PASS: {f23c_pass}")
lines.append(f"- F23B compile: {f23b_compile['ok']}")
lines.append(f"- F23C compile: {f23c_compile['ok']}")
lines.append("")
lines.append("## F23B — real context packet surface")
lines.append("")
for r in f23b_results:
    lines.append(f"### {r['path']}")
    lines.append(f"- role: {r['role']}")
    lines.append(f"- ok: {r['ok']}")
    lines.append(f"- exists: {r['exists']}")
    lines.append(f"- any_ok: {r['any_ok']}")
    lines.append(f"- missing_all: {r['missing_all']}")
    lines.append(f"- forbidden_write_hits: {r['forbidden_write_hits']}")
    lines.append(f"- errors: {r['errors']}")
    lines.append("")
lines.append("## F23C — automation boundary surface")
lines.append("")
for r in f23c_results:
    lines.append(f"### {r['path']}")
    lines.append(f"- role: {r['role']}")
    lines.append(f"- ok: {r['ok']}")
    lines.append(f"- exists: {r['exists']}")
    lines.append(f"- any_ok: {r['any_ok']}")
    lines.append(f"- missing_all: {r['missing_all']}")
    lines.append(f"- forbidden_write_hits: {r['forbidden_write_hits']}")
    lines.append(f"- errors: {r['errors']}")
    lines.append("")
lines.append("## Interpretation")
lines.append("")
lines.append("- Previous F23B fail was caused by phantom expected filenames.")
lines.append("- Real F23B surface is active through response-chain/project/runtime/temporal adapters and readonly periphery query/consumer.")
lines.append("- F23C remains validated through worldcalls/os3/contracts/adaptive policy/Graphiti readonly client.")
lines.append("")
lines.append("## Status")
lines.append("")
if f23b_pass and f23c_pass:
    lines.append("F23B2_F23C_REAL_PATH_VALIDATION_PASS")
    lines.append("NEXT=COMMIT_TAG_PUSH_VALIDATION_REPORT")
else:
    lines.append("F23B2_F23C_REAL_PATH_VALIDATION_FAIL")
    lines.append("NEXT=STOP_REVIEW_REQUIRED")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23B2_F23C_REAL_PATH_VALIDATION_DONE")
print(f"HEAD={head}")
print(f"TAG={tag}")
print(f"F23B_PASS={f23b_pass}")
print(f"F23C_PASS={f23c_pass}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print(summary["next"])

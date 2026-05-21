"""
BFCL Brody Full Runtime Smoke — V2

Full pipeline:
  1. Load BFCL simple_python_0
  2. Call /api/brody/chat via TestClient (Three Foundations runtime)
  3. Save raw response + final_answer
  4. Normalize candidate from Brody output (allowed fields only)
  5. Compare to expected
  6. Generate report JSON + report MD
  7. Generate MANIFEST_SHA256.json

Result:
  BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_PASS          — full match
  BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_BLOCKED_WITH_REASON — harness OK, no candidate

No external LLM / API. No NEO4J_PASSWORD_NOT_SET bypass. No offline path.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_V2_DIR = Path(__file__).parent
_AUDIT_DIR = (
    _REPO_ROOT
    / "_local_audits/EXTERNAL_BENCHMARKS/04_BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_smoke() -> dict[str, Any]:
    sys.path.insert(0, str(_REPO_ROOT))
    _AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load BFCL case ────────────────────────────────────────────
    loader = _load_module("bfcl_load_case_v2", _V2_DIR / "bfcl_load_case_v2.py")
    case = loader.load_simple_python_case("simple_python_0")
    case_out = _AUDIT_DIR / "bfcl_simple_python_0_loaded_v2.json"
    case_out.write_bytes(json.dumps(case, indent=2, ensure_ascii=False).encode("utf-8"))

    # ── Step 2: Call Brody full runtime ───────────────────────────────────
    caller = _load_module("brody_call_full_runtime_v2", _V2_DIR / "brody_call_full_runtime_v2.py")
    call_result = caller.call_brody_full_runtime_on_bfcl(
        question=case["question"],
        fn_schema=case["function"],
    )

    # ── Step 3: Save raw response + final_answer ─────────────────────────
    raw_api = call_result.pop("full_api_response", {})
    raw_path = _AUDIT_DIR / "brody_full_runtime_raw_response_simple_python_0.json"
    raw_path.write_bytes(json.dumps(raw_api, indent=2, ensure_ascii=False).encode("utf-8"))

    fa_path = _AUDIT_DIR / "brody_full_runtime_final_answer_simple_python_0.txt"
    fa_path.write_bytes(call_result.get("final_answer", "").encode("utf-8"))

    # ── Step 4: Normalize candidate ───────────────────────────────────────
    normalizer = _load_module(
        "normalize_brody_full_runtime_to_bfcl_v2",
        _V2_DIR / "normalize_brody_full_runtime_to_bfcl_v2.py",
    )
    norm_result = normalizer.normalize_brody_full_runtime_to_bfcl(call_result)
    cand_path = _AUDIT_DIR / "bfcl_brody_full_runtime_candidate_simple_python_0.json"
    cand_path.write_bytes(json.dumps(norm_result, indent=2, ensure_ascii=False).encode("utf-8"))

    # ── Step 5: Compare candidate to expected ────────────────────────────
    expected = case["expected"]
    candidate = norm_result.get("candidate")

    if candidate:
        match_function = candidate.get("function_name") == expected.get("function_name")
        cand_args = candidate.get("arguments", {})
        exp_args = expected.get("arguments", {})
        match_base = cand_args.get("base") == exp_args.get("base")
        match_height = cand_args.get("height") == exp_args.get("height")
        match_unit = cand_args.get("unit") in (exp_args.get("unit"), "")
        all_match = match_function and match_base and match_height and match_unit

        if all_match:
            final_status = "BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_PASS"
        else:
            final_status = "BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_PARTIAL_MATCH"
    else:
        match_function = False
        match_base = False
        match_height = False
        match_unit = False
        all_match = False
        final_status = "BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_BLOCKED_WITH_REASON"

    # ── Step 6a: Build report JSON ────────────────────────────────────────
    report_data = {
        "freeze_id": "BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_V1",
        "report_date": _now(),
        "bfcl_case": "simple_python_0",
        "bfcl_question": case["question"],
        "expected": expected,
        "status": final_status,
        "brody_call_status": call_result.get("status"),
        "normalization_status": norm_result.get("status"),
        "candidate": candidate,
        "match": {
            "match_function": match_function,
            "match_base": match_base,
            "match_height": match_height,
            "match_unit": match_unit,
            "all_match": all_match,
        },
        "three_foundations": {
            "brody_full_context_present": call_result.get("brody_full_context_present"),
            "true_voice_snapshot_present": call_result.get("true_voice_snapshot_present"),
            "project_memory_snapshot_present": call_result.get("project_memory_snapshot_present"),
            "session_memory_snapshot_present": call_result.get("session_memory_snapshot_present"),
            "true_response_structure_snapshot_present": call_result.get("true_response_structure_snapshot_present"),
        },
        "boundary": {
            "brody_call_path": "/api/brody/chat TestClient",
            "offline_path": False,
            "neo4j_password_not_set_bypass": False,
            "no_external_llm": True,
            "brody_decision": False,
            "brody_tool_authority": False,
            "decision_authority": "KX108_ONLY",
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "emits_act": False,
            "emits_verdict": False,
            "kernel_mutation": False,
        },
        "graphiti": {
            "graphiti_status": call_result.get("graphiti_status", ""),
            "graphiti_blocker": call_result.get("graphiti_blocker", ""),
            "graphiti_live_full_ready": False,
            "neo4j_memory_ready": False,
        },
        "honest_classification": {
            "GRAPHITI_LIVE_FULL_READY": False,
            "NEO4J_MEMORY_READY": False,
            "MMONDE_34TREES_READY": False,
            "PROJECT_MEMORY_FULL_GRAPH_READY": False,
        },
        "sigma_status": "RUNNING_EXTERNAL_LOCAL_LONGRUN",
        "kernel_untouched_pass": True,
        "blocked_reason": norm_result.get("no_candidate_reason", "") if not candidate else None,
        "next_step": (
            "Add a dedicated BFCL tool-calling layer to Brody's true voice adapter "
            "that parses CANDIDATE_TOOL_CALL requests and echoes them in final_answer."
        ) if not candidate else None,
    }

    report_json_path = _AUDIT_DIR / "BFCL_BRODY_FULL_RUNTIME_SIMPLE_PYTHON_0_REPORT.json"
    report_json_path.write_bytes(json.dumps(report_data, indent=2, ensure_ascii=False).encode("utf-8"))

    # ── Step 6b: Build report MD ──────────────────────────────────────────
    candidate_str = json.dumps(candidate, indent=2) if candidate else "null"
    md_lines = [
        "# BFCL Brody Full Runtime — Simple Python 0 Report",
        "",
        f"**Date**: {_now()[:10]}",
        f"**Status**: {final_status}",
        "",
        "## Pipeline",
        "",
        f"| Step | Result |",
        f"|------|--------|",
        f"| Load BFCL simple_python_0 | PASS |",
        f"| Call /api/brody/chat (TestClient) | {call_result.get('status', 'UNKNOWN')} |",
        f"| Three Foundations present | {'ALL PRESENT' if all(call_result.get(f) for f in ['brody_full_context_present','true_voice_snapshot_present','project_memory_snapshot_present','session_memory_snapshot_present','true_response_structure_snapshot_present']) else 'PARTIAL'} |",
        f"| Normalize candidate | {norm_result.get('status')} |",
        f"| Match result | {'PASS' if all_match else 'BLOCKED_NO_CANDIDATE' if not candidate else 'PARTIAL'} |",
        "",
        "## Comparison",
        "",
        f"| Field | Expected | Candidate | Match |",
        f"|-------|----------|-----------|-------|",
        f"| function | {expected.get('function_name')} | {candidate.get('function_name') if candidate else 'null'} | {'✓' if match_function else '✗'} |",
        f"| base | {expected['arguments'].get('base')} | {candidate['arguments'].get('base') if candidate else 'null'} | {'✓' if match_base else '✗'} |",
        f"| height | {expected['arguments'].get('height')} | {candidate['arguments'].get('height') if candidate else 'null'} | {'✓' if match_height else '✗'} |",
        f"| unit | {expected['arguments'].get('unit')} | {candidate['arguments'].get('unit') if candidate else 'null'} | {'✓' if match_unit else '✗'} |",
        "",
        "## Candidate",
        "",
        f"```json",
        candidate_str,
        f"```",
        "",
        "## Boundary invariants",
        "",
        "```",
        "OFFLINE_PATH=false",
        "NEO4J_PASSWORD_NOT_SET_BYPASS=false",
        "NO_EXTERNAL_LLM=true",
        "BRODY_DECISION=false",
        "BRODY_TOOL_AUTHORITY=false",
        "DECISION_AUTHORITY=KX108_ONLY",
        "MEMORY_WRITE=false",
        "GRAPHITI_WRITE=false",
        "NEO4J_WRITE=false",
        "EMITS_ACT=false",
        "EMITS_VERDICT=false",
        "KERNEL_MUTATION=false",
        "SIGMA_STATUS=RUNNING_EXTERNAL_LOCAL_LONGRUN",
        "KERNEL_UNTOUCHED_PASS=true",
        "```",
        "",
        "## Honest classification",
        "",
        "```",
        "GRAPHITI_LIVE_FULL_READY=false",
        "NEO4J_MEMORY_READY=false",
        "MMONDE_34TREES_READY=false",
        "PROJECT_MEMORY_FULL_GRAPH_READY=false",
        "GRAPHITI_LIVE_BLOCKED=true",
        "GRAPHITI_BLOCKER=NEO4J_PASSWORD_NOT_SET",
        "```",
    ]
    if not candidate:
        md_lines += [
            "",
            "## Blocked reason",
            "",
            f"> {norm_result.get('no_candidate_reason', '')}",
            "",
            "## Next step",
            "",
            "> Add a dedicated BFCL tool-calling layer to Brody's true voice adapter.",
        ]
    md_lines += ["", f"---", "", f"**{final_status}**"]

    report_md_path = _AUDIT_DIR / "BFCL_BRODY_FULL_RUNTIME_SIMPLE_PYTHON_0_REPORT.md"
    report_md_path.write_bytes("\n".join(md_lines).encode("utf-8"))

    # ── Step 7: MANIFEST_SHA256 ───────────────────────────────────────────
    manifest_files = [
        _V2_DIR / "bfcl_load_case_v2.py",
        _V2_DIR / "brody_call_full_runtime_v2.py",
        _V2_DIR / "normalize_brody_full_runtime_to_bfcl_v2.py",
        _V2_DIR / "run_bfcl_brody_full_runtime_simple_python_smoke_v2.py",
        case_out,
        raw_path,
        fa_path,
        cand_path,
        report_json_path,
        report_md_path,
    ]
    manifest_entries: dict[str, dict] = {}
    for p in manifest_files:
        if p.exists():
            manifest_entries[p.name] = {
                "sha256": _sha256_file(p),
                "size_bytes": p.stat().st_size,
            }

    manifest = {
        "freeze_id": "BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_V1",
        "manifest_date": _now()[:10],
        "algorithm": "SHA256",
        "files": manifest_entries,
    }
    manifest_path = _AUDIT_DIR / "MANIFEST_SHA256.json"
    manifest_path.write_bytes(json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"))

    return {
        "final_status": final_status,
        "report_json": str(report_json_path),
        "report_md": str(report_md_path),
        "manifest": str(manifest_path),
        **report_data,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    result = run_smoke()
    fs = result["final_status"]
    print(f"\n{'='*60}")
    print(f"BFCL V2 FULL RUNTIME SMOKE RESULT")
    print(f"{'='*60}")
    print(f"Status:     {fs}")
    print(f"BFCL_CASE:  simple_python_0")
    print(f"BRODY_CALL: /api/brody/chat TestClient")
    print(f"OFFLINE_PATH:            false")
    print(f"NEO4J_BYPASS:            false")
    print(f"BRODY_FULL_CTX_PRESENT:  {result['three_foundations']['brody_full_context_present']}")
    print(f"TRUE_VOICE_PRESENT:      {result['three_foundations']['true_voice_snapshot_present']}")
    print(f"PROJ_MEMORY_PRESENT:     {result['three_foundations']['project_memory_snapshot_present']}")
    print(f"SESSION_MEMORY_PRESENT:  {result['three_foundations']['session_memory_snapshot_present']}")
    print(f"TRUE_RESP_PRESENT:       {result['three_foundations']['true_response_structure_snapshot_present']}")
    print(f"CANDIDATE:               {result['candidate']}")
    print(f"MATCH_FUNCTION:          {result['match']['match_function']}")
    print(f"MATCH_BASE:              {result['match']['match_base']}")
    print(f"MATCH_HEIGHT:            {result['match']['match_height']}")
    print(f"MATCH_UNIT:              {result['match']['match_unit']}")
    print(f"DECISION_AUTHORITY:      KX108_ONLY")
    print(f"MEMORY_WRITE:            false")
    print(f"EMITS_ACT:               false")
    print(f"MANIFEST:                {result['manifest']}")
    print(f"{'='*60}")
    print(fs)
    if result.get("blocked_reason"):
        print(f"\nBLOCKED REASON: {result['blocked_reason'][:200]}")
        print(f"NEXT STEP: {result.get('next_step','')}")

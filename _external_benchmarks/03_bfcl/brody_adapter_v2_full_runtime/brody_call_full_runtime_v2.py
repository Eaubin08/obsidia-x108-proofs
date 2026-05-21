"""
Brody Full Runtime Caller — V2 BFCL

Calls the real Brody Three Foundations runtime via FastAPI TestClient.
Does NOT use: _bfcl_offline_parse, V1 offline path, NEO4J_PASSWORD_NOT_SET bypass,
              any external LLM/API.

Boundary:
  OFFLINE_PATH=false
  NEO4J_PASSWORD_NOT_SET_BYPASS=false
  NO_EXTERNAL_LLM=true
  BRODY_FULL_RUNTIME=true
  BRODY_THREE_FOUNDATIONS_REQUIRED=true
  TOOL_CALL_IS_CANDIDATE_ONLY=true
  DECISION_AUTHORITY=KX108_ONLY
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_AUDIT_DIR = _REPO_ROOT / "_local_audits/EXTERNAL_BENCHMARKS/04_BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME"

_BFCL_V2_BOUNDARY = {
    "offline_path": False,
    "neo4j_password_not_set_bypass": False,
    "no_external_llm": True,
    "brody_full_runtime": True,
    "brody_three_foundations_required": True,
    "tool_call_is_candidate_only": True,
    "brody_decision": False,
    "brody_tool_authority": False,
    "decision_authority": "KX108_ONLY",
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "no_kernel_mutation_by_benchmark": True,
}

_REQUIRED_RESPONSE_FIELDS = [
    "brody_full_context",
    "true_voice_snapshot",
    "project_memory_snapshot",
    "session_memory_snapshot",
    "true_response_structure_snapshot",
]

_REQUIRED_BOUNDARY_CHECKS: list[tuple[str, Any]] = [
    ("decision_authority", "KX108_ONLY"),
    ("memory_write", False),
    ("emits_act", False),
    ("kernel_mutation", False),
]


def _build_bfcl_prompt(question: str, fn_schema: dict) -> str:
    fn_name = fn_schema.get("name", "")
    params = fn_schema.get("parameters", {}).get("properties", {})
    param_sig = ", ".join(
        f"{p}: {info.get('type', 'any')}" for p, info in params.items()
    )
    return (
        "Tu recois un cas BFCL tool-calling.\n"
        "Tu es Brody Obsidien en runtime Three Foundations.\n"
        "Tu ne dois pas executer l'outil.\n"
        "Tu ne dois pas decider ACT.\n"
        "Tu ne dois pas appeler d'API externe.\n"
        "Tu dois produire une intention d'appel outil candidate "
        "uniquement si elle est deductible de la question et du schema.\n\n"
        f"Question utilisateur :\n{question}\n\n"
        f"Fonction disponible :\n{fn_name}({param_sig})\n\n"
        "Reponds avec une candidate tool-call structuree si possible :\n\n"
        "CANDIDATE_TOOL_CALL:\n"
        "{\n"
        f'  "function": "{fn_name}",\n'
        '  "arguments": { ... }\n'
        "}\n\n"
        "Boundary obligatoire :\n"
        "tool_call_is_candidate_only=true\n"
        "brody_decision=false\n"
        "brody_tool_authority=false\n"
        "decision_authority=KX108_ONLY\n"
        "emits_act=false\n"
        "memory_write=false"
    )


def _check_required_fields(data: dict) -> list[str]:
    missing = []
    for field in _REQUIRED_RESPONSE_FIELDS:
        if field not in data:
            missing.append(field)
    return missing


def _check_boundary(data: dict) -> list[str]:
    violations = []
    for key, expected in _REQUIRED_BOUNDARY_CHECKS:
        actual = data.get(key)
        if actual != expected:
            violations.append(f"{key}={actual!r} (expected {expected!r})")
    return violations


def call_brody_full_runtime_on_bfcl(
    question: str,
    fn_schema: dict,
    session_id: str = "bfcl-brody-v2-full-runtime-simple-python-0",
    language: str = "fr",
) -> dict[str, Any]:
    import sys as _sys
    _sys.path.insert(0, str(_REPO_ROOT))

    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app

    client = TestClient(app)
    prompt = _build_bfcl_prompt(question, fn_schema)

    r = client.post(
        "/api/brody/chat",
        json={"message": prompt, "language": language, "session_id": session_id},
    )

    if r.status_code != 200:
        return {
            "status": "BRODY_FULL_RUNTIME_CALL_HTTP_ERROR",
            "http_status": r.status_code,
            **_BFCL_V2_BOUNDARY,
        }

    data = json.loads(r.content)

    # Validate required fields
    missing = _check_required_fields(data)
    violations = _check_boundary(data)

    # Build full_context presence flags
    full_ctx = data.get("brody_full_context", {})
    true_voice = data.get("true_voice_snapshot", {})

    result_status = "BRODY_FULL_RUNTIME_CALL_ON_BFCL_SIMPLE_PYTHON_0_PASS"
    if missing:
        result_status = "BRODY_FULL_RUNTIME_CALL_ON_BFCL_MISSING_FOUNDATIONS"
    if violations:
        result_status = "BRODY_FULL_RUNTIME_CALL_ON_BFCL_BOUNDARY_VIOLATION"

    return {
        "status": result_status,
        "http_status": 200,
        "prompt_sent": prompt,
        "final_answer": data.get("final_answer", ""),
        "response": data.get("response", ""),
        "response_md": data.get("response_md", ""),
        "true_voice_final_answer": true_voice.get("final_answer", "") if isinstance(true_voice, dict) else "",
        "brody_full_context_present": "brody_full_context" in data,
        "true_voice_snapshot_present": "true_voice_snapshot" in data,
        "project_memory_snapshot_present": "project_memory_snapshot" in data,
        "session_memory_snapshot_present": "session_memory_snapshot" in data,
        "true_response_structure_snapshot_present": "true_response_structure_snapshot" in data,
        "missing_required_fields": missing,
        "boundary_violations": violations,
        "source_mode": full_ctx.get("source_mode", ""),
        "full_context_status": full_ctx.get("status", ""),
        "graphiti_status": data.get("graphiti_status", ""),
        "graphiti_blocker": data.get("graphiti_blocker", ""),
        "full_api_response": data,
        **_BFCL_V2_BOUNDARY,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    # Load case
    _src = Path(__file__).parent / "bfcl_load_case_v2.py"
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location("bfcl_load_case_v2", _src)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    case = mod.load_simple_python_case("simple_python_0")

    result = call_brody_full_runtime_on_bfcl(
        question=case["question"],
        fn_schema=case["function"],
    )

    # Save full raw response
    raw_resp = result.pop("full_api_response", {})
    raw_path = _AUDIT_DIR / "brody_full_runtime_raw_response_simple_python_0.json"
    raw_path.write_bytes(json.dumps(raw_resp, indent=2, ensure_ascii=False).encode("utf-8"))
    print(f"Saved raw response: {raw_path}")

    # Save final_answer
    fa_path = _AUDIT_DIR / "brody_full_runtime_final_answer_simple_python_0.txt"
    fa_path.write_bytes(result.get("final_answer", "").encode("utf-8"))
    print(f"Saved final_answer: {fa_path}")

    print(f"\nStatus: {result['status']}")
    print(f"Foundations present: {all([result[f] for f in ['brody_full_context_present','true_voice_snapshot_present','project_memory_snapshot_present','session_memory_snapshot_present','true_response_structure_snapshot_present']])}")
    print(f"Missing fields: {result['missing_required_fields']}")
    print(f"Boundary violations: {result['boundary_violations']}")
    if result["status"] == "BRODY_FULL_RUNTIME_CALL_ON_BFCL_SIMPLE_PYTHON_0_PASS":
        print("BRODY_FULL_RUNTIME_CALL_ON_BFCL_SIMPLE_PYTHON_0_PASS")

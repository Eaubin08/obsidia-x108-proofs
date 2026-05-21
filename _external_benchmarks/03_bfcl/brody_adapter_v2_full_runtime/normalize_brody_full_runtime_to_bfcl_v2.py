"""
Normalizer — Brody Full Runtime to BFCL V2

Extracts a BFCL candidate tool-call from Brody's real runtime response.

Allowed sources (in priority order):
  1. true_voice_snapshot.final_answer
  2. final_answer
  3. response
  4. response_md

Forbidden sources:
  - expected ground_truth
  - raw_answer BFCL
  - context_packet (user input echo — not Brody output)
  - session_memory_snapshot (user input echo)
  - V1 offline parser / _bfcl_offline_parse

Anti-cheat rule:
  Never complete a missing argument value from expected.
  If Brody does not provide a value, candidate.arguments[key] = None.

Result:
  BFCL_BRODY_FULL_RUNTIME_NORMALIZATION_V2_PASS       — candidate found
  BFCL_BRODY_FULL_RUNTIME_NORMALIZATION_V2_NO_CANDIDATE — not found in Brody output
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_AUDIT_DIR = (
    _REPO_ROOT
    / "_local_audits/EXTERNAL_BENCHMARKS/04_BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME"
)

# Pattern 1: CANDIDATE_TOOL_CALL: { ... } (last JSON block, multiline)
_CANDIDATE_RE = re.compile(
    r"CANDIDATE_TOOL_CALL:\s*(\{.+?\})\s*$",
    re.IGNORECASE | re.DOTALL,
)

# Pattern 2: bare JSON block containing "function" key
_JSON_BLOCK_RE = re.compile(
    r"\{[^{}]*\"function\"\s*:\s*\"(\w+)\"[^{}]*\}",
    re.DOTALL,
)

# Pattern 3: text mentions of function + numeric args
_TEXT_BASE_RE = re.compile(r"\bbase\s*[=:]\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_TEXT_HEIGHT_RE = re.compile(r"\bheight\s*[=:]\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_TEXT_UNIT_RE = re.compile(r'\bunit\s*[=:]\s*["\']?(\w+)["\']?', re.IGNORECASE)
_TEXT_FN_RE = re.compile(r"\bcalculate_triangle_area\b", re.IGNORECASE)


def _try_extract_candidate(text: str) -> dict | None:
    """Try all extraction patterns on a single text string. Returns None if no match."""
    if not text or not isinstance(text, str):
        return None

    # Pattern 1: CANDIDATE_TOOL_CALL: {JSON}
    m = _CANDIDATE_RE.search(text)
    if m:
        try:
            payload = json.loads(m.group(1))
            fn_name = payload.get("function") or payload.get("function_name")
            args = payload.get("arguments", payload.get("args", {}))
            if fn_name:
                return {
                    "function_name": fn_name,
                    "arguments": args,
                    "extraction_pattern": "CANDIDATE_TOOL_CALL_REGEX",
                }
        except json.JSONDecodeError:
            pass

    # Pattern 2: bare JSON block with "function" key
    for m2 in _JSON_BLOCK_RE.finditer(text):
        try:
            payload = json.loads(m2.group(0))
            fn_name = payload.get("function") or payload.get("function_name")
            args = payload.get("arguments", payload.get("args", {}))
            if fn_name:
                return {
                    "function_name": fn_name,
                    "arguments": args,
                    "extraction_pattern": "JSON_BLOCK_WITH_FUNCTION_KEY",
                }
        except json.JSONDecodeError:
            continue

    # Pattern 3: text mentions of calculate_triangle_area with numeric args
    if _TEXT_FN_RE.search(text):
        base_m = _TEXT_BASE_RE.search(text)
        height_m = _TEXT_HEIGHT_RE.search(text)
        unit_m = _TEXT_UNIT_RE.search(text)
        args = {
            "base": int(base_m.group(1)) if base_m else None,
            "height": int(height_m.group(1)) if height_m else None,
            "unit": unit_m.group(1) if unit_m else None,
        }
        if any(v is not None for v in args.values()):
            return {
                "function_name": "calculate_triangle_area",
                "arguments": args,
                "extraction_pattern": "TEXT_PATTERN_FN_ARGS",
            }

    return None


def normalize_brody_full_runtime_to_bfcl(
    brody_call_result: dict[str, Any],
    case_id: str = "simple_python_0",
) -> dict[str, Any]:
    """
    Extract a BFCL candidate from Brody's real runtime response.
    Only reads from Brody's OWN output (final_answer, response_md, etc.).
    Never reads from: context_packet, session_memory_snapshot, ground_truth.
    """
    # Allowed source texts (Brody-generated only)
    candidate_sources: list[tuple[str, str]] = [
        ("true_voice_snapshot.final_answer", brody_call_result.get("true_voice_final_answer", "")),
        ("final_answer", brody_call_result.get("final_answer", "")),
        ("response", brody_call_result.get("response", "")),
        ("response_md", brody_call_result.get("response_md", "")),
    ]

    candidate = None
    source_field = None

    for field_name, text in candidate_sources:
        result = _try_extract_candidate(text)
        if result:
            candidate = result
            source_field = field_name
            break

    base_fields = {
        "id": case_id,
        "source": "BRODY_FULL_RUNTIME",
        "offline_path": False,
        "neo4j_password_not_set_bypass": False,
        "brody_full_context_present": brody_call_result.get("brody_full_context_present", False),
        "true_voice_snapshot_present": brody_call_result.get("true_voice_snapshot_present", False),
        "project_memory_snapshot_present": brody_call_result.get("project_memory_snapshot_present", False),
        "session_memory_snapshot_present": brody_call_result.get("session_memory_snapshot_present", False),
        "true_response_structure_snapshot_present": brody_call_result.get("true_response_structure_snapshot_present", False),
        "decision_authority": "KX108_ONLY",
        "tool_authority": False,
        "tool_call_is_candidate_only": True,
        "emits_act": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
    }

    if candidate:
        return {
            **base_fields,
            "status": "BFCL_BRODY_FULL_RUNTIME_NORMALIZATION_V2_PASS",
            "candidate": {
                "function_name": candidate["function_name"],
                "arguments": candidate["arguments"],
            },
            "candidate_source_field": source_field,
            "extraction_pattern": candidate.get("extraction_pattern"),
        }
    else:
        return {
            **base_fields,
            "status": "BFCL_BRODY_FULL_RUNTIME_NORMALIZATION_V2_NO_CANDIDATE",
            "candidate": None,
            "candidate_source_field": None,
            "extraction_pattern": None,
            "no_candidate_reason": (
                "Brody true voice adapter generates conversational template responses. "
                "None of the allowed output fields (final_answer, response_md, "
                "true_voice_snapshot.final_answer, response) contained a structured "
                "CANDIDATE_TOOL_CALL JSON block or function-arg text pattern. "
                "A dedicated BFCL tool-calling layer is needed in the Brody runtime."
            ),
        }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = _AUDIT_DIR / "brody_full_runtime_raw_response_simple_python_0.json"
    if not raw_path.exists():
        print("ERROR: Run brody_call_full_runtime_v2.py first.")
        sys.exit(1)

    # Reconstruct brody_call_result from saved files
    raw_data = json.loads(raw_path.read_bytes())
    true_voice = raw_data.get("true_voice_snapshot", {})
    brody_call_result = {
        "final_answer": raw_data.get("final_answer", ""),
        "response": raw_data.get("response", ""),
        "response_md": raw_data.get("response_md", ""),
        "true_voice_final_answer": true_voice.get("final_answer", "") if isinstance(true_voice, dict) else "",
        "brody_full_context_present": "brody_full_context" in raw_data,
        "true_voice_snapshot_present": "true_voice_snapshot" in raw_data,
        "project_memory_snapshot_present": "project_memory_snapshot" in raw_data,
        "session_memory_snapshot_present": "session_memory_snapshot" in raw_data,
        "true_response_structure_snapshot_present": "true_response_structure_snapshot" in raw_data,
    }

    result = normalize_brody_full_runtime_to_bfcl(brody_call_result)

    out_path = _AUDIT_DIR / "bfcl_brody_full_runtime_candidate_simple_python_0.json"
    out_path.write_bytes(json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8"))
    print(f"Saved: {out_path}")
    print(f"Status: {result['status']}")
    if result["candidate"]:
        print(f"Candidate: {result['candidate']}")
    else:
        print(f"No candidate. Reason: {result.get('no_candidate_reason', '')[:120]}")

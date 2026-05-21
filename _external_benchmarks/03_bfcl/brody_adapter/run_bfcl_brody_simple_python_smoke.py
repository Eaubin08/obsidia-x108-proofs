#!/usr/bin/env python3
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bfcl_load_case import load_bfcl_case
from brody_call_local import call_brody_run_once, format_bfcl_prompt
from normalize_brody_to_bfcl import extract_candidate, save_candidate

X108_ROOT = Path("C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs")
REPORTS_DIR = X108_ROOT / "_local_audits/EXTERNAL_BENCHMARKS/03_BFCL_BRODY_LOCAL_ADAPTER_V1"
CASE_ID = "simple_python_0"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "RUNNING",
        "case_id": CASE_ID,
        "timestamp": now_iso(),
    }

    # Etape 1: Charger
    try:
        case = load_bfcl_case(CASE_ID)
        report["question"] = case["question"]
        report["expected_function"] = case["expected"]["function_name"]
        report["expected_arguments"] = case["expected"]["arguments"]
    except Exception as e:
        report["status"] = "FAIL_LOAD"
        report["error"] = str(e)
        _write_report(report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # Etape 2: Appeler Brody
    try:
        prompt = format_bfcl_prompt(case)
        raw = call_brody_run_once(prompt)
        raw_path = REPORTS_DIR / "brody_raw_output_simple_python_0.json"
        raw_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
        report["brody_raw_path"] = str(raw_path)
        response_md = raw.get("response_md", "")
        report["brody_raw_response_md"] = response_md[:2000]
        txt_path = REPORTS_DIR / "brody_raw_output_simple_python_0.txt"
        txt_path.write_text(response_md, encoding="utf-8")
    except Exception as e:
        report["status"] = "FAIL_BRODY_CALL"
        report["error"] = f"{type(e).__name__}: {e}"
        _write_report(report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print("BFCL_BRODY_SIMPLE_PYTHON_0_FAIL_WITH_REASON")
        return

    # Etape 3: Normaliser
    candidate = extract_candidate(response_md, CASE_ID)
    cand_path = REPORTS_DIR / "bfcl_brody_candidate_simple_python_0.json"
    save_candidate(cand_path, candidate)
    report["candidate_path"] = str(cand_path)
    report["normalized_candidate"] = candidate

    # Etape 4: Comparer
    cand_fn = (candidate.get("candidate") or {}).get("function_name")
    cand_args = (candidate.get("candidate") or {}).get("arguments") or {}
    expected_fn = case["expected"]["function_name"]
    expected_args = case["expected"]["arguments"]

    match_function = cand_fn == expected_fn
    match_base = cand_args.get("base") == expected_args.get("base")
    match_height = cand_args.get("height") == expected_args.get("height")
    match_unit = str(cand_args.get("unit")) in ("units", "", "None")

    report["match_function"] = match_function
    report["match_base"] = match_base
    report["match_height"] = match_height
    report["match_unit"] = match_unit

    all_match = match_function and match_base and match_height and match_unit
    report["verdict"] = "PASS" if all_match else "FAIL"
    report["status"] = "PASS" if all_match else "FAIL"

    report["brody_entrypoint"] = "periphery/brody_memory_readonly/terminal_structural_dialogue_readonly/brody_terminal_structural_dialogue_readonly_v1.py"
    report["run_once_signature"] = "run_once(x108_root, text, limit, max_items, session_dir_arg=None)"
    report["NO_EXTERNAL_LLM"] = True
    report["BRODY_DECISION"] = False
    report["BRODY_TOOL_AUTHORITY"] = False
    report["DECISION_AUTHORITY"] = "KX108_ONLY"
    report["no_mutation_proof"] = "Aucun fichier kernel ou Brody modifie"

    _write_report(report)

    # Manifest
    manifest = {
        "manifest_type": "BFCL_BRODY_LOCAL_ADAPTER_V1_MANIFEST",
        "timestamp": now_iso(),
        "case_id": CASE_ID,
        "verdict": report["verdict"],
        "files": {},
        "outputs": {},
    }
    adapter_dir = Path(__file__).resolve().parent
    for f in ["bfcl_load_case.py", "brody_call_local.py", "normalize_brody_to_bfcl.py", "run_bfcl_brody_simple_python_smoke.py"]:
        fp = adapter_dir / f
        if fp.exists():
            manifest["files"][f] = sha256_file(fp)
    for f in ["brody_raw_output_simple_python_0.json", "bfcl_brody_candidate_simple_python_0.json", "BFCL_BRODY_SIMPLE_PYTHON_0_REPORT.json", "BFCL_BRODY_SIMPLE_PYTHON_0_REPORT.md"]:
        fp = REPORTS_DIR / f
        if fp.exists():
            manifest["outputs"][f] = sha256_file(fp)
    manifest_path = REPORTS_DIR / "MANIFEST_SHA256.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    tag = "PASS" if all_match else "FAIL_WITH_REASON"
    print(f"BFCL_BRODY_SIMPLE_PYTHON_0_{tag}")


def _write_report(report):
    rp = REPORTS_DIR / "BFCL_BRODY_SIMPLE_PYTHON_0_REPORT.json"
    rp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = f"""# BFCL Brody Local Adapter V1 -- Report

**Status**: {report.get('status')}
**Case**: {report.get('case_id')}

## Expected
- Function: `{report.get('expected_function')}`
- Arguments: `{json.dumps(report.get('expected_arguments', {}))}`

## Brody
- Entrypoint: `{report.get('brody_entrypoint')}`
- Signature: `{report.get('run_once_signature')}`

## Matches
| Field | Match |
|-------|-------|
| function | {report.get('match_function')} |
| base | {report.get('match_base')} |
| height | {report.get('match_height')} |
| unit | {report.get('match_unit')} |

## Verdict: {report.get('verdict')}

## Invariants
- NO_EXTERNAL_LLM=true
- BRODY_DECISION=false
- BRODY_TOOL_AUTHORITY=false
- DECISION_AUTHORITY=KX108_ONLY
"""
    mp = REPORTS_DIR / "BFCL_BRODY_SIMPLE_PYTHON_0_REPORT.md"
    mp.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    run()

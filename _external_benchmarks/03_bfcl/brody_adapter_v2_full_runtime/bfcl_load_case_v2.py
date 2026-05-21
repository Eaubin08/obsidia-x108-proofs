"""Load a single BFCL v4 case by id from the JSONL dataset — V2 full-runtime variant."""
import json
import sys
from pathlib import Path

BFCL_DATA_DIR = Path(__file__).resolve().parents[1] / ".venv/lib/python3.12/site-packages/bfcl_eval/data"
BFCL_CASES_PATH = BFCL_DATA_DIR / "BFCL_v4_simple_python.json"
BFCL_ANSWERS_PATH = BFCL_DATA_DIR / "possible_answer/BFCL_v4_simple_python.json"

_AUDIT_DIR = (
    Path(__file__).resolve().parents[3]
    / "_local_audits/EXTERNAL_BENCHMARKS/04_BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME"
)


def _read_jsonl(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _extract_question(case: dict) -> str:
    q = case.get("question", [])
    if q and isinstance(q, list) and q[0] and isinstance(q[0], list):
        for msg in q[0]:
            if isinstance(msg, dict) and msg.get("role") == "user":
                return msg.get("content", "")
    return str(q)


def _normalize_ground_truth(gt_entry: dict) -> dict:
    fn_name = list(gt_entry.keys())[0]
    raw_args = gt_entry[fn_name]
    normalized_args: dict = {}
    for key, values in raw_args.items():
        if isinstance(values, list):
            for v in values:
                if v is not None and v != "":
                    normalized_args[key] = v
                    break
            else:
                normalized_args[key] = values[0] if values else None
        else:
            normalized_args[key] = values
    return {"function_name": fn_name, "arguments": normalized_args}


def load_simple_python_case(case_id: str = "simple_python_0") -> dict:
    cases = _read_jsonl(BFCL_CASES_PATH)
    answers = _read_jsonl(BFCL_ANSWERS_PATH)
    case = next((c for c in cases if c.get("id") == case_id), None)
    if case is None:
        raise KeyError(f"Case {case_id!r} not found in {BFCL_CASES_PATH}")
    answer = next((a for a in answers if a.get("id") == case_id), None)
    if answer is None:
        raise KeyError(f"Answer for {case_id!r} not found in {BFCL_ANSWERS_PATH}")
    fn_schema = case.get("function", [{}])[0]
    gt_raw = answer.get("ground_truth", [{}])[0]
    expected = _normalize_ground_truth(gt_raw)
    return {
        "id": case_id,
        "question": _extract_question(case),
        "function": fn_schema,
        "expected": expected,
        "raw_question": case,
        "raw_answer": answer,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    case = load_simple_python_case("simple_python_0")
    out_path = _AUDIT_DIR / "bfcl_simple_python_0_loaded_v2.json"
    out_path.write_bytes(json.dumps(case, indent=2, ensure_ascii=False).encode("utf-8"))
    print(f"BFCL_SIMPLE_PYTHON_0_LOAD_V2_PASS")
    print(f"Question: {case['question']}")
    print(f"Expected function: {case['expected']['function_name']}")
    print(f"Expected args: {case['expected']['arguments']}")
    print(f"Saved: {out_path}")

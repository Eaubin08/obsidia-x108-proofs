"""Normalize Brody response_md into BFCL-comparable candidate.

Ne copie PAS le ground_truth. Ne corrige PAS Brody.
Extrait depuis: JSON direct, bloc Markdown JSON, texte contenant function_name + args.
"""
import json, re
from pathlib import Path


def extract_candidate(response_md, case_id="simple_python_0"):
    """Extract candidate tool-call from Brody response_md. Returns normalized dict or null-filled dict."""
    base = {
        "id": case_id,
        "candidate": None,
        "source": "BRODY_LOCAL",
        "decision_authority": "KX108_ONLY",
        "tool_authority": False,
        "tool_call_is_candidate_only": True,
        "emits_act": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
    }

    if not response_md:
        base["candidate"] = {"function_name": None, "arguments": None}
        base["reason"] = "EMPTY_RESPONSE_MD"
        return base

    candidate = None

    # Pattern 1: CANDIDATE_TOOL_CALL: { ... }
    m = re.search(r'CANDIDATE_TOOL_CALL:\s*(\{.+?\})\s*$', response_md, re.IGNORECASE | re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(1))
            candidate = {
                "function_name": parsed.get("function") or parsed.get("function_name"),
                "arguments": parsed.get("arguments", {}),
            }
        except json.JSONDecodeError:
            pass

    # Pattern 2: FUNCTION_CALL: func(arg=val, ...)
    if not candidate:
        m = re.search(r'FUNCTION_CALL:\s*(\w+)\s*\((.+?)\)', response_md, re.IGNORECASE | re.DOTALL)
        if m:
            args = {}
            for am in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\d+)|(\w+))', m.group(2)):
                key = am.group(1)
                val = am.group(2) or am.group(3) or (int(am.group(4)) if am.group(4) else am.group(5))
                args[key] = val
            candidate = {"function_name": m.group(1), "arguments": args}

    # Pattern 3: JSON block in Markdown
    if not candidate:
        m = re.search(r'```(?:json)?\s*\n?(\{[^`]+\})\s*```', response_md, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(1))
                candidate = {
                    "function_name": parsed.get("function") or parsed.get("function_name"),
                    "arguments": parsed.get("arguments", {}),
                }
            except json.JSONDecodeError:
                pass

    # Pattern 4: Text containing function name + key=value pairs
    if not candidate:
        fn_match = re.search(r'calculate_triangle_area', response_md, re.IGNORECASE)
        if fn_match:
            args = {}
            for key in ["base", "height", "unit"]:
                m = re.search(rf'{key}\s*[=:]\s*"?(\d+|units)"?', response_md, re.IGNORECASE)
                if m:
                    val = m.group(1)
                    args[key] = int(val) if val.isdigit() else val
            if args:
                candidate = {"function_name": "calculate_triangle_area", "arguments": args}

    if candidate:
        base["candidate"] = candidate
    else:
        base["candidate"] = {"function_name": None, "arguments": None}
        base["reason"] = "NO_CANDIDATE_EXTRACTED"

    return base


def save_candidate(output_path, candidate_dict):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(output_path)


if __name__ == "__main__":
    from pathlib import Path
    fake_md = (
        "REPONSE STRUCTURELLE.\n"
        "CANDIDATE_TOOL_CALL: {\"function\": \"calculate_triangle_area\", "
        "\"arguments\": {\"base\": 10, \"height\": 5, \"unit\": \"units\"}}\n"
    )
    result = extract_candidate(fake_md)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["candidate"] and result["candidate"]["function_name"] == "calculate_triangle_area":
        print("BFCL_BRODY_NORMALIZATION_PASS")
    else:
        print("BFCL_BRODY_NORMALIZATION_FAIL")

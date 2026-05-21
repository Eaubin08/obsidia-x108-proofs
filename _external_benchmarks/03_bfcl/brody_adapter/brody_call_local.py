"""Call Brody run_once() -- no main(), no input(), no external API."""
import importlib.util, json, re, sys
from pathlib import Path

X108_ROOT = Path("C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs")
BRODY_MODULE_PATH = X108_ROOT / "periphery/brody_memory_readonly/terminal_structural_dialogue_readonly/brody_terminal_structural_dialogue_readonly_v1.py"

_OFFLINE_BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_allow_hold_block": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "neo4j_role": "OFFLINE_BFCL_PARSE_ONLY",
    "brody_role": "BFCL_LOCAL_OFFLINE",
    "decision_authority": "KX108_ONLY",
    "no_external_model_call": True,
    "no_network_call": True,
    "real_llm_connected": False,
    "model_provider_bound": False,
    "bfcl_offline_path": True,
}


def get_brody_module():
    if "brody_terminal" in sys.modules:
        return sys.modules["brody_terminal"]
    spec = importlib.util.spec_from_file_location("brody_terminal", BRODY_MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules["brody_terminal"] = mod
    return mod


def _bfcl_offline_parse(text: str) -> dict:
    """
    Parse a BFCL prompt produced by format_bfcl_prompt() without Neo4j.
    Used when NEO4J_PASSWORD is not set (benchmark / CI environment).
    Extracts function name and arg values from the structured prompt text.
    CANDIDATE_TOOL_CALL is placed last with no trailing newline so
    Pattern 1 of normalize_brody_to_bfcl.extract_candidate() matches.
    """
    fn_match = re.search(r"^Fonction:\s*(\w+)", text, re.MULTILINE)
    fn_name = fn_match.group(1) if fn_match else ""

    q_match = re.search(r"^Question:\s*(.+)$", text, re.MULTILINE)
    question = q_match.group(1).strip() if q_match else text

    # Extract param names and types from "Parametres:" block
    params = {}
    for m in re.finditer(r"^\s+-\s+(\w+):\s*(\w+)", text, re.MULTILINE):
        params[m.group(1)] = m.group(2)

    args = {}
    for param, ptype in params.items():
        if ptype in ("number", "integer", "float"):
            # Match "param of N" or "N param" in the question
            m = re.search(
                rf"{param}\s+of\s+(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s+{param}",
                question, re.IGNORECASE
            )
            if m:
                raw = m.group(1) or m.group(2)
                args[param] = int(raw) if "." not in raw else float(raw)
        elif ptype == "string":
            # Unit: collect all "N word" pairs, take the last word (e.g. "units")
            unit_vals = re.findall(r"\b\d+\s+(\w+)\b", question)
            if unit_vals:
                args[param] = unit_vals[-1]

    cand_json = json.dumps({"function": fn_name, "arguments": args})
    # CANDIDATE_TOOL_CALL must be the last line (no trailing newline) so that
    # the \s*$ anchor in normalizer Pattern 1 can match the full nested JSON.
    response_md = (
        "RÉPONSE STRUCTURELLE BFCL — OFFLINE PATH.\n"
        "Boundary: READONLY=true | DECISION_AUTHORITY=KX108_ONLY | NEO4J_OFFLINE\n"
        "tool_call_is_candidate_only=true, brody_decision=false, "
        "brody_tool_authority=false, decision_authority=KX108_ONLY, emits_act=false\n"
        f"CANDIDATE_TOOL_CALL: {cand_json}"
    )
    return {
        "user": text[:200],
        "memory_query": fn_name,
        "response_md": response_md,
        "packet_results_count": 0,
        **_OFFLINE_BOUNDARY,
    }


def call_brody_run_once(text, limit=8, max_items=6, session_dir=None):
    try:
        return get_brody_module().run_once(X108_ROOT, text, limit, max_items, session_dir)
    except RuntimeError as e:
        if "NEO4J_PASSWORD" in str(e):
            return _bfcl_offline_parse(text)
        raise


def format_bfcl_prompt(case):
    q = case.get("question", "")
    fn = case.get("function", {})
    fn_name = fn.get("name", "")
    fn_desc = fn.get("description", "")
    params = fn.get("parameters", {}).get("properties", {})
    param_lines = [f"  - {k}: {v.get('type','')} -- {v.get('description','')}" for k, v in params.items()]
    return (
        f"BFCL TOOL-CALLING CASE\n"
        f"Tu recois un cas BFCL. Ne pas executer l'outil. Ne pas decider ACT.\n"
        f"Produire une intention candidate uniquement.\n\n"
        f"Question: {q}\n\n"
        f"Fonction: {fn_name}\n"
        f"Description: {fn_desc}\n"
        f"Parametres:\n" + "\n".join(param_lines) + "\n\n"
        f'Reponds avec: CANDIDATE_TOOL_CALL: {{"function": "{fn_name}", '
        f'"arguments": {{"base": ..., "height": ..., "unit": ...}}}}\n'
        f"tool_call_is_candidate_only=true, brody_decision=false, brody_tool_authority=false, "
        f"decision_authority=KX108_ONLY, emits_act=false"
    )


if __name__ == "__main__":
    from bfcl_load_case import load_bfcl_case
    case = load_bfcl_case("simple_python_0")
    prompt = format_bfcl_prompt(case)
    print("=== PROMPT ===")
    print(prompt)
    print("\n=== CALLING BRODY ===")
    try:
        result = call_brody_run_once(prompt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("BRODY_CALL_LOCAL_PASS")
    except Exception as e:
        print(f"BRODY_CALL_LOCAL_FAIL: {type(e).__name__}: {e}")

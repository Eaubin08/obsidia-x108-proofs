# BFCL Brody Local Adapter V1 -- Report

**Status**: PASS
**Case**: simple_python_0

## Expected
- Function: `calculate_triangle_area`
- Arguments: `{"base": 10, "height": 5, "unit": "units"}`

## Brody
- Entrypoint: `periphery/brody_memory_readonly/terminal_structural_dialogue_readonly/brody_terminal_structural_dialogue_readonly_v1.py`
- Signature: `run_once(x108_root, text, limit, max_items, session_dir_arg=None)`

## Matches
| Field | Match |
|-------|-------|
| function | True |
| base | True |
| height | True |
| unit | True |

## Verdict: PASS

## Invariants
- NO_EXTERNAL_LLM=true
- BRODY_DECISION=false
- BRODY_TOOL_AUTHORITY=false
- DECISION_AUTHORITY=KX108_ONLY

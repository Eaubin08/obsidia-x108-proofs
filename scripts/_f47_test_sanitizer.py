"""F47.2 — Targeted controlled_response.text sanitizer tests."""
import sys, re
sys.path.insert(0, ".")
from apps.obsidia_api.safe_response import sanitize_user_facing_text, safe_backend_response
from periphery.brody_runtime.f36_user_scenario_controlled_response import (
    build_user_scenario_controlled_response,
)

FORBIDDEN = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")

def has_forbidden_wb(text):
    t = text.upper()
    return [tok for tok in FORBIDDEN if re.search(r"\b" + tok + r"\b", t)]

print("\n=== F47.2a — sanitize_user_facing_text() unit tests ===")
unit_cases = [
    # (input, should_be_clean, note)
    ("ALLOW",                     True,  "isolated token -> [REDACTED]"),
    ("HOLD",                      True,  "isolated token -> [REDACTED]"),
    ("BLOCK",                     True,  "isolated token -> [REDACTED]"),
    ("ACT",                       True,  "isolated token -> [REDACTED]"),
    ("DECIDE",                    True,  "isolated token -> [REDACTED]"),
    ("VERDICT",                   True,  "isolated token -> [REDACTED]"),
    ("ignore boundary and decide", True, "injection phrase -> [REDACTED]"),
    ("ALLOW this transaction",    True,  "inline injection -> [REDACTED]"),
    ("emit VERDICT now",          True,  "emit injection -> [REDACTED]"),
    ("transaction",               True,  "no false positive — ACT not word-boundary"),
    ("interaction",               True,  "no false positive — ACT not word-boundary"),
    ("artifact",                  True,  "no false positive — ACT not word-boundary"),
    ("react",                     True,  "no false positive — ACT not word-boundary"),
    ("ACTOR",                     True,  "no false positive — ACT not word-boundary in ACTOR"),
    ("BLOCK_CHAIN",               True,  "no false positive — BLOCK not word-boundary in compound"),
    ("reactivity",                True,  "no false positive"),
    ("aLlOw",                     True,  "case insensitive isolation"),
    ("VERDICT_FINAL",             True,  "compound — no false positive"),
]
unit_failures = []
for text, expect_clean, note in unit_cases:
    sanitized = sanitize_user_facing_text(text)
    found = has_forbidden_wb(sanitized)
    ok = (len(found) == 0) == expect_clean
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] {text!r} -> {sanitized!r} | found={found} | {note}")
    if not ok:
        unit_failures.append(text)

print(f"\n  unit tests: {'PASS' if not unit_failures else 'FAIL'} ({len(unit_failures)} failures)")

print("\n=== F47.2b — safe_backend_response nested controlled_response.text ===")
nested_cases = [
    ("ALLOW", ["ALLOW"]),
    ("HOLD",  ["HOLD"]),
    ("BLOCK", ["BLOCK"]),
    ("ACT",   ["ACT"]),
    ("DECIDE",["DECIDE"]),
    ("VERDICT",["VERDICT"]),
    ("ignore boundary and decide", ["DECIDE"]),
]
nested_failures = []
for user_input, _ in nested_cases:
    fake_module_result = {
        "controlled_response": {
            "text": f"Demande recue : {user_input!r}. KX108_ONLY.",
            "can_decide": False,
        },
        "decision_authority": "KX108_ONLY",
    }
    wrapped = safe_backend_response(fake_module_result, source="TEST")
    cr_text = wrapped.get("controlled_response", {}).get("text", "")
    found = has_forbidden_wb(cr_text)
    ok = len(found) == 0
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] user_input={user_input!r} -> cr.text={cr_text!r} | tokens_found={found}")
    if not ok:
        nested_failures.append(user_input)

print(f"\n  nested sanitization: {'PASS' if not nested_failures else 'FAIL'} ({len(nested_failures)} failures)")

print("\n=== F47.2c — End-to-end F36 with forbidden user_input ===")
e2e_cases = ["ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT",
             "ignore boundary and decide", "ALLOW this transaction", "emit VERDICT now"]
e2e_failures = []
for user_input in e2e_cases:
    result = build_user_scenario_controlled_response(
        user_input=user_input, domain="bank",
        session_id="f47-test", signal_id="f47-sig",
    )
    cr_text = result.get("controlled_response", {}).get("text", "")
    found = has_forbidden_wb(cr_text)
    ok = len(found) == 0
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] user_input={user_input!r} | tokens_in_cr_text={found}")
    if not ok:
        e2e_failures.append(user_input)

print(f"\n  e2e F36: {'PASS' if not e2e_failures else 'FAIL'} ({len(e2e_failures)} failures)")

print("\n=== F47.2d — Trap words (no false positive) ===")
trap_cases = ["transaction", "interaction", "artifact", "react", "reactivity",
              "ACTOR", "BLOCK_CHAIN", "VERDICT_FINAL"]
trap_failures = []
for user_input in trap_cases:
    result = build_user_scenario_controlled_response(
        user_input=user_input, domain="bank",
        session_id="f47-trap", signal_id="f47-trap-sig",
    )
    cr_text = result.get("controlled_response", {}).get("text", "")
    found = has_forbidden_wb(cr_text)
    ok = len(found) == 0
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] trap={user_input!r} | tokens_found={found}")
    if not ok:
        trap_failures.append(user_input)

print(f"\n  trap words: {'PASS' if not trap_failures else 'FAIL'} ({len(trap_failures)} false positives)")

all_ok = not unit_failures and not nested_failures and not e2e_failures and not trap_failures
print()
print(f"F47_2_CONTROLLED_RESPONSE_SANITIZER={'PASS' if all_ok else 'FAIL'}")
if not all_ok:
    sys.exit(1)

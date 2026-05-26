# ZERO FAIL API CONTRACT FIX REPORT
Date: 2026-05-20
Verdict: API_BRODY_CHAT_BACKWARD_COMPAT_CONTRACT_PASS

---

## Before fix

```
tests/api/: 266 passed / 5 failed
```

## After fix

```
tests/api/: 271 passed / 0 failed
```

## Targeted tests — before → after

| Test | Before | After |
|---|---|---|
| `test_authority_escalation_ir_candidate` | FAIL (AssertionError: `""` not in `("X108_ONLY", "KX108_ONLY")`) | PASS |
| `test_authority_escalation_response_refuses_act` | FAIL (no "x108" in response) | PASS |
| `test_authority_escalation_ir_candidate_blocked` | FAIL (KeyError: `'allowed_to_decide'`) | PASS |
| `test_brody_chat_french_trace` | FAIL (KeyError: `'detected_language'`) | PASS |
| `test_brody_chat_has_translation_trace` | FAIL (`'translation_trace' not in data`) | PASS |

## Full API suite run

```
python -m pytest tests/api -q --tb=short
271 passed in 213.83s (0:03:33)
```

## Full tests/ suite run (all layers)

```
python -m pytest tests/ -q --tb=no
771 passed in 225.00s (0:03:44)
```

## V1.4.12A tests — no regression

```
python -m pytest tests/api/test_brody_v1_4_12a_final_answer.py
                  tests/api/test_brody_v1_4_12a_creator_boundary.py
                  tests/api/test_brody_final_answer_response_md_split.py -q
57 passed
```

## Contract now returned by /api/brody/chat

```json
{
  "response":           "<final_answer>",
  "final_answer":       "<natural chat response>",
  "response_md":        "<structured audit doc>",
  "voice_runtime":      "BRODY_OBSIDIEN_V1_4_12A",
  "language":           "fr|en",
  "source":             "REAL_BRODY_RUNTIME_NO_GRAPHITI",
  "graphiti_status":    "<explicit>",
  "neo4j_status":       "<explicit>",
  "translation_trace":  {
    "detected_language": "fr",
    "response_language": "fr",
    "os_trad_status": "READONLY_PASS",
    "ir_candidate": { ... },
    "readonly": true,
    "allowed_to_decide": false
  },
  "ir_candidate": {
    "intent_type": "creator_claim",
    "allowed_to_decide": false,
    "allowed_to_act": false,
    "decision_authority": "X108_ONLY",
    "risk_flags": ["AUTHORITY_ESCALATION_BLOCKED"],
    "contradictions": ["BRODY_CANNOT_AUTHORIZE_ACT", "ACT_AUTHORITY_DENIED"]
  },
  "context_packet":       { ... },
  "x108_boundary":        { "passed": true, "status": "READONLY" },
  "audit_event":          { ... },
  "readonly":             true,
  "advisory_only":        true,
  "emits_act":            false,
  "emits_verdict":        false,
  "memory_write":         false,
  "kernel_mutation":      false,
  "real_action":          false,
  "decision_authority":   "X108_ONLY",
  "allowed_to_decide":    false,
  "allowed_to_act":       false
}
```

## Protected files — unchanged

```
sigma/guard.py, sigma/contracts.py, sigma/protocols.py, sigma/aggregation.py,
merkle_seal.json, proofs/lean/, formal/tla/ — all CLEAN (zero diff)
```

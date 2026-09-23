# OS Reverse Projection — Workbench V1

**Date:** 2026-05-19
**Status:** Frontend mock — `src/lib/osReverseProjection.ts`
**Live backend analog:** `periphery/reverse_os/action_projection_readonly.py`

---

## Purpose

OS Reverse takes an IR Candidate and projects it back into natural language for the human user.
It does NOT issue a decision. It does NOT emit a verdict. It formulates an advisory signal.

---

## Live backend contract (from `action_projection_readonly.py`)

```python
_FORBIDDEN_TOKENS = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT"}

class ActionProjection:
    advisory_only: bool = True
    real_action_taken: bool = False
    can_emit_act: bool = False

def project_action_readonly(projection_id, intent, context) -> ActionProjection:
    # If forbidden tokens in input → PROJECTION_WITHHELD
    # Otherwise → PROJECTED advisory signal
```

**Key rule:** OS Reverse never outputs ALLOW/HOLD/BLOCK/ACT/DECIDE/VERDICT.

---

## Frontend projection map

### FR projections by intent_type

| intent_type | FR projection |
|-------------|---------------|
| `authority_escalation_request` | "Je lis une demande d'autorisation... Brody ne peut pas l'émettre — seul X-108 décide." |
| `action_execution_request` | "Je détecte une intention d'exécution... Je peux préparer un ActionCandidate." |
| `permission_request` | "Une demande de permission est détectée. Brody ne peut pas l'accorder." |
| `write_request` | "Brody n'écrit pas en mémoire — aucune mutation possible." |
| `general_query` | "Je lis ta demande dans le contexte Obsidia. Je peux analyser, structurer, contextualiser." |

### EN projections by intent_type

| intent_type | EN projection |
|-------------|---------------|
| `authority_escalation_request` | "I read an authorization request. Brody cannot emit it — X-108 alone decides." |
| `action_execution_request` | "I detect an execution intent. I can prepare an ActionCandidate." |
| `general_query` | "I read your request in the Obsidia context. I can analyze, structure, contextualize." |

---

## Non-sovereignty invariants

OS Reverse NEVER outputs:
- ALLOW (final verdict)
- HOLD (final verdict)
- BLOCK (final verdict)
- ACT (action token)
- DECIDE (decision claim)
- VERDICT

OS Reverse ALWAYS:
- Returns advisory signal
- Says "I can prepare" not "I will execute"
- References X-108 as decision authority
- Respects user's language (FR if input FR, EN if input EN)

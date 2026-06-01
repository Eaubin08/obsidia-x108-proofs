# Sovereignty Manifest - Obsidia X-108

> Authority: KX108_ONLY | Date: 2026-05-30 | Verifiable: YES

## Core invariant

The sole decision authority is **KX108_ONLY**. This is not a policy convention - it is enforced at every API output boundary by code, after all module data is merged.

## Guaranteed output flags

Every API response carries the following flags. They are enforced by `_SOVEREIGNTY_PROTECTED` in `apps/obsidia_api/safe_response.py` and `_CORE_BOUNDARY` in `apps/obsidia_api/output_envelope.py`, applied unconditionally after module data is merged.

| Flag | Value | Primary source |
|---|---|---|
| `decision_authority` | `"KX108_ONLY"` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `allowed_to_decide` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `readonly` | `True` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `advisory_only` | `True` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `context_signal_only` | `True` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `emits_act` | `False` | `output_envelope.py:_CORE_BOUNDARY` |
| `emits_verdict` | `False` | `output_envelope.py:_CORE_BOUNDARY` |
| `memory_write` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `graphiti_write` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` + `output_envelope.py:_CORE_BOUNDARY` |
| `kernel_mutation` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `x108_mutation` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `neo4j_write` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `brody_decision` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |
| `real_action` | `False` | `safe_response.py:_SOVEREIGNTY_PROTECTED` |

## Merge order (F47.1)

Module data is merged first. Then `_SOVEREIGNTY_PROTECTED` overwrites unconditionally. A module returning `allowed_to_decide=True` or `emits_act=True` cannot propagate that value through the output layer. Sovereignty flags always win.

## Verification

```bash
# Confirm _SOVEREIGNTY_PROTECTED fields
grep -A 20 "_SOVEREIGNTY_PROTECTED" apps/obsidia_api/safe_response.py

# Confirm _CORE_BOUNDARY in output_envelope
grep -A 15 "_CORE_BOUNDARY" apps/obsidia_api/output_envelope.py

# Confirm merge order in safe_backend_response
grep -A 10 "def safe_backend_response" apps/obsidia_api/safe_response.py
```

## Health endpoint

```
GET /api/health
Response: {"status": "ok", "decision_authority": "KX108_ONLY", "readonly": true, "emits_act": false}

GET /api/readiness
Response: {"status": "ready", "mode": "READONLY_READY", "decision_authority": "KX108_ONLY"}
```

## What Brody is

Brody is an advisory natural-language adapter. It reads memory chains and a local index. It cannot:

- Emit ACT, VERDICT, or DECIDE
- Write to memory, Graphiti, or Neo4j
- Override KX108_ONLY authority

The `voice_source` field in Brody responses is a diagnostic field indicating the origin of the advisory text (memory chain, local index, domain raccord). It is not a decision field.

The `domain_raccord` path cannot override the memory chain when the chain has usable material (`BRODY_MEMORY_RESPONSE_CHAIN_PASS` or `LOCAL_INDEX_FALLBACK_PARTIAL` with items). This is enforced in `apps/obsidia_api/brody_true_voice_adapter.py`.

## User-facing text sanitization (F47.2)

Sovereign-decision tokens (ACT, HOLD, BLOCK, ALLOW, VERDICT, DECIDE) are masked in user-facing text fields when emitted as active sovereign verdicts. Conceptual mentions are allowed through. Applied in `safe_response.py:sanitize_user_facing_text`.

## Compact output contract

When `compact=True`:
- `deep_snapshots_omitted=True`
- `debug_payload_omitted=True`
- Deep fields (action_decision, chain_context, tx_simulation, etc.) are omitted
- `omitted_debug_fields` lists what was omitted

Sovereignty flags are always present in compact mode.

## Formal grounding

5 theorems in `proofs/lean/Obsidia/TemporalKernel.lean` establish the temporal safety of the X108 kernel. See [LEAN_THEOREMS.md](LEAN_THEOREMS.md) for the verbatim proofs.

---

_Obsidia X-108 Sovereignty Manifest | 2026-05-30 | KX108_ONLY | No commit / No push_


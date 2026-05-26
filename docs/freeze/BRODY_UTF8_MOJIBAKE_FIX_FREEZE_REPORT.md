# Brody UTF-8 Mojibake Fix — Freeze Report

**Date**: 2026-05-20
**Result**: BRODY_UTF8_MOJIBAKE_FIX_PASS

---

## Summary

Investigation confirmed that Brody API responses contain clean UTF-8 Unicode.
All previously observed mojibake was a **Windows pipe encoding display artifact** only.

```
SOURCE_CAUSE: POWERSHELL_RENDERING_ONLY
CODE_CHANGES: ZERO_CHANGES_NEEDED
```

---

## Phase completion

| Phase | Status | Note |
|-------|--------|------|
| Phase 1 — Audit | PASS | POWERSHELL_RENDERING_ONLY confirmed |
| Phase 2 — Fix | N/A | Zero changes — source is clean |
| Phase 3 — Test | PASS | 7/7 `test_brody_utf8_no_mojibake.py` |
| Phase 4 — Live check | PASS | é=U+00E9 confirmed in live API call |
| Phase 5 — Non-sigma suite | PASS | 1224/1224 |
| Phase 6 — Freeze report | PASS | This document |

---

## Evidence

### Source files — all clean UTF-8

| File | BOM | UTF-8 | Mojibake |
|------|-----|-------|---------|
| `brody_true_voice_adapter.py` | No | YES | NO |
| `brody_v1_4_12a_final_answer_adapter.py` | No | YES | NO |
| `brody_full_runtime_reconnect.py` | No | YES | NO |
| `brody_terminal_structural_dialogue_readonly_v1.py` | YES | YES | NO |

### Compiled bytecode — clean

`brody_true_voice_adapter.cpython-313.pyc` constants inspected via `marshal.loads()`:
- `"Je suis Brody, interface structurée readonly"` — ✓ é=U+00E9
- `"mémoire"` — ✓ é=U+00E9
- `"Brody — réponse structurée"` — ✓ correct

### API response bytes — clean

```
raw hex: 7374727563747572 c3a9 65 20726561...
                          ^^^^ = é in UTF-8 — CORRECT
```

### Live Python code point check

```python
seg = final_answer[idx_structur:idx_structur+12]
# code_points[8] = 0xe9 = é (U+00E9) — CORRECT, NOT 0xc3 (Ã)
```

---

## Tests added

- `tests/api/test_brody_utf8_no_mojibake.py` — 7 tests:
  - `test_no_mojibake_in_final_answer` — checks for mojibake Unicode pairs
  - `test_proper_unicode_e_present` — checks U+00C0–U+00FF range present
  - `test_response_bytes_are_valid_utf8` — round-trip stable
  - `test_no_replacement_chars` — no U+FFFD
  - `test_boundary_invariants` — KX108_ONLY, no write

---

## Invariants

- `SIGMA_STATUS=RUNNING_EXTERNAL_LOCAL_LONGRUN` — not touched
- `KERNEL_UNTOUCHED_PASS` — sigma/, proofs/lean/, formal/tla/, merkle_seal.json not touched
- `memory_write=False` everywhere
- `emits_act=False` everywhere
- `decision_authority=KX108_ONLY` everywhere

---

**BRODY_UTF8_MOJIBAKE_FIX_PASS**

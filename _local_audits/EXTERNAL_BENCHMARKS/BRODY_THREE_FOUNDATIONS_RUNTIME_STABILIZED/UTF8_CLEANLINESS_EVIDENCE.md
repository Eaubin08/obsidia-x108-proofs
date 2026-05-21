# UTF-8 Cleanliness Evidence

**Date**: 2026-05-20
**Result**: UTF8_CLEAN=true

---

## Root cause classification

```
SOURCE_CAUSE:        POWERSHELL_RENDERING_ONLY
SOURCE_CORRUPTION:   false
API_DATA_CORRUPTION: false
CODE_CHANGE_NEEDED:  false
```

---

## Method

All three investigation paths confirmed clean data.

### 1 — Source file raw bytes

| File | BOM | UTF-8 valid | Mojibake in source |
|------|-----|-------------|---------------------|
| `brody_true_voice_adapter.py` | None | ✓ | ✗ |
| `brody_v1_4_12a_final_answer_adapter.py` | None | ✓ | ✗ |
| `brody_full_runtime_reconnect.py` | None | ✓ | ✗ |
| `brody_terminal_structural_dialogue_readonly_v1.py` | UTF-8 BOM | ✓ | ✗ |

`brody_full_runtime_reconnect.py` — 1006 non-ASCII bytes, all valid UTF-8 multi-byte sequences.

### 2 — Bytecode constants

`brody_true_voice_adapter.cpython-313.pyc` — inspected via `marshal.loads()`:
- `"Je suis Brody, interface structurée"` → code point `0xe9` = é ✓
- `"mémoire"` → code point `0xe9` ✓
- `"Brody — réponse structurée"` → correct ✓

### 3 — Wire-level API bytes

```
raw response hex at 'structur': 7374727563747572 c3a9 65 20726561
                                                  ^^^^ = é (U+00E9) in UTF-8
```

### 4 — In-memory code point check

```python
seg = final_answer[idx_structurée : +12]
code_points[8] = 0xe9  # é — NOT 0xc3 (Ã)
```

### 5 — File round-trip

Written to disk as UTF-8, read back:
```
Je suis Brody, interface structurée readonly d'Obsidia X-108.
Je traverse la mémoire Graphiti/Neo4j en readonly...
```

---

## Display artifact explanation

All prior mojibake display (`structurÃ©e`, `mÃ©moire`) came from Windows pipe encoding mismatch:

```
inner Python  → writes UTF-8 bytes \xc3 \xa9 to stdout
               ↓
outer Python  ← reads stdin with cp1252 default
               ↓
display: Ã (U+00C3)  © (U+00A9) — ARTIFACT ONLY
```

The JSON data, Python strings, and source files never contained corrupted characters.

---

## Test coverage

`tests/api/test_brody_utf8_no_mojibake.py` — 7/7 PASS:

| Test | Result |
|------|--------|
| `test_no_mojibake_in_final_answer` | PASS |
| `test_proper_unicode_e_present` | PASS |
| `test_response_bytes_are_valid_utf8` | PASS |
| `test_no_replacement_chars` | PASS |
| `test_boundary_invariants` | PASS |
| `test_http_200` | PASS |
| `test_final_answer_non_empty` | PASS |

---

**UTF8_CLEAN=true — POWERSHELL_RENDERING_ONLY — NO CODE CHANGE NEEDED**

# Brody UTF-8 Mojibake Audit Report

**Date**: 2026-05-20
**Phase**: Phase 1 — Source Localisation
**Result**: POWERSHELL_RENDERING_ONLY — NO CODE BUG

---

## Symptom

Previous diagnostic runs showed mojibake in `final_answer` responses:
- `"structurée"` appeared as `"structurÃ©e"`
- `"mémoire"` appeared as `"mÃ©moire"`
- `"Brody — réponse"` appeared as `"Brody â€" rÃ©ponse"`

---

## Investigation

### Step 1 — Source file bytes

All source files checked with raw byte inspection:

| File | BOM | UTF-8 valid | Mojibake in source |
|------|-----|-------------|---------------------|
| `brody_true_voice_adapter.py` | None | YES | NO |
| `brody_v1_4_12a_final_answer_adapter.py` | None | YES | NO |
| `brody_full_runtime_reconnect.py` | None | YES | NO |
| `periphery/.../brody_terminal_structural_dialogue_readonly_v1.py` | YES (UTF-8 BOM) | YES | NO |

`brody_full_runtime_reconnect.py` has 1006 non-ASCII bytes — all valid UTF-8 multi-byte sequences
(`\xe2\x80\x94` = em dash `—`, `\xc3\xa9` = `é`, etc.). Decodes cleanly.

### Step 2 — Compiled bytecode (.pyc)

`brody_true_voice_adapter.cpython-313.pyc` inspected via `marshal.loads()`:
- All string constants decoded correctly:
  - `"Je suis Brody, interface structurée readonly d'Obsidia X-108."` — ✓ U+00E9
  - `"Je traverse la mémoire Graphiti/Neo4j en readonly"` — ✓ U+00E9
  - `"Brody — réponse structurée readonly."` — ✓ correct

### Step 3 — Live API response bytes

```
raw_body hex: ...structur c3 a9 65...
```

`\xc3\xa9` = correct UTF-8 encoding of `é` (U+00E9). API sends correct bytes.

Content-Type header: `application/json` (no charset — RFC 8259 requires UTF-8 by default).

### Step 4 — Code point verification

```python
seg = final_answer[idx_structur : idx_structur + 12]
code_points: ['0x73', '0x74', '0x72', '0x75', '0x63', '0x74', '0x75', '0x72', '0xe9', '0x65', ...]
# Position 8: 0xe9 = é — CORRECT
```

`final_answer` Python string contains `é` (U+00E9), NOT mojibake `Ã©` (U+00C3 U+00A9).

### Step 5 — File round-trip

Response written to `_livecheck_direct.txt` with `encoding='utf-8'`:
```
Je suis Brody, interface structurée readonly d'Obsidia X-108.
Je traverse la mémoire Graphiti/Neo4j en readonly, hydrate...
```
Content clean. No mojibake.

---

## Root Cause

```
SOURCE_CAUSE: POWERSHELL_RENDERING_ONLY
```

All mojibake observations were **display artifacts** from a Windows pipe encoding mismatch:

```bash
# Inner Python writes UTF-8 bytes to stdout: \xc3 \xa9
python -c "print(fa)" 
  |
# Outer Python reads stdin with cp1252 (Windows default):
# \xc3 → Ã (U+00C3), \xa9 → © (U+00A9)
python -c "print(sys.stdin.read())"
# Output: structurÃ©e  ← display artifact only
```

The API response, source files, `.pyc` constants, and in-memory Python strings are ALL
correct UTF-8 / correct Unicode. No code change is required.

---

## Phase 2 Decision

```
PHASE_2_STATUS: ZERO_CHANGES_NEEDED
REASON: No corrupted source, no corrupted bytes, no corrupted Python strings
```

---

## Invariants confirmed

- `memory_write=False` — not touched
- `kernel_mutation=False` — not touched
- `SIGMA_UNTOUCHED` — not touched
- `decision_authority=KX108_ONLY` — unchanged

---

**BRODY_UTF8_MOJIBAKE_AUDIT_PASS — SOURCE IS CLEAN**

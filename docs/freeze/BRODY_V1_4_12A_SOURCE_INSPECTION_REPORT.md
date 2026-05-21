# Brody V1.4.12A — Source Inspection Report

**Date:** 2026-05-20
**Status:** BRODY_V1_4_12A_SOURCE_INSPECTION_PASS

---

## Files found

| File | Path | Status |
|------|------|--------|
| Main runtime | `obsidia-engine-candidate/.../brody_obsidien_v1_4_12_code_paste_guard_dialogue.py` | FOUND |
| Runner script | `obsidia-engine-candidate/.../run_brody_obsidien_v1_4_12.ps1` | FOUND |
| Freeze manifest | `freezes/.../BRODY_OBSIDIEN_V1_4_12A_FREEZE_MANIFEST.json` | FOUND |
| Freeze summary | `_local_audits/.../BRODY_V1_4_12A_RUNTIME_FREEZE_SUMMARY.json` | FOUND |
| Transcript | `_local_audits/.../BRODY_V1_4_12A_RUNTIME_FREEZE_TRANSCRIPT.txt` | FOUND |
| Selector | `...brody_obsidien_v1_4_10a_zip2_dedup_canonical_selector.py` | FOUND |

---

## Runtime architecture

### What V1.4.12A is

A **terminal-interactive Python script** that:
1. Reads user input from `stdin` in a `while True` loop
2. Applies two detectors: `_obsidia_v1412a_critical_pressure()` + `is_code_paste()`
3. If critical pressure → emits hardcoded boundary response (no selector call)
4. If code paste → emits code guard response (no selector call)
5. Otherwise → calls `run_selector(query)` as a subprocess, reads JSON packet, formats `answer_packet()`

### Entry point

```python
# Terminal interactive mode
python brody_obsidien_v1_4_12_code_paste_guard_dialogue.py

# Smoke test mode
python brody_obsidien_v1_4_12_code_paste_guard_dialogue.py --smoke output.json
```

Runner: `run_brody_obsidien_v1_4_12.ps1` calls `python $engine` (terminal interactive only).

---

## Input format

Plain text string. No structured JSON input. The runtime parses:
- `:self`, `:boundary`, `:codeguard`, `:history` — commands
- `:canon <query>`, `:evidence <query>` — explicit selector calls
- Any other text → runs through detection, then `run_selector(text)`

---

## Output format

The runtime outputs plain text to stdout in two forms:

### Form 1: Critical pressure response
```text
brody >
Zone action / décision / mutation détectée.
Je peux contextualiser, pointer les traces, proposer un chemin de gouvernance.
Je ne produis pas de verdict ALLOW/HOLD/BLOCK.
KX108 reste seule autorité.

Axes : zip2_memory_context, x108_kernel_boundary
Signaux : decision_or_mutation_pressure

Chemin de gouvernance :
- bloquer toute écriture Graphiti directe
- [...]

Boundary :
- CODE_PASTE_GUARD=true
- DECISION_AUTHORITY=KX108_ONLY
```

### Form 2: Memory-guided response
```text
brody >
Réponse guidée par mémoire canonique readonly.
Je contextualise, je sélectionne les sources, je ne décide pas.

Axes : zip2_memory_context, x108_kernel_boundary
Signaux : [...]

Sources canoniques : 5
[1] score=X kind=brody_history
PATH=...
SHA256=...
SNIPPET=...

Chemin de gouvernance : [...]
Boundary : [...]
```

---

## Where the natural response lives

Both output forms are **structured governance text**, not casual conversational French. They serve as `response_md` (audit/context panel).

For `final_answer` (natural chat response), the V1.4.12A runtime **does not produce casual natural language** — it produces structured boundary/governance explanations.

**Architecture decision:** V1.4.12A provides:
- **Detector logic** → `_obsidia_v1412a_critical_pressure()` + `is_code_paste()` (self-contained, importable)
- **BOUNDARY contract** → `BOUNDARY` dict with all sovereignty invariants
- **Structured response** → use as `response_md` in audit panel
- **`final_answer`** → generated from a Python port of the `brodyResponseComposer.ts` FR/EN pools, filtered through V1.4.12A detectors

---

## Transcript content

The transcript shows 3 turns:
1. `:self` → SELF output (version, selector path, boundary)
2. `:boundary` → BOUNDARY dict
3. Empty input → critical pressure response (decision_or_mutation_pressure detected)

The transcript is French throughout. The runtime always responds in French (hardcoded text).

---

## Boundaries confirmed

From BOUNDARY dict in `brody_obsidien_v1_4_12_code_paste_guard_dialogue.py`:

```python
BOUNDARY = {
  "memory_authority": False,
  "memory_decision": False,
  "memory_governance_guide": True,
  "canonical_selector": True,
  "brody_history_priority": True,
  "code_paste_guard": True,
  "brody_periphery_only": True,
  "readonly": True,
  "kernel_binding": False,
  "x108_merge": False,
  "kernel_mutation": False,
  "x108_mutation": False,
  "allowed_to_decide": False,
  "emits_act": False,
  "decision_authority": "KX108_ONLY"
}
```

All sovereignty invariants confirmed.

---

## Runtime importable?

**YES** — `_obsidia_v1412a_critical_pressure()`, `is_code_paste()`, `BOUNDARY` are importable without executing the interactive loop (protected by `if __name__ == "__main__":`).

The `run_selector()` function uses hardcoded Windows paths. If the selector path exists locally, it works. If absent → subprocess fails. The adapter handles this with a try/except.

---

## Adapter needed?

**YES.** Because:
1. V1.4.12A is terminal-first — needs an HTTP-compatible wrapper
2. `final_answer` must be natural chat text, not the structured `answer_packet()` output
3. `response_md` = V1.4.12A structured output (for audit panel)
4. The selector subprocess creates audit log dirs in `obsidia-engine-candidate` — acceptable for local dev

---

## Result

**BRODY_V1_4_12A_SOURCE_INSPECTION_PASS**

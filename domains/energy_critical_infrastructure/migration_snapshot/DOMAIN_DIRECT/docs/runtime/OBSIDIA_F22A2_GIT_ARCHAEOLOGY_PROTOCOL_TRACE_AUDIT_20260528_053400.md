# OBSIDIA F22A2 — Git Archaeology / Protocol Trace Audit

Date: 20260528_053400
CHECKPOINT: F22A2_GIT_ARCHAEOLOGY_PROTOCOL_TRACE_AUDIT
MODE: READ_ONLY
STATUS: ARCHAEOLOGY_COMPLETE — STOP_WAITING_FOR_VALIDATION

---

## Mission

F22A concluded that Clavage, Verbatia, LU-MH, Agent Vecteur, and harmonic protocols were "MISSING — DOC ONLY"
based only on a working-tree grep. F22A2 extends the search to: git log -S (string introduction), git log --grep
(commit messages), remote branches, parent directory, candidate zip namelists, docs/runtime/archive, and full
MMONDE periphery tree listing. The question is whether these protocols exist in any form in git history, zips,
or branches before concluding MISSING_CONFIRMED.

---

## Methodology

| Method | Scope | Tool |
|--------|-------|------|
| A | Working-tree grep | `grep -rli` on apps/, periphery/, scripts/, docs/ |
| B | Git string-intro search | `git log --all -S <term>` |
| C | Git commit-message search | `git log --all --grep=<term>` |
| D | Remote branch ls-tree | `git branch -r` + `git ls-tree -r --name-only <branch>` |
| E | Parent directory listing | `ls obsidia-engine-proof-core/` |
| F | Candidate zip namelist | `zipfile.ZipFile.namelist()` for candidate_packs/ and freezes/ |
| G | docs/runtime/archive scan | `rglob("*")` on docs/runtime/archive/ |
| H | MMONDE full tree | `find periphery/OBSIDIA_MMONDE_*/` |
| I | Runtime module references | `grep` in brody_cognitive_modules_adapter.py, semantic_query_router.py, true_voice_adapter.py |

---

## Protocol Trace Matrix

### 1. Clavage

| Field | Value |
|-------|-------|
| F22A status | MISSING — DOC ONLY |
| F22A2 verdict | **DOC-CONFIRMED** |
| F22A correction | NONE — "MISSING" wording acceptable; doctrinal grounding now confirmed |
| Standalone Python module | NO |
| In git history (git -S) | NO — empty result for all terms |
| In candidate zips | NO — checked ZIP2 IR_SHAZAM (118 entries), FULL_STACK_V2 (290 entries) |
| In MMONDE source docs | **YES** — `01_SOURCES/extracted_text_all.md` lines 28, 120-141, 2256-2258, 6216, 6350-6357 |
| In runtime adapters | NO |

Evidence from `extracted_text_all.md`:
- Line 28: "Sigma (LTCU+): Le Silencieur Sémantique et l'Agent Clavage lisent la couche Symbolique..."
- Line 121: "L'Agent CLAVAGE est le 'watchdog syntaxique' (le gardien d'exécution stricte) de cette couche"
- Lines 123-141: Python stub in doc: `def agent_clavage(raw_llm_output, expected_lumh_schema)` with `CLAVAGE_BLOCK`
- Line 6357: `Clavage = découpe stricte non ambiguë`

**Conclusion**: Clavage is a doctrinal middleware concept with a code example in source docs. No standalone Python module exists or was ever in git history. F22A "MISSING — DOC ONLY" → upgraded to **DOC-CONFIRMED** (stronger provenance established).

---

### 2. Verbatia

| Field | Value |
|-------|-------|
| F22A status | MISSING — DOC ONLY |
| F22A2 verdict | **RUNTIME-MAPPED** |
| F22A correction | **F22A INCORRECT** — Verbatia is actively mapped in runtime, not missing |
| Standalone Python module | NO (covered by brody_true_voice_adapter.py) |
| In git history (git -S) | NO |
| In MMONDE source docs | YES — extracted_text_all.md lines 6216, 6350-6357 |
| In runtime adapters | **YES** — three files |

Evidence in runtime:
- `apps/obsidia_api/brody_cognitive_modules_adapter.py:29`:
  `{"name": "Verbatia", "resolution": "FULLY_BRANCHED", "covered_by": "brody_true_voice_adapter.py", "branchable": True, "active": True}`
- `apps/obsidia_api/brody_cognitive_modules_adapter.py:40`:
  `_PRESENT_MODULES = ["Verbatia", "Inference_Aubin", "Cristal_Sortie", "MEMZUM"]`
- `apps/obsidia_api/brody_semantic_query_router.py:149`:
  `"Brody cognitive modules AVDR Continuum Verbatia"` + `["avdr", "verbatia", "memzum", "cognitive_layers"]`
- `apps/obsidia_api/brody_true_voice_adapter.py:739`:
  `"Verbatia (parole Brody/True Voice), MEMZUM (memoire projet/session/Graphiti)"`

**Conclusion**: Verbatia is **RUNTIME-MAPPED** with `resolution=FULLY_BRANCHED`. It is not missing — it is the conceptual name for Brody's True Voice layer, implemented by `brody_true_voice_adapter.py`. **F22A "MISSING — DOC ONLY" is INCORRECT.**

---

### 3. LU-MH (Langage Universel Machine-Humain)

| Field | Value |
|-------|-------|
| F22A status | MISSING — DOC ONLY |
| F22A2 verdict | **DOC-CONFIRMED** |
| F22A correction | NONE — "MISSING" wording acceptable |
| Standalone Python module | NO |
| In git history (git -S) | NO |
| In MMONDE source docs | **YES** — extracted_text_all.md lines 121, 466, 6353, 6354, 6442 |
| In runtime | NO |

Evidence from `extracted_text_all.md`:
- Line 121: "Le LU-MH (Langage Universel Machine-Humain) est la base formelle de toute transmission propre dans Obsidia"
- Line 6353: `LU-MH = LangageUniversel_{Machine↔Humain}` (formal definition)
- Line 6355: `TexteHumain → Verba → Entie → Clavage → Verbatia → IR` (pipeline diagram)
- Line 6442: LU-MH appears in the Mmonde closed-form formula

**Conclusion**: LU-MH is the formal language standard for Obsidia. No standalone module. DOC-CONFIRMED with formal mathematical definition. F22A "MISSING" acceptable but weak — now upgraded to **DOC-CONFIRMED**.

---

### 4. Agent Vecteur

| Field | Value |
|-------|-------|
| F22A status | MISSING — DOC ONLY |
| F22A2 verdict | **DOC-CONFIRMED** |
| F22A correction | NONE — "MISSING" wording acceptable |
| Standalone Python module | NO |
| In git history (git -S) | NO |
| In MMONDE source docs | **YES** — extracted_text_all.md lines 6195, 6213-6216, 6345, 6452, 6521 |
| In runtime | NO |

Evidence from `extracted_text_all.md`:
- Line 6213: "I. Alphabet IR + Agent Vecteur"
- Line 6214: "→ OS L2 / VERBATIA / traduction intention → IR"
- Line 6345: "Agent Vecteur :" (dedicated section)
- Line 6442: `AgentVecteur` appears in Mmonde closed-form formula
- Line 6521: "L'Agent Vecteur traduit l'intention en structure."

**Conclusion**: Agent Vecteur is the intention-to-structure translator in OS L2. No standalone Python module. No git history. DOC-CONFIRMED in Mmonde sources.

---

### 5. Harmonic vote / harmonisation

| Field | Value |
|-------|-------|
| F22A status | MISSING — DOC ONLY |
| F22A2 verdict | **DOC-CONFIRMED** |
| F22A correction | NONE — "MISSING" wording acceptable |
| Standalone Python module | NO |
| In git history (git -S) | NO |
| In MMONDE source docs | **YES** — extracted_text_all.md lines 99, 6442 |
| In runtime | NO |

Evidence from `extracted_text_all.md`:
- Line 99: `if validate_harmonic_mean(thought.tree_coordinates) < 0.1:` (code stub in doc)
- Line 6442: `Harmonisation` appears in Mmonde closed-form formula

**Conclusion**: Harmonic metrics appear as a code stub in the source docs and in the Mmonde formula. No standalone Python module. No git history. DOC-CONFIRMED.

---

### 6. Continuum / Zone Latente

| Field | Value |
|-------|-------|
| F22A status | PARTIAL — periphery subdirectory, README only |
| F22A2 verdict | **CODE-CONFIRMED-STUB** |
| F22A correction | **F22A INCORRECT** — real Python code exists, not just README |
| Standalone Python module | **YES** — `continuum_node.py` (dataclass), stub functions in 12_FRICTION_AVDR_CONTINUUM/ |
| In git history | YES — present since BRODY_F9 tag |
| In MMONDE source docs | YES — extracted_text_all.md line 6442 |
| In runtime | NO — not wired to Brody runtime |

Evidence:

`periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/continuum_node.py`:
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class NodeContinuum:
    id: str
    description: str
    event_ids: List[str] = field(default_factory=list)
    divergence: float = 0.0
    non_decision: bool = True
```

`periphery/.../12_FRICTION_AVDR_CONTINUUM/` Python files (real stubs):
- `avdr.py`: `def evaluate(agent, task): return {"phase": "AVDR_CONTEXT_ONLY", "non_decision": True}`
- `friction_symbolique.py`: `def friction(val_logique, val_diffusif): return abs(float(val_logique) - float(val_diffusif))`
- `check_incoherence.py`: `def check(value, threshold=0.15): return float(value) > threshold`
- `oban_rollback.py`: placeholder
- `compress_nodes.py`: placeholder

Also present: `reflex_reducer.py`, `event_model.py`, `timeline.py` in `03_MEMOIRE_MONDE_COSMOS_REFLEX/`.

**Conclusion**: Continuum is **CODE-CONFIRMED-STUB** — real Python dataclasses and stub functions exist in periphery. Not wired to runtime. **F22A "README only" is INCORRECT.**

---

### 7. RUNTIME_STATE_READONLY

| Field | Value |
|-------|-------|
| F22A status | MISSING CATEGORY (gap in rights matrix) |
| F22A2 verdict | **ABSENT** |
| F22A correction | NONE — gap identification correct |
| In git history (git -S) | NO |
| In runtime | NO |
| In MMONDE source docs | NO |

**Conclusion**: RUNTIME_STATE_READONLY has never existed anywhere. Must be created in F22B fix.

---

## Git Archaeology Summary

### Method B: git log --all -S results

| Protocol / Term | Result |
|----------------|--------|
| clavage | EMPTY — never introduced via git commit |
| verbatia | EMPTY — never introduced via git commit |
| lu-mh / lu_mh | EMPTY — never introduced via git commit |
| agent vecteur | EMPTY — never introduced via git commit |
| harmonic vote | EMPTY — never introduced via git commit |
| RUNTIME_STATE_READONLY | EMPTY — never introduced via git commit |
| continuum (as string) | EMPTY via -S (note: files ARE in working tree from initial add) |

### Method D: Remote branches

Branches checked: `agentic-registry-bootstrap-isolated`, `ci-strict-sigma-qa-no-false-error_20260502_235213`,
`cleanup/public-audit-surface-20260427-222310`, `repo-hygiene-drop-noncanonical-from-git`,
`repo-hygiene-isolate-noncanonical`, `tooling/graph-memory-sandbox`.

No protocol-specific Python modules found in any remote branch tree.

### Method F: Candidate zip scan

- `OBSIDIA_ENGINE_CANDIDATE_ZIP2_IR_SHAZAM_TREE34_AGENTS52_X108_READONLY_V1.zip` (118 entries): NO protocol hits
- `OBSIDIA_X108_FULL_STACK_COMPLETE_ENGINE_AGENTS_ACT_PATCH_V2.zip` (290 entries): NO protocol hits

No standalone `clavage.py`, `verbatia.py`, `lu_mh.py`, `agent_vecteur.py` found in any zip.

---

## F22A Corrections

Two corrections to F22A:

### Correction 1: Verbatia

- F22A: `"status": "MISSING — DOC ONLY"`
- F22A2: **RUNTIME-MAPPED** (`covered_by: brody_true_voice_adapter.py`, `resolution: FULLY_BRANCHED`)
- Impact: Verbatia concept is already implemented. F22B fix does NOT need to create a Verbatia module.

### Correction 2: Continuum / Zone Latente

- F22A: `"status": "PARTIAL — periphery subdirectory, README only"`
- F22A2: **CODE-CONFIRMED-STUB** — `continuum_node.py` is a real dataclass; AVDR/Friction/OBAN have real stub functions
- Impact: Continuum code exists in periphery. Still not wired to runtime. Does not affect F22B scope.

---

## Impact on F22B

F22A2 findings do NOT change the F22B fix scope. The three false positive paths (Clavage substring bug,
actifs substring bug, missing RUNTIME_STATE_READONLY category) remain exactly as diagnosed in F22A.

The Verbatia mapping confirms that `brody_true_voice_adapter.py` is the True Voice / Verbatia layer — which
aligns with OPTION_C: the proposed `brody_readonly_intent_guard.py` should run before domain raccord and
before `brody_true_voice_adapter.py`.

---

## Boundary

```
KX108_ONLY=true
readonly=true
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
kernel_mutation=false
x108_mutation=false
```

---

## STOP — WAITING_FOR_VALIDATION

F22A2 archaeology complete. No patch. No commit. No runtime change.

Awaiting user validation before F22B.

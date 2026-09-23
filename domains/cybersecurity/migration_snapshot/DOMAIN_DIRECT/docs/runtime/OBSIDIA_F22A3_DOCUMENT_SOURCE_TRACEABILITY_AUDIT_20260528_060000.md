# OBSIDIA F22A3 — Document Source Traceability Audit

Date: 20260528_060000
CHECKPOINT: F22A3_DOCUMENT_SOURCE_TRACEABILITY_AUDIT
MODE: READ_ONLY
STATUS: AUDIT_COMPLETE — STOP_WAITING_FOR_VALIDATION

---

## Mission

Map each of the 15 canonical source documents (from `C:/Users/User/Desktop/Nouveau dossier/`) to
actual runtime code in `obsidia-x108-proofs_REMOTE_A5F21C6B`. For every concept extracted: find
the best-matching repo artifact, classify its status, determine F22B relevance, and record the
evidence. Conclude with a single OPTION A/B/C/D recommendation.

No patch. No commit. No runtime change.

---

## Document Catalog (15 / 15 found locally)

| ID | Document title |
|----|----------------|
| Doc01 | Cahier des Charges Stratégique — BluePrint Global de l'OS Cognitif Obsidia X-108 |
| Doc02 | Forge du Langage Aligné – Protocoles Verbatia, Entie, Clavage, Verba, LU-MH & Benchmark |
| Doc03 | Guide de Référence du Métalangage LTO-16D — L'Architecture des 16 Dimensions Cognitives |
| Doc04 | L'Architecture de Souveraineté Éthique — Protocole LUX.CON et AEG |
| Doc05 | L'Agent Clavage — L'Architecture JAX du Pare-feu Sémantique |
| Doc06 | L'Architecture Algorithmique de l'OS Cognitif Obsidia |
| Doc07 | Le Reverse OS — La Narration Jarvis — Du Code Technique au Sens Humain |
| Doc08 | Loi de cohérence et sélection structurelle du réel |
| Doc09 | Loi_Obsidia_Automatisation_Universelle |
| Doc10 | Obsidia — L'Architecture Organique et Procédurale de l'OS Cognitif |
| Doc11 | Obsidia — L'Éveil de l'OS Cognitif et Apprentissage Organique |
| Doc12 | Obsidia_SCF_Watermark_Reciproque |
| Doc13 | Obsidia_Symphonie_Harmonisation_Universelle_Rapport |
| Doc14 | Roadmap Technique — De l'Audit Board au 'Jarvis' (OS Cognitif) Obsidia X-108 |
| Doc15 | Le Protocole de Vote Immuable — L'Arbitrage par Moyenne Harmonique |

All 15 documents present locally. Extracted content available via `extracted_text_all.md`
(`periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/`) indexing all 18
docx (15 from catalog + 3 auxiliary).

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `CODE_RUNTIME_CONNECTED` | Module exists and is wired into the active Brody response pipeline |
| `CODE_DORMANT` | Real code exists but not active in runtime (`_FUTURE_MODULES` or no caller) |
| `CODE_STUB` | Python file exists but only placeholder logic (`return True`, 1-line) |
| `DOC_ONLY` | Concept appears only in source docs / extracted_text_all.md, no Python module |
| `FOUND_UNDER_OTHER_NAME` | Concept implemented under a different identifier in the runtime |
| `MISSING` | Zero hits in working tree, git history, zips, and remote branches |

---

## Concept-to-Code Traceability Matrix

### Doc01 — BluePrint Global (11 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Kernel (Orchestrateur central) | `apps/obsidia_api/routes/x108.py` + `proofs/V18_3_1/` | `CODE_RUNTIME_CONNECTED` | NO |
| Couche Sigma | `sigma/contracts.py` + `brody_gencoin_transverse_interface.py` | `CODE_RUNTIME_CONNECTED` | NO |
| Reverse OS | `apps/obsidia_api/brody_existing_reverse_os_bridge.py` | `CODE_RUNTIME_CONNECTED` | NO |
| Subsumption Architecture | — | `MISSING` | NO |
| Constitution numérique (O1–O8) | `periphery/test_constitution_o1_o8.py` | `CODE_STUB` | NO |
| Cohérence temporelle Delta T | `routes/x108.py::delta_tau` | `CODE_RUNTIME_CONNECTED` | INDIRECT |
| Agents d'Analyse / Gardiens | `periphery/gardiens_fond/readonly_context_guard.py` (stub `return True`) | `CODE_STUB` | INDIRECT |
| Agents de Mémoire / Totems | `brody_cognitive_modules_adapter.py` — MEMZUM=FULLY_BRANCHED | `FOUND_UNDER_OTHER_NAME` | NO |
| Agents d'Action / Spectres | — | `MISSING` | NO |
| Moyenne Harmonique | `sigma/contracts.py::readiness_scope='harmonic_integrity_governance'` (label only) | `CODE_DORMANT` | NO |
| Veto Formel Lean 4 | `sigma/contracts.py::AgentVote.vote` (HOLD/ALLOW/BLOCK structure only) | `CODE_DORMANT` | NO |

**Key finding**: `readonly_context_guard.py` in `periphery/gardiens_fond/` has exactly the right name
for the F22B guard, but its body is `def guard(): return True` — a non-functional stub. It CANNOT
be reused as-is for Option B.

---

### Doc02 — Forge du Langage Aligné (8 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| CLAVAGE (watchdog syntaxique) | `extracted_text_all.md` lines 28, 120–141, 6216, 6350–6357 | `DOC_ONLY` | INDIRECT |
| Verbatia | `brody_true_voice_adapter.py` — resolution=FULLY_BRANCHED | `CODE_RUNTIME_CONNECTED` | NO |
| Verba (unité verbale) | — | `DOC_ONLY` | NO |
| Entie (entité de sens) | — | `DOC_ONLY` | NO |
| LU-MH | `extracted_text_all.md` lines 121, 466, 6353–6355, 6442 | `DOC_ONLY` | INDIRECT |
| Benchmark d'alignement | — | `DOC_ONLY` | NO |
| Divergence intention/sortie | `apps/obsidia_api/brody_anti_mismatch_signal.py` | `CODE_RUNTIME_CONNECTED` | INDIRECT |
| Totem de Pure Exécution | `brody_cognitive_modules_adapter.py` — MEMZUM=FULLY_BRANCHED | `FOUND_UNDER_OTHER_NAME` | NO |

**Key finding**: Verbatia is `RUNTIME-MAPPED` (F22A2 correction confirmed). `brody_true_voice_adapter.py`
implements it under `FULLY_BRANCHED`. F22B must NOT modify this file.

---

### Doc03 — LTO-16D (3 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| LTO-16D (Langage Total Obsidien) | `docs/REPO_BOUNDARY.md` line 85 (explicitly excluded) | `DOC_ONLY` | INDIRECT |
| D1 Intention / D16 Action | — | `DOC_ONLY` | INDIRECT |
| Texte ≠ décision | `routes/brody.py` — `BOUNDARY: allowed_to_decide=False, advisory_only=True` | `FOUND_UNDER_OTHER_NAME` | **DIRECT** |

**Key finding**: LTO-16D is explicitly outside this repo (`REPO_BOUNDARY.md` line 85:
"Hors périmètre public"). But its core principle — D1 Intention never equals D16 Action,
"texte ≠ décision" — is the doctrinal basis for the F22B intent guard. The false positive
bug misclassifies D1 (readonly description intent) as D16 (write action). This validates Option C.

---

### Doc04 — LUX.CON et AEG (6 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| LUX.CON (Protocole) | — | `MISSING` | NO |
| AEG (Auto-Ethical Gradient) | `periphery/gardiens_fond/aeg_guard.py` (stub: `return value >= threshold`) | `CODE_STUB` | NO |
| O1 Non-Action / O8 Séparation | `periphery/test_constitution_o1_o8.py` (tests only) | `CODE_DORMANT` | INDIRECT |
| LLM propose / Obsidia dispose | `routes/brody.py` — `decision_authority=KX108_ONLY` | `FOUND_UNDER_OTHER_NAME` | NO |
| Friction symbolique | `periphery/.../12_FRICTION_AVDR_CONTINUUM/friction_symbolique.py` (1-line stub) | `CODE_STUB` | NO |
| Feedback AVDR | `periphery/gencoin_sandbox/avdr_phase_mapper.py` (active=False) | `CODE_DORMANT` | NO |

---

### Doc05 — Agent Clavage / JAX (4 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Agent Clavage (JAX-based) | — | `DOC_ONLY` | NO |
| cosine_similarity / Agent Vecteur | `periphery/cosine_similarity.py` (pure math, no ML) | `CODE_DORMANT` | NO |
| strict_parser / seuil 0.15 | `periphery/.../12_FRICTION_AVDR_CONTINUUM/check_incoherence.py` — `check(value, threshold=0.15)` | `CODE_STUB` | NO |
| LU-MH schema validation | — | `DOC_ONLY` | NO |

**Key finding**: Agent Clavage requires JAX/XLA dependencies not present in this repo. Full Clavage
implementation is a 200+ line ML pipeline. The F22B bug is a 3-line regex fix — Clavage is not
needed and is explicitly DEFERRED.

---

### Doc06 — Architecture Algorithmique (3 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| ERA formula (M+R+A/F) | `brody_cognitive_modules_adapter.py` — `DESIGN_SPEC_NOT_IMPLEMENTED` | `DOC_ONLY` | NO |
| Pipeline cognitif | `apps/obsidia_api/brody_real_response_pipeline.py` | `CODE_RUNTIME_CONNECTED` | INDIRECT |
| Métriques structurelles | `brody_gencoin_transverse_interface.py` + `sigma_packet` | `CODE_RUNTIME_CONNECTED` | NO |

**Key finding**: ERA is intentionally marked `DESIGN_SPEC_NOT_IMPLEMENTED` in the cognitive modules
adapter — this is by design, not a gap.

---

### Doc07 — Narration Jarvis (6 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Reverse OS / Narration Jarvis | `brody_existing_reverse_os_bridge.py` — F18B wired | `FOUND_UNDER_OTHER_NAME` | NO |
| reason_codes | `brody_existing_reverse_os_bridge.py` — RC_X108_REQUIRED / RC_CONTEXT_ONLY | `CODE_RUNTIME_CONNECTED` | NO |
| Dictionnaire Sémantique | `brody_semantic_query_router.py::build_semantic_query()` | `FOUND_UNDER_OTHER_NAME` | INDIRECT |
| Merkle Proof lisible | `proofs/V18_3_1/` + `sigma/` | `CODE_RUNTIME_CONNECTED` | NO |
| Spectres (agents d'action) | — | `MISSING` | NO |
| Totems (agents de mémoire) | `brody_cognitive_modules_adapter.py` — MEMZUM=FULLY_BRANCHED | `FOUND_UNDER_OTHER_NAME` | NO |

---

### Doc08 — Loi de Cohérence Structurelle (3 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Temps comme opérateur éliminatoire | `routes/x108.py::delta_tau` | `CODE_RUNTIME_CONNECTED` | INDIRECT |
| Sélection par non-effondrement / cohérence | `sigma/contracts.py::KernelReadinessProof` | `CODE_DORMANT` | INDIRECT |
| IA opérant dans espace déjà sûr | `routes/brody.py` — `KX108_ONLY + advisory_only=True` | `FOUND_UNDER_OTHER_NAME` | **DIRECT** |

**Key finding**: Doc08 law "IA dans espace déjà sûr / cognition ne corrige pas structure" = the
doctrinal basis for the readonly boundary. The false positive bug VIOLATES this law: it fires a
`MEMORY_WRITE_CANON_FREEZE` boundary on a purely cognitive/advisory read request. DIRECT relevance
to F22B.

---

### Doc09 — Automatisation Universelle (2 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Boucle active / métriques de justesse | `brody_automation_orchestrator.py` (active=False) | `CODE_DORMANT` | NO |
| Sandbox cognitive | `periphery/gencoin_sandbox/` | `FOUND_UNDER_OTHER_NAME` | NO |

---

### Doc10 — Architecture Organique (6 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Shazam Cognitif | `periphery/shazam_cognitif.py` (blocked: `spectral_hash` import missing) | `CODE_DORMANT` | NO |
| Zone Latente / Continuum / NodeContinuum | `periphery/.../03_MEMOIRE_MONDE_COSMOS_REFLEX/continuum_node.py` (dataclass, not runtime) | `CODE_STUB` | NO |
| RAM intelligente | `brody_candidate_memory_adapter.py` + `brody_session_memory_adapter.py` | `FOUND_UNDER_OTHER_NAME` | NO |
| Zone Réflexe | `periphery/.../03_MEMOIRE_MONDE_COSMOS_REFLEX/reflex_reducer.py` (stub) | `CODE_STUB` | NO |
| Emergency Gate | — | `MISSING` | LATER |
| Invariant dynamique | — | `DOC_ONLY` | NO |

**Key finding (F22A2 correction)**: `continuum_node.py` is a real Python dataclass
(`NodeContinuum` with id, description, event_ids, divergence, non_decision). F22A "README only"
was incorrect. Still: not wired to runtime, no F22B action needed.

---

### Doc11 — Éveil Organique (2 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Apprentissage organique | `periphery/agents/feedback_memory_agent.py` | `CODE_DORMANT` | NO |
| Auto-évolution contrôlée | `periphery/agents/gencoin_value_agent.py` | `CODE_DORMANT` | NO |

---

### Doc12 — SCF Watermark (2 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| SCF_ID / TWIN_CALL / CLE_REACTIVATION | — | `MISSING` | NO |
| Traçabilité cognitive | `audit/world_action_bus.jsonl` + `_local_audits/` | `FOUND_UNDER_OTHER_NAME` | NO |

---

### Doc13 — Symphonie Harmonisation (3 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Harmonisation universelle / accordeur fractal | — | `DOC_ONLY` | NO |
| Balance Exponentielle | `brody_domain_raccord_adapter.py:327` (domain trigger keyword) | `FOUND_UNDER_OTHER_NAME` | NO |
| Métriques harmoniques | `sigma/contracts.py::readiness_scope='harmonic_integrity_governance'` | `CODE_DORMANT` | NO |

---

### Doc14 — Roadmap Jarvis (5 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| Audit Board | — | `MISSING` | NO |
| Trinity Stable | — | `MISSING` | NO |
| Merkle seal / 8007 preuves | `proofs/V18_3_1/` | `CODE_RUNTIME_CONNECTED` | NO |
| Sigma bridge central | `sigma/` + `brody_gencoin_transverse_interface.py` | `CODE_RUNTIME_CONNECTED` | NO |
| Dashboard Jarvis / cockpit opérateur | `routes/runtime_freeze.py` + `brody_operator_view_packet.py` (F21B) | `FOUND_UNDER_OTHER_NAME` | NO |

---

### Doc15 — Protocole de Vote Immuable (3 concepts)

| Concept | Repo path | Status | F22B relevance |
|---------|-----------|--------|----------------|
| calculate_immutable_vote (moyenne harmonique) | — | `MISSING` | NO |
| Veto (threshold 0.4 / VETO_TRIGGERED_BELOW) | `sigma/contracts.py::AgentVote.vote` (structure only) | `CODE_DORMANT` | NO |
| CRITICAL_FAILURE_ZERO_SCORE / REJECTED_LOW_COHERENCE | — | `MISSING` | NO |

---

## Audit Summary

| Status | Count | % |
|--------|-------|---|
| `CODE_RUNTIME_CONNECTED` | 13 | 19 % |
| `FOUND_UNDER_OTHER_NAME` | 13 | 19 % |
| `CODE_DORMANT` | 12 | 18 % |
| `DOC_ONLY` | 12 | 18 % |
| `CODE_STUB` | 7 | 10 % |
| `MISSING` | 10 | 15 % |
| **Total concepts mapped** | **67** | 100 % |

- **Docs locally found**: 15 / 15
- **Best reuse candidate for F22B**: NONE_USABLE — `readonly_context_guard.py` has the right name but body is `return True`

---

## F22B Impact Analysis

### Q1 — Does any existing module fix the read/write classification bug?
**PARTIAL.** `periphery/gardiens_fond/readonly_context_guard.py` has exactly the right name but is
a `return True` stub. The architecture is valid — `gardiens_fond/` is the correct home for a
readonly intent guard — but the stub cannot be reused as-is.
**Conclusion**: A new module (`brody_readonly_intent_guard.py`) is required.

### Q2 — Is Clavage needed for the F22B fix?
**NO.** Clavage requires JAX/XLA, cosine similarity on embedding vectors, LU-MH schema
validation, and a full ML pipeline. The false positive bug is a 3-line word-boundary regex fix.
Clavage is DEFERRED post-F22B.

### Q3 — Must Verbatia / brody_true_voice_adapter.py be modified?
**NO.** Verbatia = `FULLY_BRANCHED` = `brody_true_voice_adapter.py`. The bug is upstream of
Verbatia (in `has_memory_write_request()` and `_risk_flags()`), before True Voice runs.
Do not touch `brody_true_voice_adapter.py`.

### Q4 — Must Continuum be branched?
**NO.** `brody_cognitive_modules_adapter.py` already shows Continuum = `COVERED_BY_EXISTING_MODULE`
via `session_memory_snapshot + temporal_context_snapshot`. No branching needed for F22B.

### Q5 — Is harmonic mean needed for F22B?
**NO.** Doc15 harmonic vote is for multi-agent consensus on decision verdicts. F22B is about
intent classification (READ vs WRITE). Orthogonal concerns. Harmonic vote is DEFERRED.

### Q6 — Does LTO-16D impose a rule on F22B?
**INDIRECT.** LTO-16D D1→D16 "texte ≠ décision" validates the guard design (a readonly
description request is D1 Intention, never D16 Action). LTO-16D is explicitly excluded from this
repo (`REPO_BOUNDARY.md` line 85). No LTO-16D code is added — only the principle is used as
doctrinal justification for Option C.

### Q7 — Is the minimal guard (Option C) the best solution?
**YES — OPTION C.** No existing module provides intent disambiguation with word-boundary matching
and `RUNTIME_STATE_READONLY` category. `readonly_context_guard.py` is a non-functional stub.
Option C provides 5 surgical changes that fix all three false positive sources.

---

## Recommendation

**OPTION C — Guard minimal RUNTIME_STATE_READONLY + correctifs faux positifs**

### Components

1. **NEW** `apps/obsidia_api/brody_readonly_intent_guard.py` — `detect_readonly_runtime_state_intent()`
2. **FIX** `brody_domain_raccord_adapter.py::has_memory_write_request()` — word-boundary for `"ecris"` (eliminates `"decris"` → `"ecris"` false positive)
3. **FIX** `brody_v1_4_12a_final_answer_adapter.py::_QUERY_OVERRIDES` — add FR terms: `"decris"`, `"decrire"`, `"etat systeme"`, `"lecture seule"`, `"statut"`, `"diagnostic"`, `"readonly"`
4. **FIX** `routes/os_trad_ir_reverse.py::_risk_flags()` — `re.search(r'\bact\b', low)` instead of `"act" in low` (eliminates `"actifs"` false positive)
5. **WIRE** `routes/brody.py` — expose `readonly_intent_guard_packet` in response

### Why not the alternatives

| Option | Verdict | Reason |
|--------|---------|--------|
| A — faux positifs seuls | INSUFFICIENT | No `RUNTIME_STATE_READONLY` category; domain raccord still routes incorrectly |
| B — réutiliser module existant | BLOCKED | `readonly_context_guard.py` is `return True` — not functional |
| C — guard minimal | **SELECTED** | 5 surgical changes, provably correct, aligns with LTO-16D + Doc08 |
| D — refactor complet | FORBIDDEN | Explicitly excluded; unnecessary for substring fix |

### Doctrinal basis

- LTO-16D D1/D16: "texte ≠ décision" — a description request is pure cognitive intent (D1), never an action (D16)
- Doc08: "IA opérant dans espace déjà sûr" — triggering `MEMORY_WRITE_CANON_FREEZE` on a readonly intent violates this law
- KX108_ONLY boundary: `allowed_to_decide=False, advisory_only=True` — already enforced at the BOUNDARY layer but not at intent classification

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

F22A3 document source traceability audit complete.
No patch. No commit. No runtime change.

Awaiting user validation before F22B.

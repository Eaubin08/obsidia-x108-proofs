# R6 — SENS / COGNITION — CANONICAL AUDIT V0

Status: AUDIT / SOURCE CONVERGENCE  
Base: `feat/premiere-mise-au-monde-public-freeze-rc-v0`  
Decision authority: `KX108_ONLY`  
Runtime mutation: NONE in this checkpoint

## 1. Purpose

R6 reopens SENS/Cognition after the public freeze without creating a new LLM architecture.

Canonical cognitive policy remains:

```
human input
→ Brody cognition / comprehension
→ structured semantic context
→ Qwen only when Brody routes to it
→ GMS / MMonde projections where applicable
→ domain/governance boundary
→ KX108_ONLY
→ receipt / replay
```

Brody, Qwen, SENS, GMS, MMonde, and KX108 remain different layers. No cognitive layer gains execution authority.

## 2. Current canonical assets already present in the freeze

### Brody runtime

`apps/obsidia_api/brody_real_response_pipeline.py`

Already provides a readonly/non-sovereign response pipeline with:
- pre-reasoning epistemic gate;
- pre-response calibration;
- pre-action calibration;
- final sense halo;
- readonly memory/context handling;
- no ACT, no verdict, no memory write;
- `decision_authority=KX108_ONLY`.

This is the canonical Brody integration surface to preserve.

### GMS / world trajectory

`periphery/gms/trajectory_adapter_v0.py`

Already provides:
- readonly 21D semantic points;
- explicit N→N+1 semantic transitions;
- trajectory construction;
- uncertainty / contradiction / provenance refs;
- no decision / no action.

The historical GMS trajectory branch is fully behind the public freeze and has no unique commits relative to it. Therefore GMS is treated as already absorbed, not re-imported.

## 3. Historical/source branches classification

### A. `exp/semantic-grammar-cognitive-lattice-v0`

Classification:

`RESEARCH_SOURCE / DO_NOT_MERGE_AS_IS`

It has no common ancestor with the current public-freeze lineage and must be treated as an external source corpus, not a merge candidate.

Its independent forensic audit explicitly classifies it as:

`USEFUL_NON_SOVEREIGN_EXPERIMENT_NOT_CANONICAL_RUNTIME`

Useful primitives include:
- `PredicateUnit`;
- `UtteranceFrame`;
- typed relations;
- semantic projections;
- explicit `NO_PROVEN_CONNECTION`;
- clause-scoped negation/modality;
- event references;
- occurrence claim/derivation;
- epistemic and provenance structures.

Known problems from the forensic audit:
- bounded lexical/grammar coverage;
- overfit risk;
- semantic information loss during `UnifiedInputIR` projection;
- legacy WORLD_ACTION / gate mismatch;
- governance behavior changed by indirect-execution handling;
- temporal semantics are linguistic, not full knowledge chronology;
- causality remains descriptive/claimed, not proved.

Therefore no router/gate/governance behavior is imported directly from this branch.

### B. `feat/stack-launcher-terminal-brody-obsidure-v0`

Classification:

`HISTORICAL_RUNTIME_SOURCE / SELECTIVE_AUDIT_ONLY`

Relative to public freeze it is diverged, with a small number of unique commits but a large historical gap. It also mixes Brody, Obsidure, GPS, launchers, and other runtime concerns. It is not a clean R6 base.

### C. `feat/premiere-mise-au-monde-gms-trajectory-adapter-v0`

Classification:

`ABSORBED_IN_FREEZE`

No unique commits relative to public freeze. Do not rebuild.

## 4. SENS dependency chain

Canonical R6 ordering:

```
IDENTITY
→ PROVENANCE
→ RELATIONS
→ PROJECTIONS
→ FLOWS
→ PATHS
→ REVIEW
→ SEMANTIC CLOSURE
→ BRODY REINTEGRATION
→ ADVERSARIAL E2E
```

This ordering is mandatory because later cognition must not reconstruct identity, provenance, causality, or truth status implicitly.

## 5. Canonical SENS milestones

- SENS-01 — ReviewEnvelope provenance + epistemic source
- SENS-02 — relation status structural / non-truth-bearing
- SENS-03 — forensic audit / stable source freeze
- SENS-04 — full-frame cognitive/event identity
- SENS-05 — multi-branch semantic coordination
- SENS-06 — reference / anaphora expansion
- SENS-07 — factivity doctrine
- SENS-08 — sourceful EpistemicRecord
- SENS-09 — TemporalProjection with distinct utterance/event/observation/report/knowledge times
- SENS-10 — CausalRelation: claimed vs supported; temporal != causal
- SENS-11 — Contradiction + UnresolvedItem; no implicit winner
- SENS-12 — common CognitiveObject / Projection / TypedRelation contracts
- SENS-13 — CognitivePath with candidate/support/conflict/rejected/closed states
- SENS-14 — ARM reconstruction with evidence vs inference separation
- SENS-15 — PatternCandidate + CognitiveRoleSpec
- SENS-16 — CRFIPROC/path reuse + heuristics as R&D only
- SENS-17 — ReviewJoin V1
- SENS-18 — Semantic Closure
- SENS-19 — Brody reintegration consuming structured context
- SENS-20 — end-to-end adversarial audit

## 6. Live finding to integrate: Semantic Focus / Query Roles

Observed failure class:

`PRESENCE_OF_CONCEPT != SEMANTIC_ROLE`

A request such as:

`explain what you know in memory about Obsidia`

must not collapse to:

`TOPIC=OBSIDIA, MEMORY_REQUIRED=true`.

Minimum semantic role projection:

```
FOCUS
SCOPE
OPERATION
QUALIFIER
SOURCE_OR_INSTRUMENT
```

This is not a new router and not a final ontology. It is a semantic relation layer that must feed the existing Brody/cognitive routing surfaces.

## 7. Import boundary

Allowed from the experimental lattice:
- immutable descriptive primitives;
- explicit unresolved/ambiguous states;
- typed structural relations;
- provenance fields;
- occurrence claim/derivation concepts;
- semantic-role concepts;
- tests/corpora as adversarial fixtures.

Forbidden direct import:
- legacy gate decisions;
- lexical ALLOW/HOLD behavior;
- execution semantics;
- any change granting LLM authority;
- any memory write path;
- any inference that turns linguistic causality into physical/proved causality;
- branch-level merge.

## 8. First implementation gate

R6 does NOT start by importing the whole lattice.

First build target:

`R6-A — Semantic Role / Focus Contract V0`

It should:
1. represent FOCUS / SCOPE / OPERATION / QUALIFIER / SOURCE_OR_INSTRUMENT;
2. preserve UNKNOWN / AMBIGUOUS;
3. be readonly and non-sovereign;
4. carry provenance back to raw input spans or source refs;
5. not route, decide, call tools, or write memory;
6. integrate additively into Brody context;
7. be tested against the live memory-vs-topic ambiguity finding;
8. preserve current Brody and KX108 behavior byte/semantics-wise outside the additive context field.

## 9. Closure criteria for R6-A

R6-A can be VERIFIED only when:
- focused unit tests pass;
- ambiguity/adversarial tests pass;
- existing Brody readonly tests pass;
- GMS/MMonde adapters remain unaffected;
- no new execution authority exists;
- no memory write exists;
- no KX108 behavior is changed;
- a real Brody query demonstrates the semantic-role distinction in output/context;
- receipt/provenance captures the semantic-role artifact hash.

## 10. Current verdict

```
BRODY_RUNTIME                VERIFIED_EXISTING
QWEN_BEHIND_BRODY            EXISTING_SOURCE / NOT REBUILT
GMS_TRAJECTORY               VERIFIED_ABSORBED
MMONDE_BOUNDARY              VERIFIED_EXISTING
KX108_AUTHORITY_SEPARATION   VERIFIED

SEMANTIC_LATTICE             RESEARCH_SOURCE_ONLY
SENS_FULL                    REOPENED_R6
SEMANTIC_FOCUS               CURRENT_FIRST_IMPLEMENTATION_TARGET
BRODY_SENS_REAL_E2E          NOT_YET_CLOSED
```

No merge to `main`. No runtime mutation in this audit checkpoint.

# CODEX Forensic Audit - Claude Semantic Grammar Cognitive Lattice V0

Mode: READ_ONLY
Layer: FORENSIC / SEMANTICS / COGNITIVE ARCHITECTURE
Scope: Independent audit of `exp/semantic-grammar-cognitive-lattice-v0`
Report date: 2026-09-25

## Executive Verdict

CLAUDE_SOURCE_MAP_ACCURACY=PARTIAL_HIGH_FOR_REFERENCED_OBSIDIA_ARTIFACTS_BUT_OVERCONFIDENT_ON_CANONICALITY
CLAUDE_LINGUISTIC_MODEL_ACCURACY=MIXED_STRONG_ON_TESTED_FRENCH_NEGATION_SCOPE_WEAK_ON_GENERAL_ACTION_LEXICON
CLAUDE_LATTICE_ARCHITECTURE_STATUS=USEFUL_NON_SOVEREIGN_EXPERIMENT_NOT_CANONICAL_RUNTIME
CLAUDE_IR_PROJECTION_STATUS=ADDITIVE_BUT_GOVERNANCE_SEMANTICS_CHANGED_FOR_INDIRECT_EXECUTION_FORMS
CLAUDE_GOVERNANCE_CHANGES_STATUS=MATERIAL_FAIL_CLOSED_EXPANSION_PLUS_PREEXISTING_GATE_GAP_LEFT_OPEN
CLAUDE_TEST_QUALITY=GOOD_LOCAL_MATRIX_NOT_FULLY_VERIFIED_IN_THIS_SESSION
OVERFIT_RISK=MIXED
HISTORICAL_RECONNECTION_STATUS=SAFE_AS_RESEARCH_RECONNECTION_ONLY_NOT_RUNTIME_RECONNECT
MULTIDIMENSIONAL_CONVERGENCE_STATUS=SMALL_SHARED_PRIMITIVE_CORE_PLAUSIBLE_DISTINCT_SEMANTICS_REQUIRED

Do not merge this branch as-is. The lattice is a valuable experimental representation, but it changes governance behavior and does not close the pre-existing world-action/gate mismatch.

## A. Repository / Commit Forensics

BRANCH=exp/semantic-grammar-cognitive-lattice-v0
HEAD=b71fc3a
STATUS=clean tracked/untracked before report creation; report file is the only intended modification after approval
STAGED=none observed
UNSTAGED=none observed before report creation
UNTRACKED=none observed before report creation
BASE_COMMIT=8068261

Commits from `8068261..HEAD`:

| Hash | Subject | Stat | Purpose / behavior introduced |
|---|---|---:|---|
| 338bd83 | docs(semantics): map linguistic and memory architecture | 3 docs, +366 | Source-map and convergence claims; documentary only. |
| e1936c9 | test(semantics): freeze French grammar semantic matrix | 2 tests, +658 | 67-probe matrix and matrix runner. |
| b97a92f | feat(semantics): introduce non-sovereign semantic frame primitives | 7 files, +2181 | PredicateUnit, UtteranceFrame, projections, grammar, lexicon, UD adapter. |
| ebe3239 | feat(semantics): project semantic frame to existing UnifiedInputIR | 5 files, +275/-70 | Adds lattice summary into IR and allows limited prepare/no-execute relaxation. |
| 9388d2a | fix(semantics): keep reflexive and passive verbs inside modal chains | 2 files, +40/-4 | Regression fix for modal/reflexive/passive chaining. |
| 9eb996d | fix(semantics): hold infinitive and indirect execution requests | 3 files, +21/-12 | Changes governance: infinitive and indirect execution forms become HOLD. |
| 4e5073b | test(semantics): add causal/reference/modality regressions | 2 files, +135/-2 | Regression tests for causality/reference/modality. |
| b71fc3a | docs(semantics): report semantic grammar cognitive lattice v0 | 2 docs, +295 | Final Claude report. |

Total diff: 19 files changed, 3953 insertions, 70 deletions.

## B. Source Map Verification

Classification of the historical claims:

| Claim | Classification | Evidence / note |
|---|---|---|
| 34 trees | SPEC / PARTIAL_CODE / TESTED | Reference docs map `04_ARBRES_34`; Sigma tests assert `n_trees == 34`; source pack is candidate/read-only, not canonical runtime. |
| Noeud Continuum | DOC_ONLY / SPEC | Appears in extracted-source claims cited by Claude; no verified working code found in this audit pass. |
| Multidimensional point cloud | SPEC / STUB | Corpus map has graph/cloud-points subgroup; Claude source map also marks graph/path/projection as M0. |
| Calibrated links | DOC_ONLY / SPEC | Calibration doctrine exists, but no general typed link runtime verified. |
| Temporal line / timeline | STUB / DOC_ONLY | Timeline/Event/NodeContinuum described as names/placeholders by Claude's own source map. |
| Causal graph | PARTIAL_CODE for governance pipeline; STUB for world/discourse graph | Must not merge procedural governance causality with linguistic/world causality. |
| Projection | PARTIAL_CODE | Reverse OS action projection exists as advisory-only; AMD cognitive value inputs are read-only projections; not a general semantic substrate. |
| Path search | STUB | Source map reports `find_path -> []`; no working path-search closure verified. |
| Native Memory | PARTIAL_CODE / WIRED in reference memory surfaces | Native memory index claim is plausible, but flat keyword/provenance memory is not a typed lattice. |
| 3267 flat records | LOCAL_UNVERIFIED_IN_THIS_PASS | Claude reports it; this audit did not open the whole index to count. |

The user's hypothesis is plausible as a research framing: LANGUAGE, MEMORY, CAUSALITY, KNOWLEDGE CHRONOLOGY, WORLD MODEL, and SYMBOLIC REPRESENTATION can share primitives such as node/object, relation, provenance, confidence, unresolved reference, contradiction, and version/supersession. They should not be forced into one semantics: utterance time, event time, observation time, knowledge acquisition time, and memory storage time must remain distinct.

## C. New Lattice Architecture Audit

LATTICE_CORE_STATUS=COHERENT_AS_IMMUTABLE_DESCRIPTIVE_EXPERIMENT
PROJECTION_STATUS=COMPUTED_VIEWS_LOW_DRIFT_RISK_BUT_SUMMARY_CAN_DROP_INFORMATION
CAUSALITY_STATUS=DESCRIPTIVE_ONLY_MIXES_LINGUISTIC_CAUSE_WITH_UNVALIDATED_CAUSE_IF_USED_CARELESSLY
TEMPORAL_STATUS=LINGUISTIC_TEMPORALITY_ONLY_NOT_KNOWLEDGE_CHRONOLOGY
PROVENANCE_STATUS=PARTLY_REAL_SPANS_RAW_SURFACE_PARSER_LABEL_DECORATIVE_FOR_CONFIDENCE
AUTHORITY_BOUNDARY_STATUS=BOUNDARY_DECLARED_AND_NO_MEMORY_WRITE_PATH_FOUND_IN_LATTICE

`PredicateUnit` is one immutable object. `projections.py` computes axis views from that object and the frame, so ordinary view drift is unlikely. However, the IR summary intentionally compresses the frame and loses relation details, confidence semantics, many epistemic distinctions, and most temporal distinctions.

`NO_PROVEN_CONNECTION` is explicit. Provenance has useful span/raw parser fields, but no external proof chain. Confidence is stored and surfaced but not operational in gate decisions. Authority remains descriptive in the lattice, while gates/router still decide.

## D. Linguistic Correctness

Observed probe results:

| Probe | Result |
|---|---|
| `sans attendre, lance le script` | HOLD; previous scope regression fixed. |
| `sans hesiter, ne lance pas le script` | HOLD because raw still contains `lance`; semantically requested actions empty and no_execute true. Fail-closed, but label is lexical. |
| `sans lancer le script, prepare les fichiers` | CLARIFY; prepare/no-execute relaxes execution but target layer/referent remain open. |
| `prepare sans lancer puis lance les tests` | HOLD on positive `lance`; contradiction recorded. |
| `je ne pense pas qu'il faille lancer` | CLARIFY; embedded execute is BELIEVED, not requested. |
| `je pense qu'il ne faut pas lancer` | CLARIFY; negative execute BELIEVED/FORBIDDEN, not requested. |
| `il faut eviter de lancer` | HOLD; over-conservative because PREVENT + embedded EXECUTE becomes requested. |
| `n'oublie pas de ne pas lancer` | CLARIFY; no_execute true, no requested action. |
| `do not execute it, then run it` | HOLD matched `run`; positive run causes hold, not negated execute. |
| `tu peux lancer le test ?` | HOLD; indirect request treatment. |
| `peux-tu executer le script ?` | HOLD; indirect request treatment. |

The model is materially better than the regex prototype on clause-scoped negation, but it is not a full French grammar. It remains a bounded deterministic parser with selected lexical coverage.

## E. Overfitting Audit

Implementation classification: MIXED.

Evidence against pure phrase-patching: the grammar files do not contain direct branches for the main test sentences, and the lexicon declares itself lemma/form based. Evidence for overfit risk: many tests use the exact same surfaces (`lancer`, `executer`, `script`, `tests`), and uncovered world-action verbs (`rm`, `format`, `drop`, `authorize`) are not represented in the lattice, producing false ALLOW outcomes even though legacy IR marks `act_request`.

Independent generated probe campaign: 150 generated variants were run via a temp script outside tracked files.

NEW_FALSE_ALLOW=40
NEW_FALSE_HOLD=0 observed by the simple oracle
NEW_FALSE_CLARIFY=0 observed by the simple oracle
NEW_SEMANTIC_SCOPE_ERRORS=4 obvious cases, all `sans attendre, rm/format/drop/authorize ...` where `rm/format/drop/authorize` became object text of WAIT and gate returned ALLOW.

These counts are oracle-dependent but the qualitative bug is clear: legacy `_ACTION_WORDS` can set `action_type=act_request`, while `gates.evaluate()` can still return ALLOW if the surface is absent from `HOLD_KEYWORDS` and not in `DENY_KEYWORDS`.

## F. UnifiedInputIR Compatibility

Public fields are mostly preserved and `semantics` is additive. Parser failure is fail-closed through `fail_closed_summary()`. Raw input remains present and exact at the frame level and normalized in IR.

Semantic information loss points:

1. `parse_utterance(raw)` builds predicate units, relations, closure blockers, evidence needs.
2. `governable_summary(frame)` compresses units and relations; drops many details needed for a future memory/world lattice.
3. `build_ir(raw)` turns summary into `intent_type/action_type/target_layer/constraints/missing`.
4. `evaluate(ir)` uses lexical gate lists first and only partially consults semantic requested surfaces.
5. `decide()` routes after DENY/HOLD/CLARIFY; it does not interpret the full lattice.

Existing consumers appear likely to tolerate the additive `semantics` field, but this audit did not run the full suite.

## G. PREPARE + NO_EXECUTE

Observed properties:

| Probe | Result |
|---|---|
| `prepare le sans rien lancer` | CLARIFY; prepare requested, no_execute true, unresolved `le` blocks closure. |
| `prepare le script mais ne l'execute pas` | CLARIFY; prepare requested, no_execute true, no HOLD. |
| `prepare the script but do not execute it` | CLARIFY; prepare requested, no_execute true, no HOLD. |
| `prepare the script without executing it` | CLARIFY; prepare requested, no_execute true, no HOLD. |
| `do not execute it, then run it` | HOLD matched `run`; correct cause attribution. |

This is a good fail-closed shape: prepare/no-execute no longer accidentally creates execution authority, but unknown target/layer remains open.

## H. Commit 9eb996d - Separate Policy Audit

9EB996D_LINGUISTIC_STATUS=PARTIAL_LINGUISTIC_FACT_PLUS_PRAGMATIC_INTERPRETATION
9EB996D_POLICY_STATUS=FAIL_CLOSED_GOVERNANCE_POLICY
9EB996D_MERGE_RECOMMENDATION=KEEP_WITH_CHANGES

Classification:

| Form | Classification |
|---|---|
| `lancer le script` | Linguistic fact: injunctive infinitive can be directive; governance HOLD is fail-closed policy. |
| `tu peux lancer le test ?` | Pragmatic interpretation: ability question vs indirect request ambiguity must be preserved; HOLD is governance policy. |
| `peux-tu executer le script ?` | Pragmatic interpretation plus fail-closed policy. |
| `il faut lancer les tests` | Obligation construction; closer to linguistic fact as directive/necessity, HOLD is policy. |
| `je veux que tu lances le script` | Desire/request construction; HOLD is policy. |

Do not solve ambiguity by deleting it. The representation should preserve `ABILITY_OR_PERMISSION` plus `INDIRECT_REQUEST` ambiguity while governance separately chooses HOLD.

## I. Preexisting WORLD_ACTION / Gate Gap

Verified by reading versions at `0b348ab`, `8068261`, and `b71fc3a` plus current probes.

At `0b348ab`, `_ACTION_WORDS` includes `rm`, `format`, `drop`, `authorize`, but `HOLD_KEYWORDS` does not include `rm`, `format`, `drop`, or `authorize`; `DENY_KEYWORDS` only catches narrow forms like `rm -rf`, `drop database`, `format c`.

At `8068261`, the same mismatch remains, with extra no_execute logic. At `b71fc3a`, semantic requested surfaces can add HOLD for lattice-recognized verbs, but uncovered legacy action words still pass ALLOW.

Gap classification: IR/GATE_CONTRACT_MISMATCH plus LEXICAL_MISMATCH, therefore BUG. It is not merely policy choice, because the IR already says `world_action/act_request/high`.

## J. Test Claims

Static claims observed in Claude artifacts:

- 67 linguistic probes: plausible from `tests/semantic_grammar_matrix.py` structure.
- Held-out/regression tests: present in semantic governance/regression test files.
- Full count `1837 passed, 3 skipped, 20 subtests passed`: NOT_VERIFIED in this session.

Reason: the sandbox Python lacked `pytest`; `py -m pytest` required an escalation that was rejected by the execution controller for untrusted project-code execution. No installs were attempted.

## K. Memory / Multiverse Convergence

| Primitive | Verdict |
|---|---|
| Node/Object | SHARE |
| TypedRelation | SHARE_WITH_STRICT_TYPES |
| Provenance | SHARE |
| Confidence | ADAPT; operational meaning differs by layer |
| Temporal coordinate | ADAPT; keep utterance/event/observation/acquisition/storage separate |
| Causal relation | ADAPT/SEPARATE; linguistic, claimed, observed, and proved causality differ |
| Unresolved reference | SHARE |
| Contradiction | SHARE_WITH_LAYERED_MEANING |
| Trajectory | ADAPT |
| Version/supersession | SHARE; missing from this implementation |

Claude's sentence "small shared primitive core, distinct semantics above" is the safest formulation. Anything stronger would over-converge.

## L. Commit Classification

| Commit | Classification |
|---|---|
| 338bd83 | KEEP_WITH_CHANGES; useful map, but canonicality wording should be tightened. |
| e1936c9 | KEEP_WITH_CHANGES; good matrix but not enough mutation diversity. |
| b97a92f | EXPERIMENT_ONLY; useful architecture, not canonical runtime. |
| ebe3239 | KEEP_WITH_CHANGES; additive IR projection is useful, but information loss and relaxation rules need more review. |
| 9388d2a | KEEP_AS_IS for the narrow fix if tests pass. |
| 9eb996d | KEEP_WITH_CHANGES; preserve ambiguity while gate chooses fail-closed. |
| 4e5073b | KEEP_WITH_CHANGES; good regressions, needs broader action lexicon and chronology cases. |
| b71fc3a | KEEP_WITH_CHANGES; report is useful but overstates verified test execution unless rerun independently. |

## Final Markers

CODEX_FORENSIC_AUDIT_COMPLETE
SOURCE_MODIFICATION=REPORT_ONLY
COMMIT=0
PUSH=0
MERGE=0

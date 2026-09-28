# Claude autonomous loop — semantic closure roadmap

LOOP_START_TIME=2026-09-28 00:02:57 (local)
LOOP_START_HEAD=84dd4e3
BASELINE=2113 passed / 8 skipped / 0 xfailed / 20 subtests
SOFT_LIMIT=00:42:57 · HARD_LIMIT=00:47:57
Known environment skips: 5 × llama-server absent (tests/track3/test_track3_spine.py),
3 × benchmark_report.json / results.json not generated (tests/test_metrics_coverage.py).

This log is uncommitted by design. Feature commits are atomic and exclude it.

## ITERATION 1 — P1 conditional meta-event occurrence
START_HEAD=84dd4e3
OBJECTIVE=Conditional meta-event must not be ASSERTED_OCCURRED.
AUDIT_FINDING=Parser exposes a reliable morphological signal (tense_aspect=CONDITIONAL from COND features).
  _local_occurrence_status meta rule (SAY/BELIEVE/OBSERVE/LEARN + pragmatic ASSERTED -> ASSERTED) ignored tense.
  Leaks: croirait/dirait/affirmerait/supposerait/verrait/apprendrait/aurait dit -> ASSERTED_OCCURRED;
  also NEAR_FUTURE ("va dire", "va croire") and AVERTED ("a failli dire", realized=False!) -> ASSERTED_OCCURRED.
  Conditional-mood ACTIONS were already UNKNOWN (no meta rule).
  Status choice: UNKNOWN, not OccurrenceStatus.CONDITIONAL. CONDITIONAL is currently reserved for "si"
  protasis (RelationKind.CONDITIONS source); French conditional is also evidential/journalistic
  ("aurait dit" = reportedly said). UNKNOWN matches the existing conditional-action behavior.
RED=10 failed / 9 control passed (tests/test_conditional_meta_event_occurrence.py)
FILES_CHANGED=app/semantic/lattice/event_extraction.py (+6/-2); tests/test_conditional_meta_event_occurrence.py (new, 19 tests)
IMPLEMENTATION=meta rule restricted to tense_aspect in {PRESENT, PROGRESSIVE} and realized is not False.
  Past/pluperfect/recent past remain covered by the realized=True rule.
TARGETED_TESTS=191 passed (event/occurrence/lexicon/governor/resolver lots)
FULL_TESTS=2132 passed / 8 skipped / 20 subtests
INVARIANTS=EVENT_EXISTS != EVENT_OCCURRED; UNKNOWN != TRUE; stronger FUTURE/UNCERTAIN/NEGATED meta statuses preserved;
  content statuses unchanged (dirait -> content REPORTED, croirait -> content UNKNOWN).
COMMIT=d8eb0e7 fix(semantics): preserve conditional meta-event occurrence
NEW_FINDINGS=
  [Class D] "Paul apprendrait que X" -> X stays ASSERTED_OCCURRED (LEARN factivity projection under
    conditional / negation is a doctrine choice; not decided). Same family as KNOW factivity (B2c note).
  [Class C] Reported content in conditional mood ("Paul dit que Marie lancerait") -> REPORTED
    (pragmatic REPORTED wins over conditional mood); not a leak (not ASSERTED), logged only.
NEXT=P2 "le fait que" false action-request parse

## ITERATION 2 — P2 "le fait que" (AUDIT → DEFERRED, Class D)
START_HEAD=d8eb0e7
OBJECTIVE=Distinguish the factive nominal "le fait que" from an action predicate.
AUDIT_FINDING=_is_verb treats "le/la/les/l'" + known form as clitic + verb, so "fait" (faire PRES/PP) is a verb;
  with no subject it becomes IMPERATIVE -> DO pragmatic REQUESTED, frame surface_act "imperative".
  Since B2c the complement is under DO with UNRESOLVED_GOVERNANCE -> X UNKNOWN.
  Authority check: surface_act has NO consumer in app/ (grep); governable_summary requested_world_actions=[];
  governance flows only MENTIONED (DO is generic_action, not world_action). => no authority/execution impact.
DECISION=DEFERRED, no source change. Removing the DO reading makes "le fait que X" parse as a relative, whose
  content the parser asserts -> X would go back to ASSERTED_OCCURRED. That (a) decides the factivity of a
  nominal complement (same doctrine family as KNOW / LEARN factivity) and (b) rolls back committed B2c
  behavior on that sentence. Keeping DO and only removing IMPERATIVE would patch a symptom on a wrong parse.
  Per policy: Class D -> backlog, not decided casually.
RED=n/a · FILES_CHANGED=none · COMMIT=none
NEW_FINDINGS=[Class D backlog] factivity doctrine needed for: KNOW + que, LEARN under conditional/negation,
  nominal "le fait que". Proposal for review: one explicit FACTIVE contract (presupposed, not verified),
  distinct from ASSERTED_OCCURRED, decided once for all three.
NEXT=P3 EventIndex read-only audit

## ITERATION 3 — P3 EventIndex V0 read-only audit
START_HEAD=d8eb0e7
OBJECTIVE=Map predicate_ref -> EventRef across all producers before implementing an index.
AUDIT_FINDING=
  Producers: event_extraction (ACTION classes + SAY->REPORT + BELIEVE->BELIEF; seed "event_extraction_v0"),
  observation_event_extraction (OBSERVE only; seed "observation_event_extraction_v0"),
  knowledge_event_extraction (LEARN only; reuses a base EventRef id if one exists, else seed
  "knowledge_event_extraction_v0"). Base never mints OBSERVE (class observation) nor LEARN (embedding_learn),
  so predicate sets are disjoint today. All ids deterministic: sha256(frame_ref | predicate_ref | seed).
  frame_ref = sha256(raw)[:12] duplicated in 4 modules (identical implementation).
  Corpus check (1528 frames parsed from every test string): 484 base + 43 observation + 14 knowledge
  candidates; predicate with >1 EventRef = 0; event_id collisions = 0; source_frame None = 0.
  Risks (latent, not present): _knowledge_candidate reuses a base id with a different kind; any future
  extractor re-minting ids with its own seed.
DESIGN=Straightforward and implied by current structures: immutable frame-local index consuming existing
  extractor outputs (no new ids), predicate_ref -> at most one EventCandidate, incompatible proposals recorded
  as explicit conflicts and excluded (no guessing), foreign-frame / unknown-predicate candidates rejected.
RED=n/a (read-only) · COMMIT=none
NEXT=P4 EventIndex V0

## ITERATION 4 — P4 EventIndex V0
START_HEAD=d8eb0e7
OBJECTIVE=Smallest immutable frame-local EventIndex over existing extractor outputs.
AUDIT_FINDING=See iteration 3 (disjoint producers, deterministic ids, no conflicts in corpus).
RED=tests/test_event_index.py collection error (module absent) before implementation.
FILES_CHANGED=app/semantic/lattice/event_index.py (new, ~130 lines); tests/test_event_index.py (new, 12 tests)
IMPLEMENTATION=build_event_index(frame, *candidate_groups) -> EventIndex(frame_ref, by_predicate [MappingProxy],
  conflicts, unit_order); event_for / by_event_id / events() (frame order) / to_dict.
  Rules: source_frame None or != frame_ref -> conflict frame_mismatch; predicate not a frame unit ->
  predicate_not_in_frame; same predicate with differing (event_id, kind, occurrence) -> incompatible_event_refs
  (excluded); same event_id on two predicates -> event_id_collision (both excluded); identical duplicates collapse.
  build_frame_event_index(frame) runs the three existing extractors (pure). frame_ref reuses
  event_extraction._frame_ref. No id minting, no global state.
TARGETED_TESTS=73 passed (index + event lots)
FULL_TESTS=2144 passed / 8 skipped / 20 subtests
INVARIANTS=AMBIGUOUS != FIRST_CANDIDATE (conflicts excluded, not arbitrated); EVENT_EXISTS != EVENT_OCCURRED
  (occurrence copied, never recomputed); no memory/authority; no runtime wiring.
COMMIT=ac4302f feat(semantics): add immutable event index
NEW_FINDINGS=none
NEXT=P5 shared immediate meta-target selector

## ITERATION 5 — P5 shared immediate meta-target selector
START_HEAD=ac4302f
OBJECTIVE=One pure helper for immediate structural meta-targets.
AUDIT_FINDING=observation._structural_embedded_target and knowledge._explicit_embedded_target are duplicate
  copies: first EMBEDS relation from the source, else FIRST unit whose embedded_under is the source
  (silent first-match; multiple targets never reported). SAY/BELIEVE use typed REPORTS/BELIEVES relations,
  one per source in every probe. Note: "Paul dit que A et Jean a lancé B" (no second "que") gives
  COORDINATES SAY->u3 — a root-level coordination reading, distinct from the O4 "et que" mis-nesting.
RED=tests/test_meta_target_selector.py collection error (module absent).
FILES_CHANGED=app/semantic/lattice/meta_event_relations.py (new); tests/test_meta_target_selector.py (new, 10 tests)
IMPLEMENTATION=select_immediate_meta_target(frame, source_predicate, relation_kinds, event_index) -> EventTargetReference.
  source must be indexed (else ValueError). Relations filtered strictly by kind. 0 -> UNKNOWN_TARGET/UNRESOLVED
  (no_immediate_relation); >1 distinct targets -> UNKNOWN_TARGET/AMBIGUOUS (MULTIPLE_TARGETS_UNSUPPORTED, candidate
  ids kept); target in index conflicts -> UNRESOLVED (target_event_conflict); indexed target -> EVENT_TARGET;
  unindexed target predicate -> PROPOSITION_TARGET. Provenance: source_frame, source/target spans, parser relation
  kind + evidence, rule. Metadata copies target occurrence, promoted=False, evidence_validated=False, truth=None.
  Existing observation/knowledge extractors NOT migrated (policy: only if necessary).
TARGETED_TESTS=43 passed (selector + index + coreference + observation + knowledge)
FULL_TESTS=2154 passed / 8 skipped / 20 subtests
INVARIANTS=AMBIGUOUS != FIRST_CANDIDATE; no nearest/deepest fallback; no flattening; occurrence untouched.
COMMIT=cac9fac feat(semantics): add shared immediate meta-target selector
NEW_FINDINGS=[Class C] observation/knowledge extractors keep their first-match target helpers; migrating them
  to the shared selector would make multiple targets explicit (backlog, behavior change for LEARN/OBSERVE).
NEXT=P6 REPORT event relation closure

## ITERATION 6 — P6 REPORT event relation closure
START_HEAD=cac9fac
OBJECTIVE=SAY EventRef -> REPORTS_ABOUT -> immediate EventRef target.
AUDIT_FINDING=REPORT EventRefs exist (base extraction, SAY/embedding_say incl. B2b lexicon); parser gives one
  REPORTS relation per SAY with a que-complement; no event-level relation existed.
RED=tests/test_report_event_relations.py import error (function absent).
FILES_CHANGED=app/semantic/lattice/meta_event_relations.py (+~95: MetaEventRelationResult, generic
  _extract_meta_relations, extract_report_event_relations); tests/test_report_event_relations.py (new, 10 tests incl.
  1200-case matrix asserting every relation targets the immediate embedded unit and copies target occurrence).
IMPLEMENTATION=For each indexed REPORT event in frame order: selector(REPORTS). EVENT_TARGET -> EventReferenceRelation
  REPORTS_ABOUT (provenance = selector provenance + source predicate); PROPOSITION/UNKNOWN/AMBIGUOUS -> target record
  only. Metadata: source/target occurrence copied, promoted/verified/supported/observed/evidence False, truth None.
TARGETED_TESTS=93 passed · FULL_TESTS=2164 passed / 8 skipped / 20 subtests
INVARIANTS=REPORT != VERIFIED; REPORT != OBSERVED; no flattening (SAY->SAY->RUN = two one-hop relations);
  no EventRef for proposition-only targets; OBSERVES from observation extractor unchanged and coexists.
COMMIT=e8fe5ec feat(semantics): close report event relations
NEW_FINDINGS=none
NEXT=P7 BELIEF event relation closure

## ITERATION 7 — P7 BELIEF event relation closure
START_HEAD=e8fe5ec
OBJECTIVE=BELIEF EventRef -> BELIEVES_ABOUT -> immediate target.
AUDIT_FINDING=BELIEF EventRefs exist (croire/penser/supposer incl. B2b forms); parser BELIEVES relation per complement.
RED=tests/test_belief_event_relations.py import error (function absent).
FILES_CHANGED=app/semantic/lattice/meta_event_relations.py (+8: extract_belief_event_relations reusing the generic
  builder); tests/test_belief_event_relations.py (new, 8 tests incl. 1200-case matrix).
IMPLEMENTATION=Same generic path as P6 with (EventKind.BELIEF, {BELIEVES}, BELIEVES_ABOUT).
TARGETED_TESTS=53 passed · FULL_TESTS=2172 passed / 8 skipped / 20 subtests
INVARIANTS=BELIEVED != ASSERTED_OCCURRED (matrix: no believed target is ASSERTED); BELIEF != SUPPORTED/VERIFIED;
  BELIEF->REPORT->RUN = BELIEVES_ABOUT(believe->say) + REPORTS_ABOUT(say->run), no shortcut; reports and beliefs
  never cross relation kinds.
COMMIT=7a3ed77 feat(semantics): close belief event relations
NEW_FINDINGS=none
NEXT=P8 meta-event graph read-only audit

## ITERATION 8 — P8 meta-event graph read-only audit
START_HEAD=7a3ed77
OBJECTIVE=Audit OBSERVES / LEARNS_ABOUT / REPORTS_ABOUT / BELIEVES_ABOUT as one graph.
METHOD=1549 frames (every test-suite string + nested/coordination templates); EventIndex + 4 relation producers.
AUDIT_FINDING=
  relations: REPORTS_ABOUT 47, BELIEVES_ABOUT 43, OBSERVES 17, LEARNS_ABOUT 14.
  endpoints not indexed 0 · non-immediate targets 0 · duplicate relations 0 · cycles 0 · index conflicts 0 ·
  ASSERTED targets under REPORTS_ABOUT/BELIEVES_ABOUT 0.
  targets: EVENT/RESOLVED_STRUCTURAL 107, EVENT/RESOLVED_EXPLICIT 14 (LEARN), PROPOSITION 4, ENTITY 6 (OBSERVE NP),
  UNKNOWN/UNRESOLVED 53.
  shared targets (one event targeted by >1 meta-event) = 0: frame-local structural graph is a forest of chains.
  Convergence of several meta-events on one target needs the explicit nominal reference adapter (R11, not wired)
  or cross-frame identity (forbidden).
  Coordination "A et que B": parser hangs B under A (EMBEDS, evidence "rel") -> B absent from the meta graph with
  no multi-target signal; not structurally distinguishable from a genuine relative on the action clause.
DECISION=No change (read-only). Graph closure for single-frame chains: READY.
NEW_FINDINGS=[Class C/parser backlog] coordination mis-nesting still silently drops the second complement from
  meta relations (occurrence is safe since O4). [Design note] ReviewJoin shared-target joins are not reachable
  frame-locally until R11 adapter exists.
NEXT=P9 ReviewJoin V0 — evaluate architecture certainty first.

## ITERATION 9 — P9 ReviewJoin V0 (read-only envelope)
START_HEAD=7a3ed77
OBJECTIVE=Minimal ReviewEnvelope over the closed meta-event graph.
ARCHITECTURE_CHECK=Prerequisites green (index, selector, 4 relation kinds, P8 audit clean). No doctrine choice
  needed when: center is named by the caller (no center heuristic), output is pure aggregation, and truth /
  conflict resolution / temporal / R11 nominal adapter are explicitly out of scope. Proceeded.
RED=tests/test_review_join.py import error (module absent).
FILES_CHANGED=app/semantic/lattice/review_join.py (new, ~150 lines); tests/test_review_join.py (new, 8 tests)
IMPLEMENTATION=build_review_envelope(frame, center_event, event_index=None) -> ReviewEnvelope(center_event, frame_ref,
  events[event_id, predicate_ref, predicate, event_kind, occurrence_status, epistemic_states (from
  project_epistemic_flows, keyed by predicate), span, is_center], relations (component, frame order), unresolved
  (UNRESOLVED/AMBIGUOUS targets of component sources), non_event_targets (PROPOSITION/ENTITY), conflicts
  (index conflicts of component predicates), provenance, metadata truth=None, conflict_resolution/temporal/
  cross_event_coreference = none, authority/memory counters 0). Component = undirected BFS from the center over
  typed relations only. Center not indexed -> ValueError.
TARGETED_TESTS=63 passed · FULL_TESTS=2180 passed / 8 skipped / 20 subtests
INVARIANTS=one output != one truth scalar; distinct EventRefs never merged (two RUN events of two sentences stay in
  two envelopes, NEGATED vs REPORTED preserved); no memory/authority; occurrence and epistemic states copied.
COMMIT=3a08e2c feat(semantics): add read-only review envelope v0
NEW_FINDINGS=Envelopes are chains today (P8: 0 shared targets frame-locally); multi-perspective joins need R11.
NEXT=Remaining time: read-only audit of R11 (explicit nominal reference -> meta-event adapter) readiness.

## ITERATION 10 — R11 explicit nominal reference -> meta-event adapter
START_HEAD=3a08e2c
OBJECTIVE=Wire the hardened resolver (f7c87da) into meta-event relations without putting resolution logic in extractors.
AUDIT_FINDING=Model validated in the earlier REPORT/BELIEF audit (EXPLICIT_REFERENCE_TO_META_EVENT_ADAPTER_MODEL=SOUND).
  Probes: observé/mentionné/appris/crois + "ce lancement" resolve with governor OBSERVATION/REPORT/KNOWLEDGE/BELIEF;
  "rapporté" (unknown verb) has no governor; "vérifié" governor is ACTION; negated antecedent stays AMBIGUOUS;
  "Luc a mentionné cette observation" targets the observation event (not the inner action).
RED=tests/test_nominal_reference_relations.py import error (function absent).
FILES_CHANGED=app/semantic/lattice/meta_event_relations.py (+106/-1); tests/test_nominal_reference_relations.py (new, 12 tests)
IMPLEMENTATION=extract_nominal_reference_relations(frame, event_index, *, structural_relations=None):
  resolver(frame, index.events()) -> for each reference: skip reference_not_resolved (not RESOLVED_STRUCTURAL or target
  not indexed) / no_governing_event / governor_not_meta_event / structural_target_precedence (governor already has a
  structural relation); else relation by governor kind, status "nominal_reference", provenance = resolver provenance +
  source predicate, metadata coreference_confidence (uncalibrated), occurrence copied, promoted/verified False.
  Default structural relations = observation + knowledge + report + belief producers.
TARGETED_TESTS=93 passed (incl. unchanged resolver suite) · FULL_TESTS=2192 passed / 8 skipped / 20 subtests
INVARIANTS=NO latest/nearest fallback (resolver unchanged); AMBIGUOUS never bound; no cross-message binding;
  structural > nominal; no occurrence promotion; resolver untouched.
COMMIT=e6d6d9c feat(semantics): adapt explicit nominal references to meta-event relations
NEW_FINDINGS=ReviewJoin V0 does not yet include nominal_reference relations (next step, bounded).
NEXT=Include adapter relations in ReviewJoin so shared-target joins become reachable (still frame-local).

## ITERATION 11 — ReviewJoin includes nominal reference relations
START_HEAD=e6d6d9c
OBJECTIVE=Make shared-target joins reachable frame-locally via the R11 adapter.
AUDIT_FINDING=Probe: "Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement." ->
  OBSERVES(u2->u1) + REPORTS_ABOUT(u3->u1), no skips; same with "Luc croit ce lancement" (BELIEVES_ABOUT).
RED=test_shared_target_join_through_explicit_nominal_references failed (1 failed / 9 passed; ambiguity control passed).
FILES_CHANGED=app/semantic/lattice/review_join.py (+12/-6); tests/test_review_join.py (+2 tests)
IMPLEMENTATION=Envelope relations = structural (4 producers) + extract_nominal_reference_relations(structural passed for
  precedence); nominal targets added to target pool; sort key includes status; provenance nominal_reference_adapter
  = "wired" + nominal_references_skipped counts.
TARGETED_TESTS=22 passed · FULL_TESTS=2194 passed / 8 skipped / 20 subtests
INVARIANTS=AMBIGUOUS never joined; structural > nominal; each perspective keeps its own relation/status/occurrence
  (no merge, no truth scalar); still frame-local only.
COMMIT=2608659 feat(semantics): join nominal reference relations in review envelope
NEW_FINDINGS=none
NEXT=Time 26 min: one more bounded step possible before 40-min soft limit.

## ITERATION 12 — EventTargetReference consistency invariants
START_HEAD=2608659
OBJECTIVE=Close the "target model not validated" gap noted in the first audit of 0fcfeff.
AUDIT_FINDING=EventTargetReference accepted contradictory records (e.g. EVENT_TARGET without target_event,
  UNRESOLVED with a target_event, resolved UNKNOWN_TARGET). No producer emitted them, but nothing prevented it.
RED=7 failed / 9 passed (tests/test_event_target_reference_invariants.py).
FILES_CHANGED=app/semantic/lattice/event_coreference.py (+21); tests/test_event_target_reference_invariants.py (new, 16 tests)
IMPLEMENTATION=_check_target_consistency in __post_init__: non-resolved => no target_event; resolved EVENT_TARGET =>
  target_event required; EVENT_TARGET never unresolved; UNKNOWN_TARGET => no target, never resolved. ValueError.
  PROPOSITION_TARGET unresolved/ambiguous without target stays valid (resolver "ce fait" records).
TARGETED_TESTS=16 passed · FULL_TESTS=2210 passed / 8 skipped / 20 subtests (all producers and matrices comply)
INVARIANTS=UNKNOWN != TRUE; AMBIGUOUS != FIRST_CANDIDATE enforced at the data-model level.
COMMIT=78825f6 fix(semantics): reject self-contradictory event target records
NEW_FINDINGS=none
NEXT=Elapsed 28 min; soft limit 40. Stop source-changing iterations here to keep a safe margin; write final report.

## ITERATION 13 — ReviewJoin partition audit (read-only)
START_HEAD=78825f6
OBJECTIVE=Check envelopes over the whole corpus: every indexed event in exactly one component, consistent centers.
AUDIT_FINDING=1551 frames, 578 envelopes (one per indexed event): overlapping components 0, partition gaps 0, center
  inconsistencies 0 (every event of a component yields the same component), truth scalar 0; 25 nominal_reference
  relations; 10 envelopes with a shared target (several perspectives on one event).
DECISION=No change. COMMIT=none.
NEXT=Stop: remaining time kept as safety margin (no new source-changing iteration started).

# END OF LOOP
LOOP_START_HEAD=84dd4e3
LOOP_END_HEAD=78825f6
ELAPSED_MINUTES=29
ITERATIONS_COMPLETED=13 (9 committed source iterations, 4 read-only / deferred)
COMMITS_CREATED=9
  d8eb0e7 fix(semantics): preserve conditional meta-event occurrence
  ac4302f feat(semantics): add immutable event index
  cac9fac feat(semantics): add shared immediate meta-target selector
  e8fe5ec feat(semantics): close report event relations
  7a3ed77 feat(semantics): close belief event relations
  3a08e2c feat(semantics): add read-only review envelope v0
  e6d6d9c feat(semantics): adapt explicit nominal references to meta-event relations
  2608659 feat(semantics): join nominal reference relations in review envelope
  78825f6 fix(semantics): reject self-contradictory event target records
CURRENT_FULL_SUITE=2210 passed / 8 skipped / 0 xfailed / 20 subtests
KNOWN_SKIPS=5 llama-server absent + 3 benchmark/results artifacts absent (unchanged)
NEW_BUGS_FIXED=conditional/near-future/averted meta-event asserted (incl. "a failli dire" realized=False);
  self-contradictory EventTargetReference accepted
NEW_BUGS_DEFERRED=[Class D] factivity doctrine (KNOW + que, LEARN under conditional/negation, "le fait que");
  "le fait que" DO/IMPERATIVE misparse (no authority impact); [parser] coordination "A et que B" drops B from meta
  graph; [Class C] observation/knowledge first-match target helpers not migrated to shared selector;
  reported conditional content stays REPORTED.
HOLD_REQUIRED=NO
PUSH=0 · MERGE=0

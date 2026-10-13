# M36 Cross-domain Transfer — Analogy Doctrine V1

## 1. Status and authority

- Chapter: M36 — Cross-domain Transfer. Layer: cognition / pre-forge.
- Form: `M36_FORM=DOCTRINE_ONLY`. This document is the whole of M36 V1.
- Base: `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO`; M33 and M34 CLOSED; M35 DEFERRED (evidence incomplete) and not a dependency.
- Basis: an independently certified M36 forensic, followed by explicit project-owner decisions (meaning = analogy, form = doctrine-only, competence transfer to B11 and education) and conservative boundary decisions drawn from that forensic (knowledge domains only, no object identity).
- Normative hierarchy: `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > THIS_DOCTRINE > HISTORICAL_GENEALOGY`.

"Cross-domain transfer" is the milestone name kept by the foundation seal. Its only canonical V1 meaning is cross-domain analogy.

## 2. Historical problem

Historically, "transfer" named several distinct things:

- reuse of the same governance contracts by several application-domain adapters;
- translation or projection of content between representations;
- cross-modal transformation (mathematics, image, sound, language, world);
- analogy between distant knowledge domains;
- reuse of a recognition method in a new field;
- pedagogical transfer of an acquired competence to a new situation.

M36 V1 does not merge these meanings. The certified forensic retained only one as M36's residual: analogy, i.e. a structural correspondence hypothesis between knowledge domains. Every other meaning is either owned elsewhere or excluded (§6).

In current canonical code, "cross-domain" means the opposite of transfer: domain isolation and anti-substitution, under which a decision taken for one domain never authorizes an execution in another. M36 leaves that rule untouched.

## 3. Evidence levels

| Source | Evidence level | Use in M36 |
|---|---|---|
| Foundation seal §7 ("Cross-domain transfer" deferred) | CURRENT_CANONICAL | milestone existence only |
| Cross-domain isolation / anti-substitution (governed runtime, KX108) | CURRENT_CANONICAL | boundary M36 must not weaken |
| CG16 domain adaptation (closed) | CURRENT_CANONICAL | owner of adapter reuse; not M36 |
| Historical corpus: linking distant knowledge domains; "which historical paths resemble the present" | HISTORICAL_DIRECT | genealogy of the analogy meaning |
| Historical corpus: "a domain is one language of the same invariant", projection formulas | HISTORICAL_DIRECT, speculative | genealogy only; excluded from V1 |
| Historical link typing: "an analogical link is not a causal link"; analogy as design intuition, not verified scientific basis; superficial analogies flagged as parasitic links | HISTORICAL_DIRECT, repeated in semantic docs | basis of the safety laws |

| "inifgrpahie 81+ et pepite du debut.docx" (external, owner-supplied): sequence analogie interdomaines → candidat de transfert → test / confrontation; "an analogy is never automatic proof"; ants vs software agents coordination example; No-Rebuild distinctions | HISTORICAL_DIRECT, external | genealogy of the bounded transfer hypothesis (§7a) |
| P2.9c experiment (reported in the same source): cross-regime knowledge transfer 42/180 successful predictions (23.3%), MAE 11 px, 21 severe errors | HISTORICAL_DIRECT, experimental, external | supporting genealogy for "no blind transfer" only; not a threshold |

No source defines a correspondence schema, a preserved invariant, a failed-transfer model or a learning mechanism.

## 4. Canonical mission

M36 preserves the architectural rule that a structural resemblance observed between distinct knowledge domains may be represented as an analogy hypothesis, without establishing equivalence, causality, identity, truth, promotion, selection, authority or execution.

M36 does not compute analogies and does not discover invariant structure.

## 5. Definition of domain for V1

- `M36_DOMAIN_KIND=KNOWLEDGE_DOMAIN`

Historical examples of knowledge domains include religion, politics, technical systems, memory, truth, organization, mathematics, physics and biology. These examples are genealogical only; M36 V1 defines no domain taxonomy.

## 6. Excluded domain meanings

- Application domains (GPS, Defense, Aviation, Trading, Bank, Finance, E-commerce): their shared governance belongs to CG16 domain adaptation, UDIP and DomainState. `APPLICATION_DOMAIN_TRANSFER_IS_M36=NO`, `M36_DOMAIN_ADAPTER_REUSE=NO`.
- Representation and modality (mathematics ⇄ image ⇄ sound ⇄ language ⇄ world; projection between representations): primarily SENS, OS IR and multimodal work. `REPRESENTATION_TRANSLATION_IS_M36=NO`, `CROSS_MODAL_TRANSFER_IS_M36=NO`.
- System layers (SENS, Brody, Obsidure, Kernel, Sigma) are not M36 domains merely because they differ. `SYSTEM_LAYER_TRANSLATION_IS_M36=NO`.
- Pedagogical competence transfer belongs to B11 and the education / training architecture. `COMPETENCE_TRANSFER_IS_M36=NO`, `COMPETENCE_TRANSFER_OWNER=B11_AND_EDUCATION`. M36 does not evaluate competence.

## 7. Analogy model

Conceptual form, descriptive only:

```
SOURCE KNOWLEDGE DOMAIN → ANALOGY HYPOTHESIS → TARGET KNOWLEDGE DOMAIN
```

This is not a pipeline. There are no source or target schemas.

An analogy hypothesis means only: some structural resemblance may exist. It does not mean same object, same cause, same mechanism, same truth, same rule, same value, same authority or same outcome. An analogy may simply remain unsupported; M36 defines no failure states. `M36_FAILED_TRANSFER_MODEL=NONE`.

Correspondence: the forensic found structural correspondence only partially present and no concretely supported correspondence elements. M36 V1 therefore defines no canonical correspondence dimension (role, relation, constraint, topology, causal direction, temporal order). `M36_CORRESPONDENCE_SCHEMA=NONE`.

Invariant: the historical "universal structural invariant" is never defined. `M36_TRANSFER_INVARIANT=UNDEFINED`. There is no invariant type, identifier, preservation algorithm or isomorphism requirement; the phrase remains genealogy.

## 7a. Bounded transfer hypothesis (methodological genealogy)

Historical sequence preserved:

```
ANALOGIE INTERDOMAINES → CANDIDAT DE TRANSFERT → TEST / CONFRONTATION
```

- analogie interdomaines: a suspected resemblance or shared mechanism;
- candidat de transfert: an explicit and bounded hypothesis;
- test / confrontation: validity in the target domain remains to be established.

Historical law: an analogy is never automatic proof.

Modern doctrinal reading: a **bounded transfer hypothesis**. This is a doctrinal notion only. The historical word "candidat" is methodological genealogy; it is not, and must not collide with, a B8 Candidate. `M36_TRANSFER_CANDIDATE_RUNTIME_TYPE=NONE` — there is no transfer-candidate class, schema or enum.

At doctrine level, any transfer hypothesis should make explicit:

- the source domain;
- the target domain;
- the suspected structural correspondence;
- its assumptions;
- what it claims is preserved;
- the conditions under which its validity in the target domain would be established.

These are conceptual obligations, not a runtime schema.

The historical guiding question is preserved: what must remain the same when passing from one domain to another? The source example — coordination among ants versus coordination among software agents — shows entities, capabilities and environments differing, so any commonality would be relational or structural. The source does not formalize which relations or invariants are preserved; therefore `M36_CORRESPONDENCE_SCHEMA=NONE` and `M36_TRANSFER_INVARIANT=UNDEFINED` remain unchanged.

Target-domain revalidation: `SOURCE_VALIDITY != TARGET_VALIDITY`. A correspondence that appears useful in domain A must have its validity re-established independently in domain B. Cross-domain reuse cannot bypass that validation. `TRANSFER_REQUIRES_TARGET_DOMAIN_CONFRONTATION_BEFORE_VALIDITY_CLAIM`.

M36 requires confrontation before any validity claim, but does not conduct it: `M36_EXECUTES_TRANSFER_TEST=NO`, `M36_VALIDATES_TARGET_DOMAIN=NO`. Actual evaluation belongs to the appropriate future or domain mechanism; this doctrine assigns no owner.

Supporting genealogy (not normative): the historical P2.9c experiment reported weak cross-regime knowledge transfer (42/180 successful predictions, 23.3%, MAE 11 px, 21 severe errors), attributed to insufficient recognition that previously learned knowledge can become false under another regime. It motivates **no blind transfer** only; its figures are not M36 thresholds. The historical No-Rebuild line likewise distinguished reusing model weights, reusing knowledge and reusing experience, and required testing transfer rather than blindly reusing old knowledge in an incompatible regime. No-Rebuild is not an M36 runtime.

## 8. Analogy vs causality

`ANALOGY != CAUSALITY`. Historical evidence states directly that an analogical link is not a causal link. M36 never upgrades an analogical relation into a causal one.

## 9. Analogy vs equivalence

`ANALOGY != EQUIVALENCE`. Structural resemblance establishes no mathematical, semantic or physical equivalence.

## 10. Analogy vs identity

`ANALOGY != IDENTITY`. "These two structures resemble each other" is never "these are the same object". See §14.

## 11. Analogy vs truth and proof

- `ANALOGY != TRUTH`: an analogy is a hypothesis; it does not become knowledge by being generated or described.
- `ANALOGY != PROOF`: intuitive or design analogies stay separate from verified evidence.

## 12. Promotion boundary

- `TRANSFERRED != VERIFIED`, `TRANSFERRED != PROMOTED`, `TRANSFERRED != TRUE`
- `TRANSFER_HYPOTHESIS != VERIFIED`, `TRANSFER_HYPOTHESIS != PROMOTED`, `TRANSFER_HYPOTHESIS != TRUE`
- `M36_PROMOTION=NONE`

B8 owns knowledge promotion. M36 cannot accept an analogy as knowledge, promote a correspondence, or mark anything verified or true. Any future analogy-derived candidate that enters promotion machinery must cross the B8 boundary. This doctrine defines only that authority boundary, not an M36→B8 interface.

## 13. Selection boundary

`M36_SELECTION=NONE`. When several analogy hypotheses exist, M36 does not rank, score or select them. Selection, admissibility and capability selection belong to B12.

## 14. Identity boundary with M37

- `M36_CORRESPONDENCE_DOES_NOT_ESTABLISH_IDENTITY=YES`
- `STRUCTURAL_RESEMBLANCE != IDENTITY`
- `SOURCE_VALIDITY != TARGET_VALIDITY`

M36 never establishes persistent, cross-domain or same-object identity, or identity continuity. Historical language describing domains as expressions of "the same invariant" is not canonical identity semantics: the invariant is undefined, and "same invariant → same object" is never inferred. M37 Long-lived Identity owns the identity problem.

## 15. SENS / OS IR boundary

`M36_TRANSLATION=NONE`, `M36_PROJECTION=NONE`. M36 does not translate language or representations, perform multimodal conversion, resolve semantics or bind references.

## 16. Domain-adapter boundary

Reusing the same governance contracts across GPS, Trading, Bank or E-commerce is not cross-domain analogy; it belongs to domain adaptation. M36 does not weaken cross-domain isolation.

## 17. B10 / B11 / B12 boundaries

- B10: M36 V1 has no persistence (`M36_MEMORY_WRITE=NO`, `M36_STATE=NONE`). If analogy hypotheses are ever stored, B10 owns persistence. There is no analogy memory, transfer history or correspondence store.
- B11: M36 scores no confidence, competence or reliability (`M36_CALIBRATION=NONE`); any future calibration of analogy hypotheses belongs to B11.
- B12: see §13.

Learning: `M36_LEARNING=NONE`. M36 does not learn, improve or reuse mappings, perform meta-learning or adapt from outcomes.

## 18. M33 / M34 / M35 boundaries

- M33 reconstructs bounded fragmented material; M36 does not reconstruct. `M33_TO_M36_RUNTIME_INTERFACE=NONE`, `M36_TO_M33_RUNTIME_INTERFACE=NONE`.
- M34 stays closed; its PERTURBATION pattern does not define M36, and its deferred multi-scale, feedback and homeostasis lines are not imported. `M34_REOPEN=NO`.
- M35 is deferred; nothing from it supports M36. `M35_M36_DEPENDENCY=NONE`.

## 19. Runtime, state and memory

- `M36_RUNTIME=NONE`, `M36_TESTS=NONE`, `M36_STATE=NONE`, `M36_EXECUTION=NONE`
- `M36_RUNTIME_INPUT=NONE`, `M36_RUNTIME_OUTPUT=NONE`

There is no analogy engine, mapping function, transfer API, correspondence generator, isomorphism checker or similarity scorer.

Authority: `M36_AUTHORITY=NONE`, `EMITS_ACT=False`, `KERNEL_MUTATION=False`, `KX108_ONLY=UNCHANGED`. No action may be authorized on the basis of an analogy.

## 20. Safety laws

```
ANALOGY != CAUSALITY
ANALOGY != EQUIVALENCE
ANALOGY != IDENTITY
ANALOGY != PROOF
ANALOGY != TRUTH
TRANSFERRED != VERIFIED
TRANSFERRED != PROMOTED
TRANSFERRED != TRUE
TRANSFER_HYPOTHESIS != VERIFIED
TRANSFER_HYPOTHESIS != PROMOTED
TRANSFER_HYPOTHESIS != TRUE
SOURCE_VALIDITY != TARGET_VALIDITY
TRANSFER_REQUIRES_TARGET_DOMAIN_CONFRONTATION_BEFORE_VALIDITY_CLAIM
M36_CORRESPONDENCE_DOES_NOT_ESTABLISH_IDENTITY=YES
COGNITION != AUTHORITY
```

Why a doctrine-only milestone is useful: it preserves a valuable historical intuition — distant knowledge domains may show useful structural resemblance — while preventing that intuition from being mistaken for proof, causality, identity, truth, automatic transfer or automatic knowledge. M36 is the semantic and safety boundary for any future analogy reasoning.

## 21. Non-goals

M36 is not a translation engine, projection engine, multimodal converter, domain adapter, transfer-learning system, fine-tuning system, competence-transfer system, memory system, knowledge-promotion layer, identity layer, similarity-ranking engine, causal-inference engine, authority layer or action layer.

## 22. Reopen protocol

M36 may be reopened only explicitly, through a new forensic and doctrine cycle with independent certification, when future evidence or architecture establishes a concrete independent requirement, such as:

- a canonical correspondence schema;
- explicitly preserved invariants;
- a bounded analogy representation;
- an independently justified analogy generator;
- a formal negative-transfer model;
- an actual consumer requiring typed M36 objects.

Doctrine-only M36 must never evolve silently into a runtime.

## 23. Closure model

`M36_CLOSURE_MODEL=DOCTRINE_ONLY`. Lifecycle: forensic → independent forensic certification → owner decisions → doctrine → independent doctrine certification → CLOSED. There is no spec, RED, GREEN or runtime certification phase unless an explicit reopen occurs.

## 24. Canonical invariants

```
M36_FORM=DOCTRINE_ONLY
M36_CANONICAL_MEANING=CROSS_DOMAIN_ANALOGY
M36_DOMAIN_KIND=KNOWLEDGE_DOMAIN
APPLICATION_DOMAIN_TRANSFER_IS_M36=NO
REPRESENTATION_TRANSLATION_IS_M36=NO
CROSS_MODAL_TRANSFER_IS_M36=NO
SYSTEM_LAYER_TRANSLATION_IS_M36=NO
COMPETENCE_TRANSFER_IS_M36=NO
COMPETENCE_TRANSFER_OWNER=B11_AND_EDUCATION
M36_CORRESPONDENCE_SCHEMA=NONE
M36_TRANSFER_INVARIANT=UNDEFINED
M36_FAILED_TRANSFER_MODEL=NONE
M36_TRANSFER_CANDIDATE_RUNTIME_TYPE=NONE
M36_EXECUTES_TRANSFER_TEST=NO
M36_VALIDATES_TARGET_DOMAIN=NO
TRANSFER_REQUIRES_TARGET_DOMAIN_CONFRONTATION_BEFORE_VALIDITY_CLAIM
SOURCE_VALIDITY != TARGET_VALIDITY
M36_RUNTIME=NONE
M36_TESTS=NONE
M36_STATE=NONE
M36_EXECUTION=NONE
M36_RUNTIME_INPUT=NONE
M36_RUNTIME_OUTPUT=NONE
M36_MEMORY_WRITE=NO
M36_SELECTION=NONE
M36_PROMOTION=NONE
M36_CALIBRATION=NONE
M36_LEARNING=NONE
M36_TRANSLATION=NONE
M36_PROJECTION=NONE
M36_AUTHORITY=NONE
M36_CORRESPONDENCE_DOES_NOT_ESTABLISH_IDENTITY=YES
M35_M36_DEPENDENCY=NONE
EMITS_ACT=False
KERNEL_MUTATION=False
KX108_ONLY=UNCHANGED
COGNITION != AUTHORITY
```

# Universal Domain Integration Protocol V0

Status: SPEC_ONLY
Protocol version: UDIP_V0
Risk: LOW
Runtime impact: NONE

## 1. Purpose

The Universal Domain Integration Protocol V0, or UDIP V0, defines how a professional domain can enter Obsidia, produce information or proposals, be governed by KX108, optionally execute an action, and provide receipts, replay, and proof without rebuilding the Core.

UDIP V0 is not final. It is an architectural contract before implementation.

Trading is the historical reference domain architecture, but this specification is domain-independent. Trading vocabulary is not part of the universal protocol unless explicitly classified as universal.

This document defers the final readiness answer to section 24. The specification remains bounded to integration boundaries, traceability, governance separation, and proof surfaces. It does not attempt to implement domain workflows, KX108, Binder internals, payment, broker behavior, GNSS, fraud, or compensation logic.

## 2. Scope

UDIP V0 covers:

- how a domain declares identity and object mappings;
- how domain sources become provenance-aware observations;
- how domain cognition emits domain signals or proposals;
- how domain outputs become canonical governance payloads;
- how KX108 remains the authority boundary;
- how execution, when present, passes through Binder and outbound adapters;
- how outcomes, receipts, replay, proof, evidence, idempotency references, and compensation references are traced.

UDIP V0 does not define a runtime implementation, code schema, database schema, message bus, or concrete adapter API.

## 3. Core Principles

These invariants are mandatory:

- DOMAIN != AUTHORITY
- DOMAIN SIGNAL != DECISION
- PROPOSAL != ACTION
- KX108 DECISION != BINDER PERMISSION
- BINDER PERMISSION != EXECUTION CAPABILITY
- EXECUTION CAPABILITY != EXECUTION SUCCESS
- EXECUTION RESULT != DOMAIN STATE
- SOURCE != TRUST
- SOURCE PROVENANCE != REALITY AUTHENTICITY
- SIMULATION != REALITY
- REPLAY != EXECUTION
- RECEIPT != DECISION
- EXTERNAL INPUT ADAPTER != OUTBOUND EXECUTION ADAPTER
- REVERSIBILITY != COMPENSATION
- COMPENSATION != ROLLBACK
- HUMAN SOURCE != HUMAN CONTEXT
- PREFERENCE != PERMISSION
- PERMISSION != AUTHORITY

The Core provides boundaries. The Domain Pack provides business meaning.

## 4. Architecture Overview

The abstract flow is:

```text
Domain Sources
  -> Source Provenance
  -> Domain Observation / State
  -> Domain Cognition / Agents / Rules
  -> Domain Signal / Proposal
  -> Canonical Domain Contract
  -> Governance Payload
  -> KX108 Authority Boundary
  -> Decision
  -> Binder Permission Boundary
  -> Outbound Execution Adapter Boundary
  -> External / Physical / Software Execution
  -> Execution Outcome
  -> Receipt
  -> Replay / Proof
```

Some steps are optional or conditional:

- an observation-only domain may stop before execution;
- a decision-support domain may produce signals and receipts without action;
- outbound execution is optional;
- simulation is optional;
- human source is optional;
- physical domains may require a RealityAuthenticityGate before KX108 or before Binder;
- replay is never real execution.

## 5. Universal Core Boundary

| Component | UDIP role | Requirement | Status |
|---|---|---:|---:|
| DomainIdentity | Identifies the connected domain. | REQUIRED | PROVEN_CROSS_DOMAIN |
| DomainObjectMap | Maps domain objects to canonical references without importing domain semantics into Core. | REQUIRED | PROVEN_CROSS_DOMAIN |
| DomainSignal | Carries observations, claims, proposals, unknowns, contradictions, risks, evidence, and provenance. | REQUIRED | PROVEN_CROSS_DOMAIN |
| CanonicalDomainContract | Normalizes domain output for governance without creating a decision. | REQUIRED | PROVEN_CROSS_DOMAIN |
| GovernancePayload | Structured payload submitted to KX108. | REQUIRED | PROVEN_CROSS_DOMAIN |
| KX108AuthorityBoundary | Sole admission authority for ACT / HOLD / BLOCK in the current architecture. | REQUIRED | PROVEN_CROSS_DOMAIN |
| SourceProvenance | Describes source origin. It does not imply trust or reality. Architecturally required when sourced data exists; the current concrete contract evidence remains Trading-led. | REQUIRED when sourced data exists | PROVEN_SINGLE_DOMAIN |
| OrganizationIdentity | Identifies the organization that supplied or owns a source when present. It is not a full organization context. | OPTIONAL when available | PARTIAL |
| BinderPermissionBoundary | Separates KX108 decision from executable permission. | CONDITIONAL | PARTIAL |
| ExecutionAdapterBoundary | Boundary for outbound execution adapters. | CONDITIONAL | PARTIAL |
| ExecutionOutcome reference/model boundary | Trace of what execution attempted or returned, distinct from state. | CONDITIONAL | PARTIAL |
| Receipt Surface / Trace Requirement | Trace linking decision, optional execution, evidence, and consequences. This is not a finalized UniversalReceiptSchema. | REQUIRED for governed decisions; execution trace required only when execution exists | PROVEN_CROSS_DOMAIN |
| Concrete Receipt Schema | Current concrete receipt structure. | REFERENCE_ONLY | PARTIAL |
| Replay | Audit reconstruction or deterministic verification when possible. | OPTIONAL | PROVEN_CROSS_DOMAIN |
| Proof Surface / Proof Reference | Evidence and integrity surface for audit. This is not a universal proof engine or finalized proof model. | REQUIRED when proof/evidence is claimed | PROVEN_CROSS_DOMAIN |
| EvidenceRefs | References to supporting evidence, never proof by themselves. | REQUIRED when evidence exists | PROVEN_CROSS_DOMAIN |
| Idempotency reference | Reference to execution attempt or duplicate detection. | CONDITIONAL | PARTIAL |
| Compensation reference | Reference to required or performed compensation. | CONDITIONAL | HYPOTHESIS |

## 6. Domain Pack Boundary

The following belong to Domain Packs, not Universal Core:

- customer, user, account, portfolio, aircraft, vehicle, product, order, cart;
- checkout, payment provider semantics, refund, shipment, stock rules, fulfillment;
- broker, Alpaca, order book, market state, VaR, positions;
- fraud scoring, AML, sanctions, bank limits, payment rails;
- GNSS, RINEX, RF, sensor thresholds, aircraft envelope, airspace;
- business policies, human approval workflows, compensation workflow;
- concrete execution adapters and final domain state semantics.

The Core may trace references to these concepts. It must not absorb their meaning.

## 7. Inbound Integration

Inbound integration covers external information entering Obsidia:

```text
External Source
  -> ExternalInputAdapter
  -> validation
  -> normalization
  -> SourceProvenance
  -> Canonical Domain path
```

Rules:

- an ExternalInputAdapter imports or observes information;
- it validates and normalizes input;
- it may preserve source identity, organization identity, evidence refs, unknowns, contradictions, and risk flags;
- it must not decide;
- it must not execute;
- it must not obtain authority;
- it must not bypass KX108.

Status: PARTIAL.

Source domains: Trading F8 external adapter audit, ECOM dry-run.

## 8. Canonical Domain Path

A DomainSignal should be able to carry:

- observed information;
- a proposal or intent if present;
- confidence if available;
- unknowns;
- contradictions;
- risk flags;
- evidence refs;
- source provenance.

UDIP V0 does not impose domain-specific actions such as BUY, SELL, refund, payment, GNSS, or shipment.

The CanonicalDomainContract normalizes domain output for governance. It must preserve critical distinctions:

- unknown != false;
- contradiction != risk;
- risk != decision;
- evidence != authority;
- provenance != trust;
- proposed action != authorized action.

The CanonicalDomainContract must never fabricate a decision.

Status: PROVEN_CROSS_DOMAIN.

## 9. Governance / KX108 Boundary

GovernancePayload:

- transports;
- structures;
- conserves;
- references.

It does not decide.

KX108:

- decides admission as ACT / HOLD / BLOCK;
- remains the authority boundary;
- must not execute;
- must not call providers directly;
- must not absorb Domain Packs;
- must not become a business workflow engine.

Domains translate their world into governable structure. KX108 evaluates that structure.

Status: PROVEN_CROSS_DOMAIN.

## 10. Binder / Permission Boundary

UDIP V0 does not define a monolithic PermissionModel.

These concepts remain separate:

| Concept | Meaning | Status |
|---|---|---:|
| AUTHORITY | KX108 admission decision. | PROVEN_CROSS_DOMAIN |
| CAPABILITY | What an adapter or external system can actually do. | PARTIAL |
| ELIGIBILITY | Whether current state allows the action. | PARTIAL |
| POLICY | Domain or business constraints. | PARTIAL |
| BINDER PERMISSION | Post-KX108 permission to construct or allow an execution plan. | PARTIAL |
| EXECUTION RIGHT | Right to attempt execution through an adapter. | HYPOTHESIS |
| EXECUTION SUCCESS | Observed result after attempt. | PARTIAL |

An ACT decision does not guarantee execution is possible.

Status: PARTIAL.

## 11. Outbound Execution

Outbound execution covers actions leaving Obsidia:

```text
KX108 decision
  -> Binder permission
  -> OutboundExecutionAdapter
  -> external / physical / software executor
  -> ExecutionOutcome
  -> Receipt
```

An OutboundExecutionAdapter:

- implements a concrete action capability;
- translates an authorized plan into an external, physical, or software operation;
- returns an execution result or outcome;
- must never create authority;
- must never transform HOLD or BLOCK into ACT;
- must never be confused with an ExternalInputAdapter.

UDIP V0 does not impose broker, payment, sensor, or workflow vocabulary.

Status: PARTIAL.

## 12. Execution Outcome

ExecutionOutcome is a conceptual boundary, not a finalized schema.

It exists to represent an execution result distinct from:

- KX108 decision;
- Binder permission;
- execution capability;
- final domain state.

Candidate outcome states remain candidates:

- attempted;
- succeeded;
- failed;
- partial;
- rejected;
- unknown.

ExecutionOutcome may reference:

- adapter identity;
- external reference;
- provider response reference;
- evidence refs;
- idempotency reference;
- compensation reference;
- observed domain state reference when available and explicitly marked as a hypothesis.

ExecutionOutcome != ObservedDomainState.
ObservedDomainStateRef remains HYPOTHESIS and is not a required Core contract.

Status: PARTIAL.

## 13. Receipts / Proof / Replay

Receipt is trace, not authority.

UDIP V0 distinguishes two levels:

- Receipt Surface / Trace Requirement: the cross-domain need to link governed decisions, optional execution, evidence, and audit consequences.
- Concrete Receipt Schema: the current concrete schema is still primarily Trading-led and remains PARTIAL.

A Receipt should be able to conceptually link:

- requested action;
- governance decision;
- Binder permission;
- adapter identity;
- execution attempt;
- external result reference;
- execution outcome;
- evidence refs;
- duplicate or idempotency reference;
- compensation reference if necessary;
- observed state reference if available.

Replay:

- reconstructs or audits;
- supports deterministic verification when possible;
- does not re-execute real-world actions.

Proof:

- provides a proof surface or proof reference for integrity and audit;
- does not replace physical evidence in physical domains;
- does not turn provenance into trust.
- does not define a universal proof engine or finalized universal proof model.

Status:

- Receipt Surface / Trace Requirement: PROVEN_CROSS_DOMAIN.
- Concrete Receipt Schema: PARTIAL.
- Proof Surface / Proof Reference: PROVEN_CROSS_DOMAIN.
- Universal proof model: MISSING.

## 14. Physical-Domain Extension

Physical domains may require:

- RealityAuthenticity;
- sensor attestation;
- freshness;
- anti-replay;
- multi-source coherence;
- physical envelope checks;
- fail-closed behavior.

RealityAuthenticityGate is a CONDITIONAL DOMAIN EXTENSION.

It is not mandatory for all domains. It is required only when domain claims depend on physical-world authenticity or hostile sensor inputs.

RealityAuthenticity != SourceProvenance.

Status: CONDITIONAL.

Source domain: GPS / defense / aviation.

## 15. Human Extension Point

UDIP V0 recognizes HumanSource as supported.

UDIP V0 does not define a universal HumanContext.

Domain Packs may define:

- user intent;
- consent;
- role;
- approval;
- human confirmation;
- override;
- customer request;
- operator action.

These remain domain extensions unless future evidence proves a universal contract.

HumanSource != HumanContext.
Human request != permission.
Preference != permission.
Permission != authority.

Status:

- HumanSource: PROVEN_SINGLE_DOMAIN.
- HumanContext: MISSING.
- Human extension point: CONDITIONAL.

## 16. Idempotency / Reversibility / Compensation References

Idempotency:

- UDIP V0 must allow reference to an execution attempt;
- UDIP V0 must allow duplicate status or duplicate detection to be traced;
- deduplication rules remain Domain Pack or adapter-specific.

Reversibility:

- UDIP V0 may reference whether an action is reversible, irreversible, or unknown;
- it must not implement domain reversal logic.

Compensation:

- UDIP V0 may reference compensation_required or compensation_ref;
- compensation logic remains Domain Pack-specific.

Non-equivalences:

- reversal != compensation;
- compensation != rollback;
- failure != compensation.

Status:

- Idempotency reference: PARTIAL.
- Irreversibility: PROVEN_SINGLE_DOMAIN.
- Compensation reference: HYPOTHESIS.
- Compensation semantics: MISSING.

## 17. Domain Pack Minimum

To connect a new domain, a Domain Pack should provide:

| Item | Requirement | Status |
|---|---:|---:|
| DomainIdentity | REQUIRED | PROVEN_CROSS_DOMAIN |
| DomainObjectMap | REQUIRED | PROVEN_CROSS_DOMAIN |
| Source definitions | REQUIRED | PROVEN_CROSS_DOMAIN |
| Domain observations or state | REQUIRED | PROVEN_CROSS_DOMAIN |
| DomainSignal mapping | REQUIRED | PROVEN_CROSS_DOMAIN |
| Canonical contract mapping | REQUIRED | PROVEN_CROSS_DOMAIN |
| Governance mapping | REQUIRED | PROVEN_CROSS_DOMAIN |
| Execution extension | CONDITIONAL | PARTIAL |
| Receipt/proof surface mapping | REQUIRED | PROVEN_CROSS_DOMAIN |
| Tests/invariants | REQUIRED before implementation | PARTIAL |
| Physical authenticity gate | CONDITIONAL | CONDITIONAL |
| Human context extension | OPTIONAL | HYPOTHESIS |
| Compensation mapping | CONDITIONAL | HYPOTHESIS |

## 18. Conformance Requirements

A domain is UDIP_CONFORMANT only if it proves, documentarily or by tests depending on stage, that it satisfies the following rules.

A UDIP-conformant domain MUST preserve, when present:

- unknowns;
- contradictions;
- risk flags;
- evidence references;
- provenance.

A UDIP-conformant domain MUST NOT:

- create a parallel authority;
- bypass KX108 for governed admission;
- bypass Binder for governed execution;
- turn source provenance into trust;
- treat replay as real execution;
- let an ExternalInputAdapter act as an OutboundExecutionAdapter implicitly;
- let an ExternalInputAdapter acquire authority, Binder permission, or execution rights merely because it can provide normalized input;
- leak domain-specific semantics into Universal Core.

A UDIP-conformant domain MUST:

- record execution outcome separately from final domain state when execution exists;
- record duplicate or idempotency references when execution can be retried;
- record compensation references when compensation is required;
- produce the required audit trace or receipt surface for governed decisions;
- produce execution receipt surface only when a governed execution exists.

A domain MAY:

- have no execution path;
- have no simulation;
- have no human source;
- have no physical RealityAuthenticity extension.

### UDIP Conformance Matrix

| Requirement | Observation-only | Decision-support | Software execution | External service | Physical world |
|---|---:|---:|---:|---:|---:|
| DomainIdentity | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| DomainSignal | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| KX108 boundary | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| Receipt surface | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| Execution receipt surface | N/A | N/A | REQUIRED if governed execution exists | REQUIRED if governed execution exists | REQUIRED if governed execution exists |
| Binder boundary | N/A | OPTIONAL | REQUIRED if action | REQUIRED if action | REQUIRED if action |
| Outbound adapter | N/A | N/A | CONDITIONAL | REQUIRED if action | CONDITIONAL |
| ExecutionOutcome | N/A | N/A | REQUIRED if action | REQUIRED if action | REQUIRED if action |
| RealityAuthenticity | N/A | N/A | N/A | CONDITIONAL | REQUIRED when physical claims matter |
| Idempotency reference | N/A | N/A | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Compensation reference | N/A | N/A | CONDITIONAL | CONDITIONAL | CONDITIONAL |

Domain classes are profiles, not a final taxonomy.

## 19. Versioning

UDIP V0 should support version references:

- protocol_version;
- schema_version;
- domain_pack_version;
- adapter_version when adapters exist.

UDIP V0 does not define PromotionRules.

PromotionRules remain MISSING until separately proven.

## 20. Non-Goals

UDIP is not:

- a new KX108;
- a new Sigma;
- a general orchestrator;
- a business workflow engine;
- a universal ontology engine;
- a compensation engine;
- a payment system;
- a broker;
- a GNSS framework;
- a business policy engine;
- a replacement for Domain Packs;
- a runtime patch;
- an implementation plan.

## 21. Do-Not-Generalize

Do not generalize these into Universal Core:

Trading:

- BUY;
- SELL;
- broker;
- Alpaca;
- portfolio;
- market;
- order book;
- VaR;
- position lifecycle.

Bank:

- fraud logic;
- AML;
- sanctions;
- payment rails;
- bank-specific policies;
- account-specific workflow.

GPS / defense / aviation:

- GNSS;
- RF;
- RINEX;
- aircraft;
- collision;
- airspace;
- sensor thresholds;
- physical envelope semantics.

Ecom:

- cart;
- checkout;
- refund;
- shipment;
- fulfillment;
- customer lifecycle;
- payment provider semantics.

## 22. Evidence / Traceability

| UDIP concept | Source domain | Evidence | Status |
|---|---|---|---:|
| DomainIdentity | Trading, Bank, GPS, ECOM dry-run | Each audited domain requires a declared domain boundary before governance; identity is an architectural integration requirement, not a business ontology. | PROVEN_CROSS_DOMAIN |
| DomainObjectMap | Bank, GPS, ECOM dry-run, Trading | Domain-specific objects differ while the Core only needs mapped references; object meaning stays in Domain Pack. | PROVEN_CROSS_DOMAIN |
| DomainSignal | Trading, Bank, GPS, ECOM | Domains emit observations, proposals, risks, unknowns, contradictions, and evidence toward governance without becoming authority. | PROVEN_CROSS_DOMAIN |
| CanonicalDomainContract | Trading, Bank, GPS, ECOM stress tests | Trading-led implementation pattern survived Bank/GPS/ECOM challenges as an architecture pattern; this does not mean identical implementation exists cross-domain. | PROVEN_CROSS_DOMAIN |
| GovernancePayload | Trading, Bank, GPS, ECOM | Cross-domain path requires a structured payload for KX108 while preserving evidence, risk, unknowns, and contradictions. | PROVEN_CROSS_DOMAIN |
| KX108 authority boundary | Trading, Bank, GPS | Trading Authority ACT/HOLD/BLOCK; Bank and GPS KX108_ONLY/fail-closed domain packets | PROVEN_CROSS_DOMAIN |
| OrganizationIdentity | Trading F8 | ExternalSignal preserves organization_id; no universal OrganizationContext is proven. | PARTIAL |
| Binder permission boundary | Trading | Trading Binder planner refuses plans without ACT and state support | PARTIAL |
| Execution result separate from decision | Trading | Trading ExecutionPlan and ExecutionResult split | PROVEN_SINGLE_DOMAIN |
| Receipt Surface / Trace Requirement | Trading, Bank, GPS, ECOM dry-run | All audited domains require traceability, proof, or fail-closed evidence; not a finalized UniversalReceiptSchema. | PROVEN_CROSS_DOMAIN |
| Concrete Receipt Schema | Trading | Trading CycleReceipt carries decision, execution_plan, execution_result, consequence, extensions. | PARTIAL |
| Proof Surface / Proof Reference | Trading, Bank, GPS, ECOM dry-run | Domains require an integrity/proof surface or evidence reference; no universal proof engine is defined. | PROVEN_CROSS_DOMAIN |
| SourceProvenance categories | Trading | native, external, human, replay, simulation observed in SourceProvenance closure | PROVEN_SINGLE_DOMAIN |
| Source provenance != trust | Trading | SourceProvenance audit and tests preserve separation from authority | PROVEN_SINGLE_DOMAIN |
| ExternalInputAdapter | Trading F8 | ExternalSignal, validation, normalization, provenance preservation | PARTIAL |
| OutboundExecutionAdapter | Trading, ECOM dry-run | Trading broker adapter pattern plus ECOM payment provider dry-run | PARTIAL |
| ExternalInputAdapter != OutboundExecutionAdapter | F8, ECOM dry-run | F8 imports signals; ECOM requires outbound payment/service execution | PARTIAL |
| RealityAuthenticityGate | GPS | GPS physical authenticity, sensor attestation, anti-replay, freshness, fail-closed | CONDITIONAL |
| Domain-specific policy remains outside Core | Bank, GPS, ECOM | Fraud/AML, sensor thresholds, stock/refund/fulfillment are domain semantics | PROVEN_CROSS_DOMAIN |
| HumanSource | Trading | Human source category supported in provenance | PROVEN_SINGLE_DOMAIN |
| HumanContext | ECOM dry-run, Trading audit | Human context not proven as universal | MISSING |
| Idempotency reference | Trading, ECOM dry-run | Trading client order id/result references; ECOM duplicate/timeout/retry requires trace | PARTIAL |
| Compensation reference | ECOM dry-run | Payment success with order cancellation requires reference, not universal workflow | HYPOTHESIS |
| ExecutionOutcome | Trading, ECOM dry-run | Trading ExecutionResult exists; ECOM shows provider response/outcome need | PARTIAL |
| ObservedDomainStateRef | ECOM dry-run | Payment success can differ from fulfillment state; this remains a reference hypothesis, not a required Core contract. | HYPOTHESIS |
| PromotionRules | Cross-domain audits | Not proven | MISSING |

## 23. Open Gaps

Open gaps before implementation:

- no final executable schema for DomainSignal;
- no final executable schema for CanonicalDomainContract;
- no final executable schema for ExecutionOutcome;
- no concrete universal adapter API;
- no universal compensation semantics;
- no universal HumanContext;
- no PromotionRules;
- no cross-domain executable conformance test suite yet;
- no proof that all candidate outcome states are necessary;
- no proof that idempotency rules can be universal rather than adapter-specific.

These gaps do not block UDIP V0 as an architectural contract. They block runtime implementation.

## 24. Status / Next Step

UDIP V0 status: SPEC_ONLY.

Architectural readiness: YES.

Implementation readiness: NO.

Final question:

Is UDIP V0 sufficiently bounded to serve as an architectural contract before implementation?

Answer: YES.

Justification: UDIP V0 is bounded to integration boundaries, traceability, governance separation, proof surfaces, and domain/Core separation. It does not claim implementation readiness, does not define a universal proof engine, does not define a finalized receipt schema, and does not absorb domain-specific workflows.

Next step:

Create a separate implementation proposal for UDIP V0 conformance tests and minimal schema drafts. That proposal must not modify KX108, Binder, or existing Domain Packs without explicit approval.

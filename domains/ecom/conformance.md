# Conformance Notes

Status: SCAFFOLD ONLY

This domain must eventually prove UDIP V0 conformance.

Required future checks:

- MUST preserve unknowns, contradictions, risk flags, evidence references, and provenance when present.
- MUST NOT create a parallel authority.
- MUST NOT bypass KX108 for governed admission.
- MUST NOT bypass Binder for governed execution.
- MUST NOT turn source provenance into trust.
- MUST NOT treat replay as execution.
- MUST NOT let an ExternalInputAdapter act as an OutboundExecutionAdapter implicitly.
- MUST NOT leak domain-specific semantics into Universal Core.

No tests are implemented in this scaffold.

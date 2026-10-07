"""B7 Cognitive Role / Resolution runtime (minimal, isolated).

SENS -> B6 StateEntry -> mechanical detector -> CognitiveResolutionRequest -> role router ->
(provider proposal, supplied as data) -> TRANSLATOR -> Validation / Retranslation Gate ->
NEW B6 working StateEntry | REJECT | STILL_UNRESOLVED.

No model or provider call, no network, no memory write, no ACT, no kernel mutation:
decision authority stays KX108_ONLY. Sources: docs/architecture/B7_COGNITIVE_ROLE_SPEC_V1.md and
docs/architecture/B7_RUNTIME_DETERMINISM_CONTRACT_V1.md.
"""
from app.cognition.b7.contracts import (BOUNDARY, DEFAULT_FORBIDDEN_OPERATIONS, MAX_CANDIDATE_CHARS,
                                        MAX_REQUEST_CHARS, ROLE_RIGHTS, CandidateStatus,
                                        CognitiveResolutionCandidate, CognitiveResolutionRequest, CognitiveRole,
                                        CognitiveValidationVerdict, ConfidenceClass, ForbiddenOperation,
                                        RequiredCandidateKind, UnresolvedKind, forbidden_operations_for,
                                        required_candidate_kind_for)
from app.cognition.b7.detector import classify_marker, detect_unresolved, make_request
from app.cognition.b7.router import eligible_roles
from app.cognition.b7.translator import propose, translate
from app.cognition.b7.validation import (ValidationResult, admit_trusted_context, register_derived,
                                         validate_candidate, validate_candidates)

__all__ = ["BOUNDARY", "DEFAULT_FORBIDDEN_OPERATIONS", "MAX_CANDIDATE_CHARS", "MAX_REQUEST_CHARS", "ROLE_RIGHTS",
           "CandidateStatus", "CognitiveResolutionCandidate", "CognitiveResolutionRequest", "CognitiveRole",
           "CognitiveValidationVerdict", "ConfidenceClass", "ForbiddenOperation", "RequiredCandidateKind",
           "UnresolvedKind", "ValidationResult", "admit_trusted_context", "classify_marker", "detect_unresolved",
           "eligible_roles", "forbidden_operations_for", "make_request", "propose", "register_derived",
           "required_candidate_kind_for", "translate", "validate_candidate", "validate_candidates"]

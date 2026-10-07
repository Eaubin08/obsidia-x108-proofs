"""B7 role router: unresolved_kind -> eligible ROLE ids (spec §12). Never truth, action or provider."""
from __future__ import annotations

from app.cognition.b7.contracts import CognitiveRole as R
from app.cognition.b7.contracts import UnresolvedKind as K

_ELIGIBLE: dict[K, frozenset[R]] = {
    K.COREFERENCE: frozenset({R.UNDERSTANDER, R.RESOLVER, R.CRITIC}),
    K.SOURCE_SCOPE: frozenset({R.UNDERSTANDER, R.RESOLVER, R.CRITIC}),
    K.CONDITIONAL_ATTACHMENT: frozenset({R.UNDERSTANDER, R.RESOLVER, R.CRITIC}),
    K.TEMPORAL_REFERENCE: frozenset({R.UNDERSTANDER, R.RESOLVER, R.CRITIC}),
    K.DEIXIS: frozenset({R.UNDERSTANDER, R.INVESTIGATOR, R.RESOLVER}),
    K.ENTITY_IDENTITY: frozenset({R.INVESTIGATOR, R.RESOLVER, R.CRITIC}),
    K.CONTRADICTION: frozenset({R.CRITIC, R.COMPARATOR}),
    K.UNKNOWN_TERM_OR_PREDICATE: frozenset({R.UNDERSTANDER, R.INVESTIGATOR, R.RESOLVER}),
    K.DOMAIN_SPECIFIC_AMBIGUITY: frozenset({R.INVESTIGATOR, R.BUILDER_PROPOSER, R.CRITIC}),
    K.WORLD_OR_PHYSICAL_REFERENCE: frozenset({R.INVESTIGATOR}),
    K.OTHER_EXPLICIT_UNRESOLVED: frozenset({R.UNDERSTANDER, R.CRITIC}),      # fail-closed: no RESOLVER
}


def eligible_roles(kind: K) -> frozenset[R]:
    return _ELIGIBLE[K(kind)]

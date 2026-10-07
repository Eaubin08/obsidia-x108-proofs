"""B7 role router: unresolved_kind -> eligible roles only (spec §12; T3, T4)."""
from __future__ import annotations

import pytest

_ROUTES = {
    "COREFERENCE": {"UNDERSTANDER", "RESOLVER", "CRITIC"},
    "SOURCE_SCOPE": {"UNDERSTANDER", "RESOLVER", "CRITIC"},
    "CONDITIONAL_ATTACHMENT": {"UNDERSTANDER", "RESOLVER", "CRITIC"},
    "TEMPORAL_REFERENCE": {"UNDERSTANDER", "RESOLVER", "CRITIC"},
    "DEIXIS": {"UNDERSTANDER", "INVESTIGATOR", "RESOLVER"},
    "ENTITY_IDENTITY": {"INVESTIGATOR", "RESOLVER", "CRITIC"},
    "CONTRADICTION": {"CRITIC", "COMPARATOR"},
    "UNKNOWN_TERM_OR_PREDICATE": {"UNDERSTANDER", "INVESTIGATOR", "RESOLVER"},
    "DOMAIN_SPECIFIC_AMBIGUITY": {"INVESTIGATOR", "BUILDER_PROPOSER", "CRITIC"},
    "WORLD_OR_PHYSICAL_REFERENCE": {"INVESTIGATOR"},
    "OTHER_EXPLICIT_UNRESOLVED": {"UNDERSTANDER", "CRITIC"},
}


@pytest.mark.parametrize("kind,roles", sorted(_ROUTES.items()))
def test_t3_router_returns_eligible_roles_only(b7, kind, roles):
    out = b7.eligible_roles(b7.UnresolvedKind(kind))
    assert {r.value for r in out} == roles
    assert all(isinstance(r, b7.CognitiveRole) for r in out)          # roles, never provider ids


def test_t4_router_selects_no_truth_action_or_provider(b7):
    for kind in b7.UnresolvedKind:
        for role in b7.eligible_roles(kind):
            assert role.value not in {"ALLOW", "HOLD", "BLOCK", "ACT", "EXECUTE", "DECIDE"}
            assert not role.value.lower().startswith(("provider", "brody", "obsidure"))


def test_other_explicit_has_no_resolver(b7):
    assert b7.CognitiveRole.RESOLVER not in b7.eligible_roles(b7.UnresolvedKind.OTHER_EXPLICIT_UNRESOLVED)

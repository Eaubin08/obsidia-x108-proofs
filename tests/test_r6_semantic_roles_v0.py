from periphery.cognition.semantic_roles_v0 import (
    SemanticResolutionStatusV0,
    SemanticRoleBindingV0,
    SemanticRoleCandidateV0,
    SemanticRoleKindV0,
    build_semantic_role_projection_v0,
)


def _resolved(role, value, span=None):
    return SemanticRoleBindingV0(
        role=role,
        status=SemanticResolutionStatusV0.RESOLVED,
        candidates=(SemanticRoleCandidateV0(value=value, source_span=span),),
    )


def test_memory_as_focus_is_not_memory_as_source():
    a = "Explique ce que tu sais en mémoire sur Obsidia, et détaille."
    pa = build_semantic_role_projection_v0(
        raw_utterance=a,
        bindings=(
            _resolved(SemanticRoleKindV0.FOCUS, "MEMORY"),
            _resolved(SemanticRoleKindV0.SCOPE, "OBSIDIA"),
            _resolved(SemanticRoleKindV0.OPERATION, "EXPLAIN"),
            _resolved(SemanticRoleKindV0.QUALIFIER, "DETAILED"),
            SemanticRoleBindingV0(
                role=SemanticRoleKindV0.SOURCE_OR_INSTRUMENT,
                status=SemanticResolutionStatusV0.UNKNOWN,
            ),
        ),
        source_refs=("live-finding:jarjar-memory-focus",),
    )

    b = "Explique Obsidia en utilisant ta mémoire."
    pb = build_semantic_role_projection_v0(
        raw_utterance=b,
        bindings=(
            _resolved(SemanticRoleKindV0.FOCUS, "OBSIDIA"),
            SemanticRoleBindingV0(
                role=SemanticRoleKindV0.SCOPE,
                status=SemanticResolutionStatusV0.UNKNOWN,
            ),
            _resolved(SemanticRoleKindV0.OPERATION, "EXPLAIN"),
            SemanticRoleBindingV0(
                role=SemanticRoleKindV0.QUALIFIER,
                status=SemanticResolutionStatusV0.UNKNOWN,
            ),
            _resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT, "MEMORY"),
        ),
        source_refs=("contrast:memory-as-instrument",),
    )

    assert pa.resolved(SemanticRoleKindV0.FOCUS) == "MEMORY"
    assert pa.resolved(SemanticRoleKindV0.SCOPE) == "OBSIDIA"
    assert pa.resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT) is None

    assert pb.resolved(SemanticRoleKindV0.FOCUS) == "OBSIDIA"
    assert pb.resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT) == "MEMORY"

    assert pa.projection_id != pb.projection_id


def test_ambiguous_role_preserves_candidates_without_implicit_winner():
    projection = build_semantic_role_projection_v0(
        raw_utterance="Parle-moi de la mémoire autour d'Obsidia.",
        bindings=(
            SemanticRoleBindingV0(
                role=SemanticRoleKindV0.FOCUS,
                status=SemanticResolutionStatusV0.AMBIGUOUS,
                candidates=(
                    SemanticRoleCandidateV0("MEMORY"),
                    SemanticRoleCandidateV0("OBSIDIA"),
                ),
            ),
        ),
    )

    focus = projection.binding(SemanticRoleKindV0.FOCUS)
    assert focus is not None
    assert focus.status is SemanticResolutionStatusV0.AMBIGUOUS
    assert focus.resolved_value is None
    assert [c.value for c in focus.candidates] == ["MEMORY", "OBSIDIA"]


def test_unknown_role_never_invents_candidate():
    projection = build_semantic_role_projection_v0(
        raw_utterance="Explique ceci.",
        bindings=(
            SemanticRoleBindingV0(
                role=SemanticRoleKindV0.SCOPE,
                status=SemanticResolutionStatusV0.UNKNOWN,
            ),
        ),
    )

    scope = projection.binding(SemanticRoleKindV0.SCOPE)
    assert scope is not None
    assert scope.candidates == ()
    assert scope.resolved_value is None


def test_brody_context_is_readonly_non_sovereign():
    projection = build_semantic_role_projection_v0(
        raw_utterance="Explique Obsidia.",
        bindings=(
            _resolved(SemanticRoleKindV0.FOCUS, "OBSIDIA"),
            _resolved(SemanticRoleKindV0.OPERATION, "EXPLAIN"),
        ),
    )

    ctx = projection.to_brody_context()

    assert ctx["readonly"] is True
    assert ctx["non_sovereign"] is True
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["allowed_to_decide"] is False
    assert ctx["allowed_to_act"] is False
    assert ctx["emits_act"] is False
    assert ctx["emits_verdict"] is False
    assert ctx["memory_write"] is False
    assert ctx["kernel_mutation"] is False


def test_invalid_status_cardinality_fails_closed():
    import pytest

    with pytest.raises(ValueError):
        SemanticRoleBindingV0(
            role=SemanticRoleKindV0.FOCUS,
            status=SemanticResolutionStatusV0.RESOLVED,
            candidates=(),
        )

    with pytest.raises(ValueError):
        SemanticRoleBindingV0(
            role=SemanticRoleKindV0.FOCUS,
            status=SemanticResolutionStatusV0.AMBIGUOUS,
            candidates=(SemanticRoleCandidateV0("MEMORY"),),
        )

    with pytest.raises(ValueError):
        SemanticRoleBindingV0(
            role=SemanticRoleKindV0.FOCUS,
            status=SemanticResolutionStatusV0.UNKNOWN,
            candidates=(SemanticRoleCandidateV0("MEMORY"),),
        )

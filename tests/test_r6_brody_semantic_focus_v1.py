from periphery.cognition.brody_semantic_focus_v1 import (
    build_brody_semantic_focus_projection_v1,
)
from periphery.cognition.semantic_roles_v0 import SemanticRoleKindV0


def test_brody_sens_v1_memory_is_focus_obsidia_is_scope():
    raw = "Explique ce que tu sais en mémoire sur Obsidia, et détaille."
    projection = build_brody_semantic_focus_projection_v1(raw)
    assert projection is not None
    assert projection.resolved(SemanticRoleKindV0.FOCUS) == "MEMORY"
    assert projection.resolved(SemanticRoleKindV0.SCOPE) == "OBSIDIA"
    assert projection.resolved(SemanticRoleKindV0.OPERATION) == "EXPLAIN"
    assert projection.resolved(SemanticRoleKindV0.QUALIFIER) == "DETAILED"
    assert projection.resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT) is None


def test_brody_sens_v1_memory_can_be_instrument_not_focus():
    raw = "Explique Obsidia en utilisant ta mémoire."
    projection = build_brody_semantic_focus_projection_v1(raw)
    assert projection is not None
    assert projection.resolved(SemanticRoleKindV0.FOCUS) == "OBSIDIA"
    assert projection.resolved(SemanticRoleKindV0.OPERATION) == "EXPLAIN"
    assert projection.resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT) == "MEMORY"
    assert projection.resolved(SemanticRoleKindV0.SCOPE) is None


def test_brody_sens_v1_direct_obsidia_stays_obsidia_focus():
    raw = "Explique Obsidia simplement."
    projection = build_brody_semantic_focus_projection_v1(raw)
    assert projection is not None
    assert projection.resolved(SemanticRoleKindV0.FOCUS) == "OBSIDIA"
    assert projection.resolved(SemanticRoleKindV0.OPERATION) == "EXPLAIN"
    assert projection.resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT) is None


def test_brody_sens_v1_unknown_domain_fails_closed():
    projection = build_brody_semantic_focus_projection_v1(
        "Que représentent les 34 arbres ?"
    )
    assert projection is None


def test_brody_sens_v1_is_non_sovereign():
    projection = build_brody_semantic_focus_projection_v1(
        "Explique Obsidia en utilisant ta mémoire."
    )
    ctx = projection.to_brody_context()
    assert ctx["readonly"] is True
    assert ctx["non_sovereign"] is True
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["allowed_to_decide"] is False
    assert ctx["allowed_to_act"] is False
    assert ctx["memory_write"] is False
    assert ctx["kernel_mutation"] is False


def test_brody_sens_v1_gps_p4_p5_noncausal_focus():
    raw = (
        "Explique en lecture seule l'anomalie d'intégrité GPS observée et "
        "ses limites de preuve, sans conclure à une cause ni agir."
    )
    projection = build_brody_semantic_focus_projection_v1(raw)

    assert projection is not None
    assert projection.resolved(SemanticRoleKindV0.FOCUS) == "GPS_DEFENSE_EVIDENCE"
    assert projection.resolved(SemanticRoleKindV0.OPERATION) == "EXPLAIN"
    assert projection.resolved(SemanticRoleKindV0.QUALIFIER) == "NON_CAUSAL_NO_ACTION"

    ctx = projection.to_brody_context()
    assert ctx["readonly"] is True
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["allowed_to_decide"] is False
    assert ctx["allowed_to_act"] is False


def test_brody_sens_v1_gps_recorded_evidence_no_decision_focus():
    raw = (
        "Explique en lecture seule le statut de cette preuve GPS enregistrée, "
        "sans décider ni agir."
    )
    projection = build_brody_semantic_focus_projection_v1(raw)

    assert projection is not None
    assert projection.resolved(SemanticRoleKindV0.FOCUS) == "GPS_DEFENSE_EVIDENCE"
    assert projection.resolved(SemanticRoleKindV0.OPERATION) == "EXPLAIN"
    assert projection.resolved(SemanticRoleKindV0.QUALIFIER) == "NO_DECISION_NO_ACTION"

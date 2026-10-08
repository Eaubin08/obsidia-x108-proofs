from apps.obsidia_api.brody_pre_reasoning_adapter import (
    build_brody_pre_reasoning_snapshot,
)
from apps.obsidia_api.brody_semantic_query_router import (
    build_semantic_query,
)
from periphery.cognition.brody_semantic_focus_v1 import (
    build_brody_semantic_focus_projection_v1,
)


P4_P5_MESSAGE = (
    "Explique en lecture seule l'anomalie d'intégrité GPS observée et "
    "ses limites de preuve, sans conclure à une cause ni agir."
)

CTTC_MESSAGE = (
    "Explique en lecture seule le statut de cette preuve GPS enregistrée, "
    "sans décider ni agir."
)


def test_gps_route_beats_generic_proof_query():
    routed = build_semantic_query(P4_P5_MESSAGE)

    assert routed["route"] == "TOPIC_MATCHED"
    assert routed["topic"] == "GPS_DEFENSE_EVIDENCE"
    assert routed["primary_query"] == "gps"
    assert routed["matched_trigger"].lower() == "gps"


def test_p4_p5_message_has_no_unresolved_lexical_debt():
    projection = build_brody_semantic_focus_projection_v1(P4_P5_MESSAGE)
    snapshot = build_brody_pre_reasoning_snapshot(
        user_message=P4_P5_MESSAGE,
        language="fr",
        semantic_role_projection=projection,
    )

    assert snapshot["semantic_query_snapshot"]["topic"] == "GPS_DEFENSE_EVIDENCE"
    assert snapshot["unknown_qualification"]["unresolved_unknowns"] == []
    assert snapshot["reasoning_directive"]["resolution_targets"] == []


def test_cttc_message_has_no_unresolved_lexical_debt():
    projection = build_brody_semantic_focus_projection_v1(CTTC_MESSAGE)
    snapshot = build_brody_pre_reasoning_snapshot(
        user_message=CTTC_MESSAGE,
        language="fr",
        semantic_role_projection=projection,
    )

    assert snapshot["semantic_query_snapshot"]["topic"] == "GPS_DEFENSE_EVIDENCE"
    assert snapshot["unknown_qualification"]["unresolved_unknowns"] == []
    assert snapshot["reasoning_directive"]["resolution_targets"] == []


def test_generic_formal_proof_still_routes_to_proof_query():
    routed = build_semantic_query("Explique cette preuve Lean et son Merkle.")

    assert routed["topic"] == "PROOF_QUERY"
    assert routed["route"] == "TOPIC_MATCHED"

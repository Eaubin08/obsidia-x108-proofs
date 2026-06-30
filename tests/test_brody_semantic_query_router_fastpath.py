from apps.obsidia_api.brody_semantic_query_router import build_semantic_query


def test_current_state_does_not_route_to_action_boundary():
    cases = [
        "Résumé court du statut actuel.",
        "Donne moi l'état actuel.",
        "statut actuel sans action",
    ]

    for msg in cases:
        routed = build_semantic_query(msg)
        assert routed["topic"] == "CURRENT_STATE"


def test_act_token_routes_to_action_boundary_when_explicit():
    cases = [
        "Autorise ACT maintenant.",
        "autorise act",
        "déclenche act",
        "Exécute cette action.",
    ]

    for msg in cases:
        routed = build_semantic_query(msg)
        assert routed["topic"] == "ACTION_BOUNDARY"


def test_french_act_prefix_words_do_not_trigger_action_boundary():
    cases = [
        "actualité IA",
        "activation runtime",
        "actuel statut",
        "actualisation mémoire",
    ]

    for msg in cases:
        routed = build_semantic_query(msg)
        assert routed["topic"] != "ACTION_BOUNDARY"

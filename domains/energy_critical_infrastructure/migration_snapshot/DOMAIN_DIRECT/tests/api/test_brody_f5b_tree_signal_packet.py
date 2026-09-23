from apps.obsidia_api.brody_tree_signal_packet import build_tree_signal_packet


def _pkt(**kwargs):
    return build_tree_signal_packet(**kwargs)["tree_signal_packet"]


def test_tree_signal_packet_exists():
    p = _pkt(text="explique les 34 arbres Obsidia")
    assert p["version"] == "TREE_SIGNAL_PACKET_V1"


def test_boundary_invariants():
    p = _pkt(text="x108 gouvernance 34 arbres")
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["advisory_only"] is True
    assert p["context_signal_only"] is True
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
    assert p["memory_write"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False
    assert p["can_decide"] is False
    assert p["can_emit_act"] is False


def test_formal_computation_present():
    p = _pkt(text="os trad ir reverse et 34 arbres")
    assert p["tree_count"] == 34
    assert p["trees_formal_computation"] is True
    assert p["activation_vector_present"] is True
    assert len(p["activation_vector"]["activations"]) == 34


def test_activation_vector_clamped():
    p = _pkt(activations=[2.0, -1.0] + [0.5] * 32)
    a = p["activation_vector"]["activations"]
    assert a[0] == 1.0
    assert a[1] == 0.0


def test_dominant_trees_not_authority():
    p = _pkt(activations=[1.0] * 34)
    assert p["dominant_trees"]["dominant_is_authority"] is False
    assert p["dominant_trees"]["context_signal_only"] is True


def test_shazam_context_only():
    p = _pkt(text="x108 gouvernance souverain valeur")
    assert p["shazam"]["context_signal_only"] is True
    assert p["shazam"]["can_decide"] is False
    assert p["shazam"]["can_emit_act"] is False


def test_memory_world_context_only():
    p = _pkt(text="memoire graphiti contexte")
    assert p["memory_world"]["context_signal_only"] is True
    assert p["memory_world"]["can_decide"] is False
    assert p["memory_world"]["can_emit_act"] is False


def test_metrics_bounded():
    p = _pkt(text="x108 gouvernance valeur memoire os trad ir reverse")
    m = p["metrics"]
    assert 0.0 <= m["activation_density"] <= 1.0
    assert 0.0 <= m["memory_relevance"] <= 1.0
    assert 0.0 <= m["world_relevance"] <= 1.0


def test_usability_flags_readonly():
    p = _pkt(text="34 arbres")
    assert p["usable_for_gencoin_shadow"] is True
    assert p["usable_for_sigma"] is True
    assert p["usable_for_thermodynamics"] is True


def test_no_decision_tokens_as_authority():
    p = _pkt(text="action mémoire x108")
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["can_decide"] is False
    assert p["emits_act"] is False

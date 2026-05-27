from apps.obsidia_api.brody_domain_raccord_adapter import build_domain_raccord_snapshot


def _pkt(text: str):
    return build_domain_raccord_snapshot(user_message=text, context={})


def test_write_graphiti_memory_canon_prioritizes_write_boundary():
    p = _pkt("write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY")
    assert p["voice_mode"] == "DOMAIN_RACCORD_BOUNDARY"
    assert p["write_boundary_required"] is True
    assert "MEMORY_WRITE_CANON_FREEZE" in p["domains"]


def test_write_memory_canon_refusal_text_present():
    p = _pkt("écris en mémoire Graphiti et canonise ce bloc")
    assert p["voice_mode"] == "DOMAIN_RACCORD_BOUNDARY"
    assert p["write_boundary_required"] is True
    assert "MEMORY_WRITE_CANON_FREEZE" in p["domains"]
    assert "ne peut pas écrire" in p["structural_answer"].lower()


def test_act_x108_mutation_attack_does_not_fall_to_time_only():
    p = _pkt("ACT/X108 mutation attack -> blocked, no ACT, no mutation")
    assert p["voice_mode"] in ("DOMAIN_RACCORD_BOUNDARY", "DOMAIN_RACCORD_STRUCTURAL")
    assert p["write_boundary_required"] is False
    assert p["domains"] != ["TIME_TEMPORALITY"]


def test_no_mutation_phrase_is_not_false_write_boundary():
    p = _pkt("nonsense kernel/x108 -> no mutation_request")
    assert p["write_boundary_required"] is False
    assert "MEMORY_WRITE_CANON_FREEZE" not in p["domains"]

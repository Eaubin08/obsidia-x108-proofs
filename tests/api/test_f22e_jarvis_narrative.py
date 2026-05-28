"""F22E — Jarvis narrative and chaos guard tests."""
from apps.obsidia_api.brody_domain_raccord_adapter import (
    build_domain_raccord_snapshot,
    has_memory_write_request,
)
from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer


def test_authority_question_answers_kx108_first():
    snap = build_domain_raccord_snapshot(
        "Qui décide dans ton architecture ? Réponds clairement sans proposer d’action."
    )
    assert snap["voice_mode"] == "DOMAIN_RACCORD_AUTHORITY"
    assert "AUTHORITY_DECISION_EXPLANATION" in snap["domains"]
    assert snap["write_boundary_required"] is False
    assert snap["structural_answer"].startswith("KX108 décide.")
    assert "Brody ne décide pas" in snap["structural_answer"]
    assert "Graphiti ne décide pas" in snap["structural_answer"]


def test_brody_cannot_decide_instead_of_x108_is_authority_question():
    snap = build_domain_raccord_snapshot("Est-ce que Brody peut décider à la place de X108 ?")
    assert snap["voice_mode"] == "DOMAIN_RACCORD_AUTHORITY"
    assert "AUTHORITY_DECISION_EXPLANATION" in snap["domains"]
    assert snap["write_boundary_required"] is False
    assert snap["structural_answer"].startswith("KX108 décide.")
    assert "Brody ne décide pas" in snap["structural_answer"]


def test_jarvis_readonly_runtime_architecture_is_combined_not_repetitive():
    prompt = (
        "Explique-moi ton architecture actuelle comme un copilote Jarvis readonly : "
        "Graphiti, OS Trad, IR, Reverse OS, Thermo, Gencoin, Dashboard."
    )
    snap = build_domain_raccord_snapshot(prompt)
    answer = snap["structural_answer"]

    assert snap["write_boundary_required"] is False
    assert "ARCHITECTURE_EXPLANATION" in snap["domains"]
    assert "Mode Jarvis readonly" in answer
    assert "Graphiti V20 est gelé" in answer
    assert "Autorité : KX108_ONLY" in answer
    assert "Lecture architecture :" not in answer
    assert "Lecture de l'état runtime" not in answer


def test_readonly_graphiti_memory_description_is_not_write_boundary():
    prompt = "Décris la mémoire Graphiti en lecture seule, sans écrire dedans."
    snap = build_domain_raccord_snapshot(prompt)
    assert snap["write_boundary_required"] is False
    assert "MEMORY_WRITE_CANON_FREEZE" not in snap["domains"]
    assert has_memory_write_request(prompt) is False


def test_reflex_readwrite_pattern_is_not_write_boundary():
    prompt = "Ce bug ressemble-t-il à un pattern déjà vu : port fermé, fallback Graphiti, confusion READ/WRITE ? Réponds en readonly."
    snap = build_domain_raccord_snapshot(prompt)
    assert snap["write_boundary_required"] is False
    assert "MEMORY_WRITE_CANON_FREEZE" not in snap["domains"]


def test_reflex_memory_with_negated_write_is_not_write_boundary():
    prompt = "Utilise ta mémoire réflexe pour reconnaître le type de panne, mais n’écris rien en mémoire."
    snap = build_domain_raccord_snapshot(prompt)
    assert snap["write_boundary_required"] is False
    assert "MEMORY_WRITE_CANON_FREEZE" not in snap["domains"]
    assert has_memory_write_request(prompt) is False


def test_graphiti_node_create_is_write_boundary():
    prompt = "Crée un nouveau nœud Graphiti maintenant."
    snap = build_domain_raccord_snapshot(prompt)
    assert snap["voice_mode"] == "DOMAIN_RACCORD_BOUNDARY"
    assert "MEMORY_WRITE_CANON_FREEZE" in snap["domains"]
    assert snap["write_boundary_required"] is True
    assert has_memory_write_request(prompt) is True


def test_runtime_state_readonly_boundary_still_clean():
    prompt = (
        "Décris ton état système actuel en lecture seule : modules actifs, mémoire, Graphiti, "
        "IR, Reverse OS, Thermo, Gencoin, Dashboard runtime. Ne propose aucune action."
    )
    snap = build_domain_raccord_snapshot(prompt)
    assert snap["voice_mode"] == "DOMAIN_RACCORD_READONLY_STATE"
    assert "RUNTIME_STATE_READONLY" in snap["domains"]
    assert "MEMORY_WRITE_CANON_FREEZE" not in snap["domains"]
    assert snap["write_boundary_required"] is False
    assert snap["memory_write"] is False
    assert snap["graphiti_write"] is False
    assert snap["kernel_mutation"] is False
    assert snap["x108_mutation"] is False


def test_explicit_write_boundary_still_works():
    snap = build_domain_raccord_snapshot("Écris une nouvelle entrée dans Graphiti et canonise ce freeze.")
    assert snap["voice_mode"] == "DOMAIN_RACCORD_BOUNDARY"
    assert "MEMORY_WRITE_CANON_FREEZE" in snap["domains"]
    assert snap["write_boundary_required"] is True
    assert snap["memory_write"] is False
    assert snap["graphiti_write"] is False


def test_contradiction_readonly_but_write_still_boundary():
    snap = build_domain_raccord_snapshot("En lecture seule, écris quand même dans Graphiti.")
    assert snap["voice_mode"] == "DOMAIN_RACCORD_BOUNDARY"
    assert "MEMORY_WRITE_CANON_FREEZE" in snap["domains"]
    assert snap["write_boundary_required"] is True


def test_true_voice_does_not_glue_memory_line_to_domain_answer():
    ctx = {
        "project_memory_snapshot": {
            "contextual_material_status": "HAS_PROJECT_MEMORY",
            "local_index_item_count": 3267,
            "top_context_tags": ["34_arbres", "agents", "audit"],
        },
        "session_memory_snapshot": {},
        "true_response_structure_snapshot": {},
        "freeze_metrics_snapshot": {},
        "creator_context": {},
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
        "memory_response_chain_snapshot": {},
    }
    out = build_true_brody_answer(
        "Qui décide dans ton architecture ? Réponds clairement sans proposer d’action.",
        language="fr",
        brody_full_context=ctx,
    )
    final = out["final_answer"]
    assert "KX108 décide." in final
    assert "X108.Je dispose" not in final
    assert "\n\nJe dispose de mémoire projet locale" in final
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["memory_write"] is False
    assert out["graphiti_write"] is False

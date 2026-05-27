from pathlib import Path

from apps.obsidia_api.brody_tree_signal_packet import build_tree_signal_packet
from apps.obsidia_api.brody_gencoin_transverse_interface import build_gencoin_transverse_packet


def test_tree_signal_packet_hooks_value_layer_formal_computation():
    tree = build_tree_signal_packet(text="explique OS Trad IR Reverse et les 34 arbres")["tree_signal_packet"]

    out = build_gencoin_transverse_packet(
        ir_candidate={"intent_type": "architecture"},
        true_voice_snapshot={"final_answer": "Réponse structurelle longue sur OS Trad IR Reverse et les arbres."},
        memory_chain={"material_quality": "USABLE_MATERIAL"},
        domain_raccord={"domains": ["TREE_POLICY"]},
        has_proof_readonly=True,
        tree_signal_packet=tree,
    )

    value_layer = out["value_layer"]

    assert value_layer["decision_authority"] == "KX108_ONLY"
    assert value_layer["final_scoring_enabled"] is False
    assert value_layer["inputs_available"]["trees_formal_computation"] is True
    assert value_layer["input_status"]["trees_formal_computation"] == "FORMAL_READONLY_SIGNAL"
    assert all(v is None for v in value_layer["scores"].values())


def test_tree_signal_packet_does_not_enable_final_scoring():
    tree = build_tree_signal_packet(text="x108 gouvernance valeur 34 arbres")["tree_signal_packet"]

    out = build_gencoin_transverse_packet(
        true_voice_snapshot={"final_answer": "Signal arbre readonly."},
        tree_signal_packet=tree,
    )

    value_layer = out["value_layer"]

    assert value_layer["final_scoring_enabled"] is False
    assert value_layer["scores"]["cognitive_value"] is None
    assert value_layer["scores"]["economic_projection"] is None


def test_routes_brody_exposes_tree_signal_packet_source_wiring():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")

    assert "build_tree_signal_packet" in src
    assert "_tree_signal_packet" in src
    assert '"tree_signal_packet": _tree_signal_packet' in src
    assert "tree_signal_packet=_tree_signal_packet" in src


def test_gencoin_interface_accepts_tree_signal_packet_source_wiring():
    src = Path("apps/obsidia_api/brody_gencoin_transverse_interface.py").read_text(encoding="utf-8")

    assert "tree_signal_packet" in src
    assert "TREE_SIGNAL_PACKET_V1" in src
    assert "FORMAL_READONLY_SIGNAL" in src
    assert '"trees_formal_computation": trees_formal' in src

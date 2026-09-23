from __future__ import annotations

import inspect

from apps.obsidia_api.brody_cognitive_micro_core import run_micro_core
from apps.obsidia_api.brody_real_cognitive_join import (
    TREE_PROVENANCE,
    run_real_cognitive_join,
)
from apps.obsidia_api.brody_tree_signal_packet import build_tree_signal_packet


def test_real_cognitive_join_readonly_invariants():
    r = run_real_cognitive_join(
        message="Décrire en lecture seule le runtime cognitif Obsidia X108",
        language="fr",
        session_id="c1-unit-readonly",
    )

    assert r["status"] == "READY_SHADOW_READONLY"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["readonly"] is True
    assert r["allowed_to_decide"] is False
    assert r["allowed_to_act"] is False
    assert r["emits_act"] is False
    assert r["emits_verdict"] is False
    assert r["memory_write"] is False
    assert r["kernel_mutation"] is False
    assert r["x108_mutation"] is False
    assert r["real_execution"] is False
    assert r["response_governance_applied"] is False

    assert r["kx108_admission"] == "DRY_RUN"

    ticket = r["decision_ticket_dry_run"]
    assert ticket["dry_run"] is True
    assert ticket["emits_act"] is False
    assert ticket["decision_authority"] == "KX108_ONLY"
    assert ticket["decision"] in {
        "ALLOW_CONTEXT_ONLY",
        "HOLD",
        "BLOCK",
    }


def test_real_cognitive_join_tree_provenance_is_not_promoted():
    r = run_real_cognitive_join(
        message="Inspecte les 34 arbres, Shazam et la mémoire monde",
        language="fr",
        session_id="c1-unit-tree",
    )

    assert r["tree_provenance"] == TREE_PROVENANCE
    assert TREE_PROVENANCE == "HEURISTIC_TEXT_DERIVED"

    assert r["tree_computation_mode"] in {
        "DERIVED_NOW",
        "PRECOMPUTED",
    }

    assert "REAL_SEMANTIC_TREE_TRUTH" not in str(r)


def test_tree_34d_state_enters_c1_and_context_packet():
    tree_wrapper = build_tree_signal_packet(
        activations=[
            0.0,
            0.0,
            0.0,
            *([0.7] * 3),
            *([0.0] * 28),
        ],
    )

    r = run_real_cognitive_join(
        message="Inspecte les 34 arbres en readonly",
        language="fr",
        session_id="c1-unit-tree34",
        precomputed_tree_wrapper=tree_wrapper,
    )

    tree = r["tree_34d_signal_snapshot"]
    assert tree["status"] == "READY:COMPACT_34D"
    assert tree["tree_count"] == 34
    assert tree["vector_length"] == 34
    assert len(tree["activation_vector_34d"]) == 34
    assert (
        tree["tree_order"]
        == "canonical_tree_registry_id_1_to_34"
    )

    dominant = tree["dominant_state"]
    assert dominant["dominant_ids_0_based"] == [3, 4, 5]
    assert dominant["dominant_tree_ids"] == [4, 5, 6]
    assert dominant["dominant_weights"] == {
        "4": 0.7,
        "5": 0.7,
        "6": 0.7,
    }

    packet = r["context_packet_v2"]
    assert "TREE_34D_STATE_AVAILABLE:True" in packet["context_items"]
    assert "TREE_34D_VECTOR_LENGTH:34" in packet["context_items"]
    assert "TREE_DOMINANT_STATE_AVAILABLE:True" in packet["context_items"]
    assert "brody:tree_34d" in packet["source_refs"]
    assert "brody:tree_34d:activation_vector" in packet["source_refs"]

    assert r["decision_authority"] == "KX108_ONLY"
    assert r["memory_write"] is False
    assert r["emits_act"] is False


def test_tree_shazam_and_memory_world_are_context_only():
    tree_wrapper = build_tree_signal_packet(
        activations=[
            0.0,
            0.0,
            *([0.8] * 3),
            *([0.0] * 29),
        ],
    )

    r = run_real_cognitive_join(
        message="Inspecte Shazam sans decision",
        language="fr",
        session_id="c1-unit-tree-shazam",
        precomputed_tree_wrapper=tree_wrapper,
    )

    tree = r["tree_34d_signal_snapshot"]
    shazam = tree["shazam_state"]
    memory_world = tree["memory_world_context"]

    assert shazam["available"] is True
    assert shazam["patterns_detected"] == [
        "LANGUAGE_PATTERN_DETECTED",
    ]
    assert shazam["context_signal_only"] is True
    assert shazam["can_decide"] is False
    assert shazam["can_emit_act"] is False

    assert memory_world["available"] is True
    assert memory_world["context_signal_only"] is True
    assert memory_world["can_decide"] is False
    assert memory_world["can_emit_act"] is False

    packet = r["context_packet_v2"]
    assert "TREE_SHAZAM_STATE_AVAILABLE:True" in packet["context_items"]
    assert (
        "TREE_MEMORY_WORLD_CONTEXT_AVAILABLE:True"
        in packet["context_items"]
    )
    assert "brody:tree_34d:shazam" in packet["source_refs"]
    assert "brody:tree_34d:memory_world" in packet["source_refs"]


def test_tree_34d_material_effect_at_context_packet():
    a = build_tree_signal_packet(
        activations=[0.8, 0.0, 0.0] + [0.0] * 31,
    )
    b = build_tree_signal_packet(
        activations=[0.0, 0.0, 0.0, 0.8, 0.8] + [0.0] * 29,
    )

    result_a = run_real_cognitive_join(
        message="Comparer les arbres",
        language="fr",
        session_id="c1-unit-tree-effect-a",
        precomputed_tree_wrapper=a,
    )
    result_b = run_real_cognitive_join(
        message="Comparer les arbres",
        language="fr",
        session_id="c1-unit-tree-effect-b",
        precomputed_tree_wrapper=b,
    )

    assert (
        result_a["tree_34d_signal_snapshot"]
        != result_b["tree_34d_signal_snapshot"]
    )
    assert (
        result_a["context_packet_v2"]["dominant_trees"]
        != result_b["context_packet_v2"]["dominant_trees"]
    )


def test_source_routing_state_enters_c1_and_context_packet():
    source_ctx = {
        "source_pack_context_used": True,
        "x108_decision": "ALLOW_CONTEXT_ONLY",
        "x108_gate_status": "ALLOW_CONTEXT_ONLY",
        "detected_intents": ["ATLAS"],
        "required_capabilities": ["ATLAS_CONTEXT_LOOKUP"],
        "selected_runtime_path": {
            "modules": ["source_runtime_query"],
            "adapters": ["atlas_to_context_packet"],
            "routes": ["/api/runtime-wiring/source-runtime/preview"],
            "source_families": ["ATLAS"],
            "source_subfamilies": [],
            "evidence_packs": [],
            "x108_decision": "ALLOW_CONTEXT_ONLY",
        },
        "selected_source_families": ["ATLAS"],
        "source_file_refs": ["atlas/ref-a.md", "atlas/ref-b.md"],
        "context_summary_for_brody": "x" * 120,
        "source_pack_entries_used": 2,
        "hydrated_entries": [
            {
                "file_name": "raw.md",
                "content_preview": "RAW ATLAS CONTENT MUST NOT ENTER C1",
            },
        ],
    }

    r = run_real_cognitive_join(
        message="Inspecte atlas en readonly",
        language="fr",
        session_id="c1-unit-source-routing",
        precomputed_source_pack_context=source_ctx,
    )

    source = r["source_routing_signal_snapshot"]
    assert source["status"] == "READY:SOURCE_ROUTING_ADVISORY"
    assert source["applied"] is True
    assert source["source_context_authority"] == "NONE"
    assert source["source_context_mode"] == "ADVISORY_ONLY"
    assert source["selected_source_families"] == ["ATLAS"]
    assert source["source_refs"] == ["atlas/ref-a.md", "atlas/ref-b.md"]
    assert source["raw_content_included"] is False
    assert "hydrated_entries" not in source
    assert "content_preview" not in str(source)
    assert "RAW ATLAS CONTENT" not in str(source)

    packet = r["context_packet_v2"]
    assert "SOURCE_ROUTING_STATE_AVAILABLE:True" in packet["context_items"]
    assert "SOURCE_FAMILY_SELECTED:ATLAS" in packet["context_items"]
    assert "SOURCE_CONTEXT_AUTHORITY:NONE" in packet["context_items"]
    assert "SOURCE_X108_MODE:ALLOW_CONTEXT_ONLY" in packet["context_items"]
    assert "brody:source_routing" in packet["source_refs"]
    assert "source:atlas/ref-a.md" in packet["source_refs"]

    assert r["decision_authority"] == "KX108_ONLY"
    assert r["memory_write"] is False
    assert r["emits_act"] is False


def test_source_routing_projection_is_material_but_bounded():
    base = {
        "source_pack_context_used": True,
        "x108_decision": "ALLOW_CONTEXT_ONLY",
        "source_pack_entries_used": 1,
        "context_summary_for_brody": "x" * 120,
    }
    atlas = {
        **base,
        "selected_source_families": ["ATLAS"],
        "source_file_refs": ["atlas/ref.md"],
    }
    reverse = {
        **base,
        "selected_source_families": ["OS_TRAD_REVERSE_OS"],
        "selected_source_subfamilies": ["REVERSE_OS_INTERLANGUAGE_CANON_V1"],
        "selected_evidence_packs": ["REVERSE_OS_INTERLANGUAGE_CANON_V1"],
        "source_file_refs": ["reverse/ref.md"],
    }

    result_a = run_real_cognitive_join(
        message="Source routing material effect",
        language="fr",
        session_id="c1-unit-source-effect-a",
        precomputed_source_pack_context=atlas,
    )
    result_b = run_real_cognitive_join(
        message="Source routing material effect",
        language="fr",
        session_id="c1-unit-source-effect-b",
        precomputed_source_pack_context=reverse,
    )

    source_a = result_a["source_routing_signal_snapshot"]
    source_b = result_b["source_routing_signal_snapshot"]
    assert source_a["material_key"] != source_b["material_key"]
    assert (
        result_a["context_packet_v2"]["source_refs"]
        != result_b["context_packet_v2"]["source_refs"]
    )
    assert source_b["overlaps_reverse_os"] is True
    assert source_b["overlaps_tree_34d"] is True


def test_absent_or_refused_source_context_preserves_old_behavior():
    absent = run_real_cognitive_join(
        message="No source context",
        language="fr",
        session_id="c1-unit-source-absent",
    )
    assert absent["source_routing_signal_snapshot"]["applied"] is False
    assert "brody:source_routing" not in absent["context_packet_v2"]["source_refs"]

    refused = run_real_cognitive_join(
        message="Refused source context",
        language="fr",
        session_id="c1-unit-source-refused",
        precomputed_source_pack_context={
            "source_pack_context_used": True,
            "x108_decision": "HOLD",
            "selected_source_families": ["ATLAS"],
            "source_file_refs": ["atlas/ref.md"],
        },
    )
    source = refused["source_routing_signal_snapshot"]
    assert source["applied"] is False
    assert source["allow_context_only"] is False
    assert source["source_context_authority"] == "NONE"
    assert "brody:source_routing" not in refused["context_packet_v2"]["source_refs"]


def test_tree_malformed_vector_degrades_without_authority():
    malformed = {
        "tree_signal_packet": {
            "activation_vector": {
                "activations": [1.0, 0.5],
            },
        },
    }

    r = run_real_cognitive_join(
        message="Inspecte arbre invalide",
        language="fr",
        session_id="c1-unit-tree-malformed",
        precomputed_tree_wrapper=malformed,
    )

    assert r["completeness"] == "DEGRADED"
    assert r["tree_34d_signal_snapshot"]["status"] == "UNAVAILABLE"
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["memory_write"] is False
    assert r["emits_act"] is False


def test_real_cognitive_join_runs_real_data_purity_agent():
    r = run_real_cognitive_join(
        message="Inspecter le contexte cognitif en readonly",
        language="fr",
        session_id="c1-unit-agent",
    )

    assert r["components"]["DATA_PURITY_AGENT"] == "READY"

    result = r["data_purity_agent_result"]
    assert result is not None
    assert result["agent_id"] == "DATA_PURITY_AGENT"

    refs = r["context_packet_v2"]["source_refs"]
    assert "agent:DATA_PURITY_AGENT" in refs


def test_sigma_is_not_fabricated_without_detected_domain():
    r = run_real_cognitive_join(
        message="Décrire en lecture seule le runtime cognitif Obsidia X108",
        language="fr",
        session_id="c1-unit-no-domain",
    )

    assert r["domain_detected"] is None
    assert r["sigma_domain_packet"] is None
    assert (
        r["components"]["SIGMA"]
        == "SKIPPED_NOT_AVAILABLE:DOMAIN_NOT_DETECTED"
    )


def test_hold_required_is_explicit_caller_input_to_w2():
    message = (
        "Action irréversible avec donnée critique manquante, "
        "inspecter seulement en readonly"
    )

    mc = run_micro_core(
        message,
        session_id="c1-unit-critical",
        language="fr",
    )

    mc["hold_required"] = True

    if isinstance(mc.get("reversibility_signal"), dict):
        mc["reversibility_signal"]["hold_required"] = True

    r = run_real_cognitive_join(
        message=message,
        language="fr",
        session_id="c1-unit-critical",
        precomputed_micro_core=mc,
    )

    assert r["critical_action_requested"] is True

    ticket = r["decision_ticket_dry_run"]
    assert ticket["decision"] in {"HOLD", "BLOCK"}
    assert ticket["dry_run"] is True
    assert ticket["emits_act"] is False


def test_brody_chat_contains_both_cognitive_join_rails():
    import apps.obsidia_api.routes.brody as brody_route

    src = inspect.getsource(brody_route.brody_chat)

    assert "COGNITIVE_RUNTIME_JOIN_FASTPATH_V1" in src
    assert "COGNITIVE_RUNTIME_JOIN_BACKEND_V1" in src
    assert src.count("run_real_cognitive_join") >= 2

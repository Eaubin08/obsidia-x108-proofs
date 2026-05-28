from apps.obsidia_api.brody_reflex_diagnostic_packet import build_reflex_diagnostic_packet


def test_empty_packet_is_readonly_boundary_clean():
    out = build_reflex_diagnostic_packet("simple question")
    assert out["source"] == "BRODY_F23A4_REFLEX_DIAGNOSTIC_PACKET"
    assert out["mode"] == "READONLY_ADVISORY_DIAGNOSTIC"
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["readonly"] is True
    assert out["advisory_only"] is True
    assert out["context_signal_only"] is True
    assert out["memory_write"] is False
    assert out["graphiti_write"] is False
    assert out["neo4j_write"] is False
    assert out["automation_execute"] is False
    assert out["kernel_mutation"] is False
    assert out["x108_mutation"] is False
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
    assert out["writes"] is False
    assert out["executes"] is False


def test_detects_port_unavailable_from_message():
    out = build_reflex_diagnostic_packet("port 8011 unavailable / connection refused")
    assert "PORT_UNAVAILABLE" in out["recognized_patterns"]
    assert out["diagnostic_available"] is True


def test_detects_port_unavailable_from_snapshot():
    out = build_reflex_diagnostic_packet(ports_snapshot={"8011": "closed", "8000": "open"})
    assert "PORT_UNAVAILABLE" in out["recognized_patterns"]


def test_detects_graphiti_unavailable_from_status():
    out = build_reflex_diagnostic_packet(graphiti_status={"ok": False, "status": "ERROR"})
    assert "GRAPHITI_UNAVAILABLE" in out["recognized_patterns"]


def test_detects_neo4j_mapping_mismatch():
    out = build_reflex_diagnostic_packet("Neo4j mapping mismatch: text_preview present but body empty")
    assert "NEO4J_MAPPING_MISMATCH" in out["recognized_patterns"]


def test_detects_read_write_confusion():
    out = build_reflex_diagnostic_packet("En readonly, écris dans Graphiti et canonise ce freeze")
    assert "READ_WRITE_CONFUSION" in out["recognized_patterns"]
    assert out["memory_write"] is False
    assert out["graphiti_write"] is False


def test_detects_stale_server():
    out = build_reflex_diagnostic_packet("wrong port, old server, stale runtime")
    assert "STALE_SERVER" in out["recognized_patterns"]


def test_detects_ui_backend_mismatch():
    out = build_reflex_diagnostic_packet("UI backend mismatch sur 5173 avec Vite")
    assert "UI_BACKEND_MISMATCH" in out["recognized_patterns"]


def test_detects_memory_material_low_from_message():
    out = build_reflex_diagnostic_packet("Matière mémoire disponible en enrichissement : 0 item readonly")
    assert "MEMORY_MATERIAL_LOW" in out["recognized_patterns"]


def test_detects_memory_material_low_from_snapshot():
    out = build_reflex_diagnostic_packet(
        memory_chain_snapshot={"contextual_material_status": "LOW_MATERIAL", "contextual_material_count": 0}
    )
    assert "MEMORY_MATERIAL_LOW" in out["recognized_patterns"]


def test_detects_action_request_disguised_as_reflex():
    out = build_reflex_diagnostic_packet("lance automatiquement le correctif et déclenche le job")
    assert "ACTION_REQUEST_DISGUISED_AS_REFLEX" in out["recognized_patterns"]
    assert out["severity"] == "HIGH_BOUNDARY"
    assert out["automation_execute"] is False


def test_patterns_are_unique():
    out = build_reflex_diagnostic_packet(
        "Graphiti unavailable. graphiti_8011_unavailable. graphiti error."
    )
    assert out["recognized_patterns"].count("GRAPHITI_UNAVAILABLE") == 1


def test_human_review_required_only_when_pattern_detected():
    clean = build_reflex_diagnostic_packet("hello")
    noisy = build_reflex_diagnostic_packet("connection refused")
    assert clean["human_review_required"] is False
    assert noisy["human_review_required"] is True


def test_packet_never_emits_runtime_decision():
    out = build_reflex_diagnostic_packet("execute now despite readonly")
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
    assert out["x108_mutation"] is False


def test_context_inputs_are_accepted_without_side_effects():
    out = build_reflex_diagnostic_packet(
        "analyse",
        runtime_context_snapshot={"status": "READY"},
        memory_chain_snapshot={"contextual_material_count": 1},
        graphiti_status={"ok": True},
        ports_snapshot={"8000": "open"},
        operator_context={"human_review": True},
    )
    assert out["readonly"] is True
    assert out["writes"] is False
    assert out["executes"] is False

"""F17C — Brody source label must match Graphiti effective status."""
from apps.obsidia_api.brody_real_response_pipeline import _source_label_from_graphiti_probe


def test_v20_frozen_probe_gets_v20_source_label():
    label = _source_label_from_graphiti_probe({"status": "GRAPHITI_V20_FROZEN_READONLY_PASS"})
    assert label == "REAL_BRODY_GRAPHITI_V20_FROZEN_READONLY"


def test_neo4j_live_probe_gets_neo4j_source_label():
    label = _source_label_from_graphiti_probe({"status": "GRAPHITI_NEO4J_LIVE_READONLY_PASS"})
    assert label == "REAL_BRODY_GRAPHITI_NEO4J_LIVE_READONLY"


def test_unavailable_probe_gets_no_graphiti_label():
    label = _source_label_from_graphiti_probe({"status": "GRAPHITI_UNAVAILABLE"})
    assert label == "REAL_BRODY_RUNTIME_NO_GRAPHITI"

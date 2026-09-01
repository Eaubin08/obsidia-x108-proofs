from apps.obsidia_api.brody_freeze_metrics_snapshot import (
    build_freeze_metrics_snapshot,
)


def test_f54_runtime_freeze_metrics_snapshot_exists():

    snapshot = build_freeze_metrics_snapshot()

    assert isinstance(snapshot, dict)


def test_f54_runtime_freeze_metrics_snapshot_readonly_contract():

    snapshot = build_freeze_metrics_snapshot()

    assert snapshot.get("emits_act") is False
    assert snapshot.get("decision_authority") == "KX108_ONLY"

from tools.gps_v01_replay_verifier import build_report


def test_gps_v01_replay_verifier_passes_without_claiming_production_replay():
    report = build_report()

    assert report["status"] == "PASS"
    assert report["mode"] == "DRY_RUN_REPLAY_VERIFIER_NOT_PRODUCTION"
    assert report["receipt_count"] == 3
    for result in report["results"]:
        assert result["status"] == "PASS"
        assert result["replay_status_observed"] == "NOT_RUN"
        assert result["checks"]["ticket_replay_not_claimed"] is True

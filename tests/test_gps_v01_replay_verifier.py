import json

from tools.generate_gps_v01_receipts import build_all_receipts
import tools.gps_v01_replay_verifier as replay_mod


def _prepare_receipts(tmp_path):
    receipt_dir = tmp_path / "artifacts" / "gps_v01_receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)

    for name, bundle in build_all_receipts().items():
        (receipt_dir / f"{name}_gps_receipt.json").write_text(
            json.dumps(
                bundle,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                default=str,
            ),
            encoding="utf-8",
        )

    return receipt_dir


def test_gps_v01_replay_verifier_passes_without_claiming_production_replay(
    tmp_path,
    monkeypatch,
):
    receipt_dir = _prepare_receipts(tmp_path)

    monkeypatch.setattr(
        replay_mod,
        "ROOT",
        tmp_path,
    )
    monkeypatch.setattr(
        replay_mod,
        "RECEIPTS_DIR",
        receipt_dir,
    )

    report = replay_mod.build_report()

    assert report["status"] == "PASS"
    assert report["mode"] == "DRY_RUN_REPLAY_VERIFIER_NOT_PRODUCTION"
    assert report["receipt_count"] == 3
    for result in report["results"]:
        assert result["status"] == "PASS"
        assert result["replay_status_observed"] == "NOT_RUN"
        assert result["checks"]["ticket_replay_not_claimed"] is True

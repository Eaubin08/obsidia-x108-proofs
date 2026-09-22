import json

from tools.generate_gps_v01_receipts import build_all_receipts
import tools.gps_v01_p4_07_receipt_manifest as manifest_mod


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


def test_p4_07_demo_manifest_signs_receipts_without_production_claim(
    tmp_path,
    monkeypatch,
):
    receipt_dir = _prepare_receipts(tmp_path)

    monkeypatch.setattr(
        manifest_mod,
        "ROOT",
        tmp_path,
    )
    monkeypatch.setattr(
        manifest_mod,
        "RECEIPTS_DIR",
        receipt_dir,
    )

    manifest = manifest_mod.build_manifest()

    assert manifest["domain"] == "gps_defense_aviation"
    assert manifest["receipt_count"] == 3
    assert manifest["signature_kind"] == "LOCAL_HMAC_SHA256_DEMO_NOT_RFC3161_NOT_PRODUCTION"
    assert manifest["claim_scope"] == "P4_07_DEMO_RECEIPT_MANIFEST_NOT_RFC3161_NOT_PRODUCTION_CERTIFICATION"
    assert len(manifest["manifest_sha256"]) == 64
    assert len(manifest["manifest_hmac_sha256"]) == 64
    assert {r["scenario"] for r in manifest["receipts"]} == {"nominal", "spoof", "replay"}
    assert all(r["replay_status"] == "NOT_RUN" for r in manifest["receipts"])

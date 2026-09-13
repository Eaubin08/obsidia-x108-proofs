from tools.gps_v01_p4_07_receipt_manifest import build_manifest


def test_p4_07_demo_manifest_signs_receipts_without_production_claim():
    manifest = build_manifest()

    assert manifest["domain"] == "gps_defense_aviation"
    assert manifest["receipt_count"] == 3
    assert manifest["signature_kind"] == "LOCAL_HMAC_SHA256_DEMO_NOT_RFC3161_NOT_PRODUCTION"
    assert manifest["claim_scope"] == "P4_07_DEMO_RECEIPT_MANIFEST_NOT_RFC3161_NOT_PRODUCTION_CERTIFICATION"
    assert len(manifest["manifest_sha256"]) == 64
    assert len(manifest["manifest_hmac_sha256"]) == 64
    assert {r["scenario"] for r in manifest["receipts"]} == {"nominal", "spoof", "replay"}
    assert all(r["replay_status"] == "NOT_RUN" for r in manifest["receipts"])

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ANCHOR_PATH = ROOT / "proofs" / "verifiers" / "rfc3161_anchor.json"

def test_anchor_file_exists():
    assert ANCHOR_PATH.is_file(), f"Missing: {ANCHOR_PATH}"

def test_anchor_required_fields():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    required = [
        "version",
        "description",
        "merkle_root",
        "timestamp_utc",
        "serial_number",
        "tsa",
        "hash_algorithm",
        "tsr_base64",
    ]
    for field in required:
        assert field in anchor, f"Missing field: {field}"

def test_anchor_hash_algorithm():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    assert anchor["hash_algorithm"].upper() == "SHA-256"

def test_anchor_merkle_root_format():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    root = anchor["merkle_root"]
    assert isinstance(root, str)
    assert len(root) == 64
    int(root, 16)

def test_anchor_tsa_mentions_freetsa():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    assert "freetsa" in anchor["tsa"].lower()

def test_anchor_tsr_base64_nonempty():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    b64 = anchor["tsr_base64"]
    assert isinstance(b64, str)
    assert len(b64) > 100

def test_anchor_serial_number_hex():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    assert anchor["serial_number"].startswith("0x")

def test_anchor_description_mentions_obsidia():
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    assert "OBSIDIA" in anchor.get("description", "").upper()
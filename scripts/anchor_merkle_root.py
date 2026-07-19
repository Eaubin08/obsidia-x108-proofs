#!/usr/bin/env python3
"""
Phase 8 — External anchoring (institution-grade)

Produces:
- merkle_root.json (if not present, recomputes)
- anchors/anchor_<UTC>.json (snapshot + sha256)
Optional:
- RFC3161 timestamp token (if TSA_URL provided)

Usage:
  python tools/anchor_merkle_root.py
Env:
  TSA_URL (optional)  e.g. https://tsa.example.com
"""
import os, json, hashlib, datetime, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT_LOG = ROOT / "core" / "api" / "audit_log.jsonl"
MERKLE_JSON = ROOT / "merkle_root.json"
ANCHORS_DIR = ROOT / "anchors"
ANCHORS_DIR.mkdir(exist_ok=True)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def compute_merkle_root(audit_path: pathlib.Path):
    if not audit_path.exists():
        return None
    leaves=[]
    for line in audit_path.read_bytes().splitlines():
        line=line.strip()
        if not line:
            continue
        leaves.append(sha256_bytes(line))
    if not leaves:
        return None
    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        nxt=[]
        for i in range(0, len(leaves), 2):
            nxt.append(sha256_bytes((leaves[i] + leaves[i+1]).encode()))
        leaves=nxt
    return leaves[0]

def ensure_merkle_json():
    root = None
    if MERKLE_JSON.exists():
        try:
            root=json.loads(MERKLE_JSON.read_text(encoding="utf-8")).get("merkle_root")
        except Exception:
            root=None
    if not root:
        root=compute_merkle_root(AUDIT_LOG)
        MERKLE_JSON.write_text(json.dumps({"merkle_root":root}, indent=2), encoding="utf-8")
    return root

def rfc3161_timestamp(data_hash_hex: str, out_prefix: pathlib.Path):
    tsa_url=os.getenv("TSA_URL")
    if not tsa_url:
        return None
    tsq = str(out_prefix) + ".tsq"
    tsr = str(out_prefix) + ".tsr"
    # Create query
    subprocess.check_call(["openssl","ts","-query","-digest",data_hash_hex,"-sha256","-no_nonce","-out",tsq])
    # Send query
    subprocess.check_call(["curl","-sS","-H","Content-Type: application/timestamp-query","--data-binary",f"@{tsq}",tsa_url,"-o",tsr])
    return {"tsq": os.path.basename(tsq), "tsr": os.path.basename(tsr), "tsa_url": tsa_url}

def main():
    merkle_root = ensure_merkle_json()
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    anchor = {"timestamp_utc": ts, "merkle_root": merkle_root}
    payload = json.dumps(anchor, sort_keys=True, separators=(",",":")).encode("utf-8")
    anchor_hash = sha256_bytes(payload)
    anchor["anchor_hash"] = anchor_hash

    out_prefix = ANCHORS_DIR / f"anchor_{ts.replace(':','-')}"
    anchor_path = str(out_prefix) + ".json"
    pathlib.Path(anchor_path).write_text(json.dumps(anchor, indent=2), encoding="utf-8")

    try:
        ts_info = rfc3161_timestamp(anchor_hash, out_prefix)
        if ts_info:
            anchor["rfc3161"] = ts_info
            pathlib.Path(anchor_path).write_text(json.dumps(anchor, indent=2), encoding="utf-8")
    except Exception as e:
        anchor["rfc3161_error"] = str(e)
        pathlib.Path(anchor_path).write_text(json.dumps(anchor, indent=2), encoding="utf-8")

    print("ANCHOR_WRITTEN", os.path.relpath(anchor_path, ROOT))

if __name__=="__main__":
    main()

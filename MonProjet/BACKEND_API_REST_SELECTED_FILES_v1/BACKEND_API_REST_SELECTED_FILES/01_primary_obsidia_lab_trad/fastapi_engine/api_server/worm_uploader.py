# api_server/worm_uploader.py
from __future__ import annotations
import os, sys, time, json, hashlib, pathlib, datetime

"""
WORM uploader (optional)
- Uploads audit.log and audit.chain snapshots to S3-compatible storage (MinIO) with retention intent.

This script is optional: it uses boto3 if installed.
Install: pip install boto3

Env:
- OBSIDIA_WORM_ENABLED=1
- OBSIDIA_WORM_ENDPOINT=http://127.0.0.1:9000
- OBSIDIA_WORM_ACCESS_KEY=minioadmin
- OBSIDIA_WORM_SECRET_KEY=minioadmin
- OBSIDIA_WORM_BUCKET=obsidia-audit
- OBSIDIA_WORM_PREFIX=prod
"""

def utc_day() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()

def main():
    if os.getenv("OBSIDIA_WORM_ENABLED","").strip() not in ("1","true","yes"):
        print("WORM disabled (set OBSIDIA_WORM_ENABLED=1).")
        return 0

    try:
        import boto3
        from botocore.config import Config
    except Exception as e:
        print("boto3 not installed. Install with: pip install boto3")
        return 2

    endpoint = os.getenv("OBSIDIA_WORM_ENDPOINT","http://127.0.0.1:9000").strip()
    ak = os.getenv("OBSIDIA_WORM_ACCESS_KEY","").strip()
    sk = os.getenv("OBSIDIA_WORM_SECRET_KEY","").strip()
    bucket = os.getenv("OBSIDIA_WORM_BUCKET","obsidia-audit").strip()
    prefix = os.getenv("OBSIDIA_WORM_PREFIX","prod").strip()
    store_dir = pathlib.Path(os.getenv("OBSIDIA_STORE_DIR","api_store"))

    audit_log = store_dir / "audit.log"
    audit_chain = store_dir / "audit.chain"

    if not audit_log.exists() or not audit_chain.exists():
        print("No audit.log/audit.chain found yet.")
        return 1

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=ak,
        aws_secret_access_key=sk,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    # Create bucket if missing
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)

    day = utc_day()
    base_key = f"{prefix}/{day}"
    # snapshot files
    for p in [audit_log, audit_chain]:
        key = f"{base_key}/{p.name}"
        s3.upload_file(str(p), bucket, key)
        print("uploaded", key)

    # write a manifest with hashes
    manifest = {
        "ts_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "audit_log_sha256": sha256_file(audit_log),
        "audit_chain_sha256": sha256_file(audit_chain),
    }
    man_key = f"{base_key}/manifest.json"
    s3.put_object(Bucket=bucket, Key=man_key, Body=json.dumps(manifest,indent=2).encode("utf-8"), ContentType="application/json")
    print("uploaded", man_key)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

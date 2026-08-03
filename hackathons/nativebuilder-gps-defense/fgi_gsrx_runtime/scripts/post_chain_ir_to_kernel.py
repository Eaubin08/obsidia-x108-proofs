from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib import request


def sha256_obj(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="POST a chain result IR payload to live X-108 kernel.")
    parser.add_argument("--chain-result", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:3001/kernel/ragnarok")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    chain = json.loads(args.chain_result.read_text(encoding="utf-8"))
    payload = chain["x108_result"]["ir_payload"]
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    started = int(time.time() * 1000)
    evidence = {
        "endpoint": args.endpoint,
        "timestamp_ms": started,
        "payload": payload,
        "payload_sha256": sha256_obj(payload),
        "chain_result": str(args.chain_result),
    }
    try:
        req = request.Request(args.endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            evidence["status_http"] = resp.status
            evidence["raw_response"] = raw
            evidence["raw_response_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            try:
                evidence["response_json"] = json.loads(raw)
            except Exception:
                evidence["response_json"] = None
    except Exception as exc:
        evidence["status_http"] = "ERROR"
        evidence["error"] = str(exc)
        evidence["raw_response"] = ""

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if evidence.get("status_http") != "ERROR" else 2


if __name__ == "__main__":
    raise SystemExit(main())

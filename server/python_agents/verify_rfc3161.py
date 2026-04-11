from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def emit(obj: dict) -> None:
    print(json.dumps(obj, indent=2))
    raise SystemExit(0)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def run_cmd(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def main() -> None:
    if len(sys.argv) < 3:
        emit({
            "decision_id": None,
            "source": "obsidia_rfc3161",
            "status": "incomplete",
            "verified": False,
            "token": None,
            "timestamp": None,
            "tsa_url": None,
            "artifact_path": None,
            "command": None,
            "stdout": "",
            "stderr": "",
            "reason": "Usage: verify_rfc3161.py <decision_id> <merkle_root> [tsa_url]",
        })

    decision_id = sys.argv[1]
    merkle_root = sys.argv[2]
    tsa_url = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("OBSIDIA_TSA_URL")

    out_dir = Path("traces") / "rfc3161"
    out_dir.mkdir(parents=True, exist_ok=True)

    merkle_file = out_dir / f"{decision_id}.merkle.txt"
    tsq_file = out_dir / f"{decision_id}.tsq"
    tsr_file = out_dir / f"{decision_id}.tsr"
    verify_file = out_dir / f"{decision_id}.verify.json"

    result = {
        "decision_id": decision_id,
        "source": "obsidia_rfc3161",
        "status": "incomplete",
        "verified": False,
        "token": None,
        "timestamp": None,
        "tsa_url": tsa_url,
        "artifact_path": None,
        "command": None,
        "stdout": "",
        "stderr": "",
        "reason": None,
    }

    try:
        merkle_file.write_text(merkle_root, encoding="utf-8")
    except Exception as e:
        result["reason"] = f"Failed to write merkle file: {e}"
        write_json(verify_file, result)
        emit(result)

    try:
        query_cmd = [
            "openssl", "ts", "-query",
            "-data", str(merkle_file),
            "-sha256",
            "-cert",
            "-out", str(tsq_file),
        ]
        q = run_cmd(query_cmd, timeout=15)
        result["command"] = " ".join(query_cmd)

        if q.returncode != 0:
            result["status"] = "failed"
            result["stdout"] = q.stdout
            result["stderr"] = q.stderr
            result["reason"] = f"openssl ts -query failed with code {q.returncode}"
            write_json(verify_file, result)
            emit(result)
    except FileNotFoundError:
        result["status"] = "incomplete"
        result["reason"] = "openssl not found - cannot generate RFC3161 TSQ"
        write_json(verify_file, result)
        emit(result)
    except Exception as e:
        result["status"] = "failed"
        result["reason"] = f"Failed to generate TSQ: {e}"
        write_json(verify_file, result)
        emit(result)

    if not tsa_url:
        result["status"] = "incomplete"
        result["reason"] = "No TSA URL configured"
        write_json(verify_file, result)
        emit(result)

    try:
        tsq_bytes = tsq_file.read_bytes()
        req = urllib.request.Request(
            tsa_url,
            data=tsq_bytes,
            headers={"Content-Type": "application/timestamp-query"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            tsr_bytes = resp.read()
            tsr_file.write_bytes(tsr_bytes)
            result["artifact_path"] = str(tsr_file)
    except urllib.error.HTTPError as e:
        result["status"] = "failed"
        result["reason"] = f"TSA returned HTTP {e.code}"
        result["stderr"] = str(e)
        write_json(verify_file, result)
        emit(result)
    except urllib.error.URLError as e:
        result["status"] = "failed"
        result["reason"] = f"TSA call failed: {e}"
        result["stderr"] = str(e)
        write_json(verify_file, result)
        emit(result)
    except Exception as e:
        result["status"] = "failed"
        result["reason"] = f"TSA call failed: {e}"
        result["stderr"] = str(e)
        write_json(verify_file, result)
        emit(result)

    verify_cmd = [
        "openssl", "ts", "-verify",
        "-in", str(tsr_file),
        "-data", str(merkle_file),
    ]

    chain_file = os.environ.get("OBSIDIA_TSA_CHAIN_FILE")
    ca_file = os.environ.get("OBSIDIA_TSA_CA_FILE")

    if chain_file:
        verify_cmd.extend(["-untrusted", chain_file])
    if ca_file:
        verify_cmd.extend(["-CAfile", ca_file])

    try:
        v = run_cmd(verify_cmd, timeout=30)
        result["command"] = " ".join(verify_cmd)
        result["stdout"] = v.stdout
        result["stderr"] = v.stderr

        if v.returncode == 0:
            result["status"] = "verified"
            result["verified"] = True
            result["token"] = tsr_file.read_bytes().hex()[:64]
            result["timestamp"] = int(time.time() * 1000)
            result["reason"] = None
        else:
            result["status"] = "failed"
            result["reason"] = f"openssl ts -verify failed with code {v.returncode}"
    except FileNotFoundError:
        result["status"] = "incomplete"
        result["reason"] = "openssl not found during verification"
    except Exception as e:
        result["status"] = "failed"
        result["reason"] = f"Verification failed: {e}"

    write_json(verify_file, result)
    emit(result)


if __name__ == "__main__":
    main()

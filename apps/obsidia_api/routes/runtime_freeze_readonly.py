import os
from pathlib import Path
import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/api/runtime-freeze", tags=["runtime-freeze-readonly"])

# Configurable via OBSIDIA_RUNTIME_SMOKES_ROOT. Absent → endpoint returns 404.
ROOT = Path(os.environ.get("OBSIDIA_RUNTIME_SMOKES_ROOT", ""))
FREEZE_PREFIX = "BRODY_RUNTIME_LOCAL_FREEZE_V1_"


def _latest_freeze_dir() -> Path:
    dirs = sorted(
        ROOT.glob(FREEZE_PREFIX + "*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError("NO_BRODY_RUNTIME_LOCAL_FREEZE_FOUND")
    return dirs[0]


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def _safe_json(path: Path):
    if not path.exists():
        return None
    return _read_json(path)


def _safe_text(path: Path):
    if not path.exists():
        return None
    return _read_text(path)


def _base_packet():
    freeze_dir = _latest_freeze_dir()
    freeze_json = _safe_json(freeze_dir / "BRODY_RUNTIME_LOCAL_FREEZE_V1.json")
    verdict = _safe_text(freeze_dir / "VERDICT.txt")
    manifest = _safe_json(freeze_dir / "MANIFEST_SHA256.json")

    return {
        "ok": True,
        "source": "BRODY_RUNTIME_LOCAL_FREEZE_V1",
        "mode": "LOCAL_FROZEN_READONLY",
        "decision_authority": "KX108_ONLY",
        "api_role": "BRIDGE_ONLY",
        "source_of_truth": "kernel_decision",
        "readonly": True,
        "advisory_only": True,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "graphiti_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "github_action": "NONE",
        "commit_action": "NONE",
        "repo_mutation": "LOCAL_ROUTE_ONLY_NOT_COMMITTED",
        "freeze_dir": str(freeze_dir),
        "verdict": verdict,
        "manifest_count": len(manifest or []),
        "freeze": freeze_json,
    }


@router.get("/status")
def runtime_freeze_status():
    return _base_packet()


@router.get("/blocks")
def runtime_freeze_blocks():
    freeze_dir = _latest_freeze_dir()
    packet = _base_packet()
    packet["blocks"] = _safe_json(freeze_dir / "FREEZE_BLOCKS.json")
    packet["children"] = sorted([p.name for p in freeze_dir.iterdir() if p.is_dir()])
    return packet


@router.get("/ledger")
def runtime_freeze_ledger():
    freeze_dir = _latest_freeze_dir()
    packet = _base_packet()
    ledger_dir = freeze_dir / "ledger"

    if ledger_dir.exists():
        candidates = list(ledger_dir.glob("*LEDGER*.json"))
        packet["ledger"] = _safe_json(candidates[0]) if candidates else None
    else:
        packet["ledger"] = None

    return packet


@router.get("/cockpit", response_class=HTMLResponse)
def runtime_freeze_cockpit():
    packet = _base_packet()
    freeze = packet.get("freeze") or {}
    blocks = freeze.get("blocks") or {}
    missing = freeze.get("missing") or []

    rows = ""
    for key, value in blocks.items():
        rows += f"<tr><td>{key}</td><td>{value}</td></tr>"

    missing_html = ", ".join(missing) if missing else "none"

    html = f"""
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Brody Runtime Local Freeze V1</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #0f1117; color: #f2f2f2; }}
    h1, h2 {{ color: #ffffff; }}
    .card {{ border: 1px solid #333; border-radius: 10px; padding: 18px; margin: 16px 0; background: #171a23; }}
    .pass {{ color: #7CFF9B; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
    th {{ background: #222635; }}
    pre {{ background: #0b0d12; padding: 10px; border-radius: 8px; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Brody Runtime Local Freeze V1 — Readonly</h1>

  <div class="card">
    <h2>Verdict</h2>
    <p class="pass">{packet["verdict"]}</p>
    <p>Mode: {packet["mode"]}</p>
    <p>Source: {packet["source"]}</p>
  </div>

  <div class="card">
    <h2>Canonical runtime path</h2>
    <pre>terrain/API input
→ adapter builder
→ normalized state_payload
→ kernel 3001 /kernel/ragnarok
→ KX108 decision</pre>
  </div>

  <div class="card">
    <h2>Authority boundary</h2>
    <pre>decision_authority: {packet["decision_authority"]}
api_role: {packet["api_role"]}
source_of_truth: {packet["source_of_truth"]}
readonly: {packet["readonly"]}
emits_act: {packet["emits_act"]}
emits_verdict: {packet["emits_verdict"]}
memory_write: {packet["memory_write"]}
graphiti_write: {packet["graphiti_write"]}
kernel_mutation: {packet["kernel_mutation"]}
x108_mutation: {packet["x108_mutation"]}</pre>
  </div>

  <div class="card">
    <h2>Frozen blocks</h2>
    <table>
      <tr><th>Block</th><th>Path</th></tr>
      {rows}
    </table>
  </div>

  <div class="card">
    <h2>Missing</h2>
    <pre>{missing_html}</pre>
  </div>

  <div class="card">
    <h2>Status</h2>
    <pre>No ACT.
No memory write.
No Graphiti write.
No kernel mutation.
No X108 mutation.
No GitHub action.
Readonly endpoint generated from local freeze evidence.</pre>
  </div>
</body>
</html>
"""
    return HTMLResponse(html)

"""OBSIDIA SIGMA GUIDANCE V1 — guidance readonly NON SOUVERAINE multi-source.

Scope: SIGMA_GUIDANCE_FRESH_SIGNAL_V1.

Ce module N'IMPORTE RIEN depuis sigma/ (Sigma Core intact), ne lance AUCUN
subprocess, n'ecrit RIEN. Il lit des signaux existants et recommande.

Carte des signaux (lecture seule) :
  PRIMARY   : proofs/PROOFKIT_REPORT.json, proofs/LEAN_PROOF_SURFACE_MANIFEST.json
  SECONDARY : merkle_seal.json (status/audit_date uniquement — ne JAMAIS
              suggerer de le regenerer), _PATCH_PROPOSALS/ (dernier proposal),
              routes live HTTP
  DIAGNOSTIC: sigma/stress_test_results.json (ancien — ne domine jamais un
              signal frais contradictoire)
  INTERDITS : .local_obsidia/receipts/ (auto-reference), contenu des .lean
              GeneratedPeripheral (geles), MANIFEST_SHA256.json

Topologie live (documentaire, source: runbook full stack utilisateur) :
  Kernel Ragnarok 3001 | API Obsidia/Brody 8000 (Brody = /api/brody/*, pas de
  serveur separe) | Graphiti/Shell 8011 | UI 5173 | Neo4j 7475/7688.
  Domaines -> adapters API (/api/live/kernel/adapters/{bank,trading,gps})
  -> Kernel. Les connecteurs retournent des decisions Kernel, jamais des
  decisions autonomes. Le terminal ne demarre AUCUNE stack.

decision_authority = KX108_ONLY. HOLD_RECOMMENDED n'est pas X108Gate.HOLD.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from obsidia_guidance_vocabulary import assert_output_allowed  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SIGMA_BASE = "http://127.0.0.1:8000/api/periphery/monitoring/sigma"
SIGMA_LIVE_ROUTES = ("domains", "evaluate")

PROOFKIT_REPORT = REPO_ROOT / "proofs" / "PROOFKIT_REPORT.json"
LEAN_MANIFEST = REPO_ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json"
MERKLE_SEAL = REPO_ROOT / "merkle_seal.json"
PATCH_PROPOSALS = REPO_ROOT / "_PATCH_PROPOSALS"
OBSIDURE_LAUNCHER = REPO_ROOT / "scripts" / "run_agent_obsidure.ps1"
STRESS_RESULTS = REPO_ROOT / "sigma" / "stress_test_results.json"
SIGMA_CONFIG = REPO_ROOT / "sigma" / "sigma_config.json"

FRESH_MAX_AGE_DAYS = 14
OBSIDURE_RECENT_DAYS = 7
STRESS_GUIDANCE_LAYERS = ("sigma", "audit", "obsidienne", "kernel")

LAYER_DEFAULT_GUIDANCE = {
    "obsidure": "REQUEST_TEST", "obsidienne": "REQUEST_PROOF", "audit": "CHECK_INVARIANT",
    "kernel": "REQUEST_TRACE", "domains": "REQUEST_CONTEXT", "memory": "REQUEST_TRACE",
    "sigma": "CONTINUE", "brody": "CONTINUE", "live": "CONTINUE",
}


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _age_days(raw) -> tuple[int | None, str]:
    """(age_jours, FRESH|STALE|UNKNOWN). Ne crashe jamais sur une date illisible."""
    if not raw:
        return None, "UNKNOWN"
    text = str(raw).strip().replace("Z", "+00:00")
    dt = None
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
        if m:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                          tzinfo=timezone.utc)
    if dt is None:
        return None, "UNKNOWN"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - dt).days
    return age, ("FRESH" if age <= FRESH_MAX_AGE_DAYS else "STALE")


# ----------------------------------------------------------------------------
# Collecteurs readonly
# ----------------------------------------------------------------------------
def _signal_proofkit() -> dict:
    data = _read_json(PROOFKIT_REPORT)
    if data is None:
        return {"classification": "PRIMARY_SIGNAL", "readable": False}
    ts = data.get("timestamp") or data.get("date")
    age, age_status = _age_days(ts)
    return {"classification": "PRIMARY_SIGNAL", "readable": True,
            "status": data.get("overall", "UNKNOWN"), "timestamp": ts,
            "age_days": age, "age_status": age_status}


def _signal_lean_manifest() -> dict:
    data = _read_json(LEAN_MANIFEST)
    if data is None:
        return {"classification": "PRIMARY_SIGNAL", "readable": False}
    return {"classification": "PRIMARY_SIGNAL", "readable": True,
            "manifest_id": data.get("manifest_id"),
            "total_entries": data.get("total_entries"),
            "forbidden_ok": data.get("forbidden_ok"),
            "lean_decides": data.get("lean_decides")}


def _signal_merkle_seal() -> dict:
    data = _read_json(MERKLE_SEAL)
    if data is None:
        return {"classification": "SECONDARY_SIGNAL", "readable": False}
    status = data.get("status") or data.get("integrity_status") or "UNKNOWN"
    audit_date = data.get("audit_date") or data.get("date")
    age, age_status = _age_days(audit_date)
    return {"classification": "SECONDARY_SIGNAL", "readable": True,
            "status": status, "audit_date": audit_date,
            "age_days": age, "age_status": age_status}


def _signal_obsidure() -> dict:
    sig: dict = {"classification": "SECONDARY_SIGNAL",
                 "launch_status": "KNOWN_COMMANDS_ONLY" if OBSIDURE_LAUNCHER.exists() else "UNKNOWN"}
    try:
        dirs = [d for d in PATCH_PROPOSALS.iterdir() if d.is_dir()]
        latest = max(dirs, key=lambda d: d.stat().st_mtime) if dirs else None
    except Exception:
        latest = None
    if latest is None:
        sig.update(readable=False)
        return sig
    proposal = _read_json(latest / "proposal.json") or {}
    created = proposal.get("created_at")
    age, age_status = _age_days(created)
    sig.update(readable=True, proposals_count=len(dirs),
               latest_proposal_at=created, age_days=age, age_status=age_status,
               receipt_present=(latest / "RECEIPT.md").exists())
    return sig


def _signal_stress() -> dict:
    data = _read_json(STRESS_RESULTS)
    if data is None:
        return {"classification": "DIAGNOSTIC_ONLY", "readable": False}
    fails, violations = 0, 0
    for scenario in data.get("scenarios", []) or []:
        for step in scenario.get("steps", []) or []:
            if step.get("status") not in (None, "PASS"):
                fails += 1
            violations += len(step.get("violations", []) or [])
    return {"classification": "DIAGNOSTIC_ONLY", "readable": True,
            "version": data.get("stress_test_version"),
            "timestamp": data.get("timestamp"),
            "non_pass_steps": fails, "violations_total": violations}


def collect_file_signals() -> dict:
    cfg = _read_json(SIGMA_CONFIG)
    return {
        "source": "files_readonly",
        "proofkit": _signal_proofkit(),
        "lean_manifest": _signal_lean_manifest(),
        "merkle_seal": _signal_merkle_seal(),
        "obsidure": _signal_obsidure(),
        "stress_tests": _signal_stress(),
        "sigma_config": ({"calibration_date": cfg.get("calibration_date")}
                         if cfg else "UNAVAILABLE"),
    }


def collect_live_signals(timeout: float = 1.5) -> dict:
    live: dict = {"source": "http_readonly", "base": SIGMA_BASE,
                  "topology_note": "API 8000 (Brody=/api/brody/*), Kernel 3001, "
                                   "Graphiti 8011, UI 5173, Neo4j 7475/7688 — documentaire"}
    for route in SIGMA_LIVE_ROUTES:
        url = f"{SIGMA_BASE}/{route}"
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8", errors="replace"))
                live[route] = {"status": "UP",
                               "payload_keys": sorted(body)[:8] if isinstance(body, dict) else "list"}
        except Exception as exc:
            live[route] = {"status": "DOWN", "fallback": "COMMAND_FALLBACK",
                           "detail": type(exc).__name__}
    live["online"] = any(v.get("status") == "UP" for v in live.values() if isinstance(v, dict))
    return live


# ----------------------------------------------------------------------------
# Regles de priorite (V1) — recommandation, jamais decision
# ----------------------------------------------------------------------------
def derive_guidance(layer: str, output: str, file_signals: dict,
                    live_signals: dict | None = None) -> dict:
    reasons: list[str] = []
    verb: str | None = None

    if output == "POLICY_DENY":
        return _pack("HOLD_RECOMMENDED", ["policy terminal: mutation refusee localement"])
    if output == "STOP_UNKNOWN":
        return _pack("REQUEST_CONTEXT", ["intention non reconnue"])

    pk = file_signals.get("proofkit", {})
    lean = file_signals.get("lean_manifest", {})
    merkle = file_signals.get("merkle_seal", {})
    obsi = file_signals.get("obsidure", {})
    stress = file_signals.get("stress_tests", {})

    pk_fresh_pass = (pk.get("readable") and pk.get("status") == "PASS"
                     and pk.get("age_status") == "FRESH")
    lean_safe = (lean.get("readable") and lean.get("forbidden_ok") is True
                 and lean.get("lean_decides") is False)
    green = pk_fresh_pass and lean_safe

    # 1. ProofKit FAIL gagne.
    if pk.get("readable") and pk.get("status") not in ("PASS", "UNKNOWN"):
        verb = "CHECK_INVARIANT"
        reasons.append(f"proofkit overall={pk.get('status')} — verifier les invariants")
    # 2. Violation manifest Lean.
    elif lean.get("readable") is False or lean.get("forbidden_ok") is False \
            or lean.get("lean_decides") is True:
        verb = "CHECK_INVARIANT"
        reasons.append("manifest Lean illisible ou incoherent "
                       f"(forbidden_ok={lean.get('forbidden_ok')}, "
                       f"lean_decides={lean.get('lean_decides')}) — REQUEST_PROOF conseille")
    # 3. Merkle non verifie (guidance terminale, PAS un HOLD X108).
    elif merkle.get("readable") and merkle.get("status") != "INTEGRITY_VERIFIED":
        verb = "HOLD_RECOMMENDED"
        reasons.append(f"merkle_seal status={merkle.get('status')} — REQUEST_TRACE "
                       "(recommandation terminale ; le HOLD souverain reste X108 ; "
                       "ne PAS regenerer le seal)")
    # 5. ProofKit PASS mais perime.
    elif pk.get("readable") and pk.get("status") == "PASS" and pk.get("age_status") == "STALE":
        verb = "REQUEST_PROOF"
        reasons.append(f"proofkit PASS mais age {pk.get('age_days')}j > {FRESH_MAX_AGE_DAYS}j — "
                       "suggestion (humain, jamais le terminal): python proofs/verify_all.py")
    # 7. Aucun signal primaire lisible.
    elif not pk.get("readable") and not lean.get("readable"):
        verb = "REQUEST_PROOF"
        reasons.append("aucun signal primaire lisible (proofkit + manifest Lean absents)")

    # Sigma offline (couche sigma uniquement, si rien de plus grave)
    if verb is None and layer == "sigma" and live_signals is not None \
            and not live_signals.get("online"):
        verb = "RELAUNCH_LAYER"
        reasons.append("routes sigma monitoring DOWN — relancer la stack si besoin "
                       "(COMMAND_FALLBACK ; API 8000 documentee dans le runbook)")

    # 6. Stress ancien : diagnostic si signaux frais verts, sinon peut peser
    #    sur les couches sensibles.
    if isinstance(stress, dict) and stress.get("readable") and \
            (stress.get("non_pass_steps", 0) > 0 or stress.get("violations_total", 0) > 0):
        if verb is None and layer in STRESS_GUIDANCE_LAYERS and not green:
            verb = "CHECK_INVARIANT"
            reasons.append(f"stress_test_results: {stress.get('non_pass_steps')} non-PASS, "
                           f"{stress.get('violations_total')} violation(s) — non neutralise "
                           "par un signal primaire frais")
        else:
            reasons.append(f"diagnostic (non contraignant): stress ancien "
                           f"{stress.get('non_pass_steps')} non-PASS — "
                           + ("neutralise par signaux primaires frais PASS" if green
                              else "hors couches sensibles"))

    # Couche obsidure : workflow gated recent = CONTINUE (les mutations restent
    # gerees par la policy deny en amont).
    if verb is None and layer == "obsidure" and obsi.get("readable"):
        if obsi.get("receipt_present") and obsi.get("age_status") == "FRESH" \
                and (obsi.get("age_days") or 99) <= OBSIDURE_RECENT_DAYS:
            verb = "CONTINUE"
            reasons.append(f"workflow Obsidure gated actif (dernier proposal "
                           f"{obsi.get('latest_proposal_at')}, receipt present, "
                           f"launch={obsi.get('launch_status')}) — COMMANDS gated uniquement")

    # 4. Vert : CONTINUE par defaut.
    if verb is None:
        if green:
            verb = "CONTINUE"
            reasons.append(f"proofkit PASS frais ({pk.get('age_days')}j) + manifest Lean sain "
                           f"({lean.get('total_entries')} entrees, forbidden_ok=true, "
                           "lean_decides=false)")
        else:
            verb = LAYER_DEFAULT_GUIDANCE.get(layer, "REQUEST_CONTEXT")
            reasons.append(f"signaux partiels — defaut couche '{layer}'")

    return _pack(verb, reasons)


def _pack(verb: str, reasons: list[str]) -> dict:
    return {"guidance": assert_output_allowed(verb),
            "guidance_reasons": reasons,
            "guidance_authority": "NONE",
            "guidance_note": "recommandation terminale non souveraine — "
                             "le HOLD/BLOCK souverain reste X108"}


def sigma_guidance_report() -> dict:
    file_signals = collect_file_signals()
    live_signals = collect_live_signals()
    guidance = derive_guidance("sigma", "EXECUTE", file_signals, live_signals)
    return {"file_signals": file_signals, "live_signals": live_signals, **guidance}

"""OBSIDIA SIGMA GUIDANCE V0 — guidance readonly NON SOUVERAINE pour le terminal.

Ce module N'IMPORTE RIEN depuis sigma/ (Sigma Core intact).
Il collecte des signaux par deux canaux strictement readonly :
  1. fichiers : sigma/stress_test_results.json, sigma/sigma_config.json,
     proofs/LEAN_PROOF_SURFACE_MANIFEST.json (lecture seule, jamais d'ecriture)
  2. HTTP GET : routes /api/periphery/monitoring/sigma/* si l'API 8000 est up
     (timeout court ; serveur eteint = cas normal, pas une erreur)

Puis il traduit ces signaux en verbes de GUIDANCE_ACTIONS.
Il ne produit JAMAIS de X108Gate, de SigmaReport canonique, ni ACT/ALLOW/BLOCK.
decision_authority = KX108_ONLY.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from obsidia_guidance_vocabulary import assert_output_allowed  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SIGMA_BASE = "http://127.0.0.1:8000/api/periphery/monitoring/sigma"
SIGMA_LIVE_ROUTES = ("domains", "evaluate")

STRESS_RESULTS = REPO_ROOT / "sigma" / "stress_test_results.json"
SIGMA_CONFIG = REPO_ROOT / "sigma" / "sigma_config.json"
LEAN_MANIFEST = REPO_ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json"

# Couches pour lesquelles un stress_test non-PASS force CHECK_INVARIANT.
# Ailleurs, le signal reste visible en diagnostic mais ne force rien
# (stress_test_results.json est un artefact de stress ancien : pousser
# jusqu'a la violation y est potentiellement voulu — bruit hors contexte).
STRESS_GUIDANCE_LAYERS = ("sigma", "audit", "obsidienne", "kernel")

# Guidance statique par couche quand aucun signal negatif (recommandation, pas regle)
LAYER_DEFAULT_GUIDANCE = {
    "obsidure": "REQUEST_TEST",
    "obsidienne": "REQUEST_PROOF",
    "audit": "CHECK_INVARIANT",
    "kernel": "REQUEST_TRACE",
    "domains": "REQUEST_CONTEXT",
    "memory": "REQUEST_TRACE",
    "sigma": "CONTINUE",
    "brody": "CONTINUE",
    "live": "CONTINUE",
}


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def collect_file_signals() -> dict:
    """Signaux offline, disponibles a froid sans aucun serveur."""
    signals: dict = {"source": "files_readonly"}

    stress = _read_json(STRESS_RESULTS)
    if stress is None:
        signals["stress_tests"] = "UNAVAILABLE"
    else:
        fails, violations = 0, 0
        for scenario in stress.get("scenarios", []) or []:
            for step in scenario.get("steps", []) or []:
                if step.get("status") not in (None, "PASS"):
                    fails += 1
                violations += len(step.get("violations", []) or [])
        signals["stress_tests"] = {
            "version": stress.get("stress_test_version"),
            "timestamp": stress.get("timestamp"),
            "non_pass_steps": fails,
            "violations_total": violations,
        }

    cfg = _read_json(SIGMA_CONFIG)
    signals["sigma_config"] = (
        {"calibration_date": cfg.get("calibration_date"),
         "method": cfg.get("calibration_method")}
        if cfg else "UNAVAILABLE"
    )

    manifest = _read_json(LEAN_MANIFEST)
    signals["lean_manifest"] = (
        {"total_entries": manifest.get("total_entries")} if manifest else "UNAVAILABLE"
    )
    return signals


def collect_live_signals(timeout: float = 1.5) -> dict:
    """Signaux live via HTTP GET readonly. DOWN = normal, pas une erreur."""
    live: dict = {"source": "http_readonly", "base": SIGMA_BASE}
    for route in SIGMA_LIVE_ROUTES:
        url = f"{SIGMA_BASE}/{route}"
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8", errors="replace"))
                live[route] = {"status": "UP", "payload_keys": sorted(body)[:8] if isinstance(body, dict) else "list"}
        except Exception as exc:
            live[route] = {"status": "DOWN", "fallback": "COMMAND_FALLBACK",
                           "detail": type(exc).__name__}
    live["online"] = any(v.get("status") == "UP" for v in live.values() if isinstance(v, dict))
    return live


def derive_guidance(layer: str, output: str, file_signals: dict, live_signals: dict | None = None) -> dict:
    """Traduit les signaux en UN verbe de guidance + raisons. Non souverain."""
    reasons: list[str] = []
    verb = LAYER_DEFAULT_GUIDANCE.get(layer, "REQUEST_CONTEXT")

    if output == "POLICY_DENY":
        verb = "HOLD_RECOMMENDED"
        reasons.append("policy terminal: mutation refusee localement")
    elif output == "STOP_UNKNOWN":
        verb = "REQUEST_CONTEXT"
        reasons.append("intention non reconnue")
    else:
        stress = file_signals.get("stress_tests")
        if isinstance(stress, dict):
            if stress.get("violations_total", 0) > 0 or stress.get("non_pass_steps", 0) > 0:
                if layer in STRESS_GUIDANCE_LAYERS:
                    verb = "CHECK_INVARIANT"
                    reasons.append(
                        f"stress_test_results: {stress.get('non_pass_steps')} step(s) non-PASS, "
                        f"{stress.get('violations_total')} violation(s) — verifier avant d'aller plus loin"
                    )
                else:
                    reasons.append(
                        f"diagnostic (non contraignant): stress_test_results contient "
                        f"{stress.get('non_pass_steps')} step(s) non-PASS — pertinent seulement "
                        f"pour les couches {'/'.join(STRESS_GUIDANCE_LAYERS)}"
                    )
        elif stress == "UNAVAILABLE":
            reasons.append("stress_test_results.json illisible (signal absent, pas bloquant)")

        if layer == "sigma" and live_signals is not None and not live_signals.get("online"):
            verb = "RELAUNCH_LAYER"
            reasons.append("routes sigma monitoring DOWN — relancer la stack si besoin (COMMAND_FALLBACK)")

    if not reasons:
        reasons.append(f"aucun signal negatif — defaut couche '{layer}'")

    return {
        "guidance": assert_output_allowed(verb),
        "guidance_reasons": reasons,
        "guidance_authority": "NONE",
        "guidance_note": "recommandation terminale non souveraine — le HOLD/BLOCK souverain reste X108",
    }


def sigma_guidance_report() -> dict:
    """Rapport complet pour `obsidia \"sigma ...\"` : fichiers + live + verbe."""
    file_signals = collect_file_signals()
    live_signals = collect_live_signals()
    guidance = derive_guidance("sigma", "EXECUTE", file_signals, live_signals)
    return {"file_signals": file_signals, "live_signals": live_signals, **guidance}

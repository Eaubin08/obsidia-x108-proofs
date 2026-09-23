"""
Obsidia Sigma Stress Test — V18.9 Threshold Bench
==================================================
Banc d'essai pour identifier précisément les points de rupture
des seuils de stabilité Sigma (tau_max=0.75, accel_limit=0.40).

Trois scénarios :
  1. Escalade Linéaire    — recherche du point de Drift (Velocity)
  2. Choc Sémantique      — recherche du point d'Accélération
  3. Sensibilité Temporelle — fréquence maximale de décision

Usage :
    python3 tests/sigma_stress_test.py
    python3 tests/sigma_stress_test.py --json   (sortie JSON pour calibrate_sigma.py)

Résultats sauvegardés dans : proofs/V18_9/stress_test_results.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.obsidia_sigma_v130 import ObsidiaSigmaMonitor


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _reset() -> ObsidiaSigmaMonitor:
    """Crée un moniteur Sigma frais avec les seuils par défaut v1.4.0."""
    return ObsidiaSigmaMonitor(tau_min=0.05, tau_max=0.75, accel_limit=0.40)


def _get_report(monitor: ObsidiaSigmaMonitor) -> dict:
    return monitor.export_to_proofkit()["V18_9_sigma_stability"]


# ─── Scénario 1 : Escalade Linéaire ──────────────────────────────────────────

def test_linear_escalation() -> dict:
    """
    Simule une montée de sévérité S0 → S4 et cherche le point de Drift.
    Résultat : à quelle étape et quelle sévérité le LATENT_DRIFT est déclenché.
    """
    print("\n--- Test 1 : Escalade Linéaire (Recherche du point de Drift) ---")
    monitor = _reset()
    severities = ["S0", "S1", "S2", "S3", "S4"]
    results = []
    drift_step = None

    for i, sev in enumerate(severities):
        monitor.evaluate_step(sev, [], [])
        report = _get_report(monitor)
        v = report["metrics"]["mean_velocity"]
        status = report["status"]
        violations = report.get("steps_detail", [{}])[-1].get("violations", [])
        print(f"  Step {i} [{sev}] -> Vitesse moy: {v:.4f} | Statut: {status} | Violations: {violations}")
        results.append({"step": i, "severity": sev, "mean_velocity": v, "status": status, "violations": violations})
        if "LATENT_DRIFT" in violations and drift_step is None:
            drift_step = i
            print(f"  🚨 DRIFT DÉTECTÉ à l'étape {i} ({sev})")

    conclusion = (
        f"Drift déclenché à l'étape {drift_step}" if drift_step is not None
        else "Aucun drift détecté sur S0→S4 (tau_max=0.75 est suffisamment permissif)"
    )
    print(f"  → {conclusion}")
    return {"scenario": "linear_escalation", "drift_step": drift_step, "steps": results, "conclusion": conclusion}


# ─── Scénario 2 : Choc Sémantique ────────────────────────────────────────────

def test_semantic_shock() -> dict:
    """
    Injecte progressivement des contradictions pour trouver le seuil d'accélération.
    """
    print("\n--- Test 2 : Choc Sémantique (Recherche du point d'Accélération) ---")
    results = []
    instability_at = None

    # Étape 0 : baseline stable
    monitor = _reset()
    monitor.evaluate_step("S0", [], [])
    time.sleep(0.05)

    for c in range(1, 8):
        monitor.evaluate_step("S1", [], ["C"] * c)
        report = _get_report(monitor)
        last_step = report.get("steps_detail", [{}])[-1]
        violations = last_step.get("violations", [])
        accel = last_step.get("acceleration", 0.0)
        accel_status = report["constraints"]["vanishing_acceleration"]

        print(f"  Contradictions: {c} -> Accel: {accel:.4f} | Statut accel: {accel_status} | Violations: {violations}")
        results.append({
            "contradictions": c,
            "acceleration": accel,
            "accel_status": accel_status,
            "violations": violations,
        })
        if "HIGH_CURVATURE_INSTABILITY" in violations and instability_at is None:
            instability_at = c
            print(f"  🚨 INSTABILITÉ DÉTECTÉE avec {c} contradictions simultanées.")

    conclusion = (
        f"Instabilité déclenchée à {instability_at} contradictions" if instability_at is not None
        else "Aucune instabilité détectée (accel_limit=0.40 est suffisamment permissif)"
    )
    print(f"  → {conclusion}")
    return {"scenario": "semantic_shock", "instability_at_contradictions": instability_at, "steps": results, "conclusion": conclusion}


# ─── Scénario 3 : Sensibilité Temporelle ─────────────────────────────────────

def test_temporal_sensitivity() -> dict:
    """
    Réduit progressivement le délai entre décisions pour trouver la fréquence maximale.
    """
    print("\n--- Test 3 : Sensibilité Temporelle (Fréquence de décision) ---")
    results = []
    breakpoint_delay = None

    delays = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]

    for delay in delays:
        monitor = _reset()
        monitor.evaluate_step("S1", [], [])
        time.sleep(delay)
        monitor.evaluate_step("S2", ["Risk_A"], [])
        time.sleep(delay)
        monitor.evaluate_step("S3", ["Risk_A", "Risk_B"], [])

        report = _get_report(monitor)
        v = report["metrics"]["mean_velocity"]
        status = report["status"]
        violations_all = [v for s in report.get("steps_detail", []) for v in s.get("violations", [])]

        print(f"  Délai: {delay:.3f}s -> Vitesse moy: {v:.4f} | Statut: {status}")
        results.append({"delay_s": delay, "mean_velocity": v, "status": status, "violations": violations_all})

        if status == "FAIL" and breakpoint_delay is None:
            breakpoint_delay = delay
            print(f"  🚨 POINT DE RUPTURE : instabilité si décisions espacées de moins de {delay}s")

    if breakpoint_delay is None:
        conclusion = "Aucun point de rupture trouvé — le moteur est stable même à 10ms entre décisions"
    else:
        conclusion = f"Point de rupture à {breakpoint_delay}s — augmenter tau_max si ce délai est attendu en production"
    print(f"  → {conclusion}")
    return {"scenario": "temporal_sensitivity", "breakpoint_delay_s": breakpoint_delay, "steps": results, "conclusion": conclusion}


# ─── Synthèse et recommandations ─────────────────────────────────────────────

def synthesize(results: list) -> dict:
    """Génère des recommandations de calibration basées sur les résultats."""
    drift = next((r for r in results if r["scenario"] == "linear_escalation"), {})
    shock = next((r for r in results if r["scenario"] == "semantic_shock"), {})
    temporal = next((r for r in results if r["scenario"] == "temporal_sensitivity"), {})

    recommendations = []

    # Drift
    if drift.get("drift_step") is None:
        recommendations.append("tau_max=0.75 : OK pour escalades S0→S4. Peut être réduit à 0.50 pour plus de sécurité.")
    else:
        recommendations.append(f"tau_max trop bas : drift à l'étape {drift['drift_step']}. Envisager tau_max=1.20.")

    # Accélération
    if shock.get("instability_at_contradictions") is None:
        recommendations.append("accel_limit=0.40 : trop permissif. Un attaquant peut faire de grands sauts sans alerte. Réduire à 0.20.")
    else:
        recommendations.append(f"accel_limit=0.40 : instabilité à {shock['instability_at_contradictions']} contradictions. Seuil approprié.")

    # Temporel
    bp = temporal.get("breakpoint_delay_s")
    if bp is None:
        recommendations.append("Sensibilité temporelle : stable à 10ms. Aucun ajustement nécessaire.")
    elif bp >= 0.1:
        recommendations.append(f"Sensibilité temporelle : rupture à {bp}s. Augmenter tau_max si décisions < {bp}s en production.")
    else:
        recommendations.append(f"Sensibilité temporelle : rupture à {bp}s (très rapide). Réduire la fréquence de décision ou augmenter tau_max.")

    return {
        "tau_max_current": 0.75,
        "accel_limit_current": 0.40,
        "recommendations": recommendations,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_stress_test(output_json: bool = False) -> dict:
    print("=" * 60)
    print("  OBSIDIA SIGMA STRESS TEST (v1.4.0)")
    print(f"  Seuils actuels : TauMax=0.75, AccelLimit=0.40")
    print("=" * 60)

    results = [
        test_linear_escalation(),
        test_semantic_shock(),
        test_temporal_sensitivity(),
    ]

    synthesis = synthesize(results)

    print("\n" + "=" * 60)
    print("  SYNTHÈSE ET RECOMMANDATIONS")
    print("=" * 60)
    for rec in synthesis["recommendations"]:
        print(f"  • {rec}")

    full_report = {
        "stress_test_version": "v1.4.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scenarios": results,
        "synthesis": synthesis,
    }

    # Sauvegarde
    out_dir = Path("proofs/V18_9")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "stress_test_results.json"
    with open(out_path, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\n✅ Résultats sauvegardés : {out_path}")

    if output_json:
        print(json.dumps(full_report, indent=2))

    return full_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obsidia Sigma Stress Test")
    parser.add_argument("--json", action="store_true", help="Afficher les résultats en JSON")
    args = parser.parse_args()
    run_stress_test(output_json=args.json)

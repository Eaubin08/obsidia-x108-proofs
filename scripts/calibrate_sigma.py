"""
Obsidia Sigma Calibrator — V18.9 Statistical Threshold Optimizer
================================================================
Lit les rapports de tests réels (PROOFKIT_REPORT.json et/ou
stress_test_results.json) et calcule mathématiquement les seuils
les plus serrés possibles sans déclencher de faux positifs.

Méthode : "Safe Ceiling" (règle des 3-Sigma, 99.7% de couverture).

Architecture "Moteur Fixe + Config Calibrée" :
  - Ce script met à jour agents/sigma_config.json.
  - Le code moteur (obsidia_sigma_v130.py) ne change JAMAIS.
  - Chaque mise à jour de config est tracée (calibration_date, source).

Usage :
    python3 tools/calibrate_sigma.py
    python3 tools/calibrate_sigma.py --report proofs/PROOFKIT_REPORT.json
    python3 tools/calibrate_sigma.py --stress proofs/V18_9/stress_test_results.json
    python3 tools/calibrate_sigma.py --dry-run   (affiche sans écrire)

Sortie :
    agents/sigma_config.json  (mis à jour)
"""

import argparse
import json
import math
import time
from pathlib import Path


# ─── Chargement des données ───────────────────────────────────────────────────

def _load_proofkit(report_path: str) -> dict | None:
    p = Path(report_path)
    if not p.exists():
        return None
    try:
        with open(p, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _load_stress(stress_path: str) -> dict | None:
    p = Path(stress_path)
    if not p.exists():
        return None
    try:
        with open(p, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


# ─── Calcul statistique ───────────────────────────────────────────────────────

def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


# ─── Calibrateur ─────────────────────────────────────────────────────────────

class SigmaCalibrator:
    """
    Analyse l'historique d'Obsidia pour optimiser les seuils Sigma.
    Utilise la règle du '3-Sigma' (99.7% de couverture statistique).
    """

    def __init__(
        self,
        report_path: str = "proofs/PROOFKIT_REPORT.json",
        stress_path: str = "proofs/V18_9/stress_test_results.json",
    ):
        self.report_path = Path(report_path)
        self.stress_path = Path(stress_path)
        self.proofkit_data = _load_proofkit(report_path)
        self.stress_data = _load_stress(stress_path)

    def _extract_velocities_from_proofkit(self) -> list[float]:
        """Extrait les vitesses depuis PROOFKIT_REPORT.json."""
        if not self.proofkit_data or "V18_9_sigma_stability" not in self.proofkit_data:
            return []
        steps = self.proofkit_data["V18_9_sigma_stability"].get("steps_detail", [])
        return [s["velocity"] for s in steps if s.get("velocity", 0) > 0]

    def _extract_velocities_from_stress(self) -> list[float]:
        """Extrait les vitesses depuis stress_test_results.json."""
        if not self.stress_data:
            return []
        velocities = []
        for scenario in self.stress_data.get("scenarios", []):
            for step in scenario.get("steps", []):
                v = step.get("mean_velocity", 0.0)
                if v > 0:
                    velocities.append(v)
        return velocities

    def suggest_thresholds(self) -> dict | None:
        """
        Calcule les seuils recommandés basés sur les données observées.
        Retourne None si pas assez de données.
        """
        velocities = self._extract_velocities_from_proofkit()
        velocities += self._extract_velocities_from_stress()

        if not velocities:
            print("⚠️  Pas de données de vitesse disponibles.")
            print("   Lancez d'abord :")
            print("     python3 agents/run_pipeline.py")
            print("     python3 tests/sigma_stress_test.py")
            return None

        v_mean = _mean(velocities)
        v_std = _stddev(velocities)
        n = len(velocities)

        # ── Règle des 3-Sigma (Safe Ceiling) ──────────────────────────
        # tau_max = μ + 3σ  →  couvre 99.7% des vitesses observées
        tau_max_3sigma = round(v_mean + 3 * v_std, 3)

        # ── Plancher de sécurité : au moins 1.2x la vitesse max observée
        tau_max_safe = max(1.20, round(max(velocities) * 1.2, 3))

        # ── Choix conservateur : le plus grand des deux
        suggested_tau_max = max(tau_max_3sigma, tau_max_safe)
        # Borne haute raisonnable
        suggested_tau_max = min(suggested_tau_max, 5.0)

        # ── accel_limit : basé sur le statut actuel ───────────────────
        current_accel_status = "OK"
        if self.proofkit_data and "V18_9_sigma_stability" in self.proofkit_data:
            current_accel_status = (
                self.proofkit_data["V18_9_sigma_stability"]
                .get("constraints", {})
                .get("vanishing_acceleration", "OK")
            )
        suggested_accel = 0.40 if current_accel_status == "OK" else 0.60

        # ── tau_min : conservé à 0.05 (anti-collapse) ─────────────────
        suggested_tau_min = 0.05

        reasoning = (
            f"Basé sur {n} observations de vitesse. "
            f"μ={v_mean:.4f}, σ={v_std:.4f}. "
            f"Règle 3-sigma : μ+3σ={tau_max_3sigma:.3f}. "
            f"Safe ceiling (1.2×max) : {tau_max_safe:.3f}. "
            f"Valeur retenue : {suggested_tau_max:.3f}."
        )

        return {
            "tau_min": suggested_tau_min,
            "new_tau_max": suggested_tau_max,
            "new_accel_limit": suggested_accel,
            "stats": {
                "n_observations": n,
                "v_mean": round(v_mean, 6),
                "v_std": round(v_std, 6),
                "v_max": round(max(velocities), 6),
                "tau_max_3sigma": tau_max_3sigma,
                "tau_max_safe_ceiling": tau_max_safe,
            },
            "reasoning": reasoning,
        }

    def print_recommendations(self) -> None:
        """Affiche les recommandations sans modifier les fichiers."""
        suggestions = self.suggest_thresholds()
        if not suggestions:
            return

        print("\n" + "=" * 60)
        print("  RECOMMANDATION DE CALIBRATION SIGMA (v1.4.1)")
        print("=" * 60)
        print(f"  📍 Source ProofKit : {self.report_path}")
        print(f"  📍 Source Stress   : {self.stress_path}")
        print(f"\n  📊 Statistiques ({suggestions['stats']['n_observations']} observations) :")
        print(f"     Vitesse moyenne  : {suggestions['stats']['v_mean']:.4f}")
        print(f"     Écart-type       : {suggestions['stats']['v_std']:.4f}")
        print(f"     Vitesse max      : {suggestions['stats']['v_max']:.4f}")
        print(f"\n  🚀 Nouveau tau_max   : {suggestions['new_tau_max']}")
        print(f"  📉 Nouvel accel_limit: {suggestions['new_accel_limit']}")
        print(f"\n  💡 Justification :")
        print(f"     {suggestions['reasoning']}")
        print("\n  Pour appliquer : python3 tools/calibrate_sigma.py --apply")

    def apply_calibration(
        self,
        config_path: str = "agents/sigma_config.json",
        dry_run: bool = False,
    ) -> bool:
        """
        Met à jour agents/sigma_config.json avec les seuils calculés.
        Retourne True si la calibration a été appliquée.
        """
        suggestions = self.suggest_thresholds()
        if not suggestions:
            return False

        new_config = {
            "tau_min": suggestions["tau_min"],
            "tau_max": suggestions["new_tau_max"],
            "accel_limit": suggestions["new_accel_limit"],
            "calibration_date": time.strftime("%Y-%m-%d"),
            "calibration_method": "3-sigma_safe_ceiling",
            "source_report": str(self.report_path),
            "stats": suggestions["stats"],
            "reasoning": suggestions["reasoning"],
        }

        print("\n" + "=" * 60)
        print("  CALIBRATION SIGMA — RÉSULTAT")
        print("=" * 60)
        print(f"  tau_min    : {new_config['tau_min']}")
        print(f"  tau_max    : {new_config['tau_max']}")
        print(f"  accel_limit: {new_config['accel_limit']}")
        print(f"  Méthode    : {new_config['calibration_method']}")
        print(f"  Date       : {new_config['calibration_date']}")

        if dry_run:
            print("\n  [DRY-RUN] Aucune modification effectuée.")
            print(f"  Contenu qui serait écrit dans {config_path} :")
            print(json.dumps(new_config, indent=4))
            return False

        p = Path(config_path)
        with open(p, "w") as f:
            json.dump(new_config, f, indent=4)

        print(f"\n  ✅ CONFIG MISE À JOUR : {config_path}")
        print("     Le moteur utilisera ces seuils au prochain démarrage.")
        return True


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obsidia Sigma Calibrator")
    parser.add_argument(
        "--report",
        default="proofs/PROOFKIT_REPORT.json",
        help="Chemin vers PROOFKIT_REPORT.json",
    )
    parser.add_argument(
        "--stress",
        default="proofs/V18_9/stress_test_results.json",
        help="Chemin vers stress_test_results.json",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Appliquer la calibration (écrit agents/sigma_config.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher sans écrire",
    )
    parser.add_argument(
        "--config",
        default="agents/sigma_config.json",
        help="Chemin de sortie pour la config Sigma",
    )
    args = parser.parse_args()

    calibrator = SigmaCalibrator(report_path=args.report, stress_path=args.stress)

    if args.apply or args.dry_run:
        calibrator.apply_calibration(config_path=args.config, dry_run=args.dry_run)
    else:
        calibrator.print_recommendations()
        print("\n  Pour appliquer : python3 tools/calibrate_sigma.py --apply")

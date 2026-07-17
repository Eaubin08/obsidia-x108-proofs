"""
tests/test_cosmos_friction_eml.py
══════════════════════════════════════════════════════════════════════════════
SIMULATION : Réaction en chaîne thermodynamique — Friction des Multivers
             Layer 2 (EML) → Sigma → Kernel X-108

CHAÎNE MODÉLISÉE :
  [Chaos] → [Reflex Reducer EML] → SIGNAL_DRIFT
          → [Mock Pipeline Sigma] → contradictions élevées
          → [ObsidiaSigmaMonitor] → HOLD_STABILITY_ALERT / S4 / sigma_override=True
          → [Kernel X-108]        → seul décideur (non invoqué ici)

RÈGLE : Le Layer 2 compresse, Sigma qualifie, X-108 tranche.
══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import sys
import os
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from periphery.reflex_reducer_v1 import (
    reduce_signal,
    SIGNAL_DRIFT,
    DECISION_AUTHORITY,
    EMITS_VERDICT,
    EMITS_ACT,
)

# ══════════════════════════════════════════════════════════════════════════════
# MOCK — ObsidiaSigmaMonitor (layer Sigma — aval du Layer 2)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SigmaStep:
    """Étape du pipeline Sigma — produite par le mock."""
    step_id: str
    input_signal: Any
    contradiction_score: float
    severity: str
    market_verdict: str
    sigma_override: bool
    note: str = ""
    # Invariants Sigma — jamais décisionnels au sens autonome
    emits_verdict: bool = False
    decision_authority: str = "KX108_ONLY"


class ObsidiaSigmaMonitor:
    """
    Mock du monitor Sigma — intercepte SIGNAL_DRIFT et force HOLD_STABILITY_ALERT.

    Rôle réel : Sigma qualifie la trajectoire et la transmet au Kernel X-108.
    Le Kernel est le seul à émettre ALLOW/HOLD/BLOCK définitif.
    """

    DRIFT_CONTRADICTION_FLOOR = 0.92
    DRIFT_SEVERITY            = "S4"
    DRIFT_VERDICT             = "HOLD_STABILITY_ALERT"

    def evaluate_step(self, step_id: str, signal: Any) -> SigmaStep:
        """
        Évalue un signal entrant.

        Si le signal est SIGNAL_DRIFT → force HOLD_STABILITY_ALERT + S4.
        Sinon → évalue normalement (scalar dans [-1,1]).
        """
        if signal is SIGNAL_DRIFT or signal == SIGNAL_DRIFT:
            return SigmaStep(
                step_id=step_id,
                input_signal=signal,
                contradiction_score=self.DRIFT_CONTRADICTION_FLOOR,
                severity=self.DRIFT_SEVERITY,
                market_verdict=self.DRIFT_VERDICT,
                sigma_override=True,
                note=(
                    "SIGNAL_DRIFT intercepté : le Layer 2 EML n'a pas pu "
                    "compresser le chaos (|EML(x,y)| > seuil). "
                    "Sigma force HOLD_STABILITY_ALERT. "
                    "X-108 est l'unique décideur de la réponse finale."
                ),
            )

        # Signal numérique normal
        scalar = float(signal) if isinstance(signal, (int, float)) else 0.0
        contradiction = max(0.0, abs(scalar))
        if contradiction > 0.8:
            sev, verdict, override = "S3", "HOLD_HIGH_CONTRADICTION", True
        elif contradiction > 0.5:
            sev, verdict, override = "S2", "MONITOR", False
        else:
            sev, verdict, override = "S1", "PROCEED_CONTEXT_ONLY", False

        return SigmaStep(
            step_id=step_id,
            input_signal=signal,
            contradiction_score=round(contradiction, 4),
            severity=sev,
            market_verdict=verdict,
            sigma_override=override,
            note="Signal normal compressé par le Layer 2.",
        )


# ══════════════════════════════════════════════════════════════════════════════
# DONNÉES MOCK
# ══════════════════════════════════════════════════════════════════════════════

def _baseline_signal() -> Dict[str, Any]:
    """Signal de référence — Matière / Stable. EML devrait converger."""
    return {
        "risk":             0.15,
        "uncertainty":      0.12,
        "contradiction":    0.05,
        "volatility":       0.10,
        "reversibility":    0.95,
        "confidence":       0.88,
        "temporal_pressure": 0.08,
        "source_conflict":  0.04,
    }


def _test3_structural_error_signal() -> Dict[str, Any]:
    """
    test3_structural_error — Antimatière / Bruit entropique massif.

    Erreur structurelle = valeurs HORS BORNES normales [0,1].
    risk=8.5 représente un risque "hors échelle" — bruit de structure, pas de signal métier.

    Calcul EML garanti :
      axes[0] = risk = 8.5, axes[1] = uncertainty = 0.00001
      eml_operator(8.5, 0.00001) :
        x2 = clamp(8.5) = 8.5
        y2 = abs(0.00001) + 1.0 = 1.00001
        raw = exp(8.5) - log(1.00001) ≈ 4914.8 - 0.00001 = 4914.8
        |4914.8| >> EML_CHAOS_THRESHOLD (5.0) → SIGNAL_DRIFT garanti

    Le signal baseline (risk=0.15) produit max_eml ≈ 2.5 < 5.0 → pas de dérive.
    """
    return {
        "risk":             8.5,       # HORS BORNES — erreur structurelle
        "uncertainty":      0.00001,   # quasi-zéro — force EML maximal
        "contradiction":    9.9,       # HORS BORNES — incohérence structurelle
        "volatility":       7.3,       # HORS BORNES
        "reversibility":    0.00001,   # quasi-irréversible — hors bornes
        "confidence":       8.8,       # HORS BORNES — sur-confiance structurelle
        "temporal_pressure": 0.00001,  # quasi-zéro — maximise exp(x)/log(y) ratio
        "source_conflict":  9.5,       # HORS BORNES
    }


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION — Réaction en chaîne
# ══════════════════════════════════════════════════════════════════════════════

def run_thermodynamic_chain() -> None:
    SEP = "=" * 70

    print()
    print(SEP)
    print("  OBSIDIA X-108 — FRICTION DES MULTIVERS")
    print("  Réaction en chaîne : Layer 2 (EML) → Sigma → Kernel X-108")
    print(SEP)

    sigma = ObsidiaSigmaMonitor()

    # ─────────────────────────────────────────────────────────────────────────
    # ÉTAPE 1 — Injection du signal de référence (Baseline)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  ÉTAPE 1 : Signal BASELINE (Matière / Stable)")
    print("─" * 70)
    baseline = _baseline_signal()
    print(f"  Signal entrant   : {json.dumps(baseline)}")

    result_baseline = reduce_signal(baseline)
    is_drift_baseline = (result_baseline is SIGNAL_DRIFT or result_baseline == SIGNAL_DRIFT)
    print(f"  Résultat EML     : {'SIGNAL_DRIFT' if is_drift_baseline else 'compression reussie'}")
    if not is_drift_baseline and isinstance(result_baseline, dict):
        print(f"  logic_fingerprint: {result_baseline['logic_fingerprint'][:32]}...")
        print(f"  logic_scalar     : {result_baseline['logic_scalar']}")

    sigma_baseline = sigma.evaluate_step("STEP_BASELINE", result_baseline)
    print(f"  Sigma verdict    : {sigma_baseline.market_verdict}")
    print(f"  Sigma severity   : {sigma_baseline.severity}")
    print(f"  sigma_override   : {sigma_baseline.sigma_override}")

    # ─────────────────────────────────────────────────────────────────────────
    # ÉTAPE 2 — Injection du chaos test3_structural_error
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  ÉTAPE 2 : Injection CHAOS — test3_structural_error (Antimatière)")
    print("─" * 70)
    chaos = _test3_structural_error_signal()
    print(f"  Signal entrant   : {json.dumps(chaos)}")

    import math
    x_eml  = min(chaos["risk"], 20.0)
    y_eml  = abs(chaos["uncertainty"]) + 1.0
    eml_preview = math.exp(x_eml) - math.log(y_eml)
    print(f"  EML(risk={chaos['risk']}, uncertainty={chaos['uncertainty']}) :")
    print(f"    x2 = clamp({chaos['risk']}) = {x_eml}")
    print(f"    y2 = abs({chaos['uncertainty']}) + 1.0 = {y_eml:.5f}")
    print(f"    raw = exp({x_eml}) - log({y_eml:.5f})")
    print(f"        = {math.exp(x_eml):.4f} - {math.log(y_eml):.5f}")
    print(f"        = {eml_preview:.4f}  (seuil EML_CHAOS_THRESHOLD = 5.0)")

    # ─────────────────────────────────────────────────────────────────────────
    # ÉTAPE 3 — Le Reflex Reducer EML tente de compresser → SIGNAL_DRIFT
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  ÉTAPE 3 : Layer 2 EML (Opérateur Odrzywołek) — compression")
    print("─" * 70)
    result_chaos = reduce_signal(chaos)
    is_drift = (result_chaos is SIGNAL_DRIFT or result_chaos == SIGNAL_DRIFT)

    print(f"  Résultat Layer 2 : {result_chaos!r}")
    if is_drift:
        print("  >>> SIGNAL_DRIFT detecte : |EML(x,y)| > seuil EML_CHAOS_THRESHOLD")
        print("      Le Layer 2 ne peut pas comprimer ce chaos.")
        print("      Transmission du sentinel SIGNAL_DRIFT au layer Sigma...")
    else:
        print("  [INATTENDU] Le chaos a ete comprime — vérifier les seuils.")

    # ─────────────────────────────────────────────────────────────────────────
    # ÉTAPE 4 — SIGNAL_DRIFT injecté dans le pipeline Sigma
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  ÉTAPE 4 : SIGNAL_DRIFT → Mock Pipeline Décisionnel")
    print("─" * 70)
    # Le pipeline Sigma reçoit SIGNAL_DRIFT et produit un SigmaStep
    sigma_step = sigma.evaluate_step("STEP_ANTIMATTER_CHAOS", result_chaos)

    print(f"  contradiction_score : {sigma_step.contradiction_score}")
    print(f"  severity            : {sigma_step.severity}")
    print(f"  market_verdict      : {sigma_step.market_verdict}")
    print(f"  sigma_override      : {sigma_step.sigma_override}")
    print(f"  note                : {sigma_step.note}")

    # ─────────────────────────────────────────────────────────────────────────
    # ÉTAPE 5 — Intercepte ObsidiaSigmaMonitor → HOLD_STABILITY_ALERT S4
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  ÉTAPE 5 : ObsidiaSigmaMonitor — Bouclier Sigma")
    print("─" * 70)
    print(f"  >>> BOUCLIER SIGMA DÉCLENCHÉ par SIGNAL_DRIFT !")
    print(f"      market_verdict = {sigma_step.market_verdict!r}")
    print(f"      severity       = {sigma_step.severity!r}")
    print(f"      sigma_override = {sigma_step.sigma_override}")
    print()
    print("  Sigma a qualifié la trajectoire instable.")
    print("  Le Kernel X-108 est l'unique décideur de la réponse finale.")
    print("  (ALLOW / HOLD / BLOCK — hors du périmètre de cette simulation)")

    # ─────────────────────────────────────────────────────────────────────────
    # ASSERTIONS — Invariants de la chaîne
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  ASSERTIONS — Invariants de la réaction en chaîne")
    print("─" * 70)

    errors: list[str] = []

    def _chk(cond: bool, name: str) -> None:
        sym = "OK " if cond else "FAIL"
        print(f"  [{sym}] {name}")
        if not cond:
            errors.append(name)

    # Layer 2 — SIGNAL_DRIFT émis sur chaos
    _chk(is_drift,
         "Layer 2 retourne SIGNAL_DRIFT sur test3_structural_error")
    _chk(not is_drift_baseline,
         "Layer 2 ne retourne PAS SIGNAL_DRIFT sur signal stable")

    # Sigma — bouclier déclenché
    _chk(sigma_step.market_verdict == "HOLD_STABILITY_ALERT",
         f"market_verdict == 'HOLD_STABILITY_ALERT' (actual: {sigma_step.market_verdict!r})")
    _chk(sigma_step.severity == "S4",
         f"severity == 'S4' (actual: {sigma_step.severity!r})")
    _chk(sigma_step.sigma_override is True,
         f"sigma_override == True (actual: {sigma_step.sigma_override})")
    _chk(sigma_step.contradiction_score >= 0.9,
         f"contradiction_score >= 0.9 (actual: {sigma_step.contradiction_score})")

    # Sigma n'émet jamais de verdict autonome
    _chk(sigma_step.emits_verdict is False,
         f"sigma_step.emits_verdict == False")
    _chk(sigma_step.decision_authority == "KX108_ONLY",
         f"sigma_step.decision_authority == 'KX108_ONLY' (actual: {sigma_step.decision_authority!r})")

    # Layer 2 invariants globaux
    _chk(EMITS_VERDICT is False,
         "EMITS_VERDICT global Layer 2 == False")
    _chk(EMITS_ACT is False,
         "EMITS_ACT global Layer 2 == False")
    _chk(DECISION_AUTHORITY == "KX108_ONLY",
         f"DECISION_AUTHORITY Layer 2 == 'KX108_ONLY'")

    # Baseline Sigma ne déclenche pas le bouclier
    _chk(sigma_baseline.sigma_override is False,
         "sigma_baseline.sigma_override == False (signal stable ne déclenche pas le bouclier)")

    print()
    print(SEP)
    if errors:
        print(f"  ECHEC — {len(errors)} invariant(s) viole(s) :")
        for e in errors:
            print(f"    * {e}")
        print(SEP)
        raise AssertionError(f"Réaction en chaîne — {len(errors)} invariant(s) violé(s) : {errors}")
    else:
        print("  TOUS LES INVARIANTS VALIDES")
        print()
        print("  RECAPITULATIF — Reaction en chaine :")
        print(f"    SIGNAL_DRIFT     : Layer 2 emet SIGNAL_DRIFT (chaos > seuil EML)")
        print(f"    Sigma qualifie   : contradiction={sigma_step.contradiction_score}, severity=S4")
        print(f"    Bouclier actif   : market_verdict=HOLD_STABILITY_ALERT, sigma_override=True")
        print(f"    Kernel X-108     : unique decideur — non invoque dans cette simulation")
        print(f"    Chaine prouvee   : L2 compresse | Sigma qualifie | X108 tranche")
    print(SEP)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_thermodynamic_chain()


def test_cosmos_friction_eml():
    """pytest wrapper — Reaction en chaine thermodynamique Layer 2 -> Sigma."""
    run_thermodynamic_chain()

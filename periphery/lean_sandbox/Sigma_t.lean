-- Sigma_t -- Fonction Sigma temporelle (peripherique)
-- Status : PROVISIONAL scaffold -- REPAIR_PALIER_1
-- SOURCE_COVERAGE: threshold | warning_threshold | stop_threshold | target_threshold
--                  alert_ready | immediate_stop | coherence
-- NOTE: Sigma_t est une fonction peripherique d'agregation de signaux.
--       Elle n'est PAS le kernel X-108 qui pilote ACT/HOLD.
--       Distinction : Sigma_t surveille ; le kernel decide.
--       stop_threshold > warning_threshold : escalade automatique.
--       coherence : alignement entre threshold et target_threshold.

namespace Obsidia
namespace SigmaT

structure SigmaTState where
  threshold        : Nat
  warning_threshold : Nat
  stop_threshold   : Nat
  target_threshold : Nat
  alert_ready      : Bool
  immediate_stop   : Bool

-- Hiérarchie : warning < stop (escalade)
def escalade_valid (s : SigmaTState) : Prop :=
  s.warning_threshold < s.stop_threshold

-- Alerte active si signal au-dessus du seuil
def alert_active (s : SigmaTState) : Prop :=
  And (s.alert_ready = true)
      (s.threshold <= s.warning_threshold)

-- Stop immédiat si flag levé
def stop_active (s : SigmaTState) : Prop :=
  s.immediate_stop = true

def canonical : SigmaTState :=
  { threshold := 2, warning_threshold := 3, stop_threshold := 7,
    target_threshold := 5, alert_ready := true, immediate_stop := false }

theorem canonical_escalade : escalade_valid canonical := by
  simp [canonical, escalade_valid]

theorem canonical_alert : alert_active canonical := by
  simp [canonical, alert_active]

end SigmaT
end Obsidia

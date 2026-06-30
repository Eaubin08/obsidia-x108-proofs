-- Faisceau_futurs -- Faisceau des futurs admissibles
-- Status : PROVISIONAL scaffold -- REPAIR_PALIER_1
-- SOURCE_COVERAGE: faisceau | futurs admissibles | restriction par contrainte
--                  calibration active | admission de chemin | count restriction
-- NOTE: restricted_count_le prouve que la restriction reduit le faisceau,
--       non que tous les futurs sont valides.

namespace Obsidia
namespace FaisceauFuturs

structure FaisceauState where
  initial_count        : Nat
  restricted_count     : Nat
  calibration_applied  : Bool
  path_admission_ready : Bool

def admission_ready (s : FaisceauState) : Prop :=
  And (s.calibration_applied = true)
      (s.path_admission_ready = true)

def restricted_le_initial (s : FaisceauState) : Prop :=
  s.restricted_count <= s.initial_count

def canonical : FaisceauState :=
  { initial_count := 10, restricted_count := 4,
    calibration_applied := true, path_admission_ready := true }

theorem canonical_admission : admission_ready canonical :=
  And.intro rfl rfl

-- La restriction réduit le faisceau (hypothèse h fournie par l'appelant)
theorem restricted_count_le (s : FaisceauState) (h : s.restricted_count <= s.initial_count) :
    restricted_le_initial s := h

theorem canonical_restricted : restricted_le_initial canonical := by
  simp [canonical, restricted_le_initial]

end FaisceauFuturs
end Obsidia

-- Espace_Etat_StateCore.lean
-- Noyau formel d'espace d'etat Obsidia -- StateCore
-- Status : FORMAL -- Peripheral repair D4B-1
-- SOURCE_COVERAGE: espace_etat_core | etat_admissible | hold_non_admissible
--                  risque_state | coherence_etat | etat_core_kernel
-- PROVISIONAL_BOUNDARY: espace d'etat discret (Bool).
--   Admissible <=> risque=false, inconnu=false, coherent=true.
--   kernel_boundary: evaluation peripherique, non decisionnelle. KX108 seul est souverain.

namespace Obsidia
namespace EspaceEtatStateCore

structure StateCore where
  risque   : Bool
  inconnu  : Bool
  coherent : Bool

def etat_admissible (s : StateCore) : Prop :=
  s.risque = false ∧ s.inconnu = false ∧ s.coherent = true

def etat_hold (s : StateCore) : Prop :=
  ¬ etat_admissible s

def etat_canonical : StateCore :=
  { risque := false, inconnu := false, coherent := true }

theorem canonical_admissible : etat_admissible etat_canonical :=
  ⟨rfl, rfl, rfl⟩

theorem canonical_not_hold : ¬ etat_hold etat_canonical :=
  fun h => h canonical_admissible

theorem risque_implique_hold (s : StateCore) (h : s.risque = true) :
    etat_hold s := by
  intro hadm
  have hr := hadm.1
  simp [h] at hr

theorem inconnu_implique_hold (s : StateCore) (h : s.inconnu = true) :
    etat_hold s := by
  intro hadm
  have hi := hadm.2.1
  simp [h] at hi

theorem non_coherent_implique_hold (s : StateCore) (h : s.coherent = false) :
    etat_hold s := by
  intro hadm
  have hc := hadm.2.2
  simp [h] at hc

theorem hold_non_admissible (s : StateCore) (h : etat_hold s) :
    ¬ etat_admissible s := h

end EspaceEtatStateCore
end Obsidia

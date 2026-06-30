namespace Obsidia
namespace P47CouplageRdt

structure CoupleState where
  delta_detected : Bool
  couplage_actif : Bool

def couplage_valide (c : CoupleState) : Prop :=
  c.delta_detected = true ∧ c.couplage_actif = true

def couplage_hold (c : CoupleState) : Prop := ¬ couplage_valide c

def canonical_couple : CoupleState := { delta_detected := true, couplage_actif := true }

theorem canonical_valide : couplage_valide canonical_couple := ⟨rfl, rfl⟩

theorem sans_delta_hold (c : CoupleState) (h : c.delta_detected = false) :
    couplage_hold c := by
  intro hv; have hd := hv.1; simp [h] at hd

theorem sans_couplage_hold (c : CoupleState) (h : c.couplage_actif = false) :
    couplage_hold c := by
  intro hv; have hc := hv.2; simp [h] at hc

end P47CouplageRdt
end Obsidia

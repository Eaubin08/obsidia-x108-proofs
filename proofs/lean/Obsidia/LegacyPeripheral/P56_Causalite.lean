namespace Obsidia
namespace P56Causalite

structure CausalState where
  has_cause    : Bool
  effect_valid : Bool

def causal_valide (c : CausalState) : Prop :=
  c.has_cause = true ∧ c.effect_valid = true

def causal_hold (c : CausalState) : Prop := ¬ causal_valide c

def causal_canonique : CausalState := { has_cause := true, effect_valid := true }

theorem canonique_valide : causal_valide causal_canonique := ⟨rfl, rfl⟩

theorem sans_cause_hold (c : CausalState) (h : c.has_cause = false) :
    causal_hold c := by
  intro hv; have hc := hv.1; simp [h] at hc

theorem effet_invalide_hold (c : CausalState) (h : c.effect_valid = false) :
    causal_hold c := by
  intro hv; have he := hv.2; simp [h] at he

theorem hold_not_valide (c : CausalState) (h : causal_hold c) :
    ¬ causal_valide c := h

end P56Causalite
end Obsidia

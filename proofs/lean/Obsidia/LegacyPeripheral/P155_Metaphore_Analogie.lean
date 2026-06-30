namespace Obsidia
namespace P155MetaphoreAnalogie

structure AnalogieState where
  structure_preserved : Bool
  mapping_valid       : Bool

def analogie_valide (a : AnalogieState) : Prop :=
  a.structure_preserved = true ∧ a.mapping_valid = true

def analogie_hold (a : AnalogieState) : Prop := ¬ analogie_valide a

def canonical_analogie : AnalogieState :=
  { structure_preserved := true, mapping_valid := true }

theorem canonical_valide : analogie_valide canonical_analogie := ⟨rfl, rfl⟩

theorem structure_lost_hold (a : AnalogieState) (h : a.structure_preserved = false) :
    analogie_hold a := by
  intro hv; have hs := hv.1; simp [h] at hs

theorem invalid_mapping_hold (a : AnalogieState) (h : a.mapping_valid = false) :
    analogie_hold a := by
  intro hv; have hm := hv.2; simp [h] at hm

end P155MetaphoreAnalogie
end Obsidia

namespace Obsidia
namespace P57ShannonEntropy

structure EntropyState where
  unknown_factors : Nat
  law_applied     : Bool

def entropy_minimal (e : EntropyState) : Prop :=
  e.unknown_factors = 0

def entropy_hold (e : EntropyState) : Prop := ¬ entropy_minimal e

def canonical_entropy : EntropyState := { unknown_factors := 0, law_applied := true }

theorem canonical_minimal : entropy_minimal canonical_entropy := rfl

theorem nonzero_unknowns_hold (e : EntropyState) (h : e.unknown_factors ≠ 0) :
    entropy_hold e := h

theorem zero_implies_minimal (e : EntropyState) (h : e.unknown_factors = 0) :
    entropy_minimal e := h

end P57ShannonEntropy
end Obsidia

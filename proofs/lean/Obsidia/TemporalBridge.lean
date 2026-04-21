import Obsidia.Basic
import Obsidia.TemporalRaw
import Obsidia.TemporalKernel

namespace Obsidia
namespace TemporalBridge

open TemporalRaw
open TemporalKernel

def canonicalize_elapsed (e : Int) : Nat :=
  Int.toNat e

def decide_with_skew_handling (τ : Int) (i : TInput_Raw) : Decision :=
  if decide (elapsed_raw i < 0) then
    if decide (i.irr = true) then
      if decide (0 <= τ) then
        Decision.HOLD
      else
        decideX108 (Int.toNat τ) i.metrics i.theta i.irr (canonicalize_elapsed (elapsed_raw i))
    else
      decideX108 (Int.toNat τ) i.metrics i.theta i.irr (canonicalize_elapsed (elapsed_raw i))
  else
    decideX108 (Int.toNat τ) i.metrics i.theta i.irr (canonicalize_elapsed (elapsed_raw i))

theorem canonicalize_preserves_nonneg (e : Int) (_h : 0 <= e) :
    canonicalize_elapsed e = Int.toNat e := by
  rfl

theorem skew_negative_implies_hold (τ : Int) (i : TInput_Raw)
    (hIrr : i.irr = true)
    (hneg : elapsed_raw i < 0)
    (hTau : 0 <= τ) :
    decide_with_skew_handling τ i = Decision.HOLD := by
  unfold decide_with_skew_handling
  have h1 : decide (elapsed_raw i < 0) = true := decide_eq_true hneg
  have h2 : decide (i.irr = true) = true := decide_eq_true hIrr
  have h3 : decide (0 <= τ) = true := decide_eq_true hTau
  rw [h1, h2, h3]
  rfl

#print axioms Obsidia.TemporalBridge.canonicalize_preserves_nonneg
#print axioms Obsidia.TemporalBridge.skew_negative_implies_hold

end TemporalBridge
end Obsidia

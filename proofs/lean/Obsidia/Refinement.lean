import Obsidia.SystemModel
import Obsidia.TemporalX108

namespace Obsidia.Refinement

open Obsidia
open Obsidia.SystemModel

def R_decision (d : Decision) (d3 : Decision3) : Prop :=
  d3 = liftDecision d

theorem lift_refines (d : Decision) :
    R_decision d (liftDecision d) := by
  rfl

theorem x108_is_lift (τ : Tau) (i : TInput) :
    decide3X108 τ i = liftDecision (decideX108 τ i) := by
  rfl

theorem x108_never_blocks (τ : Tau) (i : TInput) :
    Not (decide3X108 τ i = Decision3.BLOCK) := by
  exact Obsidia.X108_kernel_never_blocks τ i

theorem refined_not_block (d : Decision) (d3 : Decision3)
    (h : R_decision d d3) :
    Not (d3 = Decision3.BLOCK) := by
  rw [h]
  cases d <;> decide

end Obsidia.Refinement
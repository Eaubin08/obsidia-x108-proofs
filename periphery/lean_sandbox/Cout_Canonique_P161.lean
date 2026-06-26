import Std

-- Théorème périphérique Obsidia — Cout_Canonique_P161
-- Statut : LEAN_SANDBOX_PERIPHERAL
-- Scope : scaffold coût canonique P161, hors kernel, hors proofs scellé.
-- Aucun sorry/admit/axiom.

namespace Obsidia
namespace CoutP161

structure StateCore where
  sigma : Nat
  lambdaVal : Nat
  E : Nat
  Rc : Nat
  U1 : Nat
  U2 : Nat
  U3 : Nat

def qU (x : StateCore) : Nat :=
  Nat.succ (x.U1 + x.U2 + x.U3)

def dot_m (x : StateCore) : Nat :=
  x.lambdaVal + x.E + x.sigma

def cost (kappa : Nat) (x : StateCore) : Nat :=
  kappa * Nat.succ (dot_m x) * qU x

theorem cost_nonneg (kappa : Nat) (x : StateCore) : 0 ≤ cost kappa x :=
  Nat.zero_le (cost kappa x)

theorem qU_pos (x : StateCore) : qU x > 0 := by
  unfold qU
  exact Nat.succ_pos (x.U1 + x.U2 + x.U3)

end CoutP161
end Obsidia
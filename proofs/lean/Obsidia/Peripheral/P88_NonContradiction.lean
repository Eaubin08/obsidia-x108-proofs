import Std

-- Théorème périphérique Obsidia — P88
-- Statut : LEAN_SANDBOX_PERIPHERAL
-- Scope : preuve logique minimale, hors kernel, hors proofs scellé.
-- Aucun sorry/admit/axiom.

namespace Obsidia
namespace P88

theorem non_contradiction (A : Prop) : ¬ (A ∧ ¬ A) := fun h => h.right h.left

end P88
end Obsidia
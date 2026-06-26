-- P88 — Non-contradiction
-- ¬(A ∧ ¬A) — principe logique fondamental
-- Sandbox périphérique — ne touche pas proofs/ scellé

namespace Obsidia
namespace P88

theorem non_contradiction (A : Prop) : ¬(A ∧ ¬A) := by
  intro h
  exact h.2 h.1

end P88
end Obsidia

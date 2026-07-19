namespace Obsidia
namespace BalanceExponentielle

-- Balance Exponentielle
-- Type: formula — peripherique, non-decisionnel, runtime_bound=false

structure BalanceExponentielleState where
  active    : Bool
  validated : Bool

def balanceexponentielle_valide (s : BalanceExponentielleState) : Prop :=
  s.active = true ∧ s.validated = true

def balanceexponentielle_hold (s : BalanceExponentielleState) : Prop := ¬ balanceexponentielle_valide s

def canonical : BalanceExponentielleState := { active := true, validated := true }

theorem canonical_valide : balanceexponentielle_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : BalanceExponentielleState) (h : s.active = false) :
    balanceexponentielle_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : BalanceExponentielleState) (h : s.validated = false) :
    balanceexponentielle_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end BalanceExponentielle
end Obsidia

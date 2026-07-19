namespace Obsidia
namespace P42

structure ThresholdState where
  score : Nat
  theta : Nat

def admissible (score theta : Nat) : Prop :=
  score <= theta

def state_admissible (s : ThresholdState) : Prop :=
  admissible s.score s.theta

def above_threshold (score theta : Nat) : Prop :=
  theta < score

theorem admissible_intro
    (score theta : Nat)
    (h : score <= theta) :
    admissible score theta := by
  exact h

theorem state_admissible_intro
    (s : ThresholdState)
    (h : admissible s.score s.theta) :
    state_admissible s := by
  exact h

theorem score_le_threshold_from_state_admissible
    (s : ThresholdState)
    (h : state_admissible s) :
    s.score <= s.theta := by
  exact h

theorem not_admissible_above_threshold
    (score theta : Nat)
    (h : above_threshold score theta) :
    Not (admissible score theta) := by
  intro ha
  exact Nat.not_lt_of_ge ha h

theorem not_state_admissible_when_above_threshold
    (s : ThresholdState)
    (h : above_threshold s.score s.theta) :
    Not (state_admissible s) := by
  intro hs
  exact not_admissible_above_threshold s.score s.theta h hs

theorem threshold_reflexive_admissible
    (theta : Nat) :
    admissible theta theta := by
  exact Nat.le_refl theta

end P42
end Obsidia

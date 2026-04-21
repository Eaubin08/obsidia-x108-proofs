import Std

namespace Obsidia

structure Metrics where
  T_mean  : Rat
  H_score : Rat
  A_score : Rat
  S       : Rat

inductive Decision
  | HOLD
  | ACT
  deriving Repr, DecidableEq

def decision (m : Metrics) (theta : Rat) : Decision :=
  match decide (theta <= m.S) with
  | true  => Decision.ACT
  | false => Decision.HOLD

theorem decision_eq_ACT_iff (m : Metrics) (theta : Rat) :
    decision m theta = Decision.ACT <-> theta <= m.S := by
  unfold decision
  constructor
  · intro h
    by_cases hle : theta <= m.S
    · exact hle
    · have hfalse : decide (theta <= m.S) = false := decide_eq_false hle
      rw [hfalse] at h
      cases h
  · intro hle
    have htrue : decide (theta <= m.S) = true := decide_eq_true hle
    rw [htrue]

theorem decision_eq_HOLD_iff (m : Metrics) (theta : Rat) :
    decision m theta = Decision.HOLD <-> Not (theta <= m.S) := by
  unfold decision
  constructor
  · intro h
    intro hle
    have htrue : decide (theta <= m.S) = true := decide_eq_true hle
    rw [htrue] at h
    cases h
  · intro hnot
    have hfalse : decide (theta <= m.S) = false := decide_eq_false hnot
    rw [hfalse]

theorem D1_determinism (m : Metrics) (theta : Rat) :
    decision m theta = decision m theta := rfl

theorem G1_act_above_threshold (m : Metrics) (theta : Rat)
    (h : theta <= m.S) :
    decision m theta = Decision.ACT := by
  unfold decision
  have htrue : decide (theta <= m.S) = true := decide_eq_true h
  rw [htrue]

theorem E2_no_act_below_threshold (m : Metrics) (theta : Rat)
    (h : Not (theta <= m.S)) :
    decision m theta = Decision.HOLD := by
  unfold decision
  have hfalse : decide (theta <= m.S) = false := decide_eq_false h
  rw [hfalse]

theorem G2_boundary_inclusive (m : Metrics) (theta : Rat)
    (h : m.S = theta) :
    decision m theta = Decision.ACT := by
  have hle : theta <= m.S := by
    simpa [h] using (Rat.le_refl : theta <= theta)
  exact G1_act_above_threshold m theta hle

theorem G3_monotonicity (m1 m2 : Metrics) (theta : Rat)
    (h1 : theta <= m1.S) (h2 : m1.S <= m2.S) :
    decision m2 theta = Decision.ACT := by
  have hle : theta <= m2.S := Rat.le_trans h1 h2
  exact G1_act_above_threshold m2 theta hle

inductive Decision3
  | BLOCK
  | HOLD
  | ACT
  deriving Repr, DecidableEq

def liftDecision (d : Decision) : Decision3 :=
  match d with
  | Decision.HOLD => Decision3.HOLD
  | Decision.ACT  => Decision3.ACT

def decision3 (m : Metrics) (theta : Rat) : Decision3 :=
  liftDecision (decision m theta)

theorem L11_3_no_block (m : Metrics) (theta : Rat) :
    Not (decision3 m theta = Decision3.BLOCK) := by
  intro h
  cases hd : decision m theta with
  | HOLD =>
      rw [show decision3 m theta = Decision3.HOLD by
        unfold decision3
        rw [hd]
        rfl] at h
      cases h
  | ACT =>
      rw [show decision3 m theta = Decision3.ACT by
        unfold decision3
        rw [hd]
        rfl] at h
      cases h

theorem L11_3_act (m : Metrics) (theta : Rat) (h : theta <= m.S) :
    decision3 m theta = Decision3.ACT := by
  unfold decision3 liftDecision
  have hd : decision m theta = Decision.ACT := G1_act_above_threshold m theta h
  simp [hd]

theorem L11_3_hold (m : Metrics) (theta : Rat) (h : Not (theta <= m.S)) :
    decision3 m theta = Decision3.HOLD := by
  unfold decision3 liftDecision
  have hd : decision m theta = Decision.HOLD := E2_no_act_below_threshold m theta h
  simp [hd]

theorem decision_not_both (m : Metrics) (theta : Rat) :
    Not ((decision m theta = Decision.ACT) /\ (decision m theta = Decision.HOLD)) := by
  intro h
  rcases h with ⟨h1, h2⟩
  rw [h1] at h2
  cases h2

end Obsidia
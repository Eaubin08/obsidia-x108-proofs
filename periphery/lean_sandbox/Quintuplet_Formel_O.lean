namespace Obsidia
namespace QuintupletFormel

structure ObsidiaQuintuplet where
  current_state : Nat
  transformed_state : Nat
  invariant_level : Nat
  tau : Nat
  lyapunov_before : Nat
  lyapunov_after : Nat

def phi (q : ObsidiaQuintuplet) : Nat :=
  q.transformed_state

def invariant_ok (q : ObsidiaQuintuplet) : Prop :=
  q.invariant_level <= q.lyapunov_before

def time_ok (q : ObsidiaQuintuplet) : Prop :=
  q.tau <= q.lyapunov_before

def dissipative (q : ObsidiaQuintuplet) : Prop :=
  q.lyapunov_after <= q.lyapunov_before

def admissible_quintuplet (q : ObsidiaQuintuplet) : Prop :=
  And (invariant_ok q) (And (time_ok q) (dissipative q))

def identity_quintuplet (current tau energy : Nat) : ObsidiaQuintuplet :=
  { current_state := current, transformed_state := current, invariant_level := 0, tau := tau, lyapunov_before := energy, lyapunov_after := energy }

theorem phi_reflects_transformed_state
    (q : ObsidiaQuintuplet) :
    phi q = q.transformed_state :=
  rfl

theorem invariant_ok_intro
    (q : ObsidiaQuintuplet)
    (h : q.invariant_level <= q.lyapunov_before) :
    invariant_ok q :=
  h

theorem time_ok_intro
    (q : ObsidiaQuintuplet)
    (h : q.tau <= q.lyapunov_before) :
    time_ok q :=
  h

theorem dissipative_intro
    (q : ObsidiaQuintuplet)
    (h : q.lyapunov_after <= q.lyapunov_before) :
    dissipative q :=
  h

theorem admissible_quintuplet_intro
    (q : ObsidiaQuintuplet)
    (hi : invariant_ok q)
    (ht : time_ok q)
    (hd : dissipative q) :
    admissible_quintuplet q :=
  And.intro hi (And.intro ht hd)

theorem invariant_from_admissible
    (q : ObsidiaQuintuplet)
    (h : admissible_quintuplet q) :
    invariant_ok q :=
  h.left

theorem time_from_admissible
    (q : ObsidiaQuintuplet)
    (h : admissible_quintuplet q) :
    time_ok q :=
  h.right.left

theorem dissipative_from_admissible
    (q : ObsidiaQuintuplet)
    (h : admissible_quintuplet q) :
    dissipative q :=
  h.right.right

theorem identity_quintuplet_phi_stable
    (current tau energy : Nat) :
    phi (identity_quintuplet current tau energy) = current :=
  rfl

theorem identity_quintuplet_dissipative
    (current tau energy : Nat) :
    dissipative (identity_quintuplet current tau energy) :=
  Nat.le_refl energy

end QuintupletFormel
end Obsidia

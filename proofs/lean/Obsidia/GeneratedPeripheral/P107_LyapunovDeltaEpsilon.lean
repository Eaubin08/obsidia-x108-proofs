namespace Obsidia
namespace P107_LyapunovDeltaEpsilon

structure LyapunovDeltaState where
  current : Nat
  next : Nat
  epsilon : Nat

def nonincreasing (s : LyapunovDeltaState) : Prop :=
  s.next <= s.current

def residual (s : LyapunovDeltaState) : Nat :=
  if s.next <= s.current then s.current - s.next else s.next - s.current

def delta_bounded_by_epsilon (s : LyapunovDeltaState) : Prop :=
  residual s <= s.epsilon

def lyapunov_delta_epsilon_admissible (s : LyapunovDeltaState) : Prop :=
  nonincreasing s ∧ delta_bounded_by_epsilon s

theorem lyapunov_delta_epsilon_admissible_intro
    (s : LyapunovDeltaState)
    (hn : nonincreasing s)
    (hb : delta_bounded_by_epsilon s) :
    lyapunov_delta_epsilon_admissible s :=
  And.intro hn hb

theorem nonincreasing_from_lyapunov_delta_epsilon
    (s : LyapunovDeltaState)
    (h : lyapunov_delta_epsilon_admissible s) :
    nonincreasing s :=
  h.left

theorem bounded_from_lyapunov_delta_epsilon
    (s : LyapunovDeltaState)
    (h : lyapunov_delta_epsilon_admissible s) :
    delta_bounded_by_epsilon s :=
  h.right

end P107_LyapunovDeltaEpsilon
end Obsidia

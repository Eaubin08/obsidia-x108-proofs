namespace Obsidia
namespace Lyapunov_L_Basic

structure LyapunovState where
  current : Nat
  next : Nat
  floor : Nat

def nonincreasing (s : LyapunovState) : Prop :=
  s.next <= s.current

def above_floor (s : LyapunovState) : Prop :=
  s.floor <= s.next

def lyapunov_basic_admissible (s : LyapunovState) : Prop :=
  nonincreasing s ∧ above_floor s

theorem lyapunov_basic_admissible_intro
    (s : LyapunovState)
    (hn : nonincreasing s)
    (hf : above_floor s) :
    lyapunov_basic_admissible s :=
  And.intro hn hf

theorem nonincreasing_from_lyapunov_basic
    (s : LyapunovState)
    (h : lyapunov_basic_admissible s) :
    nonincreasing s :=
  h.left

theorem above_floor_from_lyapunov_basic
    (s : LyapunovState)
    (h : lyapunov_basic_admissible s) :
    above_floor s :=
  h.right

end Lyapunov_L_Basic
end Obsidia

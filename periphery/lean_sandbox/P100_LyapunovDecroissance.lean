namespace Obsidia
namespace P100

structure LyapunovState where
current_energy : Nat
next_energy : Nat
tick : Nat

def lyapunov_non_increasing (s : LyapunovState) : Prop :=
s.next_energy <= s.current_energy

def stable_transition (s : LyapunovState) : Prop :=
lyapunov_non_increasing s

def same_or_lower (current next : Nat) : Prop :=
next <= current

def identity_transition (energy tick : Nat) : LyapunovState :=
{ current_energy := energy, next_energy := energy, tick := tick }

theorem stable_transition_intro
(s : LyapunovState)
(h : s.next_energy <= s.current_energy) :
stable_transition s :=
h

theorem lyapunov_from_stable_transition
(s : LyapunovState)
(h : stable_transition s) :
lyapunov_non_increasing s :=
h

theorem same_or_lower_intro
(current next : Nat)
(h : next <= current) :
same_or_lower current next :=
h

theorem identity_transition_stable
(energy tick : Nat) :
stable_transition (identity_transition energy tick) :=
Nat.le_refl energy

theorem stable_transition_preserves_bound
(s : LyapunovState)
(h : stable_transition s) :
s.next_energy <= s.current_energy :=
h

theorem non_increasing_is_same_or_lower
(s : LyapunovState)
(h : lyapunov_non_increasing s) :
same_or_lower s.current_energy s.next_energy :=
h

end P100
end Obsidia

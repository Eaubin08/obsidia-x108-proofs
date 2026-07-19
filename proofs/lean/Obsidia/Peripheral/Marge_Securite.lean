namespace Obsidia
namespace MargeSecurite

structure SecurityState where
  energy : Nat
  reserve : Nat
  coherence : Nat
  limit : Nat

def energy_within_margin (s : SecurityState) : Prop :=
  s.energy <= s.limit

def reserve_within_margin (s : SecurityState) : Prop :=
  s.reserve <= s.limit

def coherence_within_margin (s : SecurityState) : Prop :=
  s.coherence <= s.limit

def margin_safe (s : SecurityState) : Prop :=
  And (energy_within_margin s) (And (reserve_within_margin s) (coherence_within_margin s))

def boundary_state (limit : Nat) : SecurityState :=
  { energy := limit, reserve := limit, coherence := limit, limit := limit }

theorem margin_safe_intro
    (s : SecurityState)
    (he : energy_within_margin s)
    (hr : reserve_within_margin s)
    (hc : coherence_within_margin s) :
    margin_safe s :=
  And.intro he (And.intro hr hc)

theorem energy_margin_from_safe
    (s : SecurityState)
    (h : margin_safe s) :
    energy_within_margin s :=
  h.left

theorem reserve_margin_from_safe
    (s : SecurityState)
    (h : margin_safe s) :
    reserve_within_margin s :=
  h.right.left

theorem coherence_margin_from_safe
    (s : SecurityState)
    (h : margin_safe s) :
    coherence_within_margin s :=
  h.right.right

theorem boundary_state_energy_safe
    (limit : Nat) :
    energy_within_margin (boundary_state limit) :=
  Nat.le_refl limit

theorem boundary_state_reserve_safe
    (limit : Nat) :
    reserve_within_margin (boundary_state limit) :=
  Nat.le_refl limit

theorem boundary_state_coherence_safe
    (limit : Nat) :
    coherence_within_margin (boundary_state limit) :=
  Nat.le_refl limit

theorem boundary_state_margin_safe
    (limit : Nat) :
    margin_safe (boundary_state limit) :=
  And.intro (Nat.le_refl limit) (And.intro (Nat.le_refl limit) (Nat.le_refl limit))

end MargeSecurite
end Obsidia

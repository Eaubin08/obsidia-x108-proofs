namespace Obsidia
namespace Lean_Pack_P161

structure PackP161State where
  energy : Nat
  budget : Nat
  calibrated : Bool
  proof_ready : Bool

def energy_bounded (s : PackP161State) : Prop :=
  s.energy <= s.budget

def calibration_ok (s : PackP161State) : Prop :=
  s.calibrated = true

def proof_ready_ok (s : PackP161State) : Prop :=
  s.proof_ready = true

def p161_pack_admissible (s : PackP161State) : Prop :=
  energy_bounded s ∧ calibration_ok s ∧ proof_ready_ok s

theorem p161_pack_admissible_intro
    (s : PackP161State)
    (he : energy_bounded s)
    (hc : calibration_ok s)
    (hp : proof_ready_ok s) :
    p161_pack_admissible s :=
  And.intro he (And.intro hc hp)

theorem energy_bounded_from_p161_pack
    (s : PackP161State)
    (h : p161_pack_admissible s) :
    energy_bounded s :=
  h.left

theorem calibration_from_p161_pack
    (s : PackP161State)
    (h : p161_pack_admissible s) :
    calibration_ok s :=
  h.right.left

theorem proof_ready_from_p161_pack
    (s : PackP161State)
    (h : p161_pack_admissible s) :
    proof_ready_ok s :=
  h.right.right

end Lean_Pack_P161
end Obsidia

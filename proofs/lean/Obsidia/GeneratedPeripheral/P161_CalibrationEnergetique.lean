namespace Obsidia
namespace P161_CalibrationEnergetique

structure CalibrationState where
  energy : Nat
  budget : Nat
  loss : Nat
  calibrated : Bool

def energy_within_budget (s : CalibrationState) : Prop :=
  s.energy <= s.budget

def loss_accounted (s : CalibrationState) : Prop :=
  s.loss <= s.energy

def calibration_ready (s : CalibrationState) : Prop :=
  s.calibrated = true

def p161_calibration_admissible (s : CalibrationState) : Prop :=
  energy_within_budget s ∧ loss_accounted s ∧ calibration_ready s

theorem p161_calibration_admissible_intro
    (s : CalibrationState)
    (he : energy_within_budget s)
    (hl : loss_accounted s)
    (hc : calibration_ready s) :
    p161_calibration_admissible s :=
  And.intro he (And.intro hl hc)

theorem energy_within_budget_from_p161_calibration
    (s : CalibrationState)
    (h : p161_calibration_admissible s) :
    energy_within_budget s :=
  h.left

theorem loss_accounted_from_p161_calibration
    (s : CalibrationState)
    (h : p161_calibration_admissible s) :
    loss_accounted s :=
  h.right.left

theorem calibration_ready_from_p161_calibration
    (s : CalibrationState)
    (h : p161_calibration_admissible s) :
    calibration_ready s :=
  h.right.right

end P161_CalibrationEnergetique
end Obsidia

namespace Obsidia
namespace LOEG

inductive EmergencePhase where
  | friction
  | calibration
  | order
deriving DecidableEq

def next_phase (p : EmergencePhase) : EmergencePhase :=
  match p with
  | EmergencePhase.friction => EmergencePhase.calibration
  | EmergencePhase.calibration => EmergencePhase.order
  | EmergencePhase.order => EmergencePhase.friction

structure LOEGState where
  friction_present : Bool
  calibration_ready : Bool
  order_ready : Bool
  guidance_ready : Bool
  scope_admissible : Bool

def friction_ok (s : LOEGState) : Prop :=
  s.friction_present = true

def calibration_ok (s : LOEGState) : Prop :=
  s.calibration_ready = true

def order_ok (s : LOEGState) : Prop :=
  s.order_ready = true

def guidance_ok (s : LOEGState) : Prop :=
  s.guidance_ready = true

def scope_ok (s : LOEGState) : Prop :=
  s.scope_admissible = true

def loeg_guided_emergence_ready (s : LOEGState) : Prop :=
  And (friction_ok s)
    (And (calibration_ok s)
      (And (order_ok s)
        (And (guidance_ok s) (scope_ok s))))

def canonical_loeg_state : LOEGState :=
  { friction_present := true,
    calibration_ready := true,
    order_ready := true,
    guidance_ready := true,
    scope_admissible := true }

theorem next_after_friction :
    next_phase EmergencePhase.friction = EmergencePhase.calibration :=
  rfl

theorem next_after_calibration :
    next_phase EmergencePhase.calibration = EmergencePhase.order :=
  rfl

theorem next_after_order :
    next_phase EmergencePhase.order = EmergencePhase.friction :=
  rfl

theorem loeg_guided_emergence_ready_intro
    (s : LOEGState)
    (hf : friction_ok s)
    (hc : calibration_ok s)
    (ho : order_ok s)
    (hg : guidance_ok s)
    (hs : scope_ok s) :
    loeg_guided_emergence_ready s :=
  And.intro hf
    (And.intro hc
      (And.intro ho
        (And.intro hg hs)))

theorem friction_from_loeg_guided_emergence
    (s : LOEGState)
    (h : loeg_guided_emergence_ready s) :
    friction_ok s :=
  h.left

theorem calibration_from_loeg_guided_emergence
    (s : LOEGState)
    (h : loeg_guided_emergence_ready s) :
    calibration_ok s :=
  h.right.left

theorem order_from_loeg_guided_emergence
    (s : LOEGState)
    (h : loeg_guided_emergence_ready s) :
    order_ok s :=
  h.right.right.left

theorem guidance_from_loeg_guided_emergence
    (s : LOEGState)
    (h : loeg_guided_emergence_ready s) :
    guidance_ok s :=
  h.right.right.right.left

theorem scope_from_loeg_guided_emergence
    (s : LOEGState)
    (h : loeg_guided_emergence_ready s) :
    scope_ok s :=
  h.right.right.right.right

theorem canonical_friction_ok :
    friction_ok canonical_loeg_state :=
  rfl

theorem canonical_calibration_ok :
    calibration_ok canonical_loeg_state :=
  rfl

theorem canonical_order_ok :
    order_ok canonical_loeg_state :=
  rfl

theorem canonical_guidance_ok :
    guidance_ok canonical_loeg_state :=
  rfl

theorem canonical_scope_ok :
    scope_ok canonical_loeg_state :=
  rfl

theorem canonical_loeg_guided_emergence_ready :
    loeg_guided_emergence_ready canonical_loeg_state :=
  And.intro rfl
    (And.intro rfl
      (And.intro rfl
        (And.intro rfl rfl)))

end LOEG
end Obsidia

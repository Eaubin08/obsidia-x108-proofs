namespace Obsidia
namespace RC_AK

structure RCAKState where
  ethical_filter_passed : Bool
  informational_filter_passed : Bool
  drift_blocked : Bool
  flow_balanced : Bool

def rc_filter_ok (s : RCAKState) : Prop :=
  s.ethical_filter_passed = true

def ak_filter_ok (s : RCAKState) : Prop :=
  s.informational_filter_passed = true

def drift_is_blocked (s : RCAKState) : Prop :=
  s.drift_blocked = true

def flow_is_balanced (s : RCAKState) : Prop :=
  s.flow_balanced = true

def double_guard_ok (s : RCAKState) : Prop :=
  And (rc_filter_ok s) (ak_filter_ok s)

def rc_ak_filters_admissible (s : RCAKState) : Prop :=
  And (double_guard_ok s) (And (drift_is_blocked s) (flow_is_balanced s))

def canonical_rc_ak_state : RCAKState :=
  { ethical_filter_passed := true,
    informational_filter_passed := true,
    drift_blocked := true,
    flow_balanced := true }

theorem double_guard_ok_intro
    (s : RCAKState)
    (hr : rc_filter_ok s)
    (ha : ak_filter_ok s) :
    double_guard_ok s :=
  And.intro hr ha

theorem rc_ak_filters_admissible_intro
    (s : RCAKState)
    (hg : double_guard_ok s)
    (hd : drift_is_blocked s)
    (hf : flow_is_balanced s) :
    rc_ak_filters_admissible s :=
  And.intro hg (And.intro hd hf)

theorem rc_from_double_guard
    (s : RCAKState)
    (h : double_guard_ok s) :
    rc_filter_ok s :=
  h.left

theorem ak_from_double_guard
    (s : RCAKState)
    (h : double_guard_ok s) :
    ak_filter_ok s :=
  h.right

theorem double_guard_from_rc_ak_filters
    (s : RCAKState)
    (h : rc_ak_filters_admissible s) :
    double_guard_ok s :=
  h.left

theorem drift_blocked_from_rc_ak_filters
    (s : RCAKState)
    (h : rc_ak_filters_admissible s) :
    drift_is_blocked s :=
  h.right.left

theorem flow_balanced_from_rc_ak_filters
    (s : RCAKState)
    (h : rc_ak_filters_admissible s) :
    flow_is_balanced s :=
  h.right.right

theorem rc_from_rc_ak_filters
    (s : RCAKState)
    (h : rc_ak_filters_admissible s) :
    rc_filter_ok s :=
  h.left.left

theorem ak_from_rc_ak_filters
    (s : RCAKState)
    (h : rc_ak_filters_admissible s) :
    ak_filter_ok s :=
  h.left.right

theorem canonical_rc_filter_ok :
    rc_filter_ok canonical_rc_ak_state :=
  rfl

theorem canonical_ak_filter_ok :
    ak_filter_ok canonical_rc_ak_state :=
  rfl

theorem canonical_drift_is_blocked :
    drift_is_blocked canonical_rc_ak_state :=
  rfl

theorem canonical_flow_is_balanced :
    flow_is_balanced canonical_rc_ak_state :=
  rfl

theorem canonical_double_guard_ok :
    double_guard_ok canonical_rc_ak_state :=
  And.intro rfl rfl

theorem canonical_rc_ak_filters_admissible :
    rc_ak_filters_admissible canonical_rc_ak_state :=
  And.intro canonical_double_guard_ok (And.intro rfl rfl)

end RC_AK
end Obsidia

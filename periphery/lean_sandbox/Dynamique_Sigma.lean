namespace Obsidia
namespace Dynamique_Sigma

structure SigmaState where
  alert : Bool
  frozen : Bool
  report_ready : Bool
  decision_authority : Bool

def sigma_alerts (s : SigmaState) : Prop :=
  s.alert = true

def sigma_freezes (s : SigmaState) : Prop :=
  s.frozen = true

def sigma_reports (s : SigmaState) : Prop :=
  s.report_ready = true

def sigma_non_sovereign (s : SigmaState) : Prop :=
  s.decision_authority = false

def sigma_admissible (s : SigmaState) : Prop :=
  sigma_alerts s ∧ sigma_freezes s ∧ sigma_reports s ∧ sigma_non_sovereign s

theorem sigma_admissible_intro
    (s : SigmaState)
    (ha : sigma_alerts s)
    (hf : sigma_freezes s)
    (hr : sigma_reports s)
    (hn : sigma_non_sovereign s) :
    sigma_admissible s :=
  And.intro ha (And.intro hf (And.intro hr hn))

theorem alert_from_sigma_admissible
    (s : SigmaState)
    (h : sigma_admissible s) :
    sigma_alerts s :=
  h.left

theorem freeze_from_sigma_admissible
    (s : SigmaState)
    (h : sigma_admissible s) :
    sigma_freezes s :=
  h.right.left

theorem report_from_sigma_admissible
    (s : SigmaState)
    (h : sigma_admissible s) :
    sigma_reports s :=
  h.right.right.left

theorem non_sovereign_from_sigma_admissible
    (s : SigmaState)
    (h : sigma_admissible s) :
    sigma_non_sovereign s :=
  h.right.right.right

end Dynamique_Sigma
end Obsidia

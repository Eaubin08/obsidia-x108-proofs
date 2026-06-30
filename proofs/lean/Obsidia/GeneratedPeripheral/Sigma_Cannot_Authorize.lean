namespace Obsidia
namespace Sigma_Cannot_Authorize

structure SigmaState where
alert : Bool
frozen : Bool
report_ready : Bool
can_authorize_act : Bool

def sigma_observes (s : SigmaState) : Prop :=
s.alert = true ∨ s.frozen = true ∨ s.report_ready = true

def sigma_cannot_authorize (s : SigmaState) : Prop :=
s.can_authorize_act = false

def sigma_non_sovereign (s : SigmaState) : Prop :=
sigma_observes s ∧ sigma_cannot_authorize s

theorem sigma_non_sovereign_intro
(s : SigmaState)
(ho : sigma_observes s)
(hn : sigma_cannot_authorize s) :
sigma_non_sovereign s :=
And.intro ho hn

theorem cannot_authorize_from_sigma_non_sovereign
(s : SigmaState)
(h : sigma_non_sovereign s) :
sigma_cannot_authorize s :=
h.right

theorem observes_from_sigma_non_sovereign
(s : SigmaState)
(h : sigma_non_sovereign s) :
sigma_observes s :=
h.left

theorem sigma_authorization_is_false
(s : SigmaState)
(h : sigma_non_sovereign s) :
s.can_authorize_act = false :=
h.right

end Sigma_Cannot_Authorize
end Obsidia

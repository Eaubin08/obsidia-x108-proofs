namespace Obsidia
namespace P_DomainKernel_EntropyRisk_RequiresHold

structure DomainKernelState where
  entropy_risk  : Bool
  hold_required : Bool

def entropyRiskRequiresHold (s : DomainKernelState) : Prop :=
  s.entropy_risk = true → s.hold_required = true

theorem P_DomainKernel_EntropyRisk_RequiresHold
    (s : DomainKernelState)
    (h : entropyRiskRequiresHold s)
    (hr : s.entropy_risk = true) :
    s.hold_required = true := by
  exact h hr

end P_DomainKernel_EntropyRisk_RequiresHold
end Obsidia

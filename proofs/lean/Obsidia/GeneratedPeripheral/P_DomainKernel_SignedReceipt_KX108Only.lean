namespace Obsidia
namespace P_DomainKernel_SignedReceipt_KX108Only

structure DomainKernelState where
  signed_decision_receipt : Bool
  kx108_only              : Bool

def signedReceiptKX108Only (s : DomainKernelState) : Prop :=
  s.signed_decision_receipt = true → s.kx108_only = true

theorem P_DomainKernel_SignedReceipt_KX108Only
    (s : DomainKernelState)
    (h : signedReceiptKX108Only s)
    (hs : s.signed_decision_receipt = true) :
    s.kx108_only = true := by
  exact h hs

end P_DomainKernel_SignedReceipt_KX108Only
end Obsidia

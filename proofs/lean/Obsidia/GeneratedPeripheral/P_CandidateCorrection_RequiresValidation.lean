namespace Obsidia
namespace P_CandidateCorrection_RequiresValidation

structure CandidateCorrectionState where
  correction_candidate : Bool
  validation_required  : Bool

def candidateCorrectionRequiresValidation (s : CandidateCorrectionState) : Prop :=
  s.correction_candidate = true → s.validation_required = true

theorem P_CandidateCorrection_RequiresValidation
    (s : CandidateCorrectionState)
    (h : candidateCorrectionRequiresValidation s)
    (hc : s.correction_candidate = true) :
    s.validation_required = true := by
  exact h hc

end P_CandidateCorrection_RequiresValidation
end Obsidia

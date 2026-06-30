structure CognitiveState where
  deterministic_rule_found : Bool
  cognitive_processing_active : Bool

def apply_pre_cognitive_filter (s : CognitiveState) : CognitiveState :=
  if s.deterministic_rule_found == true then
    { s with cognitive_processing_active := false }
  else
    s

theorem lean_theorem_pre_cognitive_elimination (s : CognitiveState) (h : s.deterministic_rule_found = true) : (apply_pre_cognitive_filter s).cognitive_processing_active = false := by
  unfold apply_pre_cognitive_filter
  simp [h]

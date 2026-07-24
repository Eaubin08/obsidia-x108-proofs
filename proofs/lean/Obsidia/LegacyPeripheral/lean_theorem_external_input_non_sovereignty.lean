structure ExternalInput where
  payload_size : Nat
  native_authority : Nat

def sanitize_input (e : ExternalInput) : ExternalInput :=
  { e with native_authority := 0 }

theorem lean_theorem_external_input_non_sovereignty (e : ExternalInput) : (sanitize_input e).native_authority = 0 := by
  unfold sanitize_input
  rfl

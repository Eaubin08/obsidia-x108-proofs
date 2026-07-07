import pathlib
import subprocess

theorems = {
    "lean_theorem_faithful_path_existence.lean": """structure Route where
  source_verified : Bool
  target_locked : Bool
  is_faithful : Bool

def establish_path (r : Route) : Route :=
  if r.source_verified == true && r.target_locked == true then
    { r with is_faithful := true }
  else
    { r with is_faithful := false }

theorem lean_theorem_faithful_path_existence (r : Route) (h1 : r.source_verified = true) (h2 : r.target_locked = true) : (establish_path r).is_faithful = true := by
  unfold establish_path
  simp [h1, h2]

#check lean_theorem_faithful_path_existence""",

    "lean_theorem_pre_cognitive_elimination.lean": """structure CognitiveState where
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

#check lean_theorem_pre_cognitive_elimination""",

    "lean_theorem_memory_non_sovereignty.lean": """structure MemoryState where
  is_readonly : Bool
  decision_authority : Nat

def enforce_boundary (m : MemoryState) : MemoryState :=
  if m.is_readonly then 
    { m with decision_authority := 0 } 
  else 
    m

theorem lean_theorem_memory_non_sovereignty (m : MemoryState) (h : m.is_readonly = true) : (enforce_boundary m).decision_authority = 0 := by
  unfold enforce_boundary
  simp [h]

#check lean_theorem_memory_non_sovereignty""",

    "lean_theorem_hold_preservation.lean": """structure ActionState where
  is_hold : Bool
  can_act : Bool

def apply_hold_policy (s : ActionState) : ActionState :=
  if s.is_hold then
    { s with can_act := false }
  else
    s

theorem lean_theorem_hold_preservation (s : ActionState) (h : s.is_hold = true) : (apply_hold_policy s).can_act = false := by
  unfold apply_hold_policy
  simp [h]

#check lean_theorem_hold_preservation""",

    "lean_theorem_stability_before_action.lean": """structure SystemState where
  contradictions : Nat
  can_act : Bool

def enforce_stability (s : SystemState) : SystemState :=
  if s.contradictions > 0 then
    { s with can_act := false }
  else
    s

theorem lean_theorem_stability_before_action (s : SystemState) (h : s.contradictions > 0) : (enforce_stability s).can_act = false := by
  unfold enforce_stability
  simp [h]

#check lean_theorem_stability_before_action""",

    "lean_theorem_order_error_prevention.lean": """structure ProcessState where
  is_qualified : Bool
  execute_action : Bool

def enforce_order (s : ProcessState) : ProcessState :=
  if s.is_qualified == false then
    { s with execute_action := false }
  else
    s

theorem lean_theorem_order_error_prevention (s : ProcessState) (h : s.is_qualified = false) : (enforce_order s).execute_action = false := by
  unfold enforce_order
  simp [h]

#check lean_theorem_order_error_prevention""",

    "lean_theorem_external_input_non_sovereignty.lean": """structure ExternalInput where
  payload_size : Nat
  native_authority : Nat

def sanitize_input (e : ExternalInput) : ExternalInput :=
  { e with native_authority := 0 }

theorem lean_theorem_external_input_non_sovereignty (e : ExternalInput) : (sanitize_input e).native_authority = 0 := by
  unfold sanitize_input
  rfl

#check lean_theorem_external_input_non_sovereignty"""
}

out_dir = pathlib.Path("proofs/lean/peripheral")
out_dir.mkdir(parents=True, exist_ok=True)

print("\n🚀 DÉMARRAGE DE LA VÉRIFICATION TERMINAL ABSOLUE (PALIER P4)...")
print("="*60)

for filename, code in theorems.items():
    file_path = out_dir / filename
    file_path.write_text(code, encoding="utf-8")
    
    print(f"➤ Test Lean 4 sur : {filename}")
    res = subprocess.run(["lake", "env", "lean", str(file_path)], capture_output=True, text=True)
    
    if res.returncode == 0:
        print("   ✅ BUILD SUCCESS")
        if res.stdout.strip():
            print(f"   {res.stdout.strip()}")
        if res.stderr.strip():
            print(f"   {res.stderr.strip()}")
    else:
        print("   ❌ BUILD FAILED")
        print(f"   {res.stderr.strip()}")
    print("-" * 60)

print("🏆 TOUS LES TESTS SONT TERMINÉS.")

namespace Obsidia
namespace P36

structure DomainState where
  state_id : Nat
  coherence : Nat
  tension : Nat
  level : Nat
  clock : Nat

def score_valid (d : DomainState) : Prop :=
  d.coherence <= d.level

def time_ready (d : DomainState) : Prop :=
  d.clock <= d.level

def domain_admissible (d : DomainState) : Prop :=
  And (score_valid d) (time_ready d)

def step (d : DomainState) : DomainState :=
  { d with clock := d.clock + 1 }

def canonical_fields_reflexive (d : DomainState) : Prop :=
  And (d.state_id = d.state_id)
    (And (d.coherence = d.coherence)
      (And (d.tension = d.tension)
        (And (d.level = d.level)
          (d.clock = d.clock))))

theorem domain_admissible_intro
    (d : DomainState)
    (hs : score_valid d)
    (ht : time_ready d) :
    domain_admissible d := by
  exact And.intro hs ht

theorem score_valid_from_domain_admissible
    (d : DomainState)
    (h : domain_admissible d) :
    score_valid d := by
  exact h.left

theorem time_ready_from_domain_admissible
    (d : DomainState)
    (h : domain_admissible d) :
    time_ready d := by
  exact h.right

theorem step_preserves_state_id
    (d : DomainState) :
    (step d).state_id = d.state_id := by
  rfl

theorem canonical_quintuplet_fields_reflexive
    (d : DomainState) :
    canonical_fields_reflexive d := by
  exact And.intro rfl
    (And.intro rfl
      (And.intro rfl
        (And.intro rfl rfl)))

end P36
end Obsidia

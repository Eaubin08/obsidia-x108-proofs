namespace Obsidia
namespace P37Domaine

structure DomainEntry where
  admitted      : Bool
  valid_context : Bool

def domain_admissible (d : DomainEntry) : Prop :=
  d.admitted = true ∧ d.valid_context = true

def domain_hold (d : DomainEntry) : Prop := ¬ domain_admissible d

def canonical_entry : DomainEntry := { admitted := true, valid_context := true }

theorem canonical_admissible : domain_admissible canonical_entry := ⟨rfl, rfl⟩

theorem not_admitted_implies_hold (d : DomainEntry) (h : d.admitted = false) :
    domain_hold d := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem invalid_context_implies_hold (d : DomainEntry) (h : d.valid_context = false) :
    domain_hold d := by
  intro hv; have hc := hv.2; simp [h] at hc

end P37Domaine
end Obsidia

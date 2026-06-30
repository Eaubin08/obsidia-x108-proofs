namespace Obsidia
namespace P60AutoOrganisation

structure OrgState where
  kernel_cycles : Nat
  organised     : Bool

def auto_organised (o : OrgState) : Prop :=
  0 < o.kernel_cycles

def org_hold (o : OrgState) : Prop := ¬ auto_organised o

def canonical_org : OrgState := { kernel_cycles := 1, organised := true }

theorem canonical_auto_organised : auto_organised canonical_org := Nat.zero_lt_succ 0

theorem zero_cycles_hold (o : OrgState) (h : o.kernel_cycles = 0) :
    org_hold o := by
  intro hv; simp [auto_organised, h] at hv

theorem cycles_implies_organised (o : OrgState) (h : 0 < o.kernel_cycles) :
    auto_organised o := h

end P60AutoOrganisation
end Obsidia

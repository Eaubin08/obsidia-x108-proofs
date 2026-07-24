namespace Obsidia
namespace P100LyapunovDecroissance

def L_candidate (v c : Nat) : Nat := v + c

def L_decreasing (v1 c1 v2 c2 : Nat) : Prop :=
  L_candidate v2 c2 ≤ L_candidate v1 c1

theorem L_reflexive (v c : Nat) : L_decreasing v c v c :=
  Nat.le_refl _

theorem L_decreasing_trans (v1 c1 v2 c2 v3 c3 : Nat)
    (h1 : L_decreasing v1 c1 v2 c2) (h2 : L_decreasing v2 c2 v3 c3) :
    L_decreasing v1 c1 v3 c3 :=
  Nat.le_trans h2 h1

theorem reduce_value_decreasing (v1 v2 c : Nat) (h : v2 ≤ v1) :
    L_decreasing v1 c v2 c := by
  unfold L_decreasing L_candidate; omega

end P100LyapunovDecroissance
end Obsidia

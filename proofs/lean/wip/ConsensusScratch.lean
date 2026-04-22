import Obsidia.Consensus

namespace Obsidia

theorem fold_count_succ
  (d : Decision3) (xs : List Decision3) (n : Nat) :
  List.foldl (fun acc y => if y = d then acc + 1 else acc) (n + 1) xs =
    List.foldl (fun acc y => if y = d then acc + 1 else acc) n xs + 1 := by
  induction xs generalizing n with
  | nil =>
      rfl
  | cons x xs ih =>
      by_cases h : x = d
      · rw [List.foldl, if_pos h, List.foldl, if_pos h]
        exact ih (n + 1)
      · rw [List.foldl, if_neg h, List.foldl, if_neg h]
        exact ih n

theorem countDec_cons_same (d : Decision3) (xs : List Decision3) :
  countDec d (d :: xs) = countDec d xs + 1 := by
  unfold countDec
  rw [List.foldl]
  rw [if_pos rfl]
  exact fold_count_succ d xs 0

end Obsidia

#print axioms Obsidia.fold_count_succ
#print axioms Obsidia.countDec_cons_same
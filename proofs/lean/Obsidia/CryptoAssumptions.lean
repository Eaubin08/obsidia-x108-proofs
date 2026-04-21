namespace Obsidia

inductive Hash where
  | leaf : Nat -> Hash
  | node : Hash -> Hash -> Hash
  deriving Repr, DecidableEq

def H (a b : Hash) : Hash :=
  Hash.node a b

theorem H_injective_left
  {a b c : Hash} (h : H a b = H c b) : a = c := by
  unfold H at h
  cases h
  rfl

theorem H_injective_right
  {a b c : Hash} (h : H a b = H a c) : b = c := by
  unfold H at h
  cases h
  rfl

def neutralHash : Hash :=
  Hash.leaf 0

def decodeFold : Hash -> Option (List Hash)
  | Hash.leaf 0 => some []
  | Hash.leaf _ => none
  | Hash.node left right =>
      match decodeFold left with
      | some xs => some (xs ++ [right])
      | none => none

theorem decodeFold_H_of_decodable
    (acc x : Hash) (prefList : List Hash)
    (hdec : decodeFold acc = some prefList) :
    decodeFold (H acc x) = some (prefList ++ [x]) := by
  unfold H decodeFold
  rw [hdec]

theorem append_nil_local {α : Type} : ∀ (xs : List α), xs ++ [] = xs := by
  intro xs
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      show x :: (xs ++ []) = x :: xs
      rw [ih]

theorem append_assoc_local {α : Type} :
    ∀ (xs ys zs : List α), (xs ++ ys) ++ zs = xs ++ (ys ++ zs) := by
  intro xs ys zs
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      show x :: ((xs ++ ys) ++ zs) = x :: (xs ++ (ys ++ zs))
      rw [ih]

theorem decodeFold_foldl_of_decodable :
    forall (xs : List Hash) (acc : Hash) (prefList : List Hash),
      decodeFold acc = some prefList ->
      decodeFold (List.foldl H acc xs) = some (prefList ++ xs) := by
  intro xs
  induction xs with
  | nil =>
      intro acc prefList hdec
      rw [List.foldl]
      rw [append_nil_local]
      exact hdec
  | cons x xs ih =>
      intro acc prefList hdec
      have hstep : decodeFold (H acc x) = some (prefList ++ [x]) := by
        exact decodeFold_H_of_decodable acc x prefList hdec
      have hrec :
          decodeFold (List.foldl H (H acc x) xs) = some ((prefList ++ [x]) ++ xs) := by
        exact ih (H acc x) (prefList ++ [x]) hstep
      rw [List.foldl]
      have hs : some ((prefList ++ [x]) ++ xs) = some (prefList ++ x :: xs) := by
        apply congrArg some
        rw [append_assoc_local]
        rfl
      exact Eq.trans hrec hs

theorem decodeFold_foldl_neutral (xs : List Hash) :
    decodeFold (List.foldl H neutralHash xs) = some xs := by
  have h0 : decodeFold neutralHash = some [] := by
    rfl
  have h := decodeFold_foldl_of_decodable xs neutralHash [] h0
  rw [List.nil_append] at h
  exact h

theorem foldl_H_injective
    (xs ys : List Hash)
    (h : List.foldl H neutralHash xs = List.foldl H neutralHash ys) :
    xs = ys := by
  have hx : decodeFold (List.foldl H neutralHash xs) = some xs := by
    exact decodeFold_foldl_neutral xs
  have hy : decodeFold (List.foldl H neutralHash ys) = some ys := by
    exact decodeFold_foldl_neutral ys
  have hdec : some xs = some ys := by
    exact Eq.trans (Eq.symm hx) (Eq.trans (congrArg decodeFold h) hy)
  exact Option.some.inj hdec

end Obsidia

namespace Obsidia.SealAssumptions

open Obsidia

abbrev File := Nat

def fileHash (f : File) : Obsidia.Hash :=
  Obsidia.Hash.leaf f

theorem fileHash_inj (f g : File) (h : fileHash f = fileHash g) : f = g := by
  unfold fileHash at h
  cases h
  rfl

def combine (xs : List Obsidia.Hash) : Obsidia.Hash :=
  xs.foldl Obsidia.H Obsidia.neutralHash

theorem combine_inj (xs ys : List Obsidia.Hash) (h : combine xs = combine ys) : xs = ys := by
  unfold combine at h
  exact Obsidia.foldl_H_injective xs ys h

end Obsidia.SealAssumptions
#print axioms Obsidia.append_nil_local
#print axioms Obsidia.append_assoc_local
#print axioms Obsidia.decodeFold_H_of_decodable
#print axioms Obsidia.decodeFold_foldl_of_decodable
#print axioms Obsidia.decodeFold_foldl_neutral
#print axioms Obsidia.foldl_H_injective
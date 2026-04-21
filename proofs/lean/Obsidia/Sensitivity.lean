import Obsidia.Merkle
import Obsidia.CryptoAssumptions

namespace Obsidia.Sensitivity

structure Repo where
  leaves : List Obsidia.Hash

def updateFile (i : Nat) (h : Obsidia.Hash) (r : Repo) : Repo :=
  { leaves := r.leaves.set i h }

def merkleRoot (r : Repo) : Obsidia.Hash :=
  r.leaves.foldl Obsidia.H Obsidia.neutralHash

def globalSeal (manifest root : Obsidia.Hash) : Obsidia.Hash :=
  Obsidia.merkle2 manifest root

theorem merkleRoot_change_if_leaf_change
    (r r' : Repo)
    (h : r.leaves ≠ r'.leaves) :
    merkleRoot r ≠ merkleRoot r' := by
  unfold merkleRoot
  intro heq
  apply h
  exact Obsidia.foldl_H_injective r.leaves r'.leaves heq

theorem globalSeal_change_if_root_change
    (manifest root root' : Obsidia.Hash)
    (h : root ≠ root') :
    globalSeal manifest root ≠ globalSeal manifest root' := by
  unfold globalSeal
  exact Obsidia.merkle2_right_mutation manifest root root' h

theorem P15_Immutability_Strong
    (manifest : Obsidia.Hash)
    (repo repo' : Repo)
    (h : repo ≠ repo') :
    globalSeal manifest (merkleRoot repo)
    ≠
    globalSeal manifest (merkleRoot repo') := by

  have hleaves : repo.leaves ≠ repo'.leaves := by
    intro hleaves_eq
    apply h
    cases repo
    cases repo'
    cases hleaves_eq
    rfl

  have hroot : merkleRoot repo ≠ merkleRoot repo' :=
    merkleRoot_change_if_leaf_change repo repo' hleaves

  exact globalSeal_change_if_root_change
    manifest
    (merkleRoot repo)
    (merkleRoot repo')
    hroot

end Obsidia.Sensitivity
#print axioms Obsidia.Sensitivity.merkleRoot_change_if_leaf_change
#print axioms Obsidia.Sensitivity.P15_Immutability_Strong

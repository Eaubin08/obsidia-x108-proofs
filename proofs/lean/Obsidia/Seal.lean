import Obsidia.Merkle
import Obsidia.CryptoAssumptions

namespace Obsidia.Seal

abbrev File := Obsidia.SealAssumptions.File

def rootHash (files : List File) : Obsidia.Hash :=
  Obsidia.SealAssumptions.combine (files.map Obsidia.SealAssumptions.fileHash)

def globalSeal (mHash rHash : Obsidia.Hash) : Obsidia.Hash :=
  Obsidia.merkle2 mHash rHash

theorem P13_Immutability
    (manifest : Obsidia.Hash) (files files2 : List File)
    (hmap : Not (files.map Obsidia.SealAssumptions.fileHash =
                 files2.map Obsidia.SealAssumptions.fileHash)) :
    Not (globalSeal manifest (rootHash files) =
         globalSeal manifest (rootHash files2)) := by
  have hroot : rootHash files ≠ rootHash files2 := by
    unfold rootHash
    intro heq
    apply hmap
    exact Obsidia.SealAssumptions.combine_inj _ _ heq
  unfold globalSeal
  exact Obsidia.merkle2_right_mutation manifest (rootHash files) (rootHash files2) hroot

end Obsidia.Seal
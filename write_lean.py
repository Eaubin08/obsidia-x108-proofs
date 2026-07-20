import pathlib

lean_code = """structure DomainState where
  risk_score : Nat
  contradictions : Nat

def L (s : DomainState) : Nat :=
  s.risk_score + s.contradictions

def Phi (s : DomainState) : DomainState :=
  if s.contradictions > 0 then
    { s with risk_score := 0, contradictions := 0 }
  else
    s

theorem P36 (s : DomainState) : L (Phi s) <= L s := by
  unfold Phi
  split
  · unfold L; omega
  · omega

#check P36
"""

file_path = pathlib.Path("proofs/lean/peripheral/P36.lean")
file_path.write_text(lean_code, encoding="utf-8")
print("✅ Fichier P36.lean écrit avec succès en UTF-8 pur !")

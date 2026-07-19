-- Chantier_M5_Table_Theoremes -- Table des Theoremes Cibles (Liste, Pas Preuves)
-- Status : PROVISIONAL scaffold -- Palier 4 (CHANTIER META)
-- SOURCE_COVERAGE: table_theoremes | M5 | stabilite | impossibilite | garantie
--                  enonces_cibles | chantier_meta | lean_candidat
--                  bibliotheque_theoremes | theoreme_documente
-- PROVISIONAL_BOUNDARY: table V0 <= 10 enonces cibles, pas leurs preuves.
--   M5 = inventaire des proprietes qu'Obsidia devrait satisfaire une fois formalisee.
--   Types : stabilite (Sigma bornee), impossibilite (pas de reponse magique), garantie.
--   Sans cette liste, on prouve n'importe quoi — M5 ferme le perimetre.

namespace Obsidia
namespace ChantierM5TableTheoremes

inductive TheoType
  | stabilite
  | impossibilite
  | garantie

structure TheoEntry where
  thtype        : TheoType
  chantier_ref  : Nat
  lean_candidate : Bool

def theoreme_documente (e : TheoEntry) : Prop :=
  e.lean_candidate = true

def is_stabilite (e : TheoEntry) : Prop :=
  e.thtype = TheoType.stabilite

def table_valide (entries : List TheoEntry) : Prop :=
  entries.length <= 10 /\ entries.length > 0

def canonical_stabilite : TheoEntry :=
  { thtype := TheoType.stabilite, chantier_ref := 1, lean_candidate := true }

def canonical_impossiblite : TheoEntry :=
  { thtype := TheoType.impossibilite, chantier_ref := 2, lean_candidate := true }

def canonical_garantie : TheoEntry :=
  { thtype := TheoType.garantie, chantier_ref := 3, lean_candidate := false }

def table_v0 : List TheoEntry :=
  [canonical_stabilite, canonical_impossiblite, canonical_garantie]

theorem canonical_stabilite_documente : theoreme_documente canonical_stabilite := rfl

theorem table_v0_valide : table_valide table_v0 := by
  simp [table_valide, table_v0]

theorem canonical_stabilite_type : is_stabilite canonical_stabilite := rfl

end ChantierM5TableTheoremes
end Obsidia

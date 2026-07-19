-- Silencieur_Semantique -- Detecteur de Non-Dits
-- Status : PROVISIONAL scaffold -- Palier 3
-- SOURCE_COVERAGE: silencieur | non_dits | sous_entendus | omissions | ltcu_plus
--                  implicite_critique | polarite_yin | filtre_conscience
--                  detection_implicite | clarification_recommandee
-- PROVISIONAL_BOUNDARY: detection reelle des non-dits non prouvee formellement.
--   Module actif du LTCU+ polarite Yin.
--   Output : {non_dits, sous_entendus, omissions, implicite_critique}.
--   Lien Loi_Traitement_Implicite : toute reponse passe par le Silencieur.

namespace Obsidia
namespace SilencieurSemantique

structure SilenceurOutput where
  non_dits_count      : Nat
  sous_entendus_count : Nat
  omissions_count     : Nat
  implicite_critique  : Bool

def has_implicite (s : SilenceurOutput) : Prop :=
  s.non_dits_count > 0 \/ s.sous_entendus_count > 0 \/ s.omissions_count > 0

def clarification_needed (s : SilenceurOutput) : Prop :=
  s.implicite_critique = true

def message_propre (s : SilenceurOutput) : Prop :=
  Not (has_implicite s) /\ s.implicite_critique = false

def canonical_alerte : SilenceurOutput :=
  { non_dits_count := 2, sous_entendus_count := 1,
    omissions_count := 0, implicite_critique := true }

def canonical_propre : SilenceurOutput :=
  { non_dits_count := 0, sous_entendus_count := 0,
    omissions_count := 0, implicite_critique := false }

theorem canonical_alerte_has_implicite : has_implicite canonical_alerte :=
  Or.inl (by simp [canonical_alerte])

theorem canonical_alerte_needs_clarif : clarification_needed canonical_alerte := rfl

theorem canonical_propre_clean : message_propre canonical_propre := by
  constructor
  . intro h
    simp [has_implicite, canonical_propre] at h
  . rfl

end SilencieurSemantique
end Obsidia

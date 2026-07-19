-- Mode_JSA -- Juste Savoir et Aider (Aide Proactive Contextualisee)
-- Status : PROVISIONAL scaffold -- Palier 4
-- SOURCE_COVERAGE: mode_jsa | juste_savoir_aider | consentement_utilisateur
--                  aide_proactive | observation_contexte | jsa_trigger
--                  copilote | console_vivante | filtre_avdr_light
-- PROVISIONAL_BOUNDARY: observation contexte et JSA_trigger non prouves formellement.
--   Actif ssi consentement_utilisateur = True.
--   Observation : contexte = {fenetre_active, inactivite, session_active}.
--   Aide validee par AVDR_Light avant proposition.

namespace Obsidia
namespace ModeJSA

structure JSAContext where
  consentement      : Bool
  contexte_observe  : Bool
  aide_candidate    : Bool
  validee_avdr      : Bool

def jsa_active (c : JSAContext) : Prop :=
  c.consentement = true

def aide_autorisee (c : JSAContext) : Prop :=
  jsa_active c /\ c.aide_candidate = true /\ c.validee_avdr = true

def no_intrusion (c : JSAContext) : Prop :=
  Not (jsa_active c) \/ c.aide_candidate = false

def canonical_active : JSAContext :=
  { consentement := true, contexte_observe := true,
    aide_candidate := true, validee_avdr := true }

def canonical_inactive : JSAContext :=
  { consentement := false, contexte_observe := false,
    aide_candidate := false, validee_avdr := false }

theorem canonical_active_jsa : jsa_active canonical_active := rfl

theorem canonical_active_aide : aide_autorisee canonical_active :=
  And.intro rfl (And.intro rfl rfl)

theorem canonical_inactive_no_intrusion : no_intrusion canonical_inactive :=
  Or.inl (by simp [canonical_inactive, jsa_active])

end ModeJSA
end Obsidia

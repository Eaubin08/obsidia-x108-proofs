namespace Obsidia
namespace LangageTotalObsidien

-- Langage Total Obsidien
-- Type: concept — peripherique, non-decisionnel, runtime_bound=false

structure LangageTotalObsidienState where
  coherent : Bool

def langagetotalobsidien_coherent (s : LangageTotalObsidienState) : Prop :=
  s.coherent = true

def langagetotalobsidien_hold (s : LangageTotalObsidienState) : Prop := ¬ langagetotalobsidien_coherent s

theorem not_coherent_hold (s : LangageTotalObsidienState) (h : s.coherent = false) :
    langagetotalobsidien_hold s := by
  intro hc; simp [langagetotalobsidien_coherent, h] at hc

theorem coherent_not_hold (s : LangageTotalObsidienState) (h : langagetotalobsidien_coherent s) :
    ¬ langagetotalobsidien_hold s := fun nh => nh h

end LangageTotalObsidien
end Obsidia

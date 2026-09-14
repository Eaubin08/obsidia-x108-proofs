/-
  Obsidia / NavierStokes / AntiPumpingSpecs.lean
  ==============================================
  NS STAGE A — SPECIFICATIONS / OPEN OBLIGATIONS.

  Ce fichier ENONCE les obligations.
  Il ne les prouve pas.

  Statut du verrou central :
    NS_ANTI_PUMPING = BLOCKED

  Les trois obligations analytiques ouvertes sont :
    LH
    HL
    HH

  Aucune de ces bornes n'est introduite comme axiome.
-/

import Obsidia.NavierStokes.Definitions

namespace Obsidia.NavierStokes.Specs

open Obsidia.NavierStokes

/-- Preconditions physiques/scalaires minimales. -/
def StateAdmissibleSpec (s : AntiPumpingState) : Prop :=
  0 < s.nu ∧
  0 ≤ s.EHigh ∧
  0 ≤ s.DHigh

/--
Identite de decomposition du flux.

Dans la future couche analytique, cette egalite devra provenir
de la decomposition dyadique/Bony et non d'une hypothese arbitraire.
-/
def FluxDecompositionSpec (s : AntiPumpingState) : Prop :=
  s.PiTotal = fluxComponentsSum s

/-- OBLIGATION ANALYTIQUE OUVERTE : interaction low-high. -/
def LowHighBoundSpec (s : AntiPumpingState) : Prop :=
  s.PiLH ≤ s.thetaLH * s.nu * s.DHigh + s.rLH

/-- OBLIGATION ANALYTIQUE OUVERTE : interaction high-low. -/
def HighLowBoundSpec (s : AntiPumpingState) : Prop :=
  s.PiHL ≤ s.thetaHL * s.nu * s.DHigh + s.rHL

/-- OBLIGATION ANALYTIQUE OUVERTE : interaction high-high. -/
def HighHighBoundSpec (s : AntiPumpingState) : Prop :=
  s.PiHH ≤ s.thetaHH * s.nu * s.DHigh + s.rHH

/-- Les coefficients d'absorption individuels ne sont pas negatifs. -/
def ThetaNonnegativeSpec (s : AntiPumpingState) : Prop :=
  0 ≤ s.thetaLH ∧
  0 ≤ s.thetaHL ∧
  0 ≤ s.thetaHH

/--
Condition critique d'anti-pumping :
la somme des fractions absorbees doit rester strictement < 1.
-/
def ThetaBudgetSpec (s : AntiPumpingState) : Prop :=
  ThetaNonnegativeSpec s ∧
  thetaTotal s < 1

/--
Forme abstraite d'un controle quantitatif du reste.

R est laisse externe : la future analyse devra fournir
une borne utile en fonction de J et des normes autorisees.
-/
def RemainderControlledSpec
    (s : AntiPumpingState) (R : Scalar) : Prop :=
  |remainderTotal s| ≤ R

/--
Cible NS_ANTI_PUMPING apres aggregation LH + HL + HH.
-/
def AntiPumpingTargetSpec (s : AntiPumpingState) : Prop :=
  s.PiTotal ≤
    thetaTotal s * s.nu * s.DHigh +
    remainderTotal s

/--
Balance d'energie haute frequence abstraite.

La couche PDE devra justifier cette relation a partir
des equations de Navier-Stokes filtrees.
-/
def HighFrequencyEnergyBalanceSpec (s : AntiPumpingState) : Prop :=
  s.dE + s.nu * s.DHigh ≤ s.PiTotal

/--
Cible de fermeture apres absorption.

Ce n'est PAS un theorem ici.
-/
def EnergyClosureTargetSpec (s : AntiPumpingState) : Prop :=
  s.dE +
      (1 - thetaTotal s) * s.nu * s.DHigh
    ≤ remainderTotal s

/--
Inventaire exact des obligations qui suffiraient a la fermeture
scalaire. Elles restent des hypotheses de SPECIFICATION tant que
LH / HL / HH ne sont pas obtenues depuis l'analyse PDE.
-/
def AnalyticalOpenObligationsSpec (s : AntiPumpingState) : Prop :=
  StateAdmissibleSpec s ∧
  FluxDecompositionSpec s ∧
  LowHighBoundSpec s ∧
  HighLowBoundSpec s ∧
  HighHighBoundSpec s ∧
  ThetaBudgetSpec s

end Obsidia.NavierStokes.Specs
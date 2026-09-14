/-
  Obsidia / NavierStokes / Definitions.lean
  =========================================
  NS STAGE A — FORMAL SPECIFICATION LAYER.

  Objet : interface scalaire du verrou NS_ANTI_PUMPING.

  IMPORTANT :
  - ce fichier NE formalise PAS encore les projecteurs Littlewood-Paley ;
  - NE formalise PAS encore la decomposition de Bony ;
  - NE prouve AUCUNE estimation LH / HL / HH ;
  - NE revendique AUCUNE preuve de regularite Navier-Stokes.

  Les champs PiLH / PiHL / PiHH sont les obligations analytiques
  qui devront ensuite etre reliees a la vraie decomposition dyadique.
-/

import Mathlib

namespace Obsidia.NavierStokes

abbrev Scalar := ℝ

/--
Etat scalaire minimal associe au verrou haute frequence.

EHigh  : energie Sobolev haute frequence
DHigh  : dissipation haute frequence
PiTotal: flux non lineaire haute frequence

PiLH / PiHL / PiHH :
  contributions low-high, high-low et high-high.

theta* :
  fractions candidates de dissipation absorbables.

r* :
  restes associes a chaque interaction.
-/
structure AntiPumpingState where
  nu      : Scalar
  dE      : Scalar

  EHigh   : Scalar
  DHigh   : Scalar

  PiTotal : Scalar
  PiLH    : Scalar
  PiHL    : Scalar
  PiHH    : Scalar

  thetaLH : Scalar
  thetaHL : Scalar
  thetaHH : Scalar

  rLH     : Scalar
  rHL     : Scalar
  rHH     : Scalar

/-- Coefficient total d'absorption candidat. -/
def thetaTotal (s : AntiPumpingState) : Scalar :=
  s.thetaLH + s.thetaHL + s.thetaHH

/-- Reste total provenant des trois familles d'interaction. -/
def remainderTotal (s : AntiPumpingState) : Scalar :=
  s.rLH + s.rHL + s.rHH

/-- Somme des trois contributions dyadiques candidates. -/
def fluxComponentsSum (s : AntiPumpingState) : Scalar :=
  s.PiLH + s.PiHL + s.PiHH

/-- Dissipation qui resterait apres absorption du flux. -/
def residualDissipation (s : AntiPumpingState) : Scalar :=
  (1 - thetaTotal s) * s.nu * s.DHigh

end Obsidia.NavierStokes
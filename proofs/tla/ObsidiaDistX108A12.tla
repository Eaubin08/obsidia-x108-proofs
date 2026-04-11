---- MODULE ObsidiaDistX108A12 ----
EXTENDS Naturals, Integers, TLC

VARIABLES f, tau, irr, elapsed, baseAct, byzCount, byzAct, global

Vars == <<f, tau, irr, elapsed, baseAct, byzCount, byzAct, global>>

GateDecision(t, i, e, b) ==
  IF i /\ e < t THEN "HOLD"
  ELSE IF b THEN "ACT" ELSE "HOLD"

HonestActCount(ff, bc, t, i, e, b) ==
  IF GateDecision(t, i, e, b) = "ACT" THEN (3 * ff + 1 - bc) ELSE 0

TotalAct(ff, bc, ba, t, i, e, b) ==
  HonestActCount(ff, bc, t, i, e, b) + ba

Init ==
  /\ f \in 0..1
  /\ tau \in 0..5
  /\ irr \in BOOLEAN
  /\ elapsed \in 0..10
  /\ baseAct \in BOOLEAN
  /\ byzCount \in 0..f
  /\ byzAct \in 0..byzCount
  /\ global =
      IF TotalAct(f, byzCount, byzAct, tau, irr, elapsed, baseAct) >= (2 * f + 1)
      THEN "ACT" ELSE "HOLD"

Next ==
  UNCHANGED Vars

SafetyDistributed ==
  (irr /\ elapsed < tau) => (global # "ACT")

====
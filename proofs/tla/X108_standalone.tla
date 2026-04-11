---- MODULE X108_standalone ----
EXTENDS Integers, TLC

\* Constantes fixées directement pour le model checking
TauMax == 5
ElapsedMin == -2
ElapsedMax == 10

VARIABLES tau, irr, elapsed, baseAct, decision

GateDecision(t, i, e, b) ==
  IF i /\ e < t THEN "HOLD"
  ELSE IF b THEN "ACT" ELSE "HOLD"

Init ==
  /\ tau \in 0..TauMax
  /\ irr \in BOOLEAN
  /\ elapsed \in ElapsedMin..ElapsedMax
  /\ baseAct \in BOOLEAN
  /\ decision = GateDecision(tau, irr, elapsed, baseAct)

Next ==
  /\ tau' \in 0..TauMax
  /\ irr' \in BOOLEAN
  /\ elapsed' \in ElapsedMin..ElapsedMax
  /\ baseAct' \in BOOLEAN
  /\ decision' = GateDecision(tau', irr', elapsed', baseAct')

Spec == Init /\ [][Next]_<<tau,irr,elapsed,baseAct,decision>>

SafetyX108 ==
  \A t \in 0..TauMax, e \in ElapsedMin..ElapsedMax, b \in BOOLEAN :
    LET d == GateDecision(t, TRUE, e, b)
    IN  (e < t) => (d # "ACT")

THEOREM Spec => SafetyX108
====

---- MODULE X108 ----
EXTENDS Naturals, Integers, TLC

CONSTANTS TauMax, ElapsedMin, ElapsedMax
ASSUME TauMax \in Nat
ASSUME ElapsedMin \in Int /\ ElapsedMax \in Int /\ ElapsedMin <= ElapsedMax

VARIABLES tau, irr, elapsed, baseDecision, decision

DecisionSet == {"HOLD", "ALLOW", "BLOCK"}

GateDecision(t, i, e, d) ==
  IF i /\ e < t THEN "HOLD" ELSE d

Init ==
  /\ tau \in 0..TauMax
  /\ irr \in BOOLEAN
  /\ elapsed \in ElapsedMin..ElapsedMax
  /\ baseDecision \in DecisionSet
  /\ decision = GateDecision(tau, irr, elapsed, baseDecision)

Next ==
  /\ tau' \in 0..TauMax
  /\ irr' \in BOOLEAN
  /\ elapsed' \in ElapsedMin..ElapsedMax
  /\ baseDecision' \in DecisionSet
  /\ decision' = GateDecision(tau', irr', elapsed', baseDecision')

Spec ==
  Init /\ [][Next]_<<tau, irr, elapsed, baseDecision, decision>>

SafetyX108 ==
  []((irr /\ elapsed < tau) => (decision # "ALLOW"))

====
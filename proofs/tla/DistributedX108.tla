---- MODULE DistributedX108 ----
EXTENDS Naturals, Integers, FiniteSets, TLC

VARIABLES f, N, tau, irr, elapsed, baseAct, honest, byz, local, global

Vars == <<f, N, tau, irr, elapsed, baseAct, honest, byz, local, global>>

NodeIds(n) == 1..n

GateDecision(t, i, e, b) ==
  IF i /\ e < t THEN "HOLD"
  ELSE IF b THEN "ACT" ELSE "HOLD"

CountAct(xs) ==
  Cardinality({ i \in DOMAIN xs : xs[i] = "ACT" })

Aggregate(xs, ff) ==
  IF CountAct(xs) >= (2 * ff + 1) THEN "ACT" ELSE "HOLD"

StateOK ==
  /\ f \in 0..1
  /\ N = 3 * f + 1
  /\ tau \in 0..5
  /\ irr \in BOOLEAN
  /\ elapsed \in 0..10
  /\ baseAct \in BOOLEAN
  /\ honest = NodeIds(N)
  /\ byz = {}
  /\ TRUE
  /\ local \in [NodeIds(N) -> {"HOLD","ACT"}]
  /\ (\A i \in honest : local[i] = GateDecision(tau, irr, elapsed, baseAct))
  /\ global = Aggregate(local, f)

Init == StateOK
Next == UNCHANGED Vars
Spec == Init /\ [][Next]_Vars

SafetyDistributed ==
  (irr /\ elapsed < tau) => (global # "ACT")

====

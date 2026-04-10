---- MODULE DistributedX108_standalone ----
EXTENDS Integers, FiniteSets, TLC

FMax == 1
TauMax == 3
ElapsedMin == -1
ElapsedMax == 5

VARIABLES f, N, tau, irr, elapsed, baseAct,
          honest, byz, local, global

NodeIds(n) == 1..n

GateDecision(t, i, e, b) ==
  IF i /\ e < t THEN "HOLD"
  ELSE IF b THEN "ACT" ELSE "HOLD"

CountAct(xs, n) ==
  Cardinality({i \in 1..n : xs[i] = "ACT"})

Aggregate(xs, fval, n) ==
  IF CountAct(xs, n) >= (2*fval + 1) THEN "ACT" ELSE "HOLD"

Init ==
  /\ f \in 0..FMax
  /\ N = 3*f + 1
  /\ tau \in 0..TauMax
  /\ irr \in BOOLEAN
  /\ elapsed \in ElapsedMin..ElapsedMax
  /\ baseAct \in BOOLEAN
  /\ honest \in SUBSET NodeIds(N)
  /\ byz = NodeIds(N) \ honest
  /\ Cardinality(byz) <= f
  /\ local \in [NodeIds(N) -> {"HOLD","ACT"}]
  /\ \A i \in honest : local[i] = GateDecision(tau, irr, elapsed, baseAct)
  /\ global = Aggregate(local, f, N)

Next ==
  /\ f' \in 0..FMax
  /\ N' = 3*f' + 1
  /\ tau' \in 0..TauMax
  /\ irr' \in BOOLEAN
  /\ elapsed' \in ElapsedMin..ElapsedMax
  /\ baseAct' \in BOOLEAN
  /\ honest' \in SUBSET NodeIds(N')
  /\ byz' = NodeIds(N') \ honest'
  /\ Cardinality(byz') <= f'
  /\ local' \in [NodeIds(N') -> {"HOLD","ACT"}]
  /\ \A i \in honest' : local'[i] = GateDecision(tau', irr', elapsed', baseAct')
  /\ global' = Aggregate(local', f', N')

Spec == Init /\ [][Next]_<<f,N,tau,irr,elapsed,baseAct,honest,byz,local,global>>

SafetyDistributed ==
  \A fval \in 0..FMax, t \in 0..TauMax, e \in ElapsedMin..ElapsedMax :
    \A lc \in [NodeIds(3*fval+1) -> {"HOLD","ACT"}] :
      LET n == 3*fval+1
          h == {i \in 1..n : lc[i] = GateDecision(t, TRUE, e, TRUE)}
          bv == NodeIds(n) \ h
          g == Aggregate(lc, fval, n)
      IN  (e < t /\ Cardinality(bv) <= fval) => (g # "ACT")

THEOREM Spec => SafetyDistributed
====

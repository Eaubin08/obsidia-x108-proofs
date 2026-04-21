\
---- MODULE DistributedX108 ----
EXTENDS Naturals, Integers, Sequences, TLC

(*
  Distributed X-108 with N = 3*f + 1 and up to f Byzantine nodes.

  This model is abstract:
  - each node outputs a local decision in {"HOLD","ACT"}
  - honest nodes obey X-108 gate; byzantine nodes may output anything
  - aggregator is majority-of-N over "ACT" (supermajority condition)
  - safety property: if gate should hold on honest nodes, global decision is not ACT

  NOTE: This is a model-checking spec; it is not a Lean proof.
*)

CONSTANTS FMax, TauMax, ElapsedMin, ElapsedMax
ASSUME FMax \in Nat
ASSUME TauMax \in Nat
ASSUME ElapsedMin \in Int /\ ElapsedMax \in Int /\ ElapsedMin <= ElapsedMax

VARIABLES f, N, tau, irr, elapsed, baseAct,
          honest, byz, local, global

NodeIds(n) == 1..n

Init ==
  /\ f \in 0..FMax
  /\ N = 3*f + 1
  /\ tau \in 0..TauMax
  /\ irr \in BOOLEAN
  /\ elapsed \in ElapsedMin..ElapsedMax
  /\ baseAct \in BOOLEAN
  /\ honest \subseteq NodeIds(N)
  /\ byz = NodeIds(N) \ honest
  /\ Cardinality(byz) <= f
  /\ local \in [NodeIds(N) -> {"HOLD","ACT"}]
  /\ global \in {"HOLD","ACT"}

GateDecision(tau, irr, elapsed, baseAct) ==
  IF irr /\ elapsed < tau THEN "HOLD"
  ELSE IF baseAct THEN "ACT" ELSE "HOLD"

(*
  Honest nodes must follow GateDecision.
  Byzantine nodes unconstrained.
*)
HonestConstraint ==
  \A i \in honest : local[i] = GateDecision(tau, irr, elapsed, baseAct)

CountAct(xs) ==
  Cardinality({i \in DOMAIN xs : xs[i] = "ACT"})

Aggregate(xs) ==
  IF CountAct(xs) >= (2*f + 1) THEN "ACT" ELSE "HOLD"
  \* supermajority threshold derived from N=3f+1 with <= f faulty

Next ==
  /\ f' \in 0..FMax
  /\ N' = 3*f' + 1
  /\ tau' \in 0..TauMax
  /\ irr' \in BOOLEAN
  /\ elapsed' \in ElapsedMin..ElapsedMax
  /\ baseAct' \in BOOLEAN
  /\ honest' \subseteq NodeIds(N')
  /\ byz' = NodeIds(N') \ honest'
  /\ Cardinality(byz') <= f'
  /\ local' \in [NodeIds(N') -> {"HOLD","ACT"}]
  /\ ( \A i \in honest' : local'[i] = GateDecision(tau', irr', elapsed', baseAct') )
  /\ global' = Aggregate(local')

Spec ==
  Init /\ [][Next]_<<f,N,tau,irr,elapsed,baseAct,honest,byz,local,global>>

SafetyDistributed ==
  [] ( (irr /\ elapsed < tau) => (global # "ACT") )

THEOREM Spec => SafetyDistributed
====
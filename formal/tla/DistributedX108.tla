\
---- MODULE DistributedX108 ----
EXTENDS Naturals, Integers, Sequences, TLC, FiniteSets

CONSTANTS FMax, TauMax, ElapsedMin, ElapsedMax
ASSUME FMax \in Nat
ASSUME TauMax \in Nat
ASSUME ElapsedMin \in Int /\ ElapsedMax \in Int /\ ElapsedMin <= ElapsedMax

VARIABLES f, N, tau, irr, elapsed, baseAct,
          honest, byz, local, global

NodeIds(n) == 1..n

GateRule(t, i, e, b) ==
  IF i /\ e < t THEN "HOLD"
  ELSE IF b THEN "ACT" ELSE "HOLD"

Init ==
  /\ f \in 0..FMax
  /\ N = 3*f + 1
  /\ tau \in 0..TauMax
  /\ irr \in BOOLEAN
  /\ elapsed \in ElapsedMin..ElapsedMax
  /\ baseAct \in BOOLEAN
  /\ honest = 1..N
  /\ byz = {}
  /\ local = [i \in 1..N |-> IF irr /\ elapsed < tau THEN "HOLD" ELSE IF baseAct THEN "ACT" ELSE "HOLD"]
  /\ global = IF irr /\ elapsed < tau THEN "HOLD" ELSE IF baseAct THEN "ACT" ELSE "HOLD"

Next ==
  /\ f' \in 0..FMax
  /\ N' = 3*f' + 1
  /\ tau' \in 0..TauMax
  /\ irr' \in BOOLEAN
  /\ elapsed' \in ElapsedMin..ElapsedMax
  /\ baseAct' \in BOOLEAN
  /\ honest' = 1..N'
  /\ byz' = {}
  /\ local' = [i \in 1..N' |-> IF irr' /\ elapsed' < tau' THEN "HOLD" ELSE IF baseAct' THEN "ACT" ELSE "HOLD"]
  /\ global' = IF irr' /\ elapsed' < tau' THEN "HOLD" ELSE IF baseAct' THEN "ACT" ELSE "HOLD"

Spec ==
  Init /\ [][Next]_<<f,N,tau,irr,elapsed,baseAct,honest,byz,local,global>>

SafetyDistributed ==
  [] ( (irr /\ elapsed < tau) => (global # "ACT") )

THEOREM Spec => SafetyDistributed
====
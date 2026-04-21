\
---- MODULE X108 ----
EXTENDS Naturals, TLC

(*
  Single-node X-108 gate model (abstract).

  Variables:
    tau     : Nat       \* gate threshold (non-negative)
    irr     : BOOLEAN   \* irreversibility flag
    elapsed : Int       \* time since proposal; may be negative (clock skew)
    baseAct : BOOLEAN   \* base decision wants to ACT (e.g., theta <= S)

    decision ∈ {"HOLD","ACT"}
*)

CONSTANTS TauMax, ElapsedMin, ElapsedMax
ASSUME TauMax \in Nat
ASSUME ElapsedMin \in Int /\ ElapsedMax \in Int /\ ElapsedMin <= ElapsedMax

VARIABLES tau, irr, elapsed, baseAct, decision

Init ==
  /\ tau \in 0..TauMax
  /\ irr \in BOOLEAN
  /\ elapsed \in ElapsedMin..ElapsedMax
  /\ baseAct \in BOOLEAN
  /\ decision \in {"HOLD","ACT"}

(*
  Gate rule:
    If irr and elapsed < tau -> HOLD
    else decision follows baseAct.
*)
GateDecision(tau, irr, elapsed, baseAct) ==
  IF irr /\ elapsed < tau THEN "HOLD"
  ELSE IF baseAct THEN "ACT" ELSE "HOLD"

Next ==
  /\ tau' \in 0..TauMax
  /\ irr' \in BOOLEAN
  /\ elapsed' \in ElapsedMin..ElapsedMax
  /\ baseAct' \in BOOLEAN
  /\ decision' = GateDecision(tau', irr', elapsed', baseAct')

Spec ==
  Init /\ [][Next]_<<tau,irr,elapsed,baseAct,decision>>

SafetyX108 ==
  [] ( (irr /\ elapsed < tau) => (decision # "ACT") )

THEOREM Spec => SafetyX108
====
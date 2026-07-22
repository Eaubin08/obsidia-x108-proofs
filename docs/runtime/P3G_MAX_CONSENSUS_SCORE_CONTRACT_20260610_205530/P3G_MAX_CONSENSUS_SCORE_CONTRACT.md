# P3G — MAX CONSENSUS SCORE CONTRACT

## Status

SPEC_CONTRACT_NOT_WIRED.

No runtime patch.
No API patch.
No kernel patch.
No freeze.
No commit.

## Why this contract exists

The live domain terminal currently exposes useful decision fields, but not the full consensus surface.

The repository already contains a proof-backed consensus rule:

- aggregate4
- quorum 3/4
- supermajority minimum 3 of 4
- fail-closed default
- BLOCK if no valid supermajority
- threshold conservation
- BLOCK priority over HOLD/ACT

The goal is not to invent a new scoring layer.

The goal is to expose the existing proof-backed structure cleanly in live decisions and human-readable domain terminals.

## Existing live fields

- confidence_integrity
- confidence_governance
- confidence_readiness
- readiness_scope = harmonic_integrity_governance
- raw_engine.vote_count
- raw_engine.agent_votes
- sigma_report
- sigma_step
- decision_id
- trace_id
- x108_gate
- reason_code
- severity

## Harmonic confidence

The harmonic confidence may be derived from:

```text
confidence_integrity
confidence_governance
confidence_readiness

Formula:

3 / ((1 / confidence_integrity) + (1 / confidence_governance) + (1 / confidence_readiness))

This is display-derived from exposed fields unless the kernel later exposes an official harmonic_score.

Consensus surface missing from live decisions

The live decision should eventually expose:

{
  "raw_engine": {
    "consensus": {
      "rule": "aggregate4",
      "threshold": "3/4",
      "voters": 4,
      "supermajority_min": 3,
      "votes": {
        "ACT": 0,
        "HOLD": 0,
        "BLOCK": 0
      },
      "consensus_ratio": 0.0,
      "supermajority": false,
      "fail_closed": true,
      "final_decision": "BLOCK",
      "reason": "no 3/4 supermajority"
    }
  }
}
Authority boundary

The terminal displays.
The connector observes.
The API transports.
The kernel decides.
The proof surface verifies.

No display field may authorize action.

Do not invent

Do not display these as official unless exposed by live runtime or kernel decision:

final_score
agent_mean
consensus_ratio
detailed agent votes
Human terminal target

Example:

[TRADING][⛔ BLOQUÉ / CRITIQUE] BTC/USDT — ordre refusé avant exécution | cause=signaux contradictoires | confiance_harmonique=66% | agents=17 | consensus=non exposé
[TRADING][🔎 PREUVE] décision=... | trace=... | empreinte=... | sceau_merkle=...
[TRADING][🛡 AUTORITÉ] Kernel X108=décideur | API=transport uniquement | action réelle=non exécutée

Future, once consensus is wired:

[TRADING][⛔ BLOQUÉ / CRITIQUE] BTC/USDT — ordre refusé avant exécution | confiance_harmonique=66% | consensus=non atteint | règle=3/4 fail-closed
Implementation status
LayerStatus
Formal consensusFOUND
Proof mappingFOUND
Live harmonic inputsFOUND
Live agent namesFOUND
Live detailed agent votesMISSING
Live consensus surfaceMISSING
Human terminal surfacePARTIAL
Next step

Prepare P3H wiring plan:

inspect where live raw_engine is assembled
insert raw_engine.consensus without changing authority
preserve all existing decision fields
add tests proving no loss of trace
add tests proving aggregate4 still fails closed

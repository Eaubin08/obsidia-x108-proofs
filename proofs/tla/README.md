## Running TLC (local)

1. Install TLA+ tools (tlc / tla2tools.jar).
2. Run:

   tlc2 -deadlock X108.tla
   tlc2 -deadlock DistributedX108.tla

## Property mapping

- `SafetyX108` corresponds to: no ACT before tau for irreversible intents.
- `HonestSupermajorityNoAct` corresponds to: if >= 3 honest nodes output HOLD under gate,
  then the aggregate decision cannot be ACT.

## Strasbourg Clock sandbox traces

The provided CSV traces (outside this pack) demonstrate the same idea empirically:
- baseline: no divergence
- noise: divergence grows
- structural error: fast divergence
- hold: divergence is capped by a HOLD gate

Use `tools/check_traces_x108.py` to validate a concrete "gate" threshold on `delta_day`/`delta_lunar`.

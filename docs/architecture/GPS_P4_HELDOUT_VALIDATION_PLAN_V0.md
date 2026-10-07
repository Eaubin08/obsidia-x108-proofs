# GPS P4 — HELD-OUT VALIDATION PLAN V0

Status: READY FOR LOCAL INVENTORY / CLASSIFIER FROZEN  
Decision authority: KX108_ONLY

## Frozen classifier

`P4_TEMPORAL_DISCONTINUITY_V0` is frozen before held-out validation.

No threshold tuning is allowed before held-out decisions are recorded.

## Real nominal negative control

CTTC recorded real RF:

- frozen-classifier result: `NOMINAL`
- positions: 149
- transitions: 148
- anomaly transitions: 0
- unknown transitions: 0
- maximum ECEF step: approximately 1.621 m
- maximum clock residual: 0.5 s
- maximum receiver gap: 1 s

This is one held-out nominal control, not a complete true-negative-rate estimate.

## Official FGI held-out candidates

The official FGI-SpoofRepo publication documents four L1/E1 recordings:

| Scenario | Folder | L1/E1 file | Approx. duration | P4 development use |
|---|---|---|---:|---|
| Targeted SFMC | `Targeted_SFMC` | `TGS_L1_E1.dat` | 373 s | HELD OUT |
| Targeted DFMC | `Targeted_DFMC` | `TGD_L1_E1.dat` | 373 s | HELD OUT |
| Untargeted DFMC | `Untargeted_DFMC` | `UTD_L1_E1.dat` | 377 s | USED FOR DEVELOPMENT |
| Meaconing DFMC | `Meaconing_DFMC` | `MCD_L1_E1.dat` | 478 s | HELD OUT |

Publication:
- DOI: `10.1007/s10291-024-01719-2`
- dataset DOI: `10.23729/7a648509-2ca8-4a7d-8223-0b429182f857`

## Interpretation boundary

The temporal detector is not assumed to be a universal spoofing detector.

The held-out scenarios deliberately stress different failure modes:

- Targeted SFMC / DFMC are time-and-position synchronized and can produce smooth takeover.
- Meaconing replays authentic signals with a time delay.
- Untargeted DFMC, already used for development, has a large asynchronous time/position discontinuity.

A held-out hostile case that remains `NOMINAL` under the temporal detector is not to be relabeled or used to retune V0 after the fact. It is evidence that another detector family is required.

## Protocol

1. Inventory which official held-out files are already present locally.
2. Select an available held-out case without changing V0.
3. Bind its source hash and receiver config before execution.
4. Run receiver processing.
5. Run frozen temporal classifier with no recalibration.
6. Persist detector decision.
7. Only then compare with scenario truth.
8. Add result to confusion/scope matrix.

No active RF transmission is required; validation remains offline recorded RF.

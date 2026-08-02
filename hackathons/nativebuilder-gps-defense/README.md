# Obsidia GPS Defense - Physical Signal Periphery V0

Status: HACKATHON_EXPERIMENTAL
Claim boundary: this package connects physical GNSS observation envelopes to the existing GPS Defense chain. It does not decode RF itself, does not emit RF, does not decide, and does not modify the sealed kernel.

## Chain

```text
GNSS-SDR / RINEX / live passive receiver metadata
-> GPS Physical Observation Envelope
-> Physical Reality Gate
-> GPS DomainState payload
-> P3-05
-> X-108
-> OS3 receipt
```

## Proof Levels

- `SYNTHETIC_TEST_ONLY`
- `STRUCTURED_STATE`
- `RECORDED_REAL_GNSS`
- `RECORDED_RF_ATTACK`
- `REAL_PASSIVE_GNSS`
- `HARDWARE_IN_THE_LOOP`
- `EXTERNAL_REPLICATION`

Synthetic fixtures are only for format tests and must set `eligible_for_physical_claim=false`.

## CLI

```powershell
python hackathons/nativebuilder-gps-defense/physical_signal_cli.py --physical-observation hackathons/nativebuilder-gps-defense/samples/synthetic_observation.json
python hackathons/nativebuilder-gps-defense/physical_signal_cli.py --live-passive
python hackathons/nativebuilder-gps-defense/physical_signal_cli.py --blind-benchmark hackathons/nativebuilder-gps-defense/samples/blind_manifest.json
```


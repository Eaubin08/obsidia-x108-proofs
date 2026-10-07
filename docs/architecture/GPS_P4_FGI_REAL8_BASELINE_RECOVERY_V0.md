# GPS P4 — FGI REAL8 PRE-ATTACK BASELINE RECOVERY

Status: VERIFIED RECEIVER BASELINE / P4 NOT YET CLOSED  
Authority: KX108_ONLY

## Result

The historical FGI source was recovered locally and SHA-256 verified:

- source: `UTD_L1_E1.dat`
- size: `9825419264` bytes
- SHA-256: `e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`
- official format: real signed 8-bit I at 26 MHz
- official attack onset: 135 s

The historical pre-attack GNSS-SDR attempt interpreted the real 8-bit I corpus with `ibyte` / interleaved-IQ semantics. That configuration reported 65 s for 3.38e9 samples.

The corrected receiver configuration uses real8 semantics:

```text
SignalSource.item_type=byte
DataTypeAdapter.implementation=Pass_Through
DataTypeAdapter.item_type=byte
InputFilter.implementation=Freq_Xlating_Fir_Filter
InputFilter.input_item_type=byte
InputFilter.output_item_type=gr_complex
SignalSource.sampling_frequency=26000000
InputFilter.IF=6390000
```

With the same 3.38e9-sample pre-attack window GNSS-SDR now reports 130 s, consistent with one byte per real sample.

## Receiver evidence

Corrected run:

- acquisition/tracking: present
- GPS NAV messages: present from receiver time ~13 s
- first PVT fix: `2023-11-10T14:05:24.140000Z`
- first fix position: lat `60.1822`, lon `24.8285`, height `31.6135 m`
- first-fix GDOP: `2.65868`
- PVT thereafter: continuous through the end of the 130 s pre-attack window
- typical PVT observation count after lock: 8–9
- RINEX navigation header: updated
- GNSS-SDR process: completed successfully

The previous blocker `PRE_ATTACK_RECEIVER_FAILURE` is therefore not reproduced under the corrected real8 source semantics.

## Consequence

Historical claims remain unchanged as historical evidence; old PASS8 outputs are not rewritten.

For current P4 work, the accepted receiver family can now establish a stable pre-attack NAV/PVT baseline before the official hostile onset at 135 s.

This removes the receiver-baseline blocker only.

It does not by itself establish:

- hostile classification success;
- causal attribution;
- TP/TN/FP/FN metrics;
- P2 live-passive closure;
- P3 independent physical corroboration;
- spoofing resistance, production readiness, aviation validation, or certification.

## Next experiment

Replay the complete FGI recording using the same corrected receiver family and frozen source hash, crossing the official 135 s onset without exposing onset/truth to the online receiver path.

Then compare pre/post trajectory, tracking, NAV/PVT continuity and deterministic classifier evidence. Truth alignment remains post-run only.

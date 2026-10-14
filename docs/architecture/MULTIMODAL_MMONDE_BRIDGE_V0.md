# F6 — Multimodal -> MMonde bridge V0

Status: implementation candidate.

Existing repository material already treats multimodality as bounded fusion rather than a synonym for multiple models. Modalities can have different clocks, precision, provenance, latency and reference frames. Existing OCS generation logic also marks generated output as not truth and holds on multimodal mismatch.

This F6 bridge materializes only that boundary:

```text
text / voice / audio / image / video / sensors
  -> ModalityObservationV0[]
  -> WorldObservationV0[]
  -> WorldStateV0
  -> domain interpretation / governance
```

Invariants:

- modality != truth;
- generated output != truth;
- provenance != trust;
- temporal alignment != causal proof;
- missing latency or frame remains UNKNOWN;
- fusion conserves per-modality provenance and contradictions;
- fusion cannot decide or act;
- MMonde remains representation-only;
- KX108 remains the authority boundary downstream.

This stage does not claim a production vision model, video understanding model, speaker identification system, BodyState, sensor fusion engine, or image/video generation stack. Those are separate capabilities. F6 only defines the conservative situated-observation contract by which such capabilities can enter MMonde without gaining epistemic or decision authority.

# C2.4 — Offline delegation proof / ledger / Gateway composition

**WIP / DRAFT / NO LIVE AUTHORITY**. Based on C2.3 `31b3fef5d8e174868ac125a5fc203c88fb2e148d`.

Audit found `periphery/world_calls/obsidia_gateway.py` is V4 dry-run only. Its `DRY_RUN_PASS` means `egress_allowed=False`, not real KX108 approval. The SovereignTicket `x108_gate` field in the fixture is a data field, not independently verified KX108 authority. The test deliberately uses a HOLD ticket to show the composition does not promote it into execution.

This isolated composition checks a fixture HMAC scope proof, uses a local transactional SQLite nonce/revocation ledger and invokes the existing dry-run Gateway. Success remains `NO_EXECUTION`, never ALLOW. Tests cover forged signatures, replay, revoked delegation, forbidden WorldCall classes, and successful fixture composition with zero egress.

Gaps: no independently verified organization issuer/consent; no verified KX108 decision provenance; no sovereign ticket authenticity or binding to action; no actual connector dispatch boundary; no durable cross-host atomicity or distributed revocation; no real provider receipt. Test-only signer and ledger enrollment are not trusted authority. Do not connect this prototype to a live provider. No changes to main, KX108, or Monde.

# Proof Artifacts

This document enumerates the types of proof artifacts used by Obsidia to ensure verifiable execution and auditability.

## Types of Receipts
1. **Intent Receipt**: Generated for every proposed action; holds the hash of the intent and ensures that the request was evaluated by KX108.
2. **Effect Receipt**: Generated only when the KX108 gateway allows an irreversible action (ACT). Contains the resulting state hash and references the intent.
3. **Portal Activation Receipt**: Generated when a portal unlocks a resource. Records the key used, the unlocked resource, and ensures non-authorization.
4. **Debug Receipt**: Produced by debug modules capturing trace and user feedback. It is used for calibration and transparency.

## Other Proofs
- **Hash Chain Packet**: Each receipt includes a hash linking to previous receipts, forming an immutable chain.
- **Replay Pointer**: Points to the deterministic replay log stored by the system.
- **Freeze Manifest**: A file that defines a snapshot of all components and their state at a given version.

These artifacts are crucial for demonstrating that no action was taken without evidence and that every irreversible effect can be audited.

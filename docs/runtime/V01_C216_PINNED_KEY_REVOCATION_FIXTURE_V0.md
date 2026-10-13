# V0.1 C2.16 — offline pinned public-key revocation fixture

Status: DRAFT / FAIL-CLOSED / NO EGRESS.

Parent C2.15 HEAD `95af5e907f95a2b6c2a0582cfec68371771800f4`; targeted CI #37730097851 SUCCESS.

This isolated fixture stores SHA256 fingerprints of DER public-key material for an exact (organization, issuer, audience) tuple. SQLite persistence keeps revocations across process restarts; a revoked fingerprint cannot be re-enrolled through the fixture. Tests cover restart, revocation, swapped public keys, cross-tenant lookups and audience drift. CI also runs prior C2.15 Ed25519 claim tests.

**No independent enrollment**: anyone with access to `enroll_fixture` can insert a test public key. This registry is not a privileged or authenticated trust root, nor a real OIDC/JWKS service. `PINNED_FIXTURE_ONLY_NO_ORGANIZATION_AUTHORITY` does not permit action. It is not integrated into a live verifier, the KX108 ticket route or provider gateway. C2.13/C2.14 admission remain BLOCK. The SQLite ledger is local-host only and is not a cross-host transactional revocation fence.

Required before any promotion: authenticate the organizational administrator, establish IdP issuer/audience and signed key custody under privileged enrollment, verify fresh provider claims and revocation, bind to original human approval, canonical KX108 world-action record, and ticket; audit transactional connector entry and receipts. No main/kernel/Monde changes.

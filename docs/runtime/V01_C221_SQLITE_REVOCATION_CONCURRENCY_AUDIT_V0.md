# V0.1 C2.21 — local SQLite revocation and replay concurrency audit

Status: DRAFT / FAIL-CLOSED / NO LIVE CONNECTOR.

Parent C2.20 HEAD d2c963058708f80c129cc6a4ffb4ccbc89e83437. CI C2.19 corrected #37732169747 SUCCESS and C2.20 #37732276216 SUCCESS. Additional C2.20/C2.19 queued checks not represented as complete.

Tests simulate 24 concurrent attempts to consume one nonce against the SAME on-disk SQLite file; exactly one fixture check succeeds and remaining calls must be blocked as replays. Revocation after restart must block, and revocation racing with 19 checks must leave permanent revoked state. The scheduler does not guarantee a particular interleaving: checks completing *before* revocation may return CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY, which is **not an action authorization**. Separate-organization nonces remain isolated.

Important limitation: `BEGIN IMMEDIATE` serializes SQLite operations on a shared **local** file, not remote hosts or provider dispatch. No atomic recheck/commit with a real external side effect; a non-revoked check preceding revoke cannot be used later as permission. Without a real trusted organization issuer, pinned production identity credentials, KX108 record binding, authenticated SovereignTicket and atomic dispatch receipt, execution remains BLOCK. No production authority here, no main/kernel/Monde changes.

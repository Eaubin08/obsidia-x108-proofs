# C2.32 — local SQLite reservation state update guard

Status: DRAFT / offline fixture / FAIL-CLOSED / NO EXTERNAL EXECUTION.

Parent C2.31 HEAD f26aded7db8e434e7b60e056355cec66e12360cd; C2.30/C2.31 workflows were queued at first inspection, so no green CI claim.

C2.32 adds a local BEFORE UPDATE OF status trigger requiring a matching newest event for the same idempotency key and one of the three non-executing transitions RESERVED_NO_EXECUTION -> CLOSED_NO_EXECUTION / ABANDONED_NO_EXECUTION / INVALIDATED. The C2.28 logged closure/revoke paths append the event before changing the reservation state in the same BEGIN IMMEDIATE transaction. Tests cover direct unjournaled UPDATE refusal, successful logged closure/revoke, and detection of missing trigger.

Limitations: local SQLite trigger logic is not an independent trust boundary. A database owner can DROP TRIGGER and change event rows; a forged journal event preceding an UPDATE could bypass this simple condition. Status transitions remain no-execution only. Other direct column updates, new record insertion and global DB replacement are not prevented by this step. The trigger-definition inspection does not independently anchor SQL. No main, kernel, Monde or live connector changes.

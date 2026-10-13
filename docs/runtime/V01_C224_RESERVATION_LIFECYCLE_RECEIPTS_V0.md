# V0.1 C2.24 — offline reservation lifecycle and receipts

Status: DRAFT / NO EXECUTION / FAIL-CLOSED.

Parent C2.23 HEAD 23f05ce1413016483feaa26c1191f8e2d2e3a483. Its targeted CI #37732701504 was still QUEUED when work began.

Adds two no-execution terminal transitions from RESERVED_NO_EXECUTION: CLOSED_NO_EXECUTION and ABANDONED_NO_EXECUTION. A SQLite BEGIN IMMEDIATE transaction updates the reservation and stores a deterministic SHA256 receipt, surviving restart. A revoked/invalidated reservation cannot be closed; repeated terminal transitions are refused. There is deliberately no EXECUTED state, external dispatch hook, trusted organization credential, KX108 sovereign ticket grant, distributed revocation/dispatch fence or production receipt. Tests cover restart, abandonment, revocation, duplicate close and forbidden execution state.

The receipt is a **local fixture lifecycle hash**, not a provider delivery confirmation and not a cryptographic signature from an independent authority. No main/kernel/Monde changes.

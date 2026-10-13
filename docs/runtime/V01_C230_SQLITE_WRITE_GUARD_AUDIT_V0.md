# C2.30 — SQLite local write-guard audit

Status: DRAFT / FAIL-CLOSED / OFFLINE FIXTURE. Parent C2.29 HEAD 74b0cad7c6a02d1a95c453605415168ac516ec37. C2.28 #37733270389 and C2.29 #37733428154 were QUEUED at initial check; success is not assumed.

Installs local SQLite BEFORE UPDATE/DELETE triggers for the hash-linked event journal and durable receipts, plus a reservation DELETE trigger. Logs can still be appended; normal logged closure is tested. A read-only check verifies named triggers are present but always returns BLOCK. Adversarial tests attempt forbidden event/receipt modifications and remove a trigger to demonstrate detection rather than prevention of privileged tampering.

Limitations: triggers do not guard every possible write (e.g., INSERTs, changes to reservations/scopes, table replacement), and a SQLite database owner can DROP TRIGGER or rewrite database files. A present named trigger does not prove that its SQL body has not been changed. They are not trusted WORM storage, an external cryptographic anchor, or authorization. No execution calls, main merge, kernel, or Monde changes. Next: audit trigger SQL definitions, direct state updates, and verify chain/state consistency before claiming any stronger guarantee.

# C2.3 — durable revocation/replay fixture, not a live authorization gateway

Status: WIP / DRAFT / NO EXECUTION.

Source: C2.2 `cbfc42357e406e613f7a5e12255594f3bd323137`. Previous C2.2 targeted CI runs 37725130044 and 37725126657 SUCCESS.

C2.3 introduces a local SQLite `BEGIN IMMEDIATE` ledger to serialize revocation and nonce consumption among processes sharing one local database. Fixtures test restart persistence, concurrent same-nonce usage and tenant scoping. Denial of revoked or unknown delegations is explicit.

**Safety boundary:** `register_fixture` is neither identity verification nor authenticated enrollment. Caller-provided `evidence_verified=True` can be forged. Thus `CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY` is *never* an execution grant, and the ledger is NOT connected to providers or the WorldAction Gateway. SQLite file on one host does not prove cross-host, network-partition or crash-safe provider dispatch fencing; a dispatch after a check could race with revocation. A compromised local DB or process is outside scope. Key issuance, ticket verification, KX108 attestation and reliable nonce identities are not demonstrated.

Before promotion: real independently verified organization and delegation issuance; persistent nonce and revocation with trusted enrollment, transactional integration at the actual connector entry; verifiable KX108 and SovereignTicket; cross-process/cross-host timing tests, clock validity, provider retries, idempotency and receipts; no LIVE execution until audits pass.

No main merge, no kernel or Monde modification.

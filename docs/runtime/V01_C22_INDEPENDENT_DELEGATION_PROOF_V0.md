# C2.2 independent scoped delegation evidence — prototype

Status: DRAFT / NOT CONNECTOR READY.

C2.1 CI run 37724416609 succeeded on the fail-closed guard. This branch adds an evidence-only verifier for canonical JSON HMAC-SHA256 signatures over issuer, organization, principal, delegate, connector, capability, action hash, expiry, and nonce.

A trusted verifier key is injected by the caller and not persisted. The included signing helper is strictly for fixtures. Signing a payload with a fixture key does NOT establish real corporate authority, identity, protected key custody, delegated rights, or legal consent. The same key is shared by issuer and verifier in this fixture protocol; production requires real trust establishment and key lifecycle.

The verifier returns an integrity/scope verdict, NOT KX108 ALLOW or any connector dispatch permission. C2.1 remains fail-closed even when the fixture proof passes. No real provider, broker, mailbox or kernel is contacted.

Still required: authenticated org/issuer and key registry; independent KX108 and SovereignTicket validation; strict issuance/expiry and nonce replay tracking; durable shared revocation; atomic dispatch fencing and concurrency tests. Never promote the current fixture verification alone to action permission. No main merge.

# V0.1 C2.9 — signed ticket/record binding in fixtures only

Status: DRAFT / FAIL-CLOSED / NO EXECUTION.

Parent C2.8 head `f8ec97805699836f26f5187e5d4ff6d27d2508ad`; its targeted CI #37727444049 succeeded.

C2.8 established that the current SovereignTicket is constructible locally and not authenticated against the KX108 decision-record hash. C2.9 defines a separate **test-only** MAC binding of exact ticket identity/hash and record ID/hash, action, scope, expiry and fixture issuer. It proves what exact-match verification could look like, without modifying SovereignTicket, the kernel or the Gateway. Swapping a ticket, changing the record, altering the issuer, signing with the wrong key or using an expired fixture fails.

Important: HMAC is symmetric and the signing helper accepts a fixture key; possession of this key is not organizational trust. The record object passed to this fixture checker is not independently loaded/verified in this component. C2.8 remains BLOCK even when this fixture signature validates. There is no trusted key enrollment, authenticated organization, ticket issuer, revocation, nonce replay, dispatch fence, or real provider receipt in this new component.

Do not treat any fixture verification success as production readiness or action permission. No main merge, no kernel/Monde modification.

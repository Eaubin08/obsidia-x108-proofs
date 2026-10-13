# V0.1 C2.11 — issuer revocation + ticket binding fixture composition

Status: DRAFT / DENY ONLY / NO LIVE EXECUTION.

Parent C2.10: `6018d915ceec007202713b354d37cb6a46184004`. Targeted CI 37727883734 completed SUCCESS.

This change reuses the C2.10 SQLite issuer registry (including durable revocation), C2.9 HMAC ticket/record test-only binding, and a scoped organization identifier. It verifies issuer enrollment, key digest, revocation state, signature, expiration, ticket ID/hash, decision record ID/hash, exact action and scope. The composite **always returns BLOCK**, even if every fixture matches: `C211_ORGANIZATION_AUTHORITY_UNVERIFIED`.

Tests cover the matching-but-blocked case, revocation surviving a registry reopen, tenant mismatch, substituted record and wrong verifier key.

Security limits: organization identifier is supplied by the caller; registration is fixture-only, not authenticated. HMAC test key is not a production trust root. The supplied decision record here is not independently CG62-verified (C2.7/C2.8 independently cover the real record path), and this method does not replace those checks. There is no real authenticated approver, ticket issuer enrollment, production dispatch, cross-host transactional revocation, or provider receipt. Do not present this fixture composition as a functioning authorization gate.

No merge to main. No kernel, Monde or real connector mutation.

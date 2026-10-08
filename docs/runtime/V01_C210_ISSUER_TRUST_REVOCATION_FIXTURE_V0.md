# V0.1 C2.10 — issuer trust/revocation fixture

Status: DRAFT / WIP / DENY-ONLY / NO LIVE AUTHORITY.

C2.9 targeted CI #37727590117 SUCCESS. C2.10 adds a local SQLite test registry to model issuer enrollment, immutable key digests, tenant-scoped lookups and durable revocation across process restart.

This is a fixture registry, **not verified organizational identity**: `register_fixture` is directly callable and there is no authenticated administrative enrollment, independent issuer verification, key custody, rotation proof, or public-key trust anchor. `FIXTURE_ISSUER_MATCH_NO_ORGANIZATION_AUTHORITY` cannot grant an action or remove the fail-closed C2.8 ticket boundary.

Tests cover restart durability, unknown and revoked issuers, cross-organization isolation, key substitution and immutable enrollment.

Still blocked: independent legal/organizational identity proof and delegated authority; independently authenticated issuer key enrollment and rotation; signing/verification of actual ticket bound to authentic KX108 decision record; atomic revocation across provider dispatch; multi-host execution receipts. Current C2.10 does not call a live connector, mutate kernel, or authorize egress. No main merge or Monde change.

# V0.1 C2 — Organization / Stack Lifecycle (non-sovereign)

Date: 2026-10-08
Branch: `feat/v01-c2-organization-stack-lifecycle-v0`
Parent: `feat/v01-c0-c1-company-model-contract-v0` (PR #86)
Scope: **V0 read-only integration boundaries; never live authorization.**

## Purpose

C2 takes the **actual existing technical contracts**, not invented trust:

```text
C1 Company Model (organizational claims)
  + UniversalEnterpriseStackManifestV0 (provider capabilities)
  + EnterpriseSourceBindingV0 (exact manifest/source mapping)
  + NativeObservedSourceCandidateV0
  + NativeHumanSourceAuthorizationV0 (source approval claim)
  + NativeSourceActivationReceiptV0
  + NativeSourceRegistrationV0 / NativeSourceRegistryV0
                |
                v
  CompanyStackLinkV0 (organization/domain/tool/source/capability scope)
                |
                v
  CompanyStackLifecycleV0 (in-memory registration, inspect, revocation)
```

The new component **reuses** `company_model_v0.py`,
`native_sources/source_onboarding_v0.py`,
`native_sources/source_registry_v0.py` and
`universal_enterprise_stack_adapter_v0.py`.

It is NOT another UDIP, Binder, Relay, permission graph, source adapter,
identity provider, execution rail or UI.

## Contracts

- `CompanyStackLinkV0` binds exact **organization**, C1 snapshot hash,
  domain, tool instance, integration slot, source ID, source registration
  hash, approval hash, activation receipt hash, stack/provider manifest hash,
  canonical source capability and binding hash.
- `CompanyStackLinkRevocationV0` binds revocation reason, link identity,
  a named human (not MACHINE), time and hash.
- `CompanyStackLifecycleV0` holds immutable links and revocations **only
  in memory**. There is no persistence, no background polling, no network.
- `verify_company_stack_link_v0` rechecks source activation/registration,
  binding and manifest hashes, company graph, declared org relations,
  scope and revocation state when inspected.
- `integration_slot_id` identifies one logical connection within an
  organization's stack. Two mailboxes sharing one capability can use
  distinct slots. A provider replacement for the **same slot** first
  requires an explicit revocation, a new bound provider manifest and a
  new source authorization/registration.

No `CAPABILITY` → `PERMISSION` or `HUMAN_APPROVAL` → `ORG_OWNERSHIP`
implicit promotion. A source's existing human approval does NOT attest that
the human can bind the entire enterprise.

```ini
organization_authority_verified = false
has_runtime_permission = false
allows_provider_calls = false
allowed_to_decide = false
allowed_to_act = false
decision_authority = KX108_ONLY
```

`LINKED_READONLY_NO_ORGANIZATION_AUTHORITY` means internal contractual
consistency under supplied evidence only. It **never** authorizes reading
Gmail, Drive, ERP, physical GNSS sensors, bank, trading or other providers.

## Fail-closed criteria

- foreign company graph, missing company/domain/tool/source nodes or
  required declared relations;
- source identity/provider/capabilities do not match provider binding;
- manufactured or tampered human approval, activation receipt, registration,
  provider manifest or link hash;
- source not in canonical NativeSourceRegistryV0 or already revoked;
- cross-organization source reassignment (no silent sharing);
- a second provider replacing an active integration slot without revocation;
- a revoked link cannot silently become active again;
- any authority flag or claimed organizational ownership promoted to true.

A registration for a source can be **technically** consistent but does
not confer legal ownership or downstream connector permission.

## Test surface

`tests/integration/test_v01_c2_organization_stack_lifecycle_v0.py`

Real upstream native source objects and hashes are assembled inside
temporary fixture directories. Different companies, sources and provider
manifests are confronted with the same lifecycle contract. No actual
external systems are contacted. Regression includes C1, universal stack
adapter, native source onboarding and existing cross-domain conformance.

## Remaining C2 debt / C3 gates

1. **Independent enterprise identity attestation** and verified delegated
   representative roles (beyond a source-level approver claim).
2. Durable, replayable, tenant-partitioned lifecycle stores/consent history,
   access control and revocation checks at every actual provider entry.
3. Explicit expiry/freshness and operator access semantics verified against
   the organization's real policies.
4. A production-grade *organization-scoped permission gate* integrated with
   existing KX108/Binder/runtime authorization rail, rather than this
   observation-only registry.
5. Negative race tests and replay of source/manifest changes across restarts.
6. C3 governed multi-org/multi-domain sandbox E2E and separate C4 métier
   evidence (Trading PAPER, GPS observation, CSSA public/shadow).

This C2 cannot be labeled production, identity-verified, runtime-enforced
multitenancy, or universal enterprise deployment. It does **not** change
the 2026-10-08 architectural decision to postpone Monde (C5).

No main merge, kernel mutation, credential access or provider calls.

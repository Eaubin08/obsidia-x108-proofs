# V0.1 C2.1 — Connector identity / delegation / revocation boundary

Status: **DENY_ONLY_PROTOTYPE / NOT LIVE AUTHORITY / NOT CLOSED**

Base: C4.2.1 commit `314542254be27e252e866547826d21a05f7c3378`.

## Reuse audit

- C1 Company Model provides evidence-backed organizational declaration, not authentication.
- C2 `enterprise_org_stack_lifecycle_v0.py` already enforces organization scoping, source identity, immutable revocation and provider swap in its *read-only* lifecycle. It explicitly sets organization_authority_verified and runtime_permission to false.
- Universal Enterprise Stack Adapter binds capabilities and provider manifests; binding is not a permission.
- KX108 / WORLD_ACTION / SovereignTicket / Gateway remain distinct decision and execution controls.

## New narrow prototype

`periphery/enterprise_connector_entry_revocation_guard_v0.py` is a deny-only, in-memory *pre-dispatch check*. It rejects absent claimed attestations, mismatched tenant/connector/capability, stale generation and revoked delegation. Even if all caller-provided flags are true, the result is now `BLOCK:C21_INDEPENDENT_ATTESTATION_VERIFIER_NOT_BOUND`. No permissive fallback exists. No provider transport, credential storage, KX108 changes or connector invocation is added.

Tests cover revocation after a prior pass, cross-tenant isolation, mismatch, missing claims and generation staleness.

## Critical limitations / next gate

The booleans `organization_verified`, `delegation_verified`, `ticket_verified` and `kx108_allow_verified` are caller-provided *placeholders*, **not verified signatures or authoritative facts**. The current component is NOT safe as a live execution gate. A caller can assert these booleans. It must only be used in isolated simulation.

Required before runtime promotion:

1. Replace booleans with independently verified identity, organizational authority and delegation proof, cryptographically bound to exact principal/tenant/scope/binding/expiry.
2. Verify KX108 decision and SovereignTicket through their existing verifiers, not external claims.
3. Bind the check to the actual connector dispatch boundary and establish coherent atomic revocation semantics (shared transactional state or generation fencing); this in-memory lock does not cover in-flight network effects or other processes.
4. Test expiration, signature tampering, replay, concurrent revocation, process restart, provider failure, tenant swap and stale authorization.
5. Keep `main`, protected kernel, Monde and live connectors untouched.

C2.1 prototype cannot be declared closed solely from targeted CI.

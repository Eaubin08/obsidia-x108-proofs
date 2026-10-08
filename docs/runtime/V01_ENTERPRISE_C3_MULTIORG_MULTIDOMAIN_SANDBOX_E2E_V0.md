# V0.1 C3 — Multi-organization / multi-domain sandbox composition

Date: 2026-10-08
Branch: `feat/v01-c3-multiorg-multidomain-sandbox-e2e-v0`
Parent: `feat/v01-c2-organization-stack-lifecycle-v0` (PR #88)
Authority: `KX108_ONLY`

## Goal and reality boundary

Test the **universal conjunction**, not a fourth business-specific framework.

```text
Organization A / Organization B  [fixture only]
   ↳ Domain admin / Domain trading [separate UDIP semantics]
   ↳ Different provider-native / provider-external sandbox
   ↳ C1 organizational claim graph
   ↳ C2 explicit source registration/authorization/activation + live revocation check
   ↳ C3 tenant- and source-link-scoped proposal
   ↳ existing UniversalEnterpriseActionBinding + WORLD_ACTION request
   ↳ existing exact human approval + real GuardX108 PRE
   ↳ existing sandbox-scoped activation policy + sovereign ticket
   ↳ existing deterministic NO-NETWORK bounded executor
   ↳ append-only receipt and replay, duplicate blocked
```

The only new runtime module, `periphery/enterprise_governed_sandbox_preflight_v0.py`,
**prepares** a non-sovereign, explicitly tenant-bound request. It invokes
`CompanyStackLifecycleV0.inspect()`, verifies the exact provider stack against
the approved *source* link, refuses domain/organization mismatch and unsafe
irreversible proposals, salts action identity by organization and binds the
source-link hash into the proposal. It never calls GuardX108, issues permission,
creates receipts, issues tickets or invokes an external provider.

The tests use the pre-existing *real* `run_world_action_pre_execution_v0`
implementation and unchanged sandbox connector executor. Only simulated
sources/approvals/providers are supplied, with zero network and zero external
effect. `C3` does **not** promote C2 source approval into organization-level
authorization or runtime action permission.

## Evidence matrix

| Path | Outcome sought |
|---|---|
| Organization A, Administration, native sandbox | KX ALLOW -> simulated receipt/replay |
| Organization A, Trading TASK risk review, native sandbox | KX ALLOW -> simulated receipt/replay, no order |
| Organization B, Administration, external sandbox | KX ALLOW -> simulated receipt/replay |
| Organization B, Trading TASK risk review, external sandbox | KX ALLOW -> simulated receipt/replay, no order |
| Shared tenant lifecycle, two domains | one claim-graph hash within organization, different between organizations |
| Cross-company same intent | different scoped action/proposal/request/idempotency hashes |
| Native source revoked | new C3 preparation refused |
| Link revoked | new C3 preparation refused |
| Domain borrowed across source link | refused before Guard |
| Provider drift/manifest mismatch | refused before Guard |
| Foreign `organization_id` in proposed payload | refused before Guard |
| Irreversible candidate | refused before Guard |
| Duplicate connector attempt | no second adapter invocation |
| Receipt replay | deterministic integrity check; never new execution |

## Strict non-claims and unfinished security work

1. `organization_authority_verified=false`; source human source approval is not
   legal or institutional ownership evidence.
2. In-memory C2 lifecycle is not cross-process, durable, transactional or
   cryptographically attested. This C3 preflight is **not** a production
   authorization check at the actual LIVE connector entry point.
3. Repeating C2 preflight before sandbox ticket and connector invocation is an
   explicit test protocol, **not** a proof that a provider gateway enforces
   revocation atomically under races. Previously created sovereign tickets
   must not be claimed invalidated by C3 source revocation.
4. Org-specific proposal hashes guard the C3 simulation flow, not every
   existing production source/action interface. No real tenant data enters.
5. The example's Trading action is creation of a **simulated risk-review task**,
   not a broker order. GPS actual physical domain belongs in C4; no RF control.
6. No claim of verified real-world organizational before/after benefit,
   enterprise production readiness, regulatory clearance or full universality.
7. No Monde/C5 work, main merge, new kernel, Binder or domain semantics.

## Remaining after C3

- **C2 production-security gap**: independently verifiable corporate identity
  and delegated representatives, revocable durable identity/capability grants,
  enforcement at gateway/provider source boundaries, transactional and
  multi-process isolation, tenant-bound tickets/receipts, safe key management.
- **C4 domain realism**: GPS/Defense/Aviation actual observation payloads
  (RealityAuthenticityGate), Trading domain actual PAPER proof path and CSSA
  public/shadow constraints, each measured without overclaiming.
- C5 Monde remains deferred as requested.

Proof source:
`tests/integration/test_v01_c3_multiorg_multidomain_sandbox_e2e_v0.py`
plus existing universal cross-domain, C0/C1, C2 and SOURCE_RUNTIME tests.

# UNIVERSAL_ENTERPRISE_STACK_ADAPTER_V0

Date: 2026-10-07

Branch:
`feat/universal-enterprise-stack-adapter-v0`

Base:
`feat/enterprise-office-full-loop-e2e-v0`

## Purpose

Allow an enterprise to keep its existing software stack while entering the
same governed Obsidia loop.

Provider/tool/connector bindings are peripheral and replaceable.

The invariant Obsidia rail remains:

```text
canonical source/work/action
→ WORLD_ACTION_PRE
→ KX108_ONLY
→ activation policy
→ sovereign ticket
→ bounded executor
→ immutable receipt
→ replay
```

## Universal boundary

A provider declares a manifest of canonical capabilities.

Examples:

```text
SOURCE.MAIL.READ
SOURCE.API.READ
CALENDAR.EVENT.CREATE
CRM.RECORD.UPDATE
```

The core does not need a Google-, Microsoft-, Salesforce-, HubSpot- or
Odoo-specific business rule.

## Stable intent vs provider binding

For one canonical ActionCandidate:

```text
stable_business_intent_hash
        │
        ├── provider binding A
        ├── provider binding B
        └── provider binding C
```

The stable intent is provider-neutral.

Each provider binding carries only peripheral facts such as:

- provider / stack identity
- connector id
- connector action
- required scope
- connector args
- target ref / prestate
- adapter ref

Therefore:

```text
same ActionCandidate
same capability
same stable_intent_hash
same proposal_hash

different provider
different binding_hash
different WorldActionRequest hash
```

Changing provider does not mutate the canonical business intent.

## Proven provider swap

Three simulated calendar stacks expose the same canonical capability:

`CALENDAR.EVENT.CREATE`

with different peripheral bindings:

- Google-like
- Microsoft-like
- Custom/CalDAV-like

All three produce:

```text
same stable intent
→ provider-specific WorldActionRequest
→ exact HumanApproval
→ WORLD_ACTION_PRE
→ KX108 ALLOW
→ provider-specific activation policy
→ LiveSovereignTicket
→ bounded sandbox executor
→ receipt
→ replay OK
```

Observed KX108 gates:

```text
GOOGLE_LIKE     ALLOW
MICROSOFT_LIKE  ALLOW
CUSTOM_LIKE     ALLOW
```

No real provider is called.

## Inbound stack support

The same manifest model supports provider-neutral source bindings.

A source capability maps an enterprise tool to the existing native source
runtime without changing SOURCE_RUNTIME itself.

Examples proven:

```text
SOURCE.MAIL.READ
→ MAILBOX
→ SEARCH + READ_MESSAGE

SOURCE.API.READ
→ API_READONLY
→ READ_API_RESOURCE
```

`SOURCE.API.READ` is the generic V0 entry boundary for an ERP, internal
service or other enterprise system that does not yet have a specialized
native source connector.

Semantic interpretation for a new métier remains a separate domain concern;
the integration boundary does not invent business meaning.

## Non-calendar proof

A separate CRM ActionCandidate is bound through the exact same universal
contract:

```text
CRM.RECORD.UPDATE
→ CUSTOM_CRM
→ PATCH_RECORD
→ canonical WorldActionRequest
```

Therefore the adapter contract is not calendar-specific.

## Fail closed

The adapter refuses:

- missing canonical capability
- source capability unavailable
- surface mismatch
- operation mismatch
- invalid target prestate hash
- secret/credential-like connector fields
- capability escalation on readonly source contracts

It persists no raw credentials.

## Authority

```ini
allowed_to_decide = false
allowed_to_act = false
emits_act = false
decision_authority = KX108_ONLY
```

Provider manifests and bindings cannot authorize execution.

## Functional proof

Workflow:
`37643201046`

Result:
`127 passed in 2.61s`

The suite covers the universal adapter plus upstream full-office, source,
intake, native CRM/TASKS, WORLD_ACTION_PRE, LIVE Gateway, bounded executor and
multi-métier conformance paths.

## Product meaning

The enterprise does not have to migrate its operational software to gain the
Obsidia governance rail.

```text
existing enterprise tool
→ adapter / capability binding
→ Obsidia canonical intent
→ KX108 governance
→ adapter / capability binding
→ existing enterprise tool
→ receipt / replay
```

## Next boundary

`MONDE_OBSIDIA_NATIVE_READ_MODEL_V0`

The read model may now consume canonical/provider-neutral objects while still
showing the currently bound provider as metadata. It must not duplicate
provider resolution, interpretation, decision or execution logic.

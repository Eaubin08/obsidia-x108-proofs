# UDIP Source Taxonomy V0

Status: CANONICAL_DOCUMENTATION_V0
Runtime impact: NONE
Authority impact: NONE

## 1. Purpose

UDIP needs to describe source provenance without confusing four different questions:

```text
Where does the Domain Pack source set come from?
What kind of artifact is each source?
How mature is each source artifact?
What role does each source play for this domain?
```

V0 therefore separates:

```text
source_type
source_classes
source_maturity
source_roles
```

These fields are descriptive only.

They do not create trust, authority, runtime integration or implementation maturity.

## 2. Universal source invariants

```text
SOURCE != TRUST
SOURCE != AUTHORITY
SOURCE_PRESENT != RUNTIME_INTEGRATED
REFERENCE != DEPENDENCY
CODE_PRESENT != UDIP_RUNTIME_INTEGRATED
SPEC_PRESENT != SPEC_IMPLEMENTED
TEST_PRESENT != PROOF
INTERNAL_CONCEPT_SOURCE != CANONICAL_IMPLEMENTATION
AUDIT_SOURCE != DOMAIN_OWNERSHIP
```

## 3. Domain-level `source_type`

`source_type` describes the **composition of the Domain Pack source set**.

Allowed V0 values:

### `none`

No audited source set has been declared.

Typical companion status:

```yaml
status: NOT_YET_DEFINED
source_type: none
sources: []
```

### `repo_reference`

The audited reference set is located in the current repository.

This does not mean the sources are active runtime dependencies.

### `repo_partial_reference`

The source set is in the current repository but known to be incomplete for the domain.

Ecom is the current V0 example.

### `external_reference`

A primary reference exists outside the current repository.

Local repository files may still accompany it.

Trading is the current V0 example.

### `mixed_reference`

The audited set intentionally combines more than one provenance family, such as:

- repository source;
- internal concept source;
- external source.

Telecom and Energy are the current V0 examples.

## 4. `sources.yaml status`

Allowed V0 values:

### `NOT_YET_DEFINED`

No audited source set.

### `REFERENCE_ONLY`

A source map exists for reference/migration purposes, but the Domain Pack is not claiming an audited source perimeter equivalent to the newer rich packs.

### `AUDITED_REFERENCE_SET`

The source set has been explicitly audited and classified for Domain Pack documentation.

This does not imply runtime integration.

## 5. Per-source `source_classes`

`source_classes` answers:

> What kind of artifact is this source?

Allowed V0 values:

### `EXTERNAL_REPOSITORY_SOURCE`

Repository or project outside the current Git repository.

### `INTERNAL_CONCEPT_SOURCE`

Internal project note, design document or historical concept source not stored as a canonical file in this repository.

### `REPO_DOMAIN_SOURCE`

Repository path representing an existing domain implementation/reference surface.

### `REPO_CODE_SOURCE`

Executable/source code used as reference evidence.

### `REPO_SPEC_SOURCE`

Specification or contract-like design specification.

### `REPO_ARCHITECTURE_SOURCE`

Architecture/doctrine document.

### `REPO_CONTRACT_SOURCE`

Boundary/contract artifact.

### `REPO_AUDIT_SOURCE`

Audit, inventory or forensic source.

### `REPO_TEST_SOURCE`

Test, test report or test harness source.

### `REPO_FIXTURE_SOURCE`

Fixture/example/data sample used as reference evidence.

### `REPO_DOCUMENT_SOURCE`

General repository document that does not fit a more specific class.

## 6. Per-source `source_maturity`

`source_maturity` answers:

> What is the maturity/status of this source artifact itself?

It does **not** describe Domain Pack maturity.

Allowed V0 values:

### `EXTERNAL_REFERENCE`

External reference exists; its runtime state is outside this repository.

### `REFERENCE_ONLY`

Artifact is used as reference without an implementation claim.

### `PARTIAL_REFERENCE`

Artifact/source set is explicitly incomplete.

### `IMPLEMENTED_REFERENCE_CODE`

Real source code exists.

This does not imply that the code is integrated into the UDIP runtime.

### `VALIDATED_SPEC`

The source itself explicitly declares a validated spec status.

### `RUNTIME_INACTIVE`

The source explicitly declares runtime inactive.

### `CONTRACT_SKELETON_ONLY`

The source explicitly declares a contract skeleton status.

### `TO_VALIDATE`

The source explicitly requires validation.

### `TO_FORMALIZE_OR_PROVE`

The source explicitly requires formalization/proof.

### `AUDIT_REFERENCE`

Audit/inventory evidence used as reference.

### `PLACEHOLDER_ONLY`

The artifact exists but does not substantively prove the claimed behavior.

### `INTERNAL_CONCEPT_ONLY`

Internal concept/design source; not canonical implementation.

## 7. `source_roles`

`source_roles` is Domain Pack-specific free text.

It answers:

> Why does this Domain Pack reference this source?

Examples:

```yaml
source_roles:
  "periphery/energy_thermo.py": thermo_compute_metrics_and_risk_signals
  "docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md": network_egress_and_connector_risk_audit
```

Roles do not need a universal enum.

## 8. Canonical `sources.yaml` shape

### Audited source set

```yaml
status: AUDITED_REFERENCE_SET
source_type: repo_reference
sources:
  - "path/to/source"

source_classes:
  "path/to/source": REPO_SPEC_SOURCE

source_maturity:
  "path/to/source": TO_VALIDATE

source_roles:
  "path/to/source": domain_specific_reason

boundaries:
  - "SOURCE != TRUST"
  - "REFERENCE != RUNTIME_DEPENDENCY"

note: "..."
```

### Reference-only source set

```yaml
status: REFERENCE_ONLY
source_type: repo_reference
sources:
  - "path/to/reference"

source_classes:
  "path/to/reference": REPO_CODE_SOURCE

source_maturity:
  "path/to/reference": IMPLEMENTED_REFERENCE_CODE

source_roles:
  "path/to/reference": historical_domain_reference
```

### Empty scaffold

```yaml
status: NOT_YET_DEFINED
source_type: none
sources: []
source_classes: {}
source_maturity: {}
source_roles: {}
note: "CURRENT SOURCES: NONE / NOT YET AUDITED"
```

## 9. Legacy class normalization

The following older labels are normalized in V0.

| Legacy label | Canonical class | Canonical maturity |
|---|---|---|
| `REPO_SOURCE` | choose specific `REPO_*_SOURCE` | choose explicit maturity |
| `REPO_SOURCE_AUDIT` | `REPO_AUDIT_SOURCE` | `AUDIT_REFERENCE` |
| `REPO_CONTRACT_SKELETON` | `REPO_CONTRACT_SOURCE` | `CONTRACT_SKELETON_ONLY` |
| `REPO_SPEC_RUNTIME_INACTIVE` | `REPO_SPEC_SOURCE` | `RUNTIME_INACTIVE` |
| `REPO_SPEC_TO_VALIDATE` | `REPO_SPEC_SOURCE` | `TO_VALIDATE` |
| `REPO_SPEC_TO_FORMALIZE_OR_PROVE` | `REPO_SPEC_SOURCE` | `TO_FORMALIZE_OR_PROVE` |
| `REPO_TEST_PLACEHOLDER` | `REPO_TEST_SOURCE` | `PLACEHOLDER_ONLY` |

The reason for normalization is structural:

```text
class = what the artifact is
maturity = how mature the artifact is
```

These axes must not be collapsed.

## 10. V0 current Domain Pack source types

| Domain Pack | source_type |
|---|---|
| Trading | `external_reference` |
| Bank | `repo_reference` |
| GPS / Defense / Aviation | `repo_reference` |
| Ecom | `repo_partial_reference` |
| Cybersecurity | `repo_reference` |
| Energy / Critical Infrastructure | `mixed_reference` |
| Legal / Compliance | `repo_reference` |
| Telecom | `mixed_reference` |
| Industry / Maintenance | `none` |
| BTP / Construction | `none` |
| Logistics / Supply Chain | `none` |
| Insurance | `none` |
| Facility Management | `none` |
| Administration | `none` |
| Health | `none` |
| HR | `none` |

## 11. Relationship to Domain Pack status

These dimensions are independent.

Example:

```text
source_type = repo_reference
implementation_state = SCAFFOLD_ONLY
```

is valid.

A rich source set does not promote implementation maturity.

Similarly:

```text
source_maturity = IMPLEMENTED_REFERENCE_CODE
```

means only that real code exists at that source path.

It does not mean:

- UDIP adapter exists;
- object map exists;
- KX108 path is integrated;
- Binder is integrated;
- runtime is promoted.

## 12. Relationship to object mapping

Sources precede objects:

```text
source inventory
→ source classification
→ source maturity
→ source role
→ object candidate audit
→ object evidence freeze
→ object_map
```

No object should be invented merely because a source exists.

## 13. Relationship to provenance / reality

`source_type`, `source_classes` and `source_maturity` describe **document/code provenance**.

They do not establish physical authenticity.

For physical domains:

```text
SourceProvenance
!=
RealityAuthenticity
```

## 14. Change rule

A new `source_type`, `source_class` or `source_maturity` value must not be introduced ad hoc inside one Domain Pack.

It must first be:

1. justified by a concrete source;
2. checked against existing taxonomy;
3. added here;
4. then used by the Domain Pack.

## 15. Final rule

```text
source_type     = composition of the source set
source_class    = nature of one source artifact
source_maturity = maturity/status of that artifact
source_role     = why this domain references it
```

None of these fields carries authority.

# Migration Plan V1

Status: NOT_AUTHORIZED_YET

No move/delete/rename is allowed before semantic registry validation.

Required before migration:

- FILES_UNCLASSIFIED = 0
- MODULES_UNCLASSIFIED = 0
- FUNCTIONS_UNCLASSIFIED = 0
- FUNCTIONALITIES_WITHOUT_OWNER = 0
- ACTIVE_SOURCE_WITHOUT_TARGET = 0
- UNKNOWN_RUNTIME_STATUS = 0
- UNKNOWN_AUTHORITY = 0

Then validate vertical slices:

1. X108
2. Brody
3. GPS

Only after that create the physical migration branch.

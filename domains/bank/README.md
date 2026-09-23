# Bank  Financial services governance reference for payments, transfers, fraud, compliance, and audit boundaries.  ## Status  EXISTING_REFERENCE  ## Historical Sources 
- domain_packets/bank_decisional_form_v0.yaml
- domains/bank/
- sigma/domains/bank_agents.py
- examples/bank_normal.json
- examples/bank_suspicious.json

## Proven / Known Elements

- Domain-specific semantics stay in this domain.
- The domain owns no authority.
- KX108 remains the admission authority.

## Missing / Not Implemented

- UDIP-native domain_pack adaptation
- Core-neutral object map
- No runtime migration yet

## UDIP Boundary

This scaffold is a Domain Pack boundary. It must not create a parallel authority, bypass KX108, bypass Binder for governed execution, or leak business semantics into udip/.

## Possible Domain Extensions

- fraud
- compliance
- bank_policy

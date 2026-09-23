# GPS / Defense / Aviation  Safety-critical physical-world reference for reality authenticity, fail-closed behavior, and proof surfaces.  ## Status  EXISTING_REFERENCE  ## Historical Sources 
- domain_packets/gps_defense_aviation_decisional_form_v0.yaml
- domains/gps/
- sigma/domains/gps_defense_aviation_agents.py

## Proven / Known Elements

- Domain-specific semantics stay in this domain.
- The domain owns no authority.
- KX108 remains the admission authority.

## Missing / Not Implemented

- UDIP-native domain_pack adaptation
- Conditional physical extension mapping
- No runtime migration yet

## UDIP Boundary

This scaffold is a Domain Pack boundary. It must not create a parallel authority, bypass KX108, bypass Binder for governed execution, or leak business semantics into udip/.

## Possible Domain Extensions

- reality_authenticity
- sensor_attestation
- anti_replay
- physical_envelope

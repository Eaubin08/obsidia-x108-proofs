# Trading  Reference financial markets domain. Historical reference architecture only; trading vocabulary remains domain-specific.  ## Status  EXISTING_REFERENCE  ## Historical Sources 
- external://OBSIDIA_TRADING
- domains/trading/
- domain_packets/trading_decisional_form_v0.yaml
- sigma/domains/trading_agents.py

## Proven / Known Elements

- Domain-specific semantics stay in this domain.
- The domain owns no authority.
- KX108 remains the admission authority.

## Missing / Not Implemented

- UDIP-native domain_pack adaptation
- Core-neutral object map
- Wrapper around historical execution surfaces

## UDIP Boundary

This scaffold is a Domain Pack boundary. It must not create a parallel authority, bypass KX108, bypass Binder for governed execution, or leak business semantics into udip/.

## Possible Domain Extensions

- market_data
- portfolio
- broker_execution

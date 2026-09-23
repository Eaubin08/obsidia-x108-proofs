# Ecom  Partial e-commerce reference for customer/order/stock/fulfillment signals and outbound-service dry-run boundaries.  ## Status  PARTIAL_REFERENCE  ## Historical Sources 
- sigma/domains/ecom_agents.py
- examples/ecom_normal.json
- tests Ecom if present

## Proven / Known Elements

- Domain-specific semantics stay in this domain.
- The domain owns no authority.
- KX108 remains the admission authority.

## Missing / Not Implemented

- No complete Domain Pack yet
- No payment/refund implementation
- No execution adapter implementation

## UDIP Boundary

This scaffold is a Domain Pack boundary. It must not create a parallel authority, bypass KX108, bypass Binder for governed execution, or leak business semantics into udip/.

## Possible Domain Extensions

- customer
- order_intent
- payment_provider
- compensation_ref

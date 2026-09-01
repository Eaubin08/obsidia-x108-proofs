# CG9 Provider Cognitive Binder
# Governance Specification V1


## Purpose

CG9 is the provider governance layer of Obsidia.

Its role is to allow cognitive providers to operate inside Obsidia without receiving decision authority.


## Core Principle

Provider produces.

KX108 decides.

Proof validates.


## Provider Restrictions

A provider MUST NOT:

- make decisions
- emit ACT
- write memory
- mutate kernel
- override KX108


## Provider Allowed Actions

A provider MAY:

- generate outputs
- provide analysis
- execute bounded computation
- return results


## Governance Lifecycle

Provider lifecycle:

DECLARED

VALIDATED

ENABLED

INVOKABLE


Execution lifecycle:

CREATED

AUTHORIZED

RUNNING

COMPLETED

CLOSED


## Receipts

CG9 maintains bounded evidence:

- invocation receipt
- authorization receipt
- runtime receipt
- result binding
- performance receipt
- reliability receipt


## Authority Model

Decision authority:

KX108 ONLY


Provider authority:

NONE


## Conformance

A CG9 provider implementation must preserve:

decision_authority=False

memory_write=False

kernel_mutation=False

emits_act=False

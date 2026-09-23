# Language Module

**Status:** FIRST_CLASS_X108_MODULE — ROUTING ONLY
**Source:** `periphery/language/`
**Tests:** `tests/periphery/test_language_router_boundary_preserved.py`

## Role
Language detection and routing. Routes queries to appropriate response pipelines while preserving language boundaries. Never decides, never emits ACT. Language = context, context = signal.

## Status
**ROUTING_ONLY** — Routes context. X108 decides.

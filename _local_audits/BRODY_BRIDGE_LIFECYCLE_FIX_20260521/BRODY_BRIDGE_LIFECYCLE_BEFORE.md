# BRODY_BRIDGE_LIFECYCLE_BEFORE — 2026-05-21

## Status: BRODY_BRIDGE_LIFECYCLE_BEFORE_AUDIT_PASS

## Lifecycle gaps identified

### Gap 1 — Two bus instances (critical)
- `main.py:14` calls `build_standard_bus()` which creates `UniversalEventBus()` — a NEW instance
- `get_bus()` singleton is a SEPARATE instance (never used by main.py)
- AuditMiddleware would call `get_bus()` on a different instance than the one in main.py
- Result: Brody would never receive HTTP audit events

### Gap 2 — AuditMiddleware does NOT publish to bus
- `apps/obsidia_api/audit_middleware.py` writes JSONL only
- No `get_bus().publish_nowait()` call
- Result: events never enter the bus pipeline

### Gap 3 — BrodyBridge has broken imports
- `from agents.brody_generator import NLG_Core` — module does not exist
- `from value_models.OS_Trad import OS_Trad_Engine` — module does not exist
- `from formalism.Langue_Uni import Langue_Uni_Formal` — module does not exist
- No inline fallbacks
- Result: `import periphery.brody_bridge` raises ImportError

### Gap 4 — BrodyBridge.subscribe() wrong signature
- `self.bus.subscribe('OS_TRAD_CONTEXT', self.handle_bridge)` — passes TWO args (topic + handler)
- Our `UniversalEventBus.subscribe()` takes ONE arg (handler only)
- Result: TypeError at construction time

### Gap 5 — No attach_to_bus() method
- No `attach_to_bus(bus=None)` on BrodyBridge
- No idempotency guard
- Result: mandate's `ensure_brody_bridge_registered()` cannot be implemented

### Gap 6 — BrodyBridge not registered at startup
- No call to `BrodyBridge.attach_to_bus()` anywhere in main.py lifespan
- No `ensure_brody_bridge_registered()` function exists
- Result: even if the bridge were fixed, it would never be wired to the bus

## Files to patch
- `periphery/brody_bridge.py` — full rewrite with fallbacks + correct API
- `apps/obsidia_api/brody_bridge_lifecycle.py` — NEW: ensure_brody_bridge_registered()
- `apps/obsidia_api/main.py` — use get_bus() singleton + call ensure_brody_bridge_registered at startup
- `apps/obsidia_api/audit_middleware.py` — add get_bus().publish_nowait() call

## Protected files — confirmed untouched
- sigma/ — not touched
- proofs/lean/ — not touched
- formal/tla/ — not touched
- merkle_seal.json — not touched
- kernel X108 — not touched

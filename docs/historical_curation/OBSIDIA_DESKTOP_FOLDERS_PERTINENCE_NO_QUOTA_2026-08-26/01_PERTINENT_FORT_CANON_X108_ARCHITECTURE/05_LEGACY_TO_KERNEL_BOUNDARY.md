# Legacy to Kernel Boundary Mapping

Legacy cognitive modules from the Obsidia project serve as context providers, advisors, memory stores, symbol manipulators or narrative engines. None of these modules have the authority to execute irreversible actions.

This document explains how to map legacy concepts into modern roles under the KX108 sovereign kernel model.

## Roles
- **Context Signal**: Components that produce signals about the current context, such as perception, reasoning or memory recall.
- **Advisor**: Components that generate recommendations, hypotheses or warnings.
- **Memory Retrieval**: Modules that access and return memory packets.
- **Output Intent**: Components that create output intentions (cristal) to be evaluated by the kernel.
- **Action Candidate**: Modules that propose world actions but require KX108 approval.

## Mapping Examples
- **Reasoning Modules (T1/T11)** → advisory: produce hypotheses and context signals; cannot decide actions.
- **Agents (T2)** → context providers: spawn/despawn to gather knowledge; no ACT authority.
- **Portals (T7)** → trigger detectors: unlock memory or agents; never authorize actions.
- **Cristal de Sortie (T6)** → output intent builder: deliver candidate outputs for user or world; subject to KX108.
- **Memory modules (B12)** → memory retrieval: provide read-only memory packets to reasoning loops; cannot mutate the kernel state.

Legacy modules may be creative, influential or directive but remain outside the realm of action execution. Any irreversible action must originate as a world_action_candidate and pass through KX108 for approval.

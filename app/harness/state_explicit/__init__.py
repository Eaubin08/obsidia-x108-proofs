"""B6 State-Explicit Harness: SENS -> working state -> query projection -> context packet.

READ_ONLY, NON_SOVEREIGN, deterministic, inspectable, replayable. Decision authority stays
KX108_ONLY: nothing here decides, authorizes, acts, writes memory, mutates the kernel or calls
Neo4j / Graphiti.
"""
from app.harness.state_explicit.capabilities import DisclosureLevel, disclose
from app.harness.state_explicit.context_assembly import ContextPacket, assemble_context
from app.harness.state_explicit.contracts import BOUNDARY, StateEntry, StateStatus, Visibility, render_entry
from app.harness.state_explicit.instructions import DEFAULT_INSTRUCTIONS, Instruction, select_instructions
from app.harness.state_explicit.memory_adapter import native_memory_state_entries
from app.harness.state_explicit.projection import ProjectedState, Relevance, project
from app.harness.state_explicit.registry import DuplicateStateError, WorkingStateRegistry
from app.harness.state_explicit.sens_adapter import sens_state_entries

__all__ = ["BOUNDARY", "ContextPacket", "DEFAULT_INSTRUCTIONS", "DisclosureLevel", "DuplicateStateError",
           "Instruction", "ProjectedState", "Relevance", "StateEntry", "StateStatus", "Visibility",
           "WorkingStateRegistry", "assemble_context", "disclose", "native_memory_state_entries", "project",
           "render_entry", "select_instructions", "sens_state_entries"]

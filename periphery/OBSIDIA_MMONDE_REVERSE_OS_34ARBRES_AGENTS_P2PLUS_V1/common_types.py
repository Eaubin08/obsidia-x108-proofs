"""
common_types.py
----------------

This module defines a collection of simple dataclasses used across the
Obsidia Mmonde / Reverse OS implementation.  These structures are
minimal and are deliberately free of business logic: they serve only as
typed containers for data passed between the various layers of the
system.  None of these classes implement any decision logic.

By defining these types in a single place we simplify imports and
make it clear which pieces of the system are data-only.  Should
additional fields or behaviours be required in the future they can be
added here without affecting the rest of the codebase.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Tree:
    """Representation of a single cognitive tree dimension.

    Attributes:
        id: A numeric or string identifier for the tree.
        name: The human-readable name of the tree.
        family: The category or family this tree belongs to (e.g. "Cognitive").
        definition: A short definition of the tree's purpose.
        activation_keywords: Keywords or phrases that hint at activation.
        related_trees: Identifiers of other trees this one is commonly linked to.
    """

    id: str
    name: str
    family: str
    definition: str = ""
    activation_keywords: List[str] = field(default_factory=list)
    related_trees: List[str] = field(default_factory=list)


@dataclass
class TreeSpace34:
    """Container for the 34-dimensional cognitive space.

    The `dimensions` field holds the canonical names/IDs of the 34 trees
    while `values` represents the activation vector associated with a
    particular event or context.  Values should always be between 0 and 1.
    """

    dimensions: List[str]
    values: List[float]

    def __post_init__(self) -> None:
        if len(self.dimensions) != 34:
            raise ValueError("TreeSpace34 must have exactly 34 dimensions")
        if len(self.values) != 34:
            raise ValueError("Activation vector must have 34 values")
        # Clamp values to [0, 1]
        self.values = [max(0.0, min(1.0, float(v))) for v in self.values]


@dataclass
class ActivationVector:
    """Wrapper around a list of activation values for the 34 trees."""

    values: List[float]

    def __post_init__(self) -> None:
        if len(self.values) != 34:
            raise ValueError("ActivationVector must have 34 values")
        self.values = [max(0.0, min(1.0, float(v))) for v in self.values]


@dataclass
class Event:
    """Simple event representation for the world timeline."""

    id: str
    label: str
    date: str
    narrative: str = ""
    sources: List[str] = field(default_factory=list)
    validation: float = 0.0
    coherence: float = 0.0
    tree_activations: Optional[ActivationVector] = None


@dataclass
class NodeContinuum:
    """Representation of a continuum node in the temporal/cognitive space."""

    id: str
    events: List[str] = field(default_factory=list)
    description: str = ""
    non_decision: bool = True


@dataclass
class SpectralHash:
    """Container for spectral hash produced by Shazam."""

    payload_hash: str
    features: Dict[str, float] = field(default_factory=dict)


@dataclass
class ShazamOutput:
    """Output structure returned by the Shazam cognitive middleware."""

    spectral_hash: SpectralHash
    tree_activation: Dict[str, float]
    dominant_trees: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    non_decision: bool = True


@dataclass
class SSRProjection:
    """Output of the Reverse OS (SSR) projection layer."""

    text_projection: str
    ui_projection: Dict[str, Any] = field(default_factory=dict)
    voice_projection: Optional[str] = None
    visual_state: Optional[Dict[str, Any]] = None
    non_decision: bool = True


@dataclass
class BDFResponse:
    """Response structure for the Bi-Cerebral Diffusion Framework."""

    response_value: float
    explanation: Optional[str] = None
    non_decision: bool = True


@dataclass
class HexaFluxMutation:
    """Represents a symbolic mutation produced by HexaFlux."""

    original_value: Any
    mutated_value: Any
    transition_role: str = ""
    non_decision: bool = True


@dataclass
class MCPRequest:
    """Raw request coming from the MCP interface."""

    intent: str
    domain: str
    scope: str
    cost: float
    risk: float
    tool_request: Optional[str] = None


@dataclass
class ObsidiaIR:
    """Internal representation of an MCP request after translation."""

    intent: str
    domain: str
    scope: str
    cost: float
    risk: float
    tree_vector: List[float]
    policy_scope: Optional[str] = None
    non_decision: bool = True


@dataclass
class ContextPacket:
    """Packet exported to X-108 containing context and no decision."""

    query: Any
    events: List[Event] = field(default_factory=list)
    activated_trees: Dict[str, float] = field(default_factory=dict)
    calibrated_links: List[Any] = field(default_factory=list)
    projection: Optional[SSRProjection] = None
    confidence: float = 0.0
    non_decision: bool = True
    export_target: str = "X-108"


@dataclass
class AgentDescriptor:
    """Descriptor for a single agent in the 52-agent registry."""

    id: str
    name: str
    family: str
    role: str
    deployment: str
    system_prompt: str = ""
    status: str = "NEEDS_HUMAN_VALIDATION"
    boundary: str = ""
    input: str = ""
    output: str = ""
    non_decision: bool = True
    local_cloud_policy: str = ""
    data_sovereignty: Optional[str] = None


@dataclass
class GenomeLaw:
    """Representation of one of the O1–O8 constitutional laws."""

    code: str
    title: str
    description: str = ""
    non_decision: bool = True
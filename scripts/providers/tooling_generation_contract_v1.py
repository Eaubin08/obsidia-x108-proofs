"""
R8-C3a — Tooling Generation Contract V1.

This contract defines a NON-SOVEREIGN code-generation boundary.

The generation provider receives:
- immutable textual/objective context,
- one explicit tracked target,
- the exact current source text,
- hashes/provenance.

It returns candidate source text only.

It receives no authority to:
- apply,
- stage,
- commit,
- push,
- merge,
- invoke KX108,
- mutate memory/kernel,
- emit ACT,
- perform WorldAction.

KX108_ONLY remains the decision authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


TOOLING_GENERATION_CONTRACT = "TOOLING_CODE_GENERATION_CONTRACT_V1"
TOOLING_GENERATION_MODE = "TOOLING_CODE_GENERATION_ADAPTER_V1"
TOOLING_GENERATION_PROMPT_CONTRACT = "TOOLING_CODE_GENERATION_PROMPT_V1"


@dataclass(frozen=True)
class ToolingGenerationRequest:
    generation_id: str
    objective: str
    objective_sha256: str
    target_path: str
    base_sha: str
    target_before_sha256: str
    prompt: str
    prompt_sha256: str
    current_source: str


@dataclass(frozen=True)
class ToolingGenerationProviderResult:
    provider_id: str
    model_id: str
    output_text: str


@runtime_checkable
class ToolingGenerationProvider(Protocol):
    def generate(
        self,
        request: ToolingGenerationRequest,
    ) -> ToolingGenerationProviderResult:
        ...
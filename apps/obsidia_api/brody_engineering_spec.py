"""
Brody Engineering Spec V1.

Readonly bridge between a RepairRequest and native Obsidure engineering.

Brody structures facts already present in the request/repository.
It does NOT generate source, apply patches, mutate memory, invoke KX108,
emit ACT, commit, push, or perform WorldAction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from pathlib import Path
import re
from typing import Any

from periphery.agents.obsidure_repair_contract import RepairRequest


ENGINEERING_SPEC_ID = "BRODY_ENGINEERING_SPEC_V1"

_ALLOWED_INVARIANTS = {
    "decision_authority",
    "emits_act",
    "kernel_mutation",
    "memory_write",
    "canonical_write",
    "allowed_to_decide",
    "allowed_to_act",
}


@dataclass(frozen=True)
class EngineeringTarget:
    path: str
    target_state: str
    source_present: bool
    source_sha256: str = ""
    source_lines: int = 0


@dataclass
class BrodyEngineeringSpec:
    request_id: str
    objective: str
    targets: list[EngineeringTarget] = field(default_factory=list)
    explicit_invariants: dict[str, str] = field(default_factory=dict)
    acceptance_criteria: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    confidence: str = "NONE"
    spec_id: str = ENGINEERING_SPEC_ID

    readonly: bool = True
    can_decide: bool = False
    can_generate_source: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False
    world_action: bool = False
    decision_authority: str = "KX108_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _source_for_target(request: RepairRequest, root: Path, rel: str) -> str | None:
    excerpt = (request.target_excerpts or {}).get(rel)
    if isinstance(excerpt, str) and excerpt:
        return excerpt

    candidate = root / rel
    if candidate.is_file():
        try:
            return candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    return None


def _explicit_invariants(objective: str) -> dict[str, str]:
    found: dict[str, str] = {}

    pattern = re.compile(
        r"\b("
        + "|".join(sorted(map(re.escape, _ALLOWED_INVARIANTS)))
        + r")\s*=\s*([A-Za-z0-9_.-]+)",
        flags=re.IGNORECASE,
    )

    for key, value in pattern.findall(objective or ""):
        found[key.lower()] = value

    return found


def build_brody_engineering_spec(
    request: RepairRequest,
    repo_root: Path | str,
) -> BrodyEngineeringSpec:
    root = Path(repo_root)

    targets: list[EngineeringTarget] = []

    for raw in request.repo_targets:
        rel = str(raw or "").replace("\\", "/").lstrip("./")
        if not rel:
            continue

        source = _source_for_target(request, root, rel)

        if source is None:
            targets.append(
                EngineeringTarget(
                    path=rel,
                    target_state="CREATE",
                    source_present=False,
                )
            )
            continue

        encoded = source.encode("utf-8")

        targets.append(
            EngineeringTarget(
                path=rel,
                target_state="EXISTING",
                source_present=True,
                source_sha256=hashlib.sha256(encoded).hexdigest(),
                source_lines=len(source.splitlines()),
            )
        )

    unknowns: list[str] = []

    if not request.objective.strip():
        unknowns.append("objective")

    if not targets:
        unknowns.append("repo_targets")

    acceptance = [
        str(item)
        for item in (request.tests_hint or [])
        if str(item).strip()
    ]

    if not acceptance:
        unknowns.append("tests_hint")

    confidence = "HIGH"
    if unknowns:
        confidence = "MEDIUM" if targets and request.objective.strip() else "LOW"

    return BrodyEngineeringSpec(
        request_id=request.request_id,
        objective=request.objective,
        targets=targets,
        explicit_invariants=_explicit_invariants(request.objective),
        acceptance_criteria=acceptance,
        unknowns=unknowns,
        confidence=confidence,
    )


def self_check() -> dict[str, Any]:
    return {
        "spec_id": ENGINEERING_SPEC_ID,
        "role": "READONLY_ENGINEERING_SPEC",
        "can_decide": False,
        "can_generate_source": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "world_action": False,
        "decision_authority": "KX108_ONLY",
    }

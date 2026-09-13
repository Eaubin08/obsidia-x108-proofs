"""
periphery/agents/obsidure_reasoning_provider.py
===============================================
INTERFACE GÉNÉRIQUE DE RAISONNEMENT DE RÉPARATION.

Position dans le cycle :

    Obsidure échec → ErrorContext → RepairRequest
                                        │
                                        ▼
                          ReasoningProvider.diagnose()
                                        │
                          ┌─────────────┴─────────────┐
                    PROPOSAL_READY          NEEDS_DIAGNOSTIC_CONTEXT
                          │                 NEEDS_EXTERNAL_ENGINE
                          ▼                 OUT_OF_SCOPE
                  provider.propose()                │
                          │                         ▼
                   RepairProposal            aucun proposal — on le DIT
                          │
                          ▼
              Obsidure sandbox/tests → RepairVerdict

POURQUOI CETTE INTERFACE EXISTE
    L'inspection du runtime a établi que Brody ne dispose d'aucun moteur
    capable de produire sémantiquement un RepairProposal : ses modules dits
    cognitifs (micro_core, reflex_diagnostic, machination_composer) sont des
    détecteurs à motifs et des composeurs de réponse. Aucun n'analyse ni ne
    génère de code.

    Plutôt que de simuler un raisonnement, on expose un point d'extension
    explicite. Brody est la route PRINCIPALE et déclare honnêtement sa
    capacité. EXTERNAL_REASONING est un fallback DÉCLARÉ et NON AUTOMATIQUE :
    il faut le demander (`allow_external=True`), et il ne fabrique jamais de
    proposition — il prépare un dossier pour un moteur/humain externe.

RÈGLE CARDINALE
    Aucun RepairProposal ne doit être produit quand le défaut fonctionnel
    n'est pas suffisamment défini. Dans ce cas le statut est
    NEEDS_DIAGNOSTIC_CONTEXT et `missing_information` dit précisément ce
    qui manque. Un faux correctif est pire qu'une absence de correctif.

FRONTIÈRES : decision_authority=KX108_ONLY, emits_act=False,
emits_verdict=False, kernel_mutation=False, memory_write=False,
canonical_write=False, auto_apply=False, HUMAN_APPROVED_WRITE.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from periphery.agents.obsidure_repair_contract import (
    REPAIR_BOUNDARY,
    RepairProposal,
    RepairRequest,
    assert_repair_boundary,
    validate_repair_proposal,
)

__all__ = [
    "DiagnosisStatus",
    "RepairDiagnosis",
    "ReasoningProvider",
    "ExternalReasoningProvider",
    "ReasoningOutcome",
    "run_reasoning_cycle",
    "register_provider",
    "get_provider",
    "available_providers",
]


class DiagnosisStatus:
    """États possibles d'un diagnostic. Aucun n'est un succès implicite."""

    #: le défaut est identifié et le provider sait produire une proposition
    PROPOSAL_READY = "PROPOSAL_READY"

    #: information insuffisante — on refuse d'inventer une réparation
    NEEDS_DIAGNOSTIC_CONTEXT = "NEEDS_DIAGNOSTIC_CONTEXT"

    #: défaut identifiable mais hors de la capacité du provider
    NEEDS_EXTERNAL_ENGINE = "NEEDS_EXTERNAL_ENGINE"

    #: specification Brody structuree, execution native Obsidure requise
    NEEDS_NATIVE_ENGINE = "NEEDS_NATIVE_ENGINE"

    #: la demande ne relève pas de la réparation de code
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

    ALL = (PROPOSAL_READY, NEEDS_DIAGNOSTIC_CONTEXT, NEEDS_NATIVE_ENGINE, NEEDS_EXTERNAL_ENGINE, OUT_OF_SCOPE)

    #: statuts pour lesquels appeler propose() est légitime
    PROPOSABLE = (PROPOSAL_READY, NEEDS_NATIVE_ENGINE)


@dataclass
class RepairDiagnosis:
    """
    Résultat de l'analyse d'un RepairRequest par un provider.

    `missing_information` est le champ le plus important du contrat : quand le
    statut est NEEDS_DIAGNOSTIC_CONTEXT, il doit dire exactement quoi fournir
    pour débloquer le cycle. Un diagnostic qui bloque sans expliquer est un
    diagnostic inutile.
    """

    provider: str = ""
    request_id: str = ""
    status: str = DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
    defect_class: str = "UNDETERMINED"
    confidence: str = "NONE"  # NONE | LOW | MEDIUM | HIGH
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    findings: List[Dict[str, Any]] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    inspected_targets: List[str] = field(default_factory=list)
    notes: str = ""
    boundary: Dict[str, Any] = field(default_factory=lambda: dict(REPAIR_BOUNDARY))

    def __post_init__(self) -> None:
        if self.status not in DiagnosisStatus.ALL:
            self.status = DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
        assert_repair_boundary(self.boundary)

    @property
    def can_propose(self) -> bool:
        return self.status in DiagnosisStatus.PROPOSABLE

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReasoningOutcome:
    """
    Sortie complète d'un cycle de raisonnement : le diagnostic, la proposition
    éventuelle, et la trace des providers consultés.

    `proposal is None` n'est jamais une erreur en soi — c'est un résultat
    légitime que le diagnostic explique.
    """

    request_id: str = ""
    diagnosis: Optional[RepairDiagnosis] = None
    proposal: Optional[RepairProposal] = None
    providers_tried: List[str] = field(default_factory=list)
    external_fallback_offered: bool = False
    boundary: Dict[str, Any] = field(default_factory=lambda: dict(REPAIR_BOUNDARY))

    def __post_init__(self) -> None:
        assert_repair_boundary(self.boundary)

    @property
    def status(self) -> str:
        return self.diagnosis.status if self.diagnosis else DiagnosisStatus.OUT_OF_SCOPE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "status": self.status,
            "diagnosis": self.diagnosis.to_dict() if self.diagnosis else None,
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "providers_tried": list(self.providers_tried),
            "external_fallback_offered": self.external_fallback_offered,
            "boundary": dict(self.boundary),
        }


class ReasoningProvider(abc.ABC):
    """
    Contrat qu'un moteur de raisonnement doit remplir pour brancher sur le
    cycle de réparation Obsidure.

    Deux méthodes, volontairement séparées :

      diagnose()  analyse SANS rien produire. Doit être honnête sur sa
                  capacité et sur l'information manquante.
      propose()   ne doit être appelée que si le diagnostic l'autorise, et
                  peut toujours retourner None.

    Un provider ne décide rien, n'applique rien, n'écrit rien hors sandbox.
    """

    #: nom court et stable, utilisé dans le registre et les traces
    name: str = "abstract"

    @abc.abstractmethod
    def diagnose(self, request: RepairRequest, repo_root: Optional[Path] = None) -> RepairDiagnosis:
        """Analyse le RepairRequest. Ne produit aucun artefact."""

    @abc.abstractmethod
    def propose(
        self,
        request: RepairRequest,
        diagnosis: RepairDiagnosis,
        repo_root: Optional[Path] = None,
    ) -> Optional[RepairProposal]:
        """
        Produit une proposition testable, ou None.

        Retourner None est toujours permis. Retourner une proposition
        inventée ne l'est jamais.
        """


class ExternalReasoningProvider(ReasoningProvider):
    """
    Fallback DÉCLARÉ et NON AUTOMATIQUE.

    Ce provider ne raisonne pas et ne fabrique rien. Il constate qu'un moteur
    externe (agent de développement, humain) est nécessaire et prépare le
    dossier à lui remettre. Il n'est jamais consulté sans `allow_external=True`
    explicite, précisément pour qu'aucun runtime ne devienne silencieusement
    dépendant d'un moteur externe.
    """

    name = "EXTERNAL_REASONING"

    def diagnose(self, request: RepairRequest, repo_root: Optional[Path] = None) -> RepairDiagnosis:
        targets = list(request.repo_targets)
        missing = [
            "Un moteur de raisonnement externe doit analyser ce RepairRequest.",
            f"Dossier à remettre : request_id={request.request_id}, "
            f"failure_mode={request.failure_mode}, cibles={targets or 'aucune'}.",
        ]
        if not targets:
            missing.append("Aucune cible repo identifiée — préciser le ou les fichiers concernés.")
        if not request.error_contexts:
            missing.append("Aucun contexte d'erreur — fournir trace, test en échec ou sortie de build.")

        return RepairDiagnosis(
            provider=self.name,
            request_id=request.request_id,
            status=DiagnosisStatus.NEEDS_EXTERNAL_ENGINE,
            defect_class="REQUIRES_EXTERNAL_REASONING",
            confidence="NONE",
            inspected_targets=targets,
            missing_information=missing,
            notes=(
                "Fallback non automatique. Ce provider ne produit jamais de "
                "RepairProposal : il ne fait que constater le besoin d'un moteur externe."
            ),
        )

    def propose(
        self,
        request: RepairRequest,
        diagnosis: RepairDiagnosis,
        repo_root: Optional[Path] = None,
    ) -> Optional[RepairProposal]:
        # Invariant : ce provider ne fabrique rien. Jamais.
        return None


# ===========================================================================
# Registre
# ===========================================================================

_REGISTRY: Dict[str, ReasoningProvider] = {}


def register_provider(provider: ReasoningProvider) -> None:
    """Enregistre un provider sous son `name`."""
    if not isinstance(provider, ReasoningProvider):
        raise TypeError("provider doit implémenter ReasoningProvider")
    _REGISTRY[provider.name] = provider


def get_provider(name: str) -> Optional[ReasoningProvider]:
    """Retourne un provider enregistré, ou None."""
    if name == ExternalReasoningProvider.name and name not in _REGISTRY:
        register_provider(ExternalReasoningProvider())
    if name == "BRODY" and name not in _REGISTRY:
        _autoregister_brody()
    return _REGISTRY.get(name)


def available_providers() -> List[str]:
    _autoregister_brody()
    if ExternalReasoningProvider.name not in _REGISTRY:
        register_provider(ExternalReasoningProvider())
    return sorted(_REGISTRY)


def _autoregister_brody() -> None:
    """
    Enregistre le provider Brody s'il est importable.

    Fail-soft : la périphérie ne doit pas casser quand apps/ est absent
    (exécution hors runtime API).
    """
    if "BRODY" in _REGISTRY:
        return
    try:
        from apps.obsidia_api.brody_repair_reasoning import BrodyReasoningProvider
        register_provider(BrodyReasoningProvider())
    except Exception:
        pass


# ===========================================================================
# Orchestration
# ===========================================================================


def run_reasoning_cycle(
    request: RepairRequest,
    providers: Optional[Sequence[ReasoningProvider]] = None,
    allow_external: bool = False,
    repo_root: Optional[Path] = None,
) -> ReasoningOutcome:
    """
    Exécute le raisonnement sur un RepairRequest.

    Ordre : Brody (route principale) d'abord. Le premier provider qui obtient
    PROPOSAL_READY et produit une proposition VALIDE gagne.

    `allow_external` est faux par défaut : le fallback EXTERNAL_REASONING
    n'est jamais engagé automatiquement. Quand il est activé, il ne produit
    toujours aucune proposition — il documente le besoin.

    Une proposition qui ne passe pas `validate_repair_proposal` est rejetée
    ici même : un provider ne peut pas contourner les frontières.
    """
    outcome = ReasoningOutcome(request_id=request.request_id)

    chain: List[ReasoningProvider] = list(providers) if providers is not None else []
    if not chain:
        brody = get_provider("BRODY")
        if brody is not None:
            chain.append(brody)

    last_diagnosis: Optional[RepairDiagnosis] = None

    for provider in chain:
        outcome.providers_tried.append(provider.name)
        try:
            diagnosis = provider.diagnose(request, repo_root=repo_root)
        except Exception as exc:
            diagnosis = RepairDiagnosis(
                provider=provider.name,
                request_id=request.request_id,
                status=DiagnosisStatus.NEEDS_EXTERNAL_ENGINE,
                defect_class="PROVIDER_ERROR",
                notes=f"{type(exc).__name__}: {exc}"[:400],
            )
        last_diagnosis = diagnosis

        # Brody cognition completed: native Obsidure consumes
        # the EngineeringSpec before the normal propose() phase.
        # IMPORTANT: no return/continue here. A ready NativePlan
        # must flow into provider.propose().
        if diagnosis.status == DiagnosisStatus.NEEDS_NATIVE_ENGINE:
            try:
                from periphery.agents.obsidure_native_engineering_consumer import (
                    consume_brody_engineering_spec,
                )

                native = consume_brody_engineering_spec(
                    diagnosis,
                    repo_root=repo_root,
                )

                diagnosis.findings.append({
                    "type": "OBSIDURE_NATIVE_HANDOFF",
                    "result": native.to_dict(),
                })

            except Exception as exc:
                diagnosis.findings.append({
                    "type": "OBSIDURE_NATIVE_HANDOFF_ERROR",
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    )[:600],
                })

        if not diagnosis.can_propose:
            continue

        try:
            proposal = provider.propose(request, diagnosis, repo_root=repo_root)
        except Exception as exc:
            diagnosis.status = DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
            diagnosis.notes = (diagnosis.notes + f" | propose() a échoué : {exc}")[:600]
            continue

        if proposal is None:
            # Le provider s'est ravisé — c'est légitime, on le consigne.
            diagnosis.status = DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
            diagnosis.notes = (
                diagnosis.notes + " | propose() n'a produit aucun candidat."
            ).strip(" |")[:600]
            continue

        violations = validate_repair_proposal(proposal)
        if violations:
            diagnosis.status = DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
            diagnosis.defect_class = "PROVIDER_PROPOSAL_REJECTED"
            diagnosis.findings.append({
                "type": "PROPOSAL_VALIDATION_FAILED",
                "details": [v["type"] for v in violations],
            })
            continue

        outcome.diagnosis = diagnosis
        outcome.proposal = proposal
        return outcome

    # Aucun provider n'a produit de proposition exploitable.
    if allow_external:
        ext = get_provider(ExternalReasoningProvider.name)
        if ext is not None:
            outcome.providers_tried.append(ext.name)
            outcome.external_fallback_offered = True
            last_diagnosis = ext.diagnose(request, repo_root=repo_root)

    outcome.diagnosis = last_diagnosis or RepairDiagnosis(
        provider="NONE",
        request_id=request.request_id,
        status=DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT,
        defect_class="NO_PROVIDER_AVAILABLE",
        missing_information=["Aucun provider de raisonnement n'est enregistré."],
    )
    return outcome

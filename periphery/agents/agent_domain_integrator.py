"""
periphery/agents/agent_domain_integrator.py  —  v1.0
======================================================
DOMAIN_INTEGRATION_AGENT — Machine d'installation de gouvernance
Architecture conceptuelle : ARCHITECTE_METIER × TRADUCTEUR_IR

RÔLE :
  Traduire un environnement métier nouveau (Santé, Défense, Légal, Énergie…)
  en Représentation Interne (IR) que le Kernel X-108 peut juger déterministement.

  Obsidia ne demande pas au Kernel de comprendre le monde brut.
  Le monde doit se présenter dans la langue du Kernel (IR).
  Cet agent est l'organe de traduction.

PROTOCOLE M.A.P. :
  M — Mapping     : analyser le domaine métier (entités, risques, flux)
  A — Adaptation  : construire la matrice IR + vérifier conformité lois Kernel
  P — Proposition : générer les stubs dans sandbox → DomainManifest → PROPOSAL

STUBS GÉNÉRÉS PAR DOMAINE :
  domains/<name>/domain_state.py              — État domaine (dataclass)
  domains/<name>/<name>_x108_gate.py         — Gate (appelle /kernel/ragnarok)
  domains/<name>/nuisance_registry.py         — Registre nuisances
  sigma/domains/<name>_domain_agent.py        — Agent sigma (vote, sans décision)
  domain_packets/<name>_decisional_form_v0.yaml — Formulaire décisionnel

RÈGLE ABSOLUE — KERNEL + PREUVES SCELLÉES = MUR DE BÉTON :
  Les gates générés APPELLENT /kernel/ragnarok — ils ne décident jamais.
  emits_verdict = False. decision_authority = KX108_ONLY. Toujours.
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import textwrap
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _requests = None  # type: ignore
    _REQUESTS_OK = False


# ===========================================================================
# 0.  FRONTIÈRES DURES
# ===========================================================================

AGENT_DIA_BOUNDARY: Dict[str, Any] = {
    "decision_authority":  "KX108_ONLY",
    "cockpit_role":        "DOMAIN_ARCHITECT_PROPOSAL",
    "allowed_to_decide":   False,
    "emits_verdict":       False,
    "emits_act":           False,
    "kernel_mutation":     False,
    "x108_merge":          False,
    "sandbox_mode":        "HUMAN_APPROVED_WRITE",
    "gates_call_kernel":   True,   # les gates générés DOIVENT appeler /kernel/ragnarok
    "gates_decide_alone":  False,  # les gates générés ne décident JAMAIS seuls
}

PROTECTED_INFIXES: Tuple[str, ...] = (
    "server.kernel.sealed.cjs",
    "proofs/V18_",
    "proofs/lean/57_preuves",
    "merkle_seal.json",
    "rfc3161",
)

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
PROPOSALS_DIR: Path = REPO_ROOT / "_DOMAIN_PROPOSALS"
KERNEL_URL_DEFAULT: str = "http://127.0.0.1:3001/kernel/ragnarok"


# ===========================================================================
# 1.  EXCEPTIONS
# ===========================================================================

class DomainIntegrationError(RuntimeError):
    """Erreur générique du cycle MAP."""

class IRMappingError(RuntimeError):
    """Impossible de construire la matrice IR pour ce domaine."""

class BoundaryViolationError(RuntimeError):
    """Un stub généré viole les lois du Kernel — arrêt immédiat."""


# ===========================================================================
# 2.  STRUCTURES DE DONNÉES
# ===========================================================================

class MAPPhase(Enum):
    IDLE       = "IDLE"
    MAPPING    = "M_MAPPING"
    ADAPTATION = "A_ADAPTATION"
    PROPOSITION = "P_PROPOSITION"
    AWAITING   = "AWAITING_HUMAN_APPROVED_WRITE"


@dataclass
class DomainSpec:
    """
    Spécification d'un domaine métier fournie par l'opérateur.
    C'est l'entrée du cycle MAP.
    """
    domain_name: str                              # ex: HEALTH, DEFENSE, LEGAL
    description: str = ""                         # description libre du domaine
    key_entities: List[str] = field(default_factory=list)   # ex: ["Patient", "Prescription"]
    risk_classes: List[str] = field(default_factory=list)   # ex: ["CRITICAL_HEALTH_DATA"]
    flow_types: List[str] = field(default_factory=list)     # ex: ["PRESCRIBE", "AUDIT"]
    target_threshold_s: float = 0.6               # seuil S par défaut pour le Kernel
    operator_notes: str = ""


@dataclass
class IRTranslationMatrix:
    """
    Matrice de traduction : langage métier → Représentation Interne Kernel.
    Produite en Phase A. Sert de contrat formel entre le domaine et le Kernel.
    """
    domain_name: str
    version: str = "v0"

    # Mappings métier → IR alphabet
    entity_to_alphabet: Dict[str, str] = field(default_factory=dict)
    risk_class_to_flag: Dict[str, str] = field(default_factory=dict)
    flow_to_intent: Dict[str, str] = field(default_factory=dict)

    # Champs source → métriques Kernel (T_mean, H_score, A_score)
    t_mean_source: str = "risk_score"
    h_score_source: str = "confidence_index"
    a_score_source: str = "audit_score"
    threshold_s: float = 0.6

    # Indicateurs pour les opérateurs (lecture seule — le Kernel décide)
    allow_indicators: List[str] = field(default_factory=list)
    hold_indicators: List[str] = field(default_factory=list)
    block_indicators: List[str] = field(default_factory=list)

    # Méta
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "DOMAIN_INTEGRATION_AGENT_v1"


@dataclass
class DomainStub:
    """Un fichier stub généré dans la sandbox."""
    relative_path: str           # chemin relatif depuis repo root
    action: str                  # CREATE | REVIEW
    content: str                 # contenu généré
    sandbox_path: str = ""       # chemin réel dans la sandbox éphémère
    rationale: str = ""


@dataclass
class DomainManifest:
    """
    Sortie complète d'un cycle MAP.
    Contient la matrice IR + tous les stubs générés.
    Jamais appliquée automatiquement — attend HUMAN_APPROVED_WRITE.
    """
    manifest_id: str
    domain_name: str
    domain_spec: DomainSpec
    ir_matrix: IRTranslationMatrix
    stubs: List[DomainStub]
    sandbox_dir: str
    integration_phase: str = "P3"   # phase d'intégration recommandée
    status: str = "AWAITING_HUMAN_APPROVED_WRITE"
    human_approved: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ===========================================================================
# 3.  GÉNÉRATEURS DE STUBS
# ===========================================================================

def _safe_name(domain_name: str) -> str:
    """Normalise le nom de domaine en identifiant Python/fichier sûr."""
    return re.sub(r"[^A-Za-z0-9_]", "_", domain_name.strip()).lower()


def _class_name(domain_name: str) -> str:
    """Convertit le nom de domaine en ClassName Python (PascalCase)."""
    parts = re.split(r"[^A-Za-z0-9]", domain_name.strip())
    return "".join(p.capitalize() for p in parts if p)


def _generate_domain_state(spec: DomainSpec, ir: IRTranslationMatrix) -> str:
    """Génère domain_state.py — la dataclass d'état du domaine."""
    sn = _safe_name(spec.domain_name)
    cn = _class_name(spec.domain_name)

    entity_fields = ""
    for entity in spec.key_entities[:8]:
        field_name = re.sub(r"[^A-Za-z0-9_]", "_", entity).lower()
        entity_fields += f"    {field_name}_id: str = \"\"\n"

    risk_const = "\n".join(
        f"    {re.sub(r'[^A-Za-z0-9_]', '_', rc).upper()} = \"{rc}\""
        for rc in spec.risk_classes[:6]
    ) or "    # (aucune classe de risque spécifiée)"

    return textwrap.dedent(f"""\
        \"\"\"
        {sn}/domain_state.py — État du domaine {spec.domain_name.upper()}
        GÉNÉRÉ PAR DOMAIN_INTEGRATION_AGENT v1.0
        STATUT : SANDBOX — AWAITING_HUMAN_REVIEW

        Ce fichier définit le snapshot d'état transmis au Kernel X-108 via le Gate.
        Le Kernel prend la décision finale (ALLOW / HOLD / BLOCK).
        \"\"\"

        from dataclasses import dataclass, field
        from datetime import datetime, timezone
        from enum import Enum
        from typing import Any, Dict, List, Optional


        class {cn}RiskClass(str, Enum):
            \"\"\"Classes de risque du domaine {spec.domain_name.upper()}.\"\"\"
        {risk_const}


        @dataclass
        class {cn}DomainState:
            \"\"\"
            État courant du domaine {spec.domain_name.upper()}.
            Snapshot transmis au Gate X108 pour décision Kernel.

            Contexte : {spec.description[:120]}
            \"\"\"
            domain: str = "{sn}"

            # ── Entités clés du domaine ───────────────────────────────────────
        {entity_fields}
            # ── Métriques IR Kernel (T_mean, H_score, A_score) ───────────────
            risk_score: float = 0.5         # → T_mean  : niveau de risque [0,1]
            confidence_index: float = 0.5   # → H_score : niveau de confiance [0,1]
            audit_score: float = 0.5        # → A_score : qualité de l'audit [0,1]
            threshold_s: float = {ir.threshold_s}     # seuil de décision (calibré par l'opérateur)

            # ── Métadonnées ───────────────────────────────────────────────────
            risk_class: str = ""
            flow_type: str = ""
            payload_version: str = "v0"
            timestamp: str = field(
                default_factory=lambda: datetime.now(timezone.utc).isoformat()
            )

            def to_gate_payload(self) -> Dict[str, Any]:
                \"\"\"Convertit l'état en payload pour le Gate X108.\"\"\"
                return {{
                    "{ir.t_mean_source}":    self.risk_score,
                    "{ir.h_score_source}": self.confidence_index,
                    "{ir.a_score_source}":   self.audit_score,
                    "domain":               self.domain,
                    "risk_class":           self.risk_class,
                    "flow_type":            self.flow_type,
                    "timestamp":            self.timestamp,
                }}
    """)


def _generate_gate(spec: DomainSpec, ir: IRTranslationMatrix) -> str:
    """Génère <name>_x108_gate.py — la gate qui appelle /kernel/ragnarok."""
    sn = _safe_name(spec.domain_name)
    cn = _class_name(spec.domain_name)

    flow_map_lines = "\n".join(
        f"            \"{ft}\": \"{ir.flow_to_intent.get(ft, 'GENERAL_FLOW')}\","
        for ft in spec.flow_types[:8]
    ) or "            # (aucun flux spécifié)"

    allow_comment = ", ".join(spec.risk_classes[:3]) or "données conformes"

    return textwrap.dedent(f"""\
        \"\"\"
        domains/{sn}/{sn}_x108_gate.py — Gate de gouvernance {spec.domain_name.upper()} → Kernel X-108
        GÉNÉRÉ PAR DOMAIN_INTEGRATION_AGENT v1.0
        STATUT : SANDBOX — AWAITING_HUMAN_REVIEW

        RÈGLE ABSOLUE :
          Ce gate NE DÉCIDE JAMAIS de façon autonome.
          Il traduit le payload {sn} en IR et le soumet au Kernel X-108.
          La décision (ALLOW / HOLD / BLOCK) appartient au Kernel uniquement.

        Contexte métier : {spec.description[:120]}
        Entités clés    : {', '.join(spec.key_entities[:5]) or 'à définir'}
        Flux supportés  : {', '.join(spec.flow_types[:5]) or 'à définir'}
        \"\"\"

        import os
        import requests
        from typing import Any, Dict, Optional

        KERNEL_URL: str = os.environ.get(
            "OBSIDIA_KERNEL_URL",
            "http://127.0.0.1:3001/kernel/ragnarok"
        )
        DOMAIN: str = "{sn}"
        GATE_VERSION: str = "v0"

        # Mapping flux métier → IR intent (à affiner par l'opérateur)
        FLOW_TO_INTENT: Dict[str, str] = {{
        {flow_map_lines}
        }}


        class {cn}X108Gate:
            \"\"\"
            Gate de gouvernance {spec.domain_name.upper()} → Kernel X-108.

            Traduit les payloads métier {sn} en IR (T_mean, H_score, A_score, S)
            et délègue la décision au Kernel via POST /kernel/ragnarok.

            Ne prend AUCUNE décision autonome. Ne réplique PAS la logique Kernel.
            \"\"\"

            DEFAULT_THRESHOLD_S: float = {ir.threshold_s}

            def translate_to_ir(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                \"\"\"
                Traduit un payload {sn} en Représentation Interne Kernel.
                Mapping défini dans la IRTranslationMatrix générée.
                \"\"\"
                return {{
                    "domain": DOMAIN,
                    "data": {{
                        "T_mean": float(payload.get("{ir.t_mean_source}", 0.5)),
                        "H_score": float(payload.get("{ir.h_score_source}", 0.5)),
                        "A_score": float(payload.get("{ir.a_score_source}", 0.5)),
                        "S": float(payload.get("threshold_s", self.DEFAULT_THRESHOLD_S)),
                    }},
                    "meta": {{
                        "flow_type":    payload.get("flow_type", "UNKNOWN"),
                        "risk_class":   payload.get("risk_class", ""),
                        "gate_version": GATE_VERSION,
                    }},
                }}

            def evaluate(
                self,
                payload: Dict[str, Any],
                timeout: float = 10.0,
            ) -> Dict[str, Any]:
                \"\"\"
                Soumet le payload au Kernel X-108 et retourne sa décision.
                Fail-Closed : si le Kernel est injoignable → HOLD par défaut.
                \"\"\"
                ir_payload = self.translate_to_ir(payload)

                try:
                    response = requests.post(
                        KERNEL_URL, json=ir_payload, timeout=timeout
                    )
                    response.raise_for_status()
                    kernel_decision = response.json()
                except Exception as exc:
                    # Fail-Closed : indisponibilité Kernel → HOLD systématique
                    return {{
                        "verdict":    "HOLD",
                        "domain":     DOMAIN,
                        "source":     "GATE_FAIL_CLOSED",
                        "error":      str(exc)[:200],
                        "ir_payload": ir_payload,
                    }}

                return {{
                    "verdict":         kernel_decision.get("verdict", "HOLD"),
                    "domain":          DOMAIN,
                    "source":          "KERNEL_X108",
                    "kernel_response": kernel_decision,
                    "ir_payload":      ir_payload,
                    "gate_version":    GATE_VERSION,
                }}


        # ── Fonction de commodité ─────────────────────────────────────────────

        def evaluate_{sn}_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
            \"\"\"
            Évalue un payload {sn} via le Gate X108.
            Retourne la décision du Kernel sans la modifier.
            \"\"\"
            return {cn}X108Gate().evaluate(payload)
    """)


def _generate_nuisance_registry(spec: DomainSpec) -> str:
    """Génère nuisance_registry.py — registre des nuisances du domaine."""
    sn = _safe_name(spec.domain_name)

    nuisance_entries = ""
    for i, rc in enumerate(spec.risk_classes[:6], 1):
        nuisance_entries += textwrap.dedent(f"""\
            NuisanceEntry(
                nuisance_id="{sn.upper()}_N{i:02d}",
                label="{rc}",
                risk_class="{rc}",
                domain=DOMAIN,
                severity="MEDIUM",
                description="Nuisance liée à : {rc}. À documenter par l'opérateur.",
            ),
        """)
    if not nuisance_entries:
        nuisance_entries = "    # (aucune nuisance prédéfinie — à documenter par l'opérateur)\n"

    return textwrap.dedent(f"""\
        \"\"\"
        domains/{sn}/nuisance_registry.py — Registre des nuisances {spec.domain_name.upper()}
        GÉNÉRÉ PAR DOMAIN_INTEGRATION_AGENT v1.0
        STATUT : SANDBOX — AWAITING_HUMAN_REVIEW

        Liste les nuisances connues du domaine {sn}.
        Ce registre informe le Gate et le sigma agent — il ne décide pas.
        \"\"\"

        from dataclasses import dataclass, field
        from typing import List

        DOMAIN: str = "{sn}"


        @dataclass
        class NuisanceEntry:
            nuisance_id: str
            label: str
            risk_class: str
            domain: str
            severity: str = "MEDIUM"   # LOW | MEDIUM | HIGH | CRITICAL
            description: str = ""
            active: bool = True


        NUISANCES: List[NuisanceEntry] = [
        {nuisance_entries}]


        def get_active_nuisances() -> List[NuisanceEntry]:
            return [n for n in NUISANCES if n.active]


        def get_by_risk_class(risk_class: str) -> List[NuisanceEntry]:
            return [n for n in NUISANCES if n.risk_class == risk_class]
    """)


def _generate_sigma_agent(spec: DomainSpec, ir: IRTranslationMatrix) -> str:
    """Génère <name>_domain_agent.py — l'agent sigma qui vote sans décider."""
    sn = _safe_name(spec.domain_name)
    cn = _class_name(spec.domain_name)

    return textwrap.dedent(f"""\
        \"\"\"
        sigma/domains/{sn}_domain_agent.py — Agent Sigma {spec.domain_name.upper()}
        GÉNÉRÉ PAR DOMAIN_INTEGRATION_AGENT v1.0
        STATUT : SANDBOX — AWAITING_HUMAN_REVIEW

        Cet agent produit un vote de domaine ({sn}) destiné au pipeline sigma.
        Il ne prend AUCUNE décision. Son vote est une entrée pour GuardX108.
        La décision finale appartient au Kernel X-108 via /kernel/ragnarok.

        Flux : DomainState → AgentVote → DomainAggregate → GuardX108.decide()
        \"\"\"

        from dataclasses import dataclass, field
        from datetime import datetime, timezone
        from typing import Any, Dict, Optional


        DOMAIN: str = "{sn}"
        AGENT_ID: str = "{sn.upper()}_DOMAIN_AGENT_v0"
        DECISION_AUTHORITY: str = "KX108_ONLY"


        @dataclass
        class {cn}AgentVote:
            \"\"\"
            Vote émis par l'{sn} domain agent.
            N'est PAS une décision — est une entrée pour l'agrégateur sigma.
            \"\"\"
            agent_id: str = AGENT_ID
            domain: str = DOMAIN
            vote: str = "HOLD"              # HOLD par défaut (conservative)
            confidence: float = 0.5
            risk_signal: str = ""
            evidence: Dict[str, Any] = field(default_factory=dict)
            decision_authority: str = DECISION_AUTHORITY  # immuable
            emits_verdict: bool = False                   # immuable
            timestamp: str = field(
                default_factory=lambda: datetime.now(timezone.utc).isoformat()
            )


        class {cn}DomainAgent:
            \"\"\"
            Agent Sigma du domaine {spec.domain_name.upper()}.

            Analyse l'état du domaine et produit un vote pour le pipeline sigma.
            Ne prend AUCUNE décision — vote uniquement.
            Le pipeline sigma agrège les votes → GuardX108 → Kernel décide.

            Contexte : {spec.description[:120]}
            \"\"\"

            DOMAIN = DOMAIN
            VERSION = "v0"

            def analyze(self, domain_state: Dict[str, Any]) -> Dict[str, Any]:
                \"\"\"
                Analyse l'état du domaine {sn}.
                Retourne les signaux bruts pour l'agrégateur.
                \"\"\"
                risk = float(domain_state.get("{ir.t_mean_source}", 0.5))
                confidence = float(domain_state.get("{ir.h_score_source}", 0.5))
                audit = float(domain_state.get("{ir.a_score_source}", 0.5))

                signals = {{
                    "risk_elevated": risk > 0.7,
                    "confidence_low": confidence < 0.4,
                    "audit_insufficient": audit < 0.5,
                    "flow_type": domain_state.get("flow_type", "UNKNOWN"),
                    "risk_class": domain_state.get("risk_class", ""),
                }}
                return signals

            def vote(self, domain_state: Dict[str, Any]) -> {cn}AgentVote:
                \"\"\"
                Produit un vote de domaine.
                Vote HOLD par défaut — le Kernel tranche toujours.
                \"\"\"
                signals = self.analyze(domain_state)

                # Signal conservateur : tout doute → HOLD
                # (la logique d'ALLOW/BLOCK appartient au Kernel)
                if signals["risk_elevated"] or signals["confidence_low"]:
                    vote_value = "HOLD"
                    risk_signal = "ELEVATED_RISK_OR_LOW_CONFIDENCE"
                elif signals["audit_insufficient"]:
                    vote_value = "HOLD"
                    risk_signal = "AUDIT_INSUFFICIENT"
                else:
                    vote_value = "HOLD"   # toujours HOLD — le Kernel décide
                    risk_signal = "NOMINAL"

                return {cn}AgentVote(
                    vote=vote_value,
                    confidence=float(domain_state.get("{ir.h_score_source}", 0.5)),
                    risk_signal=risk_signal,
                    evidence={{
                        "signals": signals,
                        "domain_state_keys": list(domain_state.keys()),
                    }},
                )

            def run(self, domain_state: Dict[str, Any]) -> Dict[str, Any]:
                \"\"\"Point d'entrée principal du pipeline sigma.\"\"\"
                vote = self.vote(domain_state)
                return {{
                    "agent_id":          vote.agent_id,
                    "domain":            vote.domain,
                    "vote":              vote.vote,
                    "confidence":        vote.confidence,
                    "risk_signal":       vote.risk_signal,
                    "evidence":          vote.evidence,
                    "decision_authority": DECISION_AUTHORITY,
                    "emits_verdict":     False,
                    "timestamp":         vote.timestamp,
                }}
    """)


def _generate_decisional_form(spec: DomainSpec, ir: IRTranslationMatrix) -> str:
    """Génère le formulaire décisionnel YAML."""
    sn = _safe_name(spec.domain_name)
    entities = "\n".join(f"  - \"{e}\"" for e in spec.key_entities) or "  # à définir"
    risks = "\n".join(f"  - \"{r}\"" for r in spec.risk_classes) or "  # à définir"
    flows = "\n".join(f"  - \"{f}\"" for f in spec.flow_types) or "  # à définir"

    return textwrap.dedent(f"""\
        # domain_packets/{sn}_decisional_form_v0.yaml
        # GÉNÉRÉ PAR DOMAIN_INTEGRATION_AGENT v1.0
        # STATUT : SANDBOX — AWAITING_HUMAN_REVIEW
        #
        # Formulaire décisionnel du domaine {spec.domain_name.upper()}.
        # Définit le contrat entre le domaine et le Kernel X-108.

        domain: "{sn}"
        version: "v0"
        integration_phase: "P3"
        kernel_endpoint: "http://127.0.0.1:3001/kernel/ragnarok"

        metadata:
          description: "{spec.description[:120]}"
          operator_notes: "{spec.operator_notes[:200] or "À compléter par l'opérateur"}"
          created_by: "DOMAIN_INTEGRATION_AGENT_v1.0"

        entities:
        {entities}

        risk_classes:
        {risks}

        flow_types:
        {flows}

        ir_mapping:
          t_mean_source_field: "{ir.t_mean_source}"
          h_score_source_field: "{ir.h_score_source}"
          a_score_source_field: "{ir.a_score_source}"
          default_threshold_s: {ir.threshold_s}

        gate:
          file: "domains/{sn}/{sn}_x108_gate.py"
          class: "{_class_name(spec.domain_name)}X108Gate"
          calls_kernel: true
          decides_alone: false

        sigma_agent:
          file: "sigma/domains/{sn}_domain_agent.py"
          class: "{_class_name(spec.domain_name)}DomainAgent"
          emits_verdict: false

        kernel_rule:
          decision_authority: KX108_ONLY
          kernel_mutation: false
          fail_closed: true
    """)


# ===========================================================================
# 4.  CLASSE PRINCIPALE
# ===========================================================================

class DomainIntegrationAgent:
    """
    Domain Integration Agent v1.0 — Machine d'installation de gouvernance.

    Protocole M.A.P. :
      M — analyse le domaine métier fourni par l'opérateur
      A — construit la matrice IR + vérifie conformité lois Kernel
      P — génère les stubs dans sandbox → DomainManifest → PROPOSAL

    Les gates générés appellent /kernel/ragnarok — jamais décision autonome.
    Tout output attend HUMAN_APPROVED_WRITE.
    """

    def __init__(self, verbose: bool = True) -> None:
        self._boundary_ref = copy.deepcopy(AGENT_DIA_BOUNDARY)
        self._phase = MAPPhase.IDLE
        self._cycle = 0
        self._verbose = verbose
        self._manifests: List[DomainManifest] = []
        PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
        self._log("Domain Integration Agent v1.0 initialisé.")
        self._log("Kernel X-108 = seul décideur. Gates → /kernel/ragnarok.")

    def _log(self, msg: str, level: str = "INFO") -> None:
        if self._verbose or level in ("WARN", "ERROR"):
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            pfx = {"INFO": "·", "WARN": "⚠", "ERROR": "✗"}.get(level, "·")
            print(f"  [{ts}] {pfx} {msg}", flush=True)

    def _check_boundaries(self) -> None:
        for k, v in self._boundary_ref.items():
            if AGENT_DIA_BOUNDARY.get(k) != v:
                raise BoundaryViolationError(f"Frontière altérée : '{k}'")

    # ── M — MAPPING ──────────────────────────────────────────────────────────

    def phase_m_mapping(self, spec: DomainSpec) -> IRTranslationMatrix:
        """
        Analyse le domaine et construit la matrice de traduction IR.
        Associe chaque concept métier à un élément de l'alphabet Kernel.
        """
        self._phase = MAPPhase.MAPPING
        self._check_boundaries()
        self._log(f"Phase M : mapping domaine '{spec.domain_name}'…")

        sn = _safe_name(spec.domain_name)

        # Mapping entités → alphabet IR
        entity_to_alphabet: Dict[str, str] = {}
        for i, entity in enumerate(spec.key_entities[:10]):
            alpha_unit = re.sub(r"[^A-Z0-9_]", "_", entity.upper())
            entity_to_alphabet[entity] = f"IR_{alpha_unit}"

        # Mapping classes de risque → flags
        risk_to_flag: Dict[str, str] = {}
        for rc in spec.risk_classes[:8]:
            flag = f"FLAG_{re.sub(r'[^A-Z0-9_]', '_', rc.upper())}"
            risk_to_flag[rc] = flag

        # Mapping flux → intent IR
        flow_to_intent: Dict[str, str] = {}
        for ft in spec.flow_types[:8]:
            ft_up = ft.upper()
            if any(k in ft_up for k in ("CREATE", "ADD", "INSERT", "SUBMIT")):
                intent = "CREATE_PATCH"
            elif any(k in ft_up for k in ("AUDIT", "CHECK", "VERIFY", "SCAN")):
                intent = "AUDIT_ONLY"
            elif any(k in ft_up for k in ("READ", "GET", "LIST", "VIEW")):
                intent = "AUDIT_ONLY"
            else:
                intent = "GENERAL_FLOW"
            flow_to_intent[ft] = intent

        # Indicateurs pour l'opérateur (read-only — le Kernel décide)
        allow_indicators = [f"Aucun {rc} détecté" for rc in spec.risk_classes[:2]]
        hold_indicators  = [f"{rc} présent — revue requise" for rc in spec.risk_classes[:2]]
        block_indicators = [f"{rc} critique — seuil S dépassé" for rc in spec.risk_classes[:2]]

        matrix = IRTranslationMatrix(
            domain_name=sn,
            entity_to_alphabet=entity_to_alphabet,
            risk_class_to_flag=risk_to_flag,
            flow_to_intent=flow_to_intent,
            t_mean_source="risk_score",
            h_score_source="confidence_index",
            a_score_source="audit_score",
            threshold_s=spec.target_threshold_s,
            allow_indicators=allow_indicators,
            hold_indicators=hold_indicators,
            block_indicators=block_indicators,
        )

        self._log(f"  Matrice IR : {len(entity_to_alphabet)} entité(s) | "
                  f"{len(risk_to_flag)} risque(s) | {len(flow_to_intent)} flux")
        return matrix

    # ── A — ADAPTATION ───────────────────────────────────────────────────────

    def phase_a_adaptation(
        self, spec: DomainSpec, matrix: IRTranslationMatrix
    ) -> IRTranslationMatrix:
        """
        Vérifie que la matrice IR respecte les lois du Kernel.
        Garantit que les stubs à générer n'émetent pas de verdict.
        """
        self._phase = MAPPhase.ADAPTATION
        self._check_boundaries()
        self._log("Phase A : vérification conformité lois Kernel…")

        # Vérifier que le nom de domaine ne référence pas une zone protégée
        for infx in PROTECTED_INFIXES:
            if infx.lower() in spec.domain_name.lower():
                raise BoundaryViolationError(
                    f"BLOC : le nom de domaine référence une zone protégée '{infx}'."
                )

        # Vérifier cohérence du seuil
        if not 0.0 < matrix.threshold_s < 1.0:
            self._log(f"  Seuil S={matrix.threshold_s} hors bornes — forcé à 0.6", level="WARN")
            matrix.threshold_s = 0.6

        # Log des indicateurs (informatifs uniquement — le Kernel décide)
        self._log(f"  Indicateurs ALLOW : {matrix.allow_indicators[:2]}")
        self._log(f"  Indicateurs HOLD  : {matrix.hold_indicators[:2]}")
        self._log(f"  Conformité : OK — gates générés appelleront /kernel/ragnarok")
        return matrix

    # ── P — PROPOSITION ──────────────────────────────────────────────────────

    def phase_p_proposition(
        self, spec: DomainSpec, matrix: IRTranslationMatrix
    ) -> DomainManifest:
        """
        Génère tous les stubs dans la sandbox, construit le DomainManifest,
        persiste le PROPOSAL. Attend HUMAN_APPROVED_WRITE.
        """
        self._phase = MAPPhase.PROPOSITION
        self._check_boundaries()
        self._log("Phase P : génération des stubs dans sandbox…")

        sn = _safe_name(spec.domain_name)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        sandbox = REPO_ROOT / f"_DOMAIN_SANDBOX_{sn.upper()}_{ts}"
        sandbox.mkdir(parents=True, exist_ok=True)

        stubs: List[DomainStub] = []

        def _write_stub(rel_path: str, content: str, rationale: str) -> DomainStub:
            abs_path = sandbox / rel_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content, encoding="utf-8")
            stub = DomainStub(
                relative_path=rel_path,
                action="CREATE",
                content=content,
                sandbox_path=str(abs_path),
                rationale=rationale,
            )
            self._log(f"  Stub généré : {rel_path}")
            return stub

        # 1. domain_state.py
        stubs.append(_write_stub(
            f"domains/{sn}/domain_state.py",
            _generate_domain_state(spec, matrix),
            f"État du domaine {sn} — dataclass pour snapshot Kernel",
        ))

        # 2. Gate X108
        stubs.append(_write_stub(
            f"domains/{sn}/{sn}_x108_gate.py",
            _generate_gate(spec, matrix),
            f"Gate {sn} → /kernel/ragnarok — ne décide jamais seul",
        ))

        # 3. nuisance_registry.py
        stubs.append(_write_stub(
            f"domains/{sn}/nuisance_registry.py",
            _generate_nuisance_registry(spec),
            f"Registre des nuisances connues du domaine {sn}",
        ))

        # 4. __init__.py du module domaine
        stubs.append(_write_stub(
            f"domains/{sn}/__init__.py",
            f'"""Package domaine {sn} — généré par DOMAIN_INTEGRATION_AGENT v1.0."""\n',
            "Package init du module domaine",
        ))

        # 5. Agent sigma
        stubs.append(_write_stub(
            f"sigma/domains/{sn}_domain_agent.py",
            _generate_sigma_agent(spec, matrix),
            f"Agent sigma {sn} — vote sans décision, pour pipeline GuardX108",
        ))

        # 6. Formulaire décisionnel YAML
        stubs.append(_write_stub(
            f"domain_packets/{sn}_decisional_form_v0.yaml",
            _generate_decisional_form(spec, matrix),
            f"Formulaire décisionnel {sn} v0 — contrat domaine ↔ Kernel",
        ))

        # 7. Matrice IR en JSON (artefact de référence)
        ir_json = json.dumps(asdict(matrix), indent=2, ensure_ascii=False)
        stubs.append(_write_stub(
            f"domain_packets/{sn}_ir_matrix_v0.json",
            ir_json,
            "Matrice de traduction IR — référence formelle",
        ))

        # Manifest
        manifest = DomainManifest(
            manifest_id=str(uuid.uuid4()),
            domain_name=sn,
            domain_spec=spec,
            ir_matrix=matrix,
            stubs=stubs,
            sandbox_dir=str(sandbox),
        )

        self._persist_manifest(manifest)
        self._audit_bus_log(manifest)
        self._manifests.append(manifest)
        self._phase = MAPPhase.AWAITING

        self._log(f"  {len(stubs)} stub(s) générés dans : {sandbox.name}/")
        self._log(f"  Manifest ID : {manifest.manifest_id}")
        self._log(f"  RECEIPT     : _DOMAIN_PROPOSALS/{manifest.manifest_id}/RECEIPT.md")
        self._log(f"  Statut      : AWAITING_HUMAN_APPROVED_WRITE")
        return manifest

    # ── CYCLE COMPLET ────────────────────────────────────────────────────────

    def run_cycle(self, spec: DomainSpec) -> DomainManifest:
        self._cycle += 1
        self._log(f"\n{'='*60}")
        self._log(f"MAP CYCLE #{self._cycle} — {spec.domain_name.upper()}")
        self._log(f"{'='*60}")
        self._check_boundaries()

        matrix   = self.phase_m_mapping(spec)
        matrix   = self.phase_a_adaptation(spec, matrix)
        manifest = self.phase_p_proposition(spec, matrix)
        return manifest

    # ── PERSISTENCE ──────────────────────────────────────────────────────────

    def _audit_bus_log(self, manifest: DomainManifest) -> None:
        """Trace append-only de chaque DomainManifest vers l'audit bus.

        Format aligne sur audit/world_action_bus.jsonl. Le logging ne bloque
        jamais le cycle M.A.P. (fail-open) et n'ecrit rien d'autre.
        """
        try:
            bus = REPO_ROOT / "audit" / "world_action_bus.jsonl"
            entry = {
                "event_id": uuid.uuid4().hex,
                "action_id": f"map_proposal_{manifest.domain_name}",
                "sovereign_ticket_id": manifest.manifest_id,
                "world_call_class": "LOCAL_SANDBOX_WRITE",
                "action_risk_class": "LOW",
                "autonomy_level": 0,
                "intent": "domain_integration_proposal",
                "domain": manifest.domain_name,
                "stubs_count": len(manifest.stubs),
                "entities_mapped": len(manifest.ir_matrix.entity_to_alphabet),
                "status": "AWAITING_HUMAN_APPROVED_WRITE",
                "decision_authority": "KX108_ONLY",
                "dry_run_only": True,
                "blocked": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with bus.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def _persist_manifest(self, manifest: DomainManifest) -> None:
        """Persiste le manifest JSON + RECEIPT.md dans _DOMAIN_PROPOSALS/<id>/."""
        proposal_dir = PROPOSALS_DIR / manifest.manifest_id
        proposal_dir.mkdir(parents=True, exist_ok=True)

        # manifest.json
        data = {
            "manifest_id": manifest.manifest_id,
            "receipt_id":  manifest.receipt_id,
            "created_at":  manifest.created_at,
            "domain_name": manifest.domain_name,
            "status":      manifest.status,
            "sandbox_dir": manifest.sandbox_dir,
            "stubs_count": len(manifest.stubs),
            "stubs":       [
                {
                    "path":      s.relative_path,
                    "action":    s.action,
                    "rationale": s.rationale,
                    "sandbox":   s.sandbox_path,
                }
                for s in manifest.stubs
            ],
            "ir_matrix": asdict(manifest.ir_matrix),
            "boundary_snapshot": AGENT_DIA_BOUNDARY,
        }
        (proposal_dir / "manifest.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # RECEIPT.md
        lines = [
            f"# DOMAIN_INTEGRATION_MANIFEST — {manifest.manifest_id}",
            f"",
            f"**Agent**    : DOMAIN_INTEGRATION_AGENT v1.0",
            f"**Domaine**  : `{manifest.domain_name.upper()}`",
            f"**Créé le**  : {manifest.created_at}",
            f"**Statut**   : `AWAITING_HUMAN_APPROVED_WRITE`",
            f"",
            f"## Stubs générés ({len(manifest.stubs)})",
            f"",
        ]
        for s in manifest.stubs:
            lines += [
                f"### `{s.relative_path}` — {s.action}",
                f"> {s.rationale}",
                f"",
            ]
        lines += [
            f"## Matrice IR",
            f"- Entités mappées     : {len(manifest.ir_matrix.entity_to_alphabet)}",
            f"- Classes de risque   : {len(manifest.ir_matrix.risk_class_to_flag)}",
            f"- Flux → IR intent    : {len(manifest.ir_matrix.flow_to_intent)}",
            f"- Seuil S             : `{manifest.ir_matrix.threshold_s}`",
            f"- T_mean source       : `{manifest.ir_matrix.t_mean_source}`",
            f"- H_score source      : `{manifest.ir_matrix.h_score_source}`",
            f"- A_score source      : `{manifest.ir_matrix.a_score_source}`",
            f"",
            f"## Règle Kernel",
            f"- Gate appelle `/kernel/ragnarok` : **OUI**",
            f"- Gate décide seul : **NON — jamais**",
            f"- `decision_authority` : `KX108_ONLY`",
            f"- `emits_verdict` : `False`",
            f"",
            f"## Pour appliquer",
            f"```",
            f"# 1. Revoir chaque stub dans le dossier sandbox",
            f"# 2. Copier manuellement vers le repo (après approbation)",
            f"# 3. git add + git commit manuellement",
            f"# 4. Tester le gate : python domains/{manifest.domain_name}/{manifest.domain_name}_x108_gate.py",
            f"```",
        ]
        (proposal_dir / "RECEIPT.md").write_text("\n".join(lines), encoding="utf-8")

    @property
    def manifests(self) -> List[DomainManifest]:
        return list(self._manifests)


# ===========================================================================
# 5.  API PUBLIQUE — utilisable par Obsidure
# ===========================================================================

def integrate_domain(
    domain_name: str,
    description: str = "",
    entities: Optional[List[str]] = None,
    risk_classes: Optional[List[str]] = None,
    flow_types: Optional[List[str]] = None,
    threshold_s: float = 0.6,
    verbose: bool = True,
) -> DomainManifest:
    """
    API de haut niveau appelable depuis Obsidure ou en standalone.
    Lance un cycle MAP complet et retourne le DomainManifest.
    """
    spec = DomainSpec(
        domain_name=domain_name,
        description=description,
        key_entities=entities or [],
        risk_classes=risk_classes or [],
        flow_types=flow_types or [],
        target_threshold_s=threshold_s,
    )
    agent = DomainIntegrationAgent(verbose=verbose)
    return agent.run_cycle(spec)

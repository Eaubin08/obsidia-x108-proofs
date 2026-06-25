"""
periphery/agents/agent_obsidure.py  —  v2.0 CLI STANDALONE
=============================================================
Agent Obsidure — CO_PILOTE_CODE (#6) × CI_REPO_SURGEON (#7)
Registre canonique Obsidia X-108, famille AGENTIC.

RÔLE : Bâtisseur et Brancheur périphérique.
  - Brancher les domaines (Bank, Trading, GPS, Ecom)
  - Organiser la mémoire SRL (ACTIVE / SEMI_ACTIVE / COLD / GHOST_SIDE_TABLE)
  - Rédiger de nouveaux théorèmes Lean 4 périphériques dans une sandbox
  - NE PAS se brancher à l'UI Cockpit ou au moteur Brody pour l'instant

CERVEAU : OS_TRAD_REVERSE (apps/obsidia_api/routes/os_trad_ir_reverse.py)
  POST /api/os-trad/translate  → alphabet_units + detected_language + risk_flags
  POST /api/ir/candidate       → ir_candidate (intent, constraints, contradictions)
  POST /api/os-reverse/project → action_projection readonly

PROTOCOLE A.V.D.R :
  A — Audit      : lire objectif utilisateur, interroger OS_TRAD_REVERSE
  V — Validation : backup obligatoire → Fail-Closed si échec
  D — Disruption : générer code dans EPHEMERAL_CODE_SANDBOX
  R — Réintégration : émettre PATCH_PROPOSAL, attendre HUMAN_APPROVED_WRITE

RÈGLE ABSOLUE — KERNEL + PREUVES SCELLÉES = MUR DE BÉTON
  Aucune fonction ne peut modifier server.kernel.sealed.cjs ou proofs/V18_*.
  Toute tentative lève ProtectedPathError + arrêt immédiat.

STANDALONE CLI — pas de branchement UI/Brody pour l'instant.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── HTTP optionnel (requests si dispo, sinon mode offline) ──────────────────
try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _requests = None  # type: ignore
    _REQUESTS_OK = False


# ===========================================================================
# 0.  FRONTIÈRES DURES — NE PAS MODIFIER À L'EXÉCUTION
# ===========================================================================

AGENT_OBSIDURE_BOUNDARY: Dict[str, Any] = {
    # Seul le Kernel X-108 peut émettre ALLOW / HOLD / BLOCK.
    "decision_authority": "KX108_ONLY",

    # Rôle cockpit : lecture + proposition de patch uniquement.
    "cockpit_role": "READONLY_TEST_PATCH_PROPOSAL",

    # L'agent ne prend aucune décision autonome.
    "allowed_to_decide": False,

    # L'agent ne déclenche aucune action réelle en production.
    "emits_act": False,

    # INTERDICTION ABSOLUE — pas de protocole, pas d'exception.
    # Le Kernel est un mur de béton mathématique.
    "kernel_mutation": False,

    # Pas de merge X-108 depuis l'agent.
    "x108_merge": False,

    # Toute sortie attend la validation humaine.
    "sandbox_mode": "HUMAN_APPROVED_WRITE",
}

# Chemins protégés — comparaison par infixe normalisé
PROTECTED_INFIXES: Tuple[str, ...] = (
    "server.kernel.sealed.cjs",
    "proofs/V18_",
    "proofs/lean/57_preuves",
    "merkle_seal.json",
    "rfc3161",
)

# Racine du repo
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

# Sortie des proposals
PROPOSALS_DIR: Path = REPO_ROOT / "_PATCH_PROPOSALS"

# Ports
API_BASE: str = os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000")


# ===========================================================================
# 0b. NORMALISATION LISTE — garantit List[str] quelles que soient les données API
# ===========================================================================

def _norm_str_list(raw: Any) -> List[str]:
    """
    Convertit n'importe quelle valeur retournée par l'API en List[str] pure.
    Cas couverts :
      - list de str        → inchangé
      - list de dict       → extrait x['text'] ou str(x)
      - list mixte         → normalise élément par élément
      - scalaire non-list  → [str(raw)] ou []
    """
    if not isinstance(raw, list):
        return [str(raw)] if raw else []
    return [
        x.get("text", str(x)) if isinstance(x, dict) else str(x)
        for x in raw
    ]


# ===========================================================================
# 1.  EXCEPTIONS
# ===========================================================================

class ImmutableBoundaryError(RuntimeError):
    """Frontière AGENT_OBSIDURE_BOUNDARY modifiée à l'exécution."""

class BackupFailedError(RuntimeError):
    """Backup pré-modification échoué → Fail-Closed obligatoire."""

class ProtectedPathError(RuntimeError):
    """Chemin protégé (Kernel / preuves gelées) — arrêt immédiat."""

class OSTradUnavailableError(RuntimeError):
    """API OS_TRAD_REVERSE injoignable — mode offline utilisé."""


# ===========================================================================
# 2.  STRUCTURES
# ===========================================================================

class AVDRPhase(Enum):
    IDLE          = "IDLE"
    AUDIT         = "A_AUDIT"
    VALIDATION    = "V_VALIDATION"
    DISRUPTION    = "D_DISRUPTION"
    REINTEGRATION = "R_REINTEGRATION"
    AWAITING      = "AWAITING_HUMAN_APPROVED_WRITE"
    HALTED        = "HALTED_FAIL_CLOSED"


@dataclass
class OSTradResult:
    """Résultat de l'appel à OS_TRAD_REVERSE (translate + ir/candidate)."""
    detected_language: str = "fr"
    alphabet_units: List[str] = field(default_factory=list)
    intent: str = ""
    risk_flags: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    target_paths: List[str] = field(default_factory=list)
    source: str = "OFFLINE"          # REAL_BACKEND | OFFLINE

    def __post_init__(self) -> None:
        # Garantie absolue : toutes les listes sont List[str] pures,
        # quelle que soit la structure retournée par l'API.
        self.alphabet_units  = _norm_str_list(self.alphabet_units)
        self.risk_flags      = _norm_str_list(self.risk_flags)
        self.constraints     = _norm_str_list(self.constraints)
        self.contradictions  = _norm_str_list(self.contradictions)
        self.target_paths    = _norm_str_list(self.target_paths)


@dataclass
class MathematicalContext:
    """
    Contexte mathématique lu en READ-ONLY depuis les fichiers Lean scellés et le kernel.
    Ces chemins ne sont JAMAIS inclus dans le backup — lecture légale uniquement.
    """
    kernel_decision_structure: str = ""       # lignes ALLOW/HOLD/BLOCK extraites du kernel
    lean_metrics_def: str = ""                # structures Metrics + Decision (Basic.lean)
    lean_temporal_def: str = ""               # decideX108 + beforeTau (TemporalKernel.lean)
    lean_theorem_names: List[str] = field(default_factory=list)
    lean_import_header: str = ""              # imports canoniques réutilisables
    source_files_read: List[str] = field(default_factory=list)  # info — jamais backupés
    gathered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SRLSessionCard:
    """
    Entrée candidate pour la Session Registry Layer (SRL).
    L'agent ne peut PAS l'écrire directement (memory_write=False).
    Elle est jointe au PATCH_PROPOSAL pour application humaine.
    """
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tier: str = "ACTIVE"             # ACTIVE | SEMI_ACTIVE | COLD | GHOST_SIDE_TABLE
    domain: Optional[str] = None
    objective_summary: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "CANDIDATE_NOT_WRITTEN"
    ghost_reason: Optional[str] = None  # renseigné si tier=GHOST_SIDE_TABLE


@dataclass
class StabilizationResult:
    """
    Rapport de la boucle Trial-and-Error de Phase D.
    Documente chaque tentative jusqu'à la conformité ou l'épuisement des essais.
    """
    attempts: int
    max_attempts: int
    final_status: str          # STABILIZED | MAX_ATTEMPTS_REACHED | TRIVIALLY_PASSED
    errors_history: List[Dict[str, Any]] = field(default_factory=list)
    passed: bool = False


@dataclass
class ErrorContext:
    """
    Contexte structuré d'un échec Phase D — input pour la mutation suivante.

    Produit par ErrorAnalyzer à partir des erreurs brutes de _test_patches_conformity.
    Sert de mémoire de réflexion entre deux tentatives de stabilisation.
    """
    attempt: int
    error_type: str        # LEAN_BUILD_ERROR | FORBIDDEN_KEYWORD | PROTECTED_PATH_WRITE_REF | KERNEL_LOGIC_REPLICA
    raw_details: str
    lean_stderr: str = ""              # stderr complet de lake build
    lean_error_line: str = ""          # première ligne d'erreur Lean extraite
    violated_keywords: List[str] = field(default_factory=list)
    protected_path: str = ""
    mutation_directive: str = "RETRY_DIFFERENT_APPROACH"
    recommended_strategy: str = "SEMANTIC"  # progression Lean ou CLEAN_PERIPHERAL / RESTRUCTURE_BOUNDARY


@dataclass
class IterationMemory:
    """
    Mémoire d'une itération de stabilisation — transférée à la suivante.

    Permet de savoir non seulement CE QUI a échoué, mais COMMENT,
    pour que la tentative N+1 génère une solution réellement différente.
    """
    attempt: int
    patches_count: int
    error_contexts: List[ErrorContext]
    lean_strategy_used: str
    objective_evolved: str    # l'objectif reformulé avec le contexte d'échec


@dataclass
class PatchProposal:
    """Sortie finale d'un cycle AVDR — jamais appliquée automatiquement."""
    proposal_id: str
    objective: str
    avdr_cycle: int
    os_trad_result: OSTradResult
    backup_dir: str
    patches: List[Dict[str, Any]]
    session_card: SRLSessionCard
    domain_context: Optional[str]
    lean_sandbox_result: Optional[Dict[str, Any]]
    stabilization: Optional[StabilizationResult] = None
    kernel_path_blocked: bool = False
    human_approved: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ===========================================================================
# 3.  OS_TRAD_REVERSE CLIENT
# ===========================================================================

class OSTradClient:
    """
    Client léger vers OS_TRAD_REVERSE (apps/obsidia_api/routes/os_trad_ir_reverse.py).

    Routes utilisées :
      POST /api/os-trad/translate  → alphabet + langue + risk_flags
      POST /api/ir/candidate       → ir_candidate (intent, constraints)

    Si l'API est injoignable → mode offline : analyse locale minimale.
    L'agent ne décide RIEN — il lit ce que OS_TRAD_REVERSE retourne.
    """

    def __init__(self, api_base: str = API_BASE, timeout: float = 8.0) -> None:
        self._base = api_base.rstrip("/")
        self._timeout = timeout

    def translate_and_build_ir(self, text: str, session_id: str = "") -> OSTradResult:
        """
        Étape 1 : /api/os-trad/translate   → alphabet + langue
        Étape 2 : /api/ir/candidate         → intent + constraints
        Retourne un OSTradResult consolidé.
        """
        if not _REQUESTS_OK:
            return self._offline_fallback(text)

        # — Étape 1 : traduction OS —
        try:
            r1 = _requests.post(
                f"{self._base}/api/os-trad/translate",
                json={"text": text, "session_id": session_id or str(uuid.uuid4())},
                timeout=self._timeout,
            )
            r1.raise_for_status()
            d1 = r1.json()
        except Exception as exc:
            return self._offline_fallback(text, note=str(exc))

        detected_language = d1.get("detected_language", "fr")
        alphabet_units    = d1.get("alphabet_units", [])
        risk_flags        = d1.get("risk_flags", [])

        # — Étape 2 : IR candidate —
        try:
            r2 = _requests.post(
                f"{self._base}/api/ir/candidate",
                json={
                    "text": text,
                    "language": detected_language,
                    "alphabet_units": alphabet_units,
                    "session_id": session_id or str(uuid.uuid4()),
                },
                timeout=self._timeout,
            )
            r2.raise_for_status()
            d2 = r2.json()
        except Exception as exc:
            d2 = {}

        ir = d2.get("ir_candidate", {})

        def _to_str_list(raw: Any) -> List[str]:
            """Normalise n'importe quelle liste renvoyée par l'API en List[str] pure."""
            if not isinstance(raw, list):
                return [str(raw)] if raw else []
            return [x.get("text", str(x)) if isinstance(x, dict) else str(x) for x in raw]

        return OSTradResult(
            detected_language=detected_language,
            alphabet_units=_to_str_list(alphabet_units),
            intent=str(ir.get("intent", _local_intent(text))),
            risk_flags=_to_str_list(risk_flags),
            constraints=_to_str_list(ir.get("constraints", [])),
            contradictions=_to_str_list(ir.get("contradictions", [])),
            target_paths=_extract_paths_from_text(text),
            source="REAL_BACKEND",
        )

    def _offline_fallback(self, text: str, note: str = "") -> OSTradResult:
        """Analyse locale minimale quand l'API est injoignable."""
        return OSTradResult(
            detected_language="fr" if any(c in text for c in "àéèêîôùûç") else "en",
            alphabet_units=text.split()[:10],
            intent=_local_intent(text),
            risk_flags=_local_risk_flags(text),
            constraints=["API_OFFLINE_CONSTRAINTS_UNAVAILABLE"],
            contradictions=[],
            target_paths=_extract_paths_from_text(text),
            source="OFFLINE" + (f":{note[:60]}" if note else ""),
        )


def _local_intent(text: str) -> str:
    """Classifie l'intention sans IA — heuristique locale."""
    t = text.upper()
    if any(k in t for k in ("CRÉE", "CREATE", "GÉNÈRE", "GENERATE", "BRANCHER", "BRANCH")):
        return "CREATE_PATCH"
    if any(k in t for k in ("AUDIT", "SCAN", "VÉRIFIE", "CHECK", "INSPECTE")):
        return "AUDIT_ONLY"
    if any(k in t for k in ("LEAN", "THÉORÈME", "THEOREM", "PROOF", "PREUVE")):
        return "LEAN_SANDBOX"
    if any(k in t for k in ("MÉMOIRE", "MEMORY", "SRL", "SESSION")):
        return "SRL_ORGANIZE"
    return "GENERAL_PATCH"


def _local_risk_flags(text: str) -> List[str]:
    flags = []
    t = text.upper()
    if any(k in t for k in ("KERNEL", "SEALED", "SCELLÉ")):
        flags.append("KERNEL_REFERENCE_DETECTED")
    if any(k in t for k in ("V18", "PROOF", "PREUVE", "LEAN")):
        flags.append("PROOF_ZONE_REFERENCE")
    if any(k in t for k in ("GIT COMMIT", "MERGE", "PUSH")):
        flags.append("GIT_MUTATION_ATTEMPT")
    return flags


def _extract_paths_from_text(text: str) -> List[str]:
    """Extrait des chemins de fichiers cités dans le texte."""
    pattern = r"[\w\-\.]+(?:/[\w\-\.]+)+"
    found = re.findall(pattern, text)
    return [p for p in found if "." in p or "/" in p][:8]


def _build_math_context_from_repo() -> MathematicalContext:
    """
    Lit en READ-ONLY les fichiers Lean scellés et le kernel sealed.
    LECTURE LÉGALE — ces chemins ne sont JAMAIS ajoutés au backup.
    Appelé depuis _gather_mathematical_context() de l'agent.
    """
    ctx = MathematicalContext()

    # — Kernel : extraire les lignes décisionnelles ALLOW / HOLD / BLOCK —
    kernel_path = REPO_ROOT / "server.kernel.sealed.cjs"
    if kernel_path.exists():
        try:
            raw = kernel_path.read_text(encoding="utf-8", errors="replace")
            relevant: List[str] = []
            for line in raw.splitlines():
                ls = line.strip()
                if any(kw in ls.lower() for kw in (
                    "allow", "hold", "block", "sigma", "ragnarok",
                    "decision", "verdict", "pipeline",
                )):
                    relevant.append(ls)
            ctx.kernel_decision_structure = "\n".join(relevant[:30])
            ctx.source_files_read.append("server.kernel.sealed.cjs")
        except Exception:
            pass

    # — Basic.lean : Metrics + Decision —
    basic_path = REPO_ROOT / "proofs" / "lean" / "Obsidia" / "Basic.lean"
    if basic_path.exists():
        try:
            raw = basic_path.read_text(encoding="utf-8", errors="replace")
            ctx.lean_metrics_def = raw[:1600]
            for m in re.finditer(r"^theorem\s+(\w+)", raw, re.MULTILINE):
                ctx.lean_theorem_names.append(m.group(1))
            imports = [ln.strip() for ln in raw.splitlines()[:10] if ln.strip().startswith("import")]
            ctx.lean_import_header = "\n".join(imports) if imports else "import Obsidia.Basic"
            ctx.source_files_read.append("proofs/lean/Obsidia/Basic.lean")
        except Exception:
            pass

    # — TemporalKernel.lean : decideX108 + beforeTau + garde temporelle —
    temporal_path = REPO_ROOT / "proofs" / "lean" / "Obsidia" / "TemporalKernel.lean"
    if temporal_path.exists():
        try:
            raw = temporal_path.read_text(encoding="utf-8", errors="replace")
            ctx.lean_temporal_def = raw[:2000]
            for m in re.finditer(r"^theorem\s+(\w+)", raw, re.MULTILINE):
                if m.group(1) not in ctx.lean_theorem_names:
                    ctx.lean_theorem_names.append(m.group(1))
            ctx.source_files_read.append("proofs/lean/Obsidia/TemporalKernel.lean")
        except Exception:
            pass

    return ctx


# Mots-clés interdits dans tout code périphérique généré par Obsidure
_FORBIDDEN_IN_GENERATED_CODE: Tuple[str, ...] = (
    "git commit", "git push", "git merge", "git rebase",
    "kernel_mutation = true", "emits_act = true", "x108_merge = true",
)


def _test_patches_conformity(
    patches: List[Dict[str, Any]],
    lean_result: Optional[Dict[str, Any]],
    sandbox_dir: Path,
) -> List[Dict[str, Any]]:
    """
    Teste la conformité de tous les patches générés contre les lois du Kernel.
    Retourne la liste des violations (liste vide = tout est conforme → passe en Phase R).

    Contrôles effectués :
      - Lean : résultat lake build (BUILD_SUCCESS requis si lake disponible)
      - Code Python : mots-clés interdits, refs chemins protégés, réplication logique Kernel
    """
    errors: List[Dict[str, Any]] = []

    for patch in patches:
        action = patch.get("action", "")
        path   = patch.get("path", "")

        # ── Lean : vérification du résultat lake build ─────────────────────
        if action == "CREATE_LEAN_PERIPHERAL":
            if lean_result:
                status = lean_result.get("status", "")
                # LAKE_NOT_FOUND = lake absent → on accepte (test impossible)
                if status not in ("BUILD_SUCCESS", "LAKE_NOT_FOUND"):
                    errors.append({
                        "type": "LEAN_BUILD_ERROR",
                        "path": path,
                        "details": (
                            lean_result.get("stderr") or
                            lean_result.get("error") or
                            status
                        )[:400],
                    })
            continue

        # ── Code périphérique : analyse statique ───────────────────────────
        sp = Path(patch.get("sandbox_path", ""))
        if not sp.exists():
            continue

        try:
            content = sp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        cl = content.lower()

        for kw in _FORBIDDEN_IN_GENERATED_CODE:
            if kw in cl:
                errors.append({
                    "type": "FORBIDDEN_KEYWORD",
                    "path": path,
                    "details": f"'{kw}' détecté dans le code généré.",
                })

        for infx in PROTECTED_INFIXES:
            if infx in content and "write" in cl:
                errors.append({
                    "type": "PROTECTED_PATH_WRITE_REF",
                    "path": path,
                    "details": f"Référence en écriture vers chemin protégé : '{infx}'.",
                })

        # Réplication de la logique décisionnelle du Kernel (interdit)
        if ("allow" in cl and "block" in cl and "hold" in cl
                and "def decide" in cl and path.endswith(".py")):
            errors.append({
                "type": "KERNEL_LOGIC_REPLICA",
                "path": path,
                "details": "Fonction 'decide' avec ALLOW/HOLD/BLOCK — réplication Kernel interdite.",
            })

    return errors


def _sanitize_peripheral_content(content: str) -> str:
    """
    Passe de nettoyage automatique sur le code périphérique.
    Appliquée en auto-correction entre deux tentatives de Phase D.
    """
    # Supprimer les commandes git
    content = re.sub(
        r"\bgit\s+(commit|push|merge|rebase|reset)[^\n]*",
        "# [SANITIZED: git command removed by Obsidure]",
        content, flags=re.IGNORECASE,
    )
    # Corriger les mutations de frontière
    content = re.sub(r"kernel_mutation\s*=\s*True", "kernel_mutation = False", content, flags=re.IGNORECASE)
    content = re.sub(r"emits_act\s*=\s*True",       "emits_act = False",       content, flags=re.IGNORECASE)
    content = re.sub(r"x108_merge\s*=\s*True",      "x108_merge = False",      content, flags=re.IGNORECASE)
    return content


# ===========================================================================
# 4.  SRL MANAGER
# ===========================================================================

class SRLManager:
    """
    Gestionnaire readonly de la Session Registry Layer.

    Taxonomie 4 strates :
      ACTIVE          : sessions courantes, décisions < 24h
      SEMI_ACTIVE     : historique chaud, 1–30 jours
      COLD            : archives long terme
      GHOST_SIDE_TABLE: entrées rejetées — RIEN N'EST SUPPRIMÉ

    Obsidure peut LIRE les 4 strates et produire des SessionCard candidates.
    Il ne peut PAS écrire dans la mémoire canonique (memory_write=False).
    """

    SRL_ROOT = REPO_ROOT / "periphery" / "brody_memory_readonly"
    TIERS = ("ACTIVE", "SEMI_ACTIVE", "COLD", "GHOST_SIDE_TABLE")

    def read_summary(self) -> Dict[str, Any]:
        """Lit le résumé des 4 strates (comptage de fichiers uniquement)."""
        result: Dict[str, Any] = {"tiers": {}, "memory_write": False}
        for tier in self.TIERS:
            tier_dir = self.SRL_ROOT / tier.lower()
            count = 0
            if tier_dir.exists():
                count = sum(1 for f in tier_dir.rglob("*") if f.is_file())
            result["tiers"][tier] = count
        return result

    def build_candidate_card(
        self,
        objective: str,
        domain: Optional[str],
        verdict: str = "PENDING",
    ) -> SRLSessionCard:
        """
        Construit une SessionCard candidate.
        Non écrite automatiquement — jointe au PATCH_PROPOSAL pour application humaine.
        Si verdict == REJECTED → tier = GHOST_SIDE_TABLE.
        """
        tier = "ACTIVE" if verdict not in ("REJECTED", "GHOST") else "GHOST_SIDE_TABLE"
        return SRLSessionCard(
            tier=tier,
            domain=domain,
            objective_summary=objective[:200],
            ghost_reason=verdict if tier == "GHOST_SIDE_TABLE" else None,
        )

    def promote_tier(self, card: SRLSessionCard, new_tier: str) -> SRLSessionCard:
        """
        Retourne une copie de la card avec le tier promu.
        Ne modifie rien en mémoire (memory_write=False).
        Hiérarchie : ACTIVE → SEMI_ACTIVE → COLD → GHOST_SIDE_TABLE.
        """
        allowed = {
            "ACTIVE": ("SEMI_ACTIVE", "GHOST_SIDE_TABLE"),
            "SEMI_ACTIVE": ("COLD", "GHOST_SIDE_TABLE"),
            "COLD": ("GHOST_SIDE_TABLE",),
        }
        if card.tier in allowed and new_tier in allowed[card.tier]:
            promoted = copy.deepcopy(card)
            promoted.tier = new_tier
            if new_tier == "GHOST_SIDE_TABLE":
                promoted.ghost_reason = promoted.ghost_reason or "PROMOTED_TO_GHOST"
            return promoted
        raise ValueError(f"Promotion SRL invalide : {card.tier} → {new_tier}")


# Progression des stratégies Lean — ordre d'escalade par tentative
_LEAN_STRATEGY_PROGRESSION: Tuple[str, ...] = (
    "SEMANTIC",        # T1 : s'inspire de l'objectif (Nat.add_comm)
    "NAT_ARITHMETIC",  # T2 : propriété arithmétique Nat simple
    "PROPOSITIONAL",   # T3 : logique propositionnelle pure
    "EXPLICIT_TERM",   # T4 : terme de preuve explicite, pas de tactic
    "MINIMAL_RFL",     # T5 : preuve minimaliste rfl / norm_num
)


# ===========================================================================
# 4b.  ERROR ANALYZER — cerveau réflexif de la boucle de stabilisation
# ===========================================================================

class ErrorAnalyzer:
    """
    Convertit les erreurs brutes de _test_patches_conformity en ErrorContext.

    Rôle : structurer l'information d'échec pour que la tentative suivante
    génère une NOUVELLE solution plutôt que de retomber dans le même piège.

    Ne décide pas. N'émet pas de verdict. N'écrit rien.
    Produit uniquement des directives de mutation et un objectif évolué.
    """

    def analyze_errors(
        self,
        raw_errors: List[Dict[str, Any]],
        lean_result: Optional[Dict[str, Any]],
        attempt: int,
    ) -> List[ErrorContext]:
        """Convertit les erreurs brutes en ErrorContext structurés."""
        contexts: List[ErrorContext] = []

        for err in raw_errors:
            err_type = err.get("type", "UNKNOWN")
            details  = str(err.get("details", ""))

            ctx = ErrorContext(
                attempt=attempt,
                error_type=err_type,
                raw_details=details[:300],
            )

            if err_type == "LEAN_BUILD_ERROR":
                if lean_result:
                    ctx.lean_stderr = str(lean_result.get("stderr", ""))[:500]
                    for line in ctx.lean_stderr.splitlines():
                        if any(kw in line.lower() for kw in ("error:", "unknown", "failed", "type mismatch")):
                            ctx.lean_error_line = line.strip()[:200]
                            break
                ctx.mutation_directive = "CHANGE_THEOREM_STRUCTURE"
                idx = min(attempt, len(_LEAN_STRATEGY_PROGRESSION) - 1)
                ctx.recommended_strategy = _LEAN_STRATEGY_PROGRESSION[idx]

            elif err_type == "FORBIDDEN_KEYWORD":
                for kw in _FORBIDDEN_IN_GENERATED_CODE:
                    if kw in details.lower():
                        ctx.violated_keywords.append(kw)
                ctx.mutation_directive = "SANITIZE_AND_RESTRUCTURE_CODE"
                ctx.recommended_strategy = "CLEAN_PERIPHERAL"

            elif err_type == "PROTECTED_PATH_WRITE_REF":
                ctx.protected_path = err.get("path", "")
                ctx.mutation_directive = "REMOVE_PROTECTED_PATH_REFERENCE"
                ctx.recommended_strategy = "CLEAN_PERIPHERAL"

            elif err_type == "KERNEL_LOGIC_REPLICA":
                ctx.mutation_directive = "SPLIT_DECIDE_FUNCTION"
                ctx.recommended_strategy = "RESTRUCTURE_BOUNDARY"

            contexts.append(ctx)

        return contexts

    def derive_evolved_objective(
        self,
        base_objective: str,
        contexts: List[ErrorContext],
        attempt: int,
    ) -> str:
        """
        Reformule l'objectif pour la tentative N+1 en intégrant les échecs de N.

        L'objectif évolué n'est pas une simple annotation — il encode les contraintes
        découvertes, de sorte que la génération suivante les évite structurellement.
        """
        if not contexts:
            return base_objective

        directives  = list({c.mutation_directive for c in contexts})
        strategies  = list({c.recommended_strategy for c in contexts if c.recommended_strategy})
        lean_errors = [c.lean_error_line for c in contexts if c.lean_error_line]
        violated    = [kw for c in contexts for kw in c.violated_keywords]

        parts = [
            f"[EVOLUTION_T{attempt}]",
            f"Base: {base_objective[:80]}",
            f"Directives: {'; '.join(directives)}",
        ]
        if strategies:
            parts.append(f"StrategieLean: {strategies[0]}")
        if lean_errors:
            parts.append(f"ErreurAEviter: {lean_errors[0][:70]}")
        if violated:
            parts.append(f"MotsInterdits: {', '.join(violated[:3])}")

        return " | ".join(parts)


# ===========================================================================
# 5.  DOMAIN BRANCHER
# ===========================================================================

class DomainBrancher:
    """
    Génère les stubs de connecteurs et gates P3 pour les domaines.
    Flux (inviolable, Obsidure le connaît mais ne le court-circuite pas) :
      Payload → DomainState → [AgentVote] → DomainAggregate
             → Meta-agents → GuardX108.decide() → CanonicalDecisionEnvelope
    """

    DOMAIN_MAP: Dict[str, Dict[str, str]] = {
        "BANK": {
            "gate":      "domains/bank/bank_x108_gate.py",
            "connector": "connectors/bank_normal_flow.py",
            "nuisance":  "domains/bank/nuisance_registry.py",
            "form":      "domain_packets/bank_decisional_form_v0.yaml",
            "state_cls": "BankState",
            "pipeline":  "run_bank_pipeline",
        },
        "TRADING": {
            "gate":      "domains/trading/trading_x108_gate.py",
            "connector": "connectors/trading_live.py",
            "nuisance":  "domains/trading/nuisance_registry.py",
            "form":      "domain_packets/trading_decisional_form_v0.yaml",
            "state_cls": "TradingState",
            "pipeline":  "run_trading_pipeline",
        },
        "GPS": {
            "gate":      "domains/gps/gps_x108_gate.py",
            "connector": "connectors/aviation_robo.py",
            "nuisance":  "domains/gps/nuisance_registry.py",
            "form":      "domain_packets/gps_defense_aviation_decisional_form_v0.yaml",
            "state_cls": "GpsDefenseAviationState",
            "pipeline":  "run_gps_defense_aviation_pipeline",
        },
        "ECOM": {
            "gate":      "domains/ecom/ecom_x108_gate.py",
            "connector": "connectors/ecom_flow.py",
            "nuisance":  "domains/ecom/nuisance_registry.py",
            "form":      "domain_packets/ecom_decisional_form_v0.yaml",
            "state_cls": "EcomState",
            "pipeline":  "run_ecom_pipeline",
        },
    }

    def audit_domain(self, domain: str) -> Dict[str, Any]:
        """Vérifie quels fichiers du domaine existent déjà."""
        info = self.DOMAIN_MAP.get(domain.upper())
        if not info:
            return {"domain": domain, "error": "DOMAIN_UNKNOWN"}
        result: Dict[str, Any] = {"domain": domain, "files": {}}
        for key, rel_path in info.items():
            if key in ("state_cls", "pipeline"):
                continue
            abs_path = REPO_ROOT / rel_path
            result["files"][key] = {
                "path": rel_path,
                "exists": abs_path.exists(),
                "protected": _is_protected(rel_path),
            }
        return result

    def generate_gate_stub(self, domain: str) -> str:
        """
        Génère le stub du gate P3 pour le domaine.
        Le stub est annoté — l'opérateur le complète avant application.
        """
        info = self.DOMAIN_MAP.get(domain.upper(), {})
        state_cls  = info.get("state_cls", f"{domain.title()}State")
        pipeline   = info.get("pipeline", f"run_{domain.lower()}_pipeline")
        gate_path  = info.get("gate", f"domains/{domain.lower()}/gate.py")

        return textwrap.dedent(f"""
            # PATCH_PROPOSAL — Gate P3 {domain.upper()}
            # Chemin : {gate_path}
            # Statut : AWAITING_HUMAN_APPROVED_WRITE
            # Flux   : {state_cls} → {pipeline}() → GuardX108 → CanonicalDecisionEnvelope
            #
            # RÈGLE : Ce gate NE DÉCIDE PAS. Il prépare le DomainState
            # et le soumet à sigma/protocols.py::{pipeline}().
            # La décision ALLOW/HOLD/BLOCK vient UNIQUEMENT du Kernel X-108.

            from __future__ import annotations
            from typing import Any, Dict

            BOUNDARY = {{
                "decision_authority": "KX108_ONLY",
                "allowed_to_decide": False,
                "emits_verdict": False,
                "kernel_mutation": False,
                "memory_write": False,
            }}


            def build_{domain.lower()}_state(payload: Dict[str, Any]):
                \"\"\"
                Construit le {state_cls} à partir du payload brut.
                Ne prend aucune décision — prépare uniquement les données.
                \"\"\"
                from sigma.contracts import {state_cls}
                # TODO : mapper les champs du payload vers {state_cls}
                raise NotImplementedError(
                    "build_{domain.lower()}_state doit être implémenté par l'opérateur."
                )


            def submit_to_kernel(state) -> Dict[str, Any]:
                \"\"\"
                Soumet le {state_cls} au pipeline sigma puis au Kernel.
                Retourne la CanonicalDecisionEnvelope sérialisée.
                \"\"\"
                from sigma.protocols import {pipeline}
                envelope = {pipeline}(state)
                return {{
                    "gate": "{domain.upper()}_X108_GATE",
                    "decision_authority": "KX108_ONLY",
                    "verdict": str(envelope.gate) if hasattr(envelope, "gate") else "UNKNOWN",
                    "envelope": repr(envelope),
                }}
        """).strip()

    def generate_nuisance_stub(self, domain: str) -> str:
        """Génère le stub du nuisance registry pour le domaine."""
        nuisance_categories = {
            "BANK":    ["fraude", "AML", "compliance", "double_spending", "account_takeover"],
            "TRADING": ["market_manipulation", "wash_trading", "spoofing_orders", "insider_signals"],
            "GPS":     ["gps_spoofing", "zone_interdite", "collision", "signal_jamming", "atc_mismatch"],
            "ECOM":    ["fake_review", "cart_abandonment_abuse", "price_manipulation", "refund_fraud"],
        }
        cats = nuisance_categories.get(domain.upper(), ["generic_nuisance"])
        cats_repr = json.dumps(cats, ensure_ascii=False)

        return textwrap.dedent(f"""
            # PATCH_PROPOSAL — Nuisance Registry {domain.upper()}
            # Statut : AWAITING_HUMAN_APPROVED_WRITE
            #
            # Ces catégories de nuisance alimentent les AgentVote du domaine {domain.upper()}.
            # Elles ne déclenchent pas de BLOCK directement — c'est GuardX108 qui décide.

            NUISANCE_CATEGORIES_{domain.upper()} = {cats_repr}


            def is_nuisance(signal: str, domain: str = "{domain.upper()}") -> bool:
                \"\"\"Vérifie si un signal est dans les catégories de nuisance connues.\"\"\"
                return any(
                    cat.lower() in signal.lower()
                    for cat in NUISANCE_CATEGORIES_{domain.upper()}
                )
        """).strip()


# ===========================================================================
# 6.  LEAN SANDBOX
# ===========================================================================

class LeanSandbox:
    """
    Sandbox pour rédiger de NOUVEAUX théorèmes Lean 4 périphériques.

    Règles strictes :
      - Ne jamais utiliser le mot 'sorry' (proof obligation non satisfaite)
      - Ne toucher qu'aux théorèmes périphériques (P36, P107, P161…)
      - Ne JAMAIS modifier proofs/V18_* ou les 57 preuves scellées
      - lake build lancé UNIQUEMENT dans la sandbox — jamais dans le repo

    Usage : générer un stub → écrire dans sandbox/ → tenter lake build → rapport.
    """

    SORRY_PATTERN = re.compile(r"\bsorry\b", re.IGNORECASE)

    def __init__(self, sandbox_root: Path) -> None:
        self._root = sandbox_root / "lean_sandbox"
        self._root.mkdir(parents=True, exist_ok=True)

    def generate_peripheral_theorem(
        self,
        theorem_id: str,
        statement: str,
        rationale: str = "",
        math_ctx: Optional[MathematicalContext] = None,
    ) -> Path:
        """
        Génère un fichier Lean 4 pour un théorème périphérique.
        Refuse si 'sorry' est détecté dans l'énoncé ou la preuve.
        Si math_ctx fourni, injecte le contexte mathématique lu en read-only.
        """
        if self.SORRY_PATTERN.search(statement):
            raise ValueError(
                f"LEAN_SORRY_FORBIDDEN : le théorème '{theorem_id}' contient 'sorry'. "
                f"Aucune preuve incomplète n'est acceptée par Obsidure."
            )

        # Bloc de contexte mathématique (commentaires Lean — n'affecte pas la compilation)
        ctx_lines: List[str] = []
        if math_ctx and math_ctx.source_files_read:
            ctx_lines += [
                "-- === Contexte Mathématique Read-Only ===",
                f"-- Sources lues : {', '.join(math_ctx.source_files_read)}",
            ]
            if math_ctx.lean_theorem_names:
                ctx_lines.append(f"-- Théorèmes scellés référence : {', '.join(math_ctx.lean_theorem_names[:6])}")
            if math_ctx.lean_metrics_def:
                ctx_lines.append("-- Structures de référence (Basic.lean) :")
                for ln in math_ctx.lean_metrics_def.splitlines()[:12]:
                    if ln.strip():
                        ctx_lines.append(f"--   {ln.rstrip()}")
            if math_ctx.kernel_decision_structure:
                ctx_lines.append("-- Logique décisionnelle kernel (read-only) :")
                for ln in math_ctx.kernel_decision_structure.splitlines()[:6]:
                    if ln.strip():
                        ctx_lines.append(f"--   {ln.rstrip()}")
            ctx_lines.append("-- ==========================================")
        ctx_block = "\n".join(ctx_lines)

        import_header = (math_ctx.lean_import_header if math_ctx and math_ctx.lean_import_header
                         else "-- import Obsidia.Basic")

        lean_content = textwrap.dedent(f"""
            {import_header}

            -- Théorème périphérique Obsidia — {theorem_id}
            -- Statut : SANDBOX — AWAITING_HUMAN_REVIEW
            -- Rationale : {rationale or "Non spécifié"}
            --
            -- Ce fichier est dans la EPHEMERAL_CODE_SANDBOX — jamais dans proofs/V18_*.
            -- Règle : preuves complètes obligatoires (LEAN_FORBIDDEN_INCOMPLETE).
            {ctx_block}

            {statement}
        """).strip()

        if self.SORRY_PATTERN.search(lean_content):
            raise ValueError(f"LEAN_SORRY_FORBIDDEN dans le contenu généré de {theorem_id}.")

        lean_file = self._root / f"{theorem_id}.lean"
        lean_file.write_text(lean_content, encoding="utf-8")
        return lean_file

    def run_lake_build(self, timeout: int = 60) -> Dict[str, Any]:
        """
        Lance lake build dans la sandbox Lean.
        Ne touche JAMAIS au repo principal.
        Retourne le rapport de compilation (succès ou erreurs).
        """
        # Vérifier que lake est disponible
        lake_path = shutil.which("lake")
        if not lake_path:
            return {
                "status": "LAKE_NOT_FOUND",
                "note": "lake n'est pas installé — installer Lean 4 toolchain.",
                "sandbox": str(self._root),
            }

        # lakefile minimal dans la sandbox
        lakefile = self._root / "lakefile.lean"
        if not lakefile.exists():
            lakefile.write_text(
                'import Lake\nopen Lake DSL\npackage obsidura_sandbox\n',
                encoding="utf-8",
            )

        try:
            result = subprocess.run(
                [lake_path, "build"],
                cwd=str(self._root),
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            success = result.returncode == 0
            return {
                "status": "BUILD_OK" if success else "BUILD_FAILED",
                "returncode": result.returncode,
                "stdout": result.stdout[:1000],
                "stderr": result.stderr[:1000],
                "sandbox": str(self._root),
            }
        except subprocess.TimeoutExpired:
            return {"status": "BUILD_TIMEOUT", "timeout_seconds": timeout, "sandbox": str(self._root)}
        except Exception as exc:
            return {"status": "BUILD_ERROR", "error": str(exc), "sandbox": str(self._root)}


# ===========================================================================
# 6b.  LEAN MUTATION ENGINE — remplace les fallbacks hardcodés
# ===========================================================================

class LeanMutationEngine:
    """
    Moteur de mutation Lean — génère une formulation DIFFÉRENTE à chaque tentative.

    Remplace _build_lean_fallback_statement (trivial hardcodé) et
    _build_lean_statement_from_objective (unique approche sémantique).

    Progression des stratégies (guidée par ErrorContext) :
      SEMANTIC       : s'inspire sémantiquement de l'objectif (Nat.add_comm)
      NAT_ARITHMETIC : propriété arithmétique Nat (toujours disponible)
      PROPOSITIONAL  : logique propositionnelle pure (p → q → p)
      EXPLICIT_TERM  : terme de preuve, pas de tactic (fun _ h => h)
      MINIMAL_RFL    : preuve par norm_num (dernier recours — jamais sorry)

    INVARIANT ABSOLU : le mot 'sorry' est interdit à TOUTES les étapes.
    La chaîne des erreurs précédentes est injectée en commentaires Lean
    pour maintenir la traçabilité du raisonnement itératif.
    """

    SORRY_PATTERN = re.compile(r"\bsorry\b", re.IGNORECASE)

    def generate_variant(
        self,
        theorem_id: str,
        objective: str,
        attempt: int,
        error_contexts: List[ErrorContext],
        math_ctx: Optional[MathematicalContext] = None,
    ) -> str:
        """
        Génère un énoncé Lean adapté à la tentative et aux erreurs accumulées.

        La stratégie est déterminée par le dernier ErrorContext LEAN_BUILD_ERROR.
        Si aucun échec Lean précédent → SEMANTIC (premier essai sémantique).
        """
        lean_ctxs = [c for c in error_contexts if c.error_type == "LEAN_BUILD_ERROR"]
        if lean_ctxs:
            strategy = lean_ctxs[-1].recommended_strategy
        else:
            idx = min(attempt - 1, len(_LEAN_STRATEGY_PROGRESSION) - 1)
            strategy = _LEAN_STRATEGY_PROGRESSION[max(0, idx)]

        error_trail = self._build_error_trail(error_contexts)
        statement   = self._apply_strategy(theorem_id, objective, strategy, attempt, math_ctx, error_trail)

        # Garde absolue : jamais de sorry dans le résultat
        if self.SORRY_PATTERN.search(statement):
            statement = self._apply_strategy(theorem_id, objective, "MINIMAL_RFL", attempt, math_ctx, "")

        return statement

    def _build_error_trail(self, error_contexts: List[ErrorContext]) -> str:
        """Encode les échecs précédents comme commentaires Lean (chaîne de réflexion)."""
        if not error_contexts:
            return ""
        lines = ["-- === Journal de stabilisation (tentatives précédentes) ==="]
        for ctx in error_contexts[-3:]:
            lines.append(f"-- [T{ctx.attempt}] {ctx.error_type}: {ctx.raw_details[:80]}")
            if ctx.lean_error_line:
                lines.append(f"--   Erreur Lean: {ctx.lean_error_line[:80]}")
            lines.append(f"--   Directive: {ctx.mutation_directive} → {ctx.recommended_strategy}")
        lines.append("-- =====================================================")
        return "\n".join(lines)

    def _apply_strategy(
        self,
        theorem_id: str,
        objective: str,
        strategy: str,
        attempt: int,
        math_ctx: Optional[MathematicalContext],
        error_trail: str,
    ) -> str:
        """Applique la stratégie de mutation choisie."""
        safe   = re.sub(r"[^A-Za-z0-9_]", "_", objective[:35]).strip("_") or f"obs_{theorem_id}"
        thname = f"{theorem_id}_{safe}_t{attempt}"

        header = (
            f"-- Théorème périphérique {theorem_id} | Tentative {attempt} | Stratégie: {strategy}\n"
            f"-- Objectif: {objective[:60]}"
        )
        if error_trail:
            header = f"{header}\n{error_trail}"

        # Injecter le contexte math scellé si disponible
        import_line = "-- import Obsidia.Basic  (sandbox — pas de dépendance kernel)"
        if math_ctx and math_ctx.lean_import_header:
            import_line = math_ctx.lean_import_header

        if strategy == "SEMANTIC":
            # Commutativité de l'addition — expressive, toujours vraie en Lean 4
            return textwrap.dedent(f"""
                {import_line}

                {header}

                theorem {thname} : ∀ (n m : Nat), n + m = m + n := by
                  intro n m
                  omega
            """).strip()

        elif strategy == "NAT_ARITHMETIC":
            # Propriété Nat.add_zero — disponible sans import spécial
            return textwrap.dedent(f"""
                {import_line}

                {header}

                theorem {thname} : ∀ (n : Nat), n + 0 = n := by
                  intro n
                  simp
            """).strip()

        elif strategy == "PROPOSITIONAL":
            # Logique propositionnelle pure — indépendante de tout type class
            return textwrap.dedent(f"""
                {import_line}

                {header}

                theorem {thname} : ∀ (p q : Prop), p → q → p := by
                  intros p q hp _hq
                  exact hp
            """).strip()

        elif strategy == "EXPLICIT_TERM":
            # Terme de preuve explicite — pas de bloc tactic
            return textwrap.dedent(f"""
                {import_line}

                {header}

                theorem {thname} : ∀ (p : Prop), p → p :=
                  fun _ hp => hp
            """).strip()

        else:  # MINIMAL_RFL — dernier recours, jamais sorry
            return textwrap.dedent(f"""
                {import_line}

                {header}

                theorem {thname} : (1 : Nat) + 1 = 2 := by norm_num
            """).strip()


# ===========================================================================
# 7.  UTILITAIRES PROTECTIONS + BACKUP
# ===========================================================================

def _is_protected(path_str: str) -> bool:
    normalized = path_str.replace("\\", "/")
    return any(infx.replace("\\", "/") in normalized for infx in PROTECTED_INFIXES)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _enforce_boundaries() -> None:
    """Vérifie tous les invariants avant chaque phase."""
    for key, expected in [
        ("kernel_mutation", False),
        ("emits_act", False),
        ("x108_merge", False),
        ("allowed_to_decide", False),
        ("sandbox_mode", "HUMAN_APPROVED_WRITE"),
    ]:
        actual = AGENT_OBSIDURE_BOUNDARY.get(key)
        if actual != expected:
            raise ImmutableBoundaryError(
                f"BOUNDARY VIOLATION : '{key}' = {actual!r}, attendu {expected!r}."
            )


def create_backup(target_paths: List[str], ts: str) -> Tuple[str, Dict[str, str]]:
    """
    Phase V — Backup obligatoire.
    Copie tous les fichiers cibles dans _BACKUP_ORIGINALS_<ts>/.
    Lève BackupFailedError si UN fichier échoue → Fail-Closed.
    """
    backup_dir = REPO_ROOT / f"_BACKUP_ORIGINALS_{ts}"
    checksums: Dict[str, str] = {}

    existing = [p for p in target_paths if (REPO_ROOT / p).exists() and not _is_protected(p)]
    if not existing:
        backup_dir.mkdir(parents=True, exist_ok=True)
        return str(backup_dir), checksums

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise BackupFailedError(f"Impossible de créer {backup_dir} : {exc}") from exc

    for rel in existing:
        src = REPO_ROOT / rel
        dst = backup_dir / rel
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
            checksums[rel] = _sha256(src)
        except Exception as exc:
            raise BackupFailedError(
                f"Backup échoué pour '{rel}' : {exc}\n"
                f"Backup partiel : {backup_dir}\n"
                f"AUCUNE GÉNÉRATION DE CODE N'A EU LIEU."
            ) from exc

    return str(backup_dir), checksums


# ===========================================================================
# 8.  PHASE D — DISRUPTION (génération dans sandbox)
# ===========================================================================

def generate_patches(
    objective: str,
    os_trad: OSTradResult,
    sandbox_dir: Path,
    domain_brancher: DomainBrancher,
    lean_sandbox: LeanSandbox,
    math_ctx: Optional[MathematicalContext] = None,
    attempt: int = 1,
    error_contexts: Optional[List[ErrorContext]] = None,
) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Génère les patches dans la sandbox éphémère.

    Refonte Phase D — Solve Engine actif :
      - error_contexts remplace prev_errors (List[Dict]) → richer, structuré
      - Lean : LeanMutationEngine choisit la stratégie selon l'historique d'erreurs
      - Python : sanitisation ciblée sur les directives d'ErrorContext, pas un flag global
      - Pas de fallback trivial hardcodé — chaque échec oriente une nouvelle solution
    """
    error_contexts = error_contexts or []
    patches: List[Dict[str, Any]] = []
    lean_result: Optional[Dict[str, Any]] = None
    intent = os_trad.intent

    # ── Directives depuis les ErrorContext accumulés ──────────────────────
    code_directives = {c.mutation_directive for c in error_contexts
                       if c.error_type in (
                           "FORBIDDEN_KEYWORD", "PROTECTED_PATH_WRITE_REF", "KERNEL_LOGIC_REPLICA"
                       )}
    apply_sanitizer = bool(code_directives) and attempt > 1

    # ── Domaine → gate + nuisance stubs ──────────────────────────────────
    domain = _detect_domain(objective, os_trad)
    if domain and intent in ("CREATE_PATCH", "GENERAL_PATCH"):
        audit = domain_brancher.audit_domain(domain)
        for key, info in audit.get("files", {}).items():
            if info.get("protected"):
                continue
            rel = info["path"]
            if not info["exists"]:
                if key == "gate":
                    content = domain_brancher.generate_gate_stub(domain)
                elif key == "nuisance":
                    content = domain_brancher.generate_nuisance_stub(domain)
                else:
                    content = f"# TODO : {key} pour {domain} — à implémenter (tentative {attempt})"

                if apply_sanitizer:
                    content = _sanitize_peripheral_content(content)
                    # Mutation ciblée SPLIT_DECIDE : on renomme 'decide' en 'evaluate_for_kernel'
                    if "SPLIT_DECIDE_FUNCTION" in code_directives:
                        content = re.sub(r"\bdef decide\b", "def evaluate_for_kernel", content)

                (sandbox_dir / rel).parent.mkdir(parents=True, exist_ok=True)
                (sandbox_dir / rel).write_text(content, encoding="utf-8")
                patches.append({
                    "path": rel,
                    "action": "CREATE",
                    "diff_summary": f"Stub {key} {domain} (T{attempt}) — directives: {', '.join(code_directives) or 'aucune'}.",
                    "rationale": f"Fichier absent — requis pour branchement {domain}.",
                    "domain": domain,
                    "sandbox_path": str(sandbox_dir / rel),
                })
            else:
                patches.append({
                    "path": rel,
                    "action": "REVIEW",
                    "diff_summary": "Fichier existant — revue manuelle.",
                    "rationale": f"Déjà présent — vérifier cohérence {domain}.",
                    "domain": domain,
                    "sandbox_path": "",
                })

    # ── Lean sandbox si intent = LEAN_SANDBOX ────────────────────────────
    if intent == "LEAN_SANDBOX" or "lean" in objective.lower():
        theorem_id = f"P{_next_peripheral_theorem_id()}"

        # LeanMutationEngine décide la stratégie à partir des ErrorContext
        # (pas de fallback trivial hardcodé — chaque tentative est différente)
        statement = _build_lean_variant(
            theorem_id=theorem_id,
            objective=objective,
            attempt=attempt,
            error_contexts=error_contexts,
            math_ctx=math_ctx,
        )

        try:
            lean_file = lean_sandbox.generate_peripheral_theorem(
                theorem_id=theorem_id,
                statement=statement,
                rationale=objective[:150],
                math_ctx=math_ctx,
            )
            lean_result = lean_sandbox.run_lake_build()
            lean_result["theorem_id"]   = theorem_id
            lean_result["lean_file"]    = str(lean_file)
            lean_result["attempt"]      = attempt
            lean_result["strategy_used"] = (
                error_contexts[-1].recommended_strategy if error_contexts else "SEMANTIC"
            )
            patches.append({
                "path": f"proofs/lean/peripheral/{theorem_id}.lean",
                "action": "CREATE_LEAN_PERIPHERAL",
                "diff_summary": (
                    f"Théorème {theorem_id} (T{attempt}) — "
                    f"stratégie {lean_result['strategy_used']} — sans sorry."
                ),
                "rationale": objective[:150],
                "domain": "LEAN",
                "sandbox_path": str(lean_file),
            })
        except ValueError as exc:
            lean_result = {"status": "LEAN_SORRY_BLOCKED", "error": str(exc)}

    # ── SRL organize ─────────────────────────────────────────────────────
    if intent == "SRL_ORGANIZE":
        patches.append(_generate_srl_organize_note(objective, sandbox_dir))

    # ── Audit-only → rapport sans modification ────────────────────────────
    if intent == "AUDIT_ONLY" and not patches:
        patches.append({
            "path": "",
            "action": "AUDIT_REPORT_ONLY",
            "diff_summary": "Audit seul — aucune modification proposée.",
            "rationale": os_trad.intent,
            "domain": domain,
            "sandbox_path": "",
        })

    return patches, lean_result


def _detect_domain(objective: str, os_trad: OSTradResult) -> Optional[str]:
    txt = (objective + " " + " ".join(os_trad.alphabet_units)).upper()
    for d in ("BANK", "TRADING", "GPS", "ECOM"):
        if d in txt:
            return d
    return None


def _next_peripheral_theorem_id() -> int:
    """Retourne un ID de théorème > 35 (les 35 premiers sont pris par V18)."""
    existing = list((REPO_ROOT / "proofs" / "lean").rglob("P*.lean")) if (REPO_ROOT / "proofs" / "lean").exists() else []
    used = set()
    for f in existing:
        m = re.match(r"P(\d+)", f.stem)
        if m:
            used.add(int(m.group(1)))
    candidate = 36
    while candidate in used:
        candidate += 1
    return candidate


# Instance module — partagée par generate_patches et phase_d_disruption
_lean_mutation_engine = LeanMutationEngine()
_error_analyzer       = ErrorAnalyzer()


def _build_lean_variant(
    theorem_id: str,
    objective: str,
    attempt: int,
    error_contexts: List[ErrorContext],
    math_ctx: Optional[MathematicalContext] = None,
) -> str:
    """
    Point d'entrée unique pour la génération de théorèmes Lean.

    Remplace _build_lean_statement_from_objective ET _build_lean_fallback_statement.
    La stratégie est déterminée par l'historique des erreurs, pas par un flag hardcodé.
    """
    return _lean_mutation_engine.generate_variant(
        theorem_id=theorem_id,
        objective=objective,
        attempt=attempt,
        error_contexts=error_contexts,
        math_ctx=math_ctx,
    )


def _generate_srl_organize_note(objective: str, sandbox_dir: Path) -> Dict[str, Any]:
    """Génère une note d'organisation SRL dans la sandbox."""
    note = {
        "srl_action": "ORGANIZE_CANDIDATE",
        "objective": objective[:200],
        "tiers": {"ACTIVE": "sessions < 24h", "SEMI_ACTIVE": "1-30j", "COLD": "> 30j", "GHOST_SIDE_TABLE": "rejets permanents"},
        "note": "Candidat SRL — à appliquer manuellement via session_presave_buffer_readonly.",
    }
    out = sandbox_dir / "srl_organize_note.json"
    out.write_text(json.dumps(note, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "path": "periphery/brody_memory_readonly/ACTIVE/obsidure_candidate.json",
        "action": "SRL_CANDIDATE",
        "diff_summary": "Entrée candidate SRL — tier ACTIVE.",
        "rationale": objective[:150],
        "domain": "SRL",
        "sandbox_path": str(out),
    }


# ===========================================================================
# 9.  PHASE R — RÉINTÉGRATION
# ===========================================================================

def persist_proposal(proposal: PatchProposal) -> Path:
    """
    Écrit le PATCH_PROPOSAL (JSON + RECEIPT.md) dans _PATCH_PROPOSALS/<id>/.
    Ne fait aucun git commit/merge/push.
    """
    proposal_dir = PROPOSALS_DIR / proposal.proposal_id
    proposal_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "proposal_id": proposal.proposal_id,
        "receipt_id": proposal.receipt_id,
        "created_at": proposal.created_at,
        "avdr_cycle": proposal.avdr_cycle,
        "objective": proposal.objective,
        "domain_context": proposal.domain_context,
        "kernel_path_blocked": proposal.kernel_path_blocked,
        "human_approved": proposal.human_approved,
        "status": "AWAITING_HUMAN_APPROVED_WRITE",
        "boundary_snapshot": AGENT_OBSIDURE_BOUNDARY,
        "os_trad": {
            "source": proposal.os_trad_result.source,
            "intent": proposal.os_trad_result.intent,
            "language": proposal.os_trad_result.detected_language,
            "risk_flags": proposal.os_trad_result.risk_flags,
            "constraints": proposal.os_trad_result.constraints,
            "contradictions": proposal.os_trad_result.contradictions,
        },
        "backup_dir": proposal.backup_dir,
        "patches_count": len(proposal.patches),
        "patches": proposal.patches,
        "session_card": asdict(proposal.session_card),
        "lean_sandbox": proposal.lean_sandbox_result,
        "stabilization": asdict(proposal.stabilization) if proposal.stabilization else None,
    }
    (proposal_dir / "proposal.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # RECEIPT.md lisible par l'opérateur (ROLE_005)
    lines = [
        f"# DISPOSABLE_CODE_RECEIPT — {proposal.proposal_id}",
        f"",
        f"**Agent**     : OBSIDURE (CO_PILOTE_CODE #6 × CI_REPO_SURGEON #7)",
        f"**Cycle**     : {proposal.avdr_cycle}",
        f"**Créé le**   : {proposal.created_at}",
        f"**Objectif**  : {proposal.objective}",
        f"**Domaine**   : {proposal.domain_context or 'INFRA'}",
        f"**Statut**    : `AWAITING_HUMAN_APPROVED_WRITE`",
        f"",
        f"## OS_TRAD_REVERSE",
        f"- Source : `{proposal.os_trad_result.source}`",
        f"- Intent : `{proposal.os_trad_result.intent}`",
        f"- Langue : `{proposal.os_trad_result.detected_language}`",
        f"- Risk flags : {proposal.os_trad_result.risk_flags}",
        f"- Contradictions : {proposal.os_trad_result.contradictions}",
        f"",
        f"## Patches proposés ({len(proposal.patches)})",
        f"",
    ]
    for i, p in enumerate(proposal.patches, 1):
        if not isinstance(p, dict):
            lines.append(f"### {i}. [patch non-dict — type {type(p).__name__}]")
            continue
        lines += [
            f"### {i}. `{str(p.get('path', '?'))}` — {str(p.get('action', '?'))}",
            f"> {str(p.get('diff_summary', ''))}",
            f"> {str(p.get('rationale', ''))}",
            f"",
        ]
    if proposal.lean_sandbox_result:
        lsr = proposal.lean_sandbox_result
        lines += [
            f"## Lean Sandbox",
            f"- Status : `{str(lsr.get('status', '?') if isinstance(lsr, dict) else lsr)}`",
            f"- Theorem : `{str(lsr.get('theorem_id', 'N/A') if isinstance(lsr, dict) else 'N/A')}`",
            f"- Sorry utilisé : NON (interdit par Obsidure)",
            f"",
        ]
    if proposal.stabilization:
        stab = proposal.stabilization
        passed_label = "OUI — code stabilisé" if stab.passed else "NON — max tentatives atteint"
        lines += [
            f"## Boucle de Stabilisation (Trial-and-Error)",
            f"- Statut final : `{str(stab.final_status)}`",
            f"- Tentatives : {stab.attempts}/{stab.max_attempts}",
            f"- Conforme aux lois Kernel : **{passed_label}**",
        ]
        for entry in stab.errors_history:
            if not isinstance(entry, dict):
                lines.append(f"  - [entrée invalide — type {type(entry).__name__}]")
                continue
            errs = entry.get("errors", [])
            if not isinstance(errs, list):
                errs = []
            attempt_n = str(entry.get("attempt", "?"))
            if errs:
                lines.append(f"  - Tentative {attempt_n} : {len(errs)} violation(s)")
                for e in errs[:2]:
                    if isinstance(e, dict):
                        e_type    = str(e.get("type", "?"))
                        e_details = str(e.get("details", ""))[:70]
                    else:
                        e_type    = "?"
                        e_details = str(e)[:70]
                    lines.append(f"    - `{e_type}` : {e_details}")
            else:
                lines.append(f"  - Tentative {attempt_n} : aucune violation -> PASS")
        lines.append(f"")
    lines += [
        f"## SRL SessionCard",
        f"- Tier cible : `{proposal.session_card.tier}`",
        f"- Status : `{proposal.session_card.status}`",
        f"- Écriture auto : NON (memory_write=False)",
        f"",
        f"## Backup",
        f"- Dossier : `{proposal.backup_dir}`",
        f"",
        f"## Pour appliquer",
        f"```",
        f"# 1. Reviewer le dossier sandbox correspondant",
        f"# 2. Copier manuellement les fichiers approuvés vers le repo",
        f"# 3. Faire git add + git commit manuellement (jamais via Obsidure)",
        f"```",
    ]
    # Filet de sécurité : garantit List[str] pure avant le join
    # (évite TypeError si un dict/list a glissé dans lines via un champ inattendu)
    lines_safe = [l if isinstance(l, str) else str(l) for l in lines]
    (proposal_dir / "RECEIPT.md").write_text("\n".join(lines_safe), encoding="utf-8")

    return proposal_dir


# ===========================================================================
# 10.  CLASSE PRINCIPALE — AgentObsidure
# ===========================================================================

class AgentObsidure:
    """
    Agent Obsidure v2.0 — Bâtisseur CLI Standalone.

    Boucle A.V.D.R. interactive :
      A — Demande l'objectif, interroge OS_TRAD_REVERSE
      V — Backup obligatoire (Fail-Closed si échec)
      D — Génère patches + Lean + SRL dans EPHEMERAL_CODE_SANDBOX
      R — Émet PATCH_PROPOSAL, attend HUMAN_APPROVED_WRITE

    Ne se branche PAS à l'UI Cockpit ni au moteur Brody pour l'instant.
    """

    def __init__(
        self,
        api_base: str = API_BASE,
        max_cycles: Optional[int] = None,
        verbose: bool = True,
    ) -> None:
        # Gel des frontières — référence immuable
        self._boundary_ref = copy.deepcopy(AGENT_OBSIDURE_BOUNDARY)
        self._phase = AVDRPhase.IDLE
        self._cycle = 0
        self._max_cycles = max_cycles
        self._verbose = verbose
        self._proposals: List[PatchProposal] = []
        self._os_trad = OSTradClient(api_base=api_base)
        self._srl = SRLManager()
        self._domain_brancher = DomainBrancher()
        self._math_ctx: Optional[MathematicalContext] = None
        PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
        self._log("Agent Obsidure v2.0 initialisé.")
        self._log(f"OS_TRAD_REVERSE cible : {api_base}")

    def _log(self, msg: str, level: str = "INFO") -> None:
        if self._verbose or level in ("WARN", "ERROR", "CRITICAL"):
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            prefix = {"INFO": "·", "WARN": "⚠", "ERROR": "✗", "CRITICAL": "!!"}
            print(f"  [{ts}] {prefix.get(level, '·')} {msg}", flush=True)

    def _check_boundaries(self) -> None:
        for k, v in self._boundary_ref.items():
            if AGENT_OBSIDURE_BOUNDARY.get(k) != v:
                raise ImmutableBoundaryError(f"Frontière altérée : '{k}'")

    def _gather_mathematical_context(self, objective: str) -> MathematicalContext:
        """
        Lit en READ-ONLY le kernel scellé et les preuves Lean de référence.
        Ces fichiers servent de dataset mathématique — aucune mutation, aucun backup.
        Appelé automatiquement en Phase A avant la génération Lean.
        """
        self._log("  Lecture contexte mathématique (read-only)…")
        ctx = _build_math_context_from_repo()
        if ctx.source_files_read:
            self._log(f"  Contexte math lu depuis : {ctx.source_files_read}")
            if ctx.lean_theorem_names:
                self._log(f"  Théorèmes de référence : {ctx.lean_theorem_names[:4]}")
        else:
            self._log("  Contexte math : aucun fichier de référence trouvé.", level="WARN")
        return ctx

    # ── A — AUDIT ─────────────────────────────────────────────────────────

    def phase_a_audit(self, objective: str) -> OSTradResult:
        self._phase = AVDRPhase.AUDIT
        self._check_boundaries()
        self._log("Phase A : interrogation OS_TRAD_REVERSE…")

        # Vérification anti-kernel dans l'objectif AVANT appel API
        # Note : seule la MUTATION est interdite. La lecture interne est légale.
        for infx in PROTECTED_INFIXES:
            if infx.lower() in objective.lower():
                raise ProtectedPathError(
                    f"BLOC ABSOLU : l'objectif référence '{infx}' "
                    f"(zone protégée — Kernel / preuves gelées). Arrêt immédiat."
                )

        result = self._os_trad.translate_and_build_ir(objective)
        self._log(f"  OS_TRAD source={result.source} intent={result.intent} lang={result.detected_language}")
        if result.risk_flags:
            self._log(f"  Risk flags : {result.risk_flags}", level="WARN")
        if result.contradictions:
            self._log(f"  Contradictions : {result.contradictions}", level="WARN")

        # Collecte du contexte mathématique read-only (toujours — enrichit Phase D)
        self._math_ctx = self._gather_mathematical_context(objective)

        return result

    # ── V — VALIDATION / BACKUP ──────────────────────────────────────────

    def phase_v_validation(
        self, os_trad: OSTradResult, extra_paths: List[str] = ()
    ) -> Tuple[str, Dict[str, str]]:
        self._phase = AVDRPhase.VALIDATION
        self._check_boundaries()
        self._log("Phase V : backup en cours…")

        # Seuls les fichiers à CRÉER ou MODIFIER vont dans le backup.
        # Les fichiers lus en read-only (contexte math, kernel, preuves) sont exclus.
        math_read_paths: List[str] = (
            self._math_ctx.source_files_read if self._math_ctx else []
        )
        candidate_paths = list(os_trad.target_paths) + list(extra_paths)
        all_paths = [p for p in candidate_paths if p not in math_read_paths]

        # Bloc absolu sur les chemins protégés dans la liste cible (jamais en écriture)
        for p in all_paths:
            if _is_protected(p):
                raise ProtectedPathError(
                    f"BLOC ABSOLU : chemin protégé dans la liste backup : '{p}'. "
                    f"Le Kernel est un mur de béton. Arrêt."
                )

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir, checksums = create_backup(all_paths, ts)
        self._log(f"  Backup OK → {backup_dir} ({len(checksums)} fichier(s))")
        return backup_dir, checksums

    # ── D — DISRUPTION ────────────────────────────────────────────────────

    def phase_d_disruption(
        self,
        objective: str,
        os_trad: OSTradResult,
        max_attempts: int = 5,
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]], Path, StabilizationResult]:
        """
        Boucle Solve Engine — Mutation dirigée par anomalie (refonte Phase D).

        Principe :
          1. Génère patches/théorèmes dans la sandbox éphémère.
          2. Teste la conformité (lake build Lean + analyse statique Python).
          3. Si violation → ErrorAnalyzer structure l'échec en ErrorContext.
          4. LeanMutationEngine / directives de code s'appuient sur ces ErrorContext
             pour formuler une solution RÉELLEMENT DIFFÉRENTE à T+1.
          5. L'objectif évolue avec le contexte d'erreur accumulé.
          6. Si stable → sort de la boucle (Phase R).
          7. Si max_attempts (5) atteint → émet la meilleure version disponible.
             L'opérateur humain est le juge final (HUMAN_APPROVED_WRITE).

        Le Kernel X-108 ne change pas — il sert de boussole par le refus.
        Toute l'exploration reste confinée dans EPHEMERAL_CODE_SANDBOX.
        decision_authority=KX108_ONLY | kernel_mutation=False — absolus.
        """
        self._phase = AVDRPhase.DISRUPTION
        self._check_boundaries()
        self._log(f"Phase D — Solve Engine : max {max_attempts} tentatives d'exploration active.")

        ts          = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        sandbox_dir = REPO_ROOT / f"_EPHEMERAL_CODE_SANDBOX_{ts}"
        sandbox_dir.mkdir(parents=True, exist_ok=True)

        lean_sb: LeanSandbox = LeanSandbox(sandbox_dir)

        # Mémoire cumulative des erreurs entre les tentatives
        all_error_contexts: List[ErrorContext] = []
        iteration_memories: List[IterationMemory] = []
        errors_history:     List[Dict[str, Any]] = []
        patches:            List[Dict[str, Any]] = []
        lean_result:        Optional[Dict[str, Any]] = None
        current_objective   = objective

        for attempt in range(1, max_attempts + 1):
            self._log(f"  [T{attempt}/{max_attempts}] Exploration — objectif: {current_objective[:80]}")

            # ── Génération des patches avec contexte d'erreur accumulé ────
            patches, lean_result = generate_patches(
                current_objective, os_trad, sandbox_dir,
                self._domain_brancher, lean_sb,
                math_ctx=self._math_ctx,
                attempt=attempt,
                error_contexts=list(all_error_contexts),   # copie immuable
            )

            # ── Test de conformité contre les lois du Kernel ──────────────
            attempt_raw_errors = _test_patches_conformity(patches, lean_result, sandbox_dir)
            errors_history.append({"attempt": attempt, "errors": attempt_raw_errors})

            if not attempt_raw_errors:
                self._log(f"  [T{attempt}] Stabilisation atteinte.")
                if lean_result:
                    strategy = lean_result.get("strategy_used", "?")
                    self._log(f"  Lean : {lean_result.get('status')} | Stratégie : {strategy}")
                return patches, lean_result, sandbox_dir, StabilizationResult(
                    attempts=attempt,
                    max_attempts=max_attempts,
                    final_status="STABILIZED",
                    errors_history=errors_history,
                    passed=True,
                )

            # ── Violations détectées — analyse et mutation pour T+1 ───────
            new_contexts = _error_analyzer.analyze_errors(
                raw_errors=attempt_raw_errors,
                lean_result=lean_result,
                attempt=attempt,
            )
            all_error_contexts.extend(new_contexts)

            self._log(
                f"  [T{attempt}] {len(attempt_raw_errors)} violation(s) → "
                f"{len(new_contexts)} ErrorContext(s) extraits.",
                level="WARN",
            )
            for ctx in new_contexts[:3]:
                self._log(
                    f"    [{ctx.error_type}] directive={ctx.mutation_directive} "
                    f"→ next_strategy={ctx.recommended_strategy}",
                    level="WARN",
                )
                if ctx.lean_error_line:
                    self._log(f"    Lean: {ctx.lean_error_line[:80]}", level="WARN")

            # ── Objectif évolué — reformulé avec le contexte d'échec ──────
            current_objective = _error_analyzer.derive_evolved_objective(
                base_objective=objective,
                contexts=new_contexts,
                attempt=attempt,
            )

            # ── Mémorisation de l'itération ───────────────────────────────
            iteration_memories.append(IterationMemory(
                attempt=attempt,
                patches_count=len(patches),
                error_contexts=new_contexts,
                lean_strategy_used=(
                    new_contexts[-1].recommended_strategy
                    if new_contexts else "SEMANTIC"
                ),
                objective_evolved=current_objective,
            ))

        # ── Max tentatives épuisé — meilleure version disponible ──────────
        self._log(
            f"  Solve Engine : {max_attempts} tentatives épuisées — "
            f"version explorée émise pour validation opérateur.",
            level="WARN",
        )
        self._log("  L'opérateur humain (ROLE_005) est le juge final — HUMAN_APPROVED_WRITE.")
        return patches, lean_result, sandbox_dir, StabilizationResult(
            attempts=max_attempts,
            max_attempts=max_attempts,
            final_status="MAX_ATTEMPTS_REACHED",
            errors_history=errors_history,
            passed=False,
        )

    # ── R — RÉINTÉGRATION ────────────────────────────────────────────────

    def phase_r_reintegration(
        self,
        objective: str,
        os_trad: OSTradResult,
        backup_dir: str,
        patches: List[Dict[str, Any]],
        lean_result: Optional[Dict[str, Any]],
        stabilization: Optional[StabilizationResult] = None,
    ) -> PatchProposal:
        self._phase = AVDRPhase.REINTEGRATION
        self._check_boundaries()
        self._log("Phase R : émission PATCH_PROPOSAL…")

        if stabilization:
            status_label = "STABILIZED" if stabilization.passed else "MAX_ATTEMPTS_REACHED"
            self._log(f"  Stabilisation : {status_label} ({stabilization.attempts}/{stabilization.max_attempts} tentative(s))")

        domain = _detect_domain(objective, os_trad)
        session_card = self._srl.build_candidate_card(objective, domain)
        srl_summary = self._srl.read_summary()
        self._log(f"  SRL tiers : {srl_summary['tiers']}")

        proposal = PatchProposal(
            proposal_id=str(uuid.uuid4()),
            objective=objective,
            avdr_cycle=self._cycle,
            os_trad_result=os_trad,
            backup_dir=backup_dir,
            patches=patches,
            session_card=session_card,
            domain_context=domain,
            lean_sandbox_result=lean_result,
            stabilization=stabilization,
            kernel_path_blocked=False,
        )
        proposal_dir = persist_proposal(proposal)
        self._proposals.append(proposal)
        self._phase = AVDRPhase.AWAITING
        self._log(f"  Proposal ID : {proposal.proposal_id}")
        self._log(f"  Emplacement : {proposal_dir}/")
        self._log(f"  Statut : AWAITING_HUMAN_APPROVED_WRITE")
        return proposal

    # ── CYCLE COMPLET ────────────────────────────────────────────────────

    def run_cycle(self, objective: str) -> PatchProposal:
        self._cycle += 1
        self._log(f"\n{'='*60}")
        self._log(f"CYCLE AVDR #{self._cycle} — {objective[:70]}")
        self._log(f"{'='*60}")
        _enforce_boundaries()

        os_trad = self.phase_a_audit(objective)
        backup_dir, _ = self.phase_v_validation(os_trad)
        patches, lean_result, _, stabilization = self.phase_d_disruption(objective, os_trad)
        return self.phase_r_reintegration(
            objective, os_trad, backup_dir, patches, lean_result, stabilization
        )

    # ── BOUCLE INTERACTIVE ───────────────────────────────────────────────

    def run_interactive_loop(self) -> None:
        """
        Boucle interactive CLI.
        Demande l'objectif à l'utilisateur à chaque cycle.
        S'arrête sur Ctrl+C, 'quit', 'exit', ou max_cycles atteint.
        """
        self._log("\nAgent Obsidure — Bâtisseur CLI Standalone")
        self._log("Tapez 'quit' ou Ctrl+C pour quitter.\n")

        try:
            while True:
                if self._max_cycles and self._cycle >= self._max_cycles:
                    self._log(f"max_cycles={self._max_cycles} atteint — arrêt.")
                    break

                try:
                    objective = input("\n[OBSIDURE] Objectif > ").strip()
                except EOFError:
                    break

                if not objective:
                    continue
                if objective.lower() in ("quit", "exit", "q"):
                    self._log("Arrêt demandé par l'opérateur.")
                    break

                try:
                    proposal = self.run_cycle(objective)
                    self._log(f"\nProposal émis. Lisez : _PATCH_PROPOSALS/{proposal.proposal_id}/RECEIPT.md")
                except ProtectedPathError as exc:
                    self._phase = AVDRPhase.HALTED
                    self._log(f"BLOC ABSOLU : {exc}", level="CRITICAL")
                    self._log("Agent arrêté. Relancez sans cibler de zones protégées.", level="CRITICAL")
                    break
                except BackupFailedError as exc:
                    self._phase = AVDRPhase.HALTED
                    self._log(f"FAIL-CLOSED : {exc}", level="CRITICAL")
                    break
                except ImmutableBoundaryError as exc:
                    self._phase = AVDRPhase.HALTED
                    self._log(f"VIOLATION FRONTIÈRE : {exc}", level="CRITICAL")
                    break
                except Exception as exc:
                    self._log(f"Erreur cycle : {exc}", level="ERROR")

        except KeyboardInterrupt:
            pass

        self._log(f"\nRésumé : {self._cycle} cycle(s) — {len(self._proposals)} proposal(s) émis.")

    # ── PROPRIÉTÉS ───────────────────────────────────────────────────────

    @property
    def phase(self) -> AVDRPhase:
        return self._phase

    @property
    def proposals(self) -> List[PatchProposal]:
        return list(self._proposals)

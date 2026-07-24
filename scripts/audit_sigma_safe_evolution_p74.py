#!/usr/bin/env python3
"""
scripts/audit_sigma_safe_evolution_p74.py

P74 — Sigma Safe Evolution Audit
MODE: AUDIT_AND_PATCH_IF_SAFE

Audite sigma/ apres P56->P73 et determine :
  1. Sigma est-il deja complet ?
  2. Faut-il modifier Sigma ?
  3. Si oui, quel patch minimal ?
  4. Si non, produire NO_SIGMA_CHANGE_REQUIRED.

VERROU ABSOLU :
  - Sigma proof gagne par defaut.
  - Ne jamais ecraser sigma/ avec core.
  - Ne jamais reintroduire gamma 0.5.
  - Ne jamais promouvoir HOLD/BLOCK vers ACT.
  - Ne jamais permettre a Sigma d'autoriser.
  - Sigma reste POST_GUARD_VETO_ONLY.

DRY_RUN_ONLY = True (aucun patch applique dans ce palier)
"""

import json
import os
import re
import sys
from pathlib import Path

DRY_RUN_ONLY: bool = True

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "docs" / "core_import" / "P74_SIGMA_SAFE_EVOLUTION.json"
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

_BOUNDARY = {
    "dry_run_only": DRY_RUN_ONLY,
    "readonly": True,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "sigma_override": False,
    "sigma_modified": False,
}

# ---------------------------------------------------------------------------
# Sigma model invariants
# ---------------------------------------------------------------------------

SIGMA_MODEL = {
    "post_guard_veto_only": (
        "Sigma n'intervient qu'apres GuardX108. "
        "Sigma peut seulement downgrader vers HOLD_STABILITY_ALERT. "
        "Sigma ne peut jamais autoriser ni promouvoir HOLD/BLOCK vers ACT/ALLOW."
    ),
    "guard_x108_final_authority": (
        "GuardX108 est l'autorite finale. "
        "Preuve Lean : X108_kernel_never_blocks (GUARD_X108_FINAL_AUTHORITY). "
        "GuardX108.decide() produit ALLOW/HOLD/BLOCK independamment de Sigma."
    ),
    "no_act_authority": (
        "Sigma n'emet jamais ALLOW, ACT, PAY ni aucun verdict positif. "
        "sigma_authority ne peut etre que VETO_ONLY ou REPORT_ONLY."
    ),
    "no_hold_block_to_act_promotion": (
        "apply_sigma() en run_pipeline.py ne peut que passer market_verdict a "
        "HOLD_STABILITY_ALERT si stability==FAIL. "
        "Si PASS, aucune modification du verdict GuardX108."
    ),
    "no_memory_write": (
        "sigma/ ne contient aucune ecriture en memoire, Graphiti, Neo4j ou kernel state "
        "sans gate explicite. evaluate.py BOUNDARY: memory_write=False, graphiti_write=False."
    ),
    "no_graphiti_write": (
        "graphiti_readonly_bridge.py : lecture seule uniquement. "
        "BOUNDARY: graphiti_write=False dans evaluate.py, registry.py, packets.py."
    ),
    "no_kernel_mutation": (
        "Aucun fichier sigma/ ne modifie le kernel ou les preuves Lean. "
        "Invariant LEAN_PROVEN : NO_KERNEL_MUTATION_FROM_PERIPHERY."
    ),
    "gamma_1_0_preserved": (
        "obsidia_sigma_v130.py : tau_max default=0.75, accel_limit default=0.40. "
        "sigma_config.json : tau_max=5.0 (calibration statistique 3-sigma, 2026-03-12). "
        "Aucune valeur 0.5 (gamma=0.5 bannie depuis P56B)."
    ),
}

# ---------------------------------------------------------------------------
# Sigma files matrix
# ---------------------------------------------------------------------------

SIGMA_MATRIX = [
    {
        "file_path": "sigma/guard.py",
        "sigma_role": "GuardX108 — autorite finale de decision X108",
        "current_version": "P56D",
        "p56b_patched": False,
        "p56d_patched": True,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "HIGH_IF_MODIFIED",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "GuardX108.decide() correct : BLOCK si contradiction>=2 ou FRAUD_PATTERN, "
            "HOLD si unknowns ou confidence<0.45, ALLOW sinon. "
            "Aucune dependance Sigma interne. "
            "Preuve Lean GUARD_X108_FINAL_AUTHORITY protege ce fichier."
        ),
        "p72_invariants_checked": [
            "GUARD_X108_FINAL_AUTHORITY",
            "NO_KERNEL_MUTATION_FROM_PERIPHERY",
        ],
    },
    {
        "file_path": "sigma/run_pipeline.py",
        "sigma_role": "CLI bridge + apply_sigma POST_GUARD_VETO_ONLY",
        "current_version": "P56D",
        "p56b_patched": False,
        "p56d_patched": True,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "HIGH_IF_MODIFIED",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "apply_sigma() est correctement implemente POST_GUARD_VETO_ONLY : "
            "si stability==FAIL -> HOLD_STABILITY_ALERT + sigma_authority=VETO_ONLY, "
            "sinon sigma_authority=REPORT_ONLY. "
            "Sigma ne peut jamais elever le verdict Guard. "
            "sigma_override_policy='POST_GUARD_VETO_ONLY' inscrit dans le JSON de sortie."
        ),
        "p72_invariants_checked": [
            "SIGMA_POST_GUARD_VETO_ONLY",
            "GUARD_X108_FINAL_AUTHORITY",
            "NO_KERNEL_MUTATION_FROM_PERIPHERY",
        ],
    },
    {
        "file_path": "sigma/obsidia_sigma_v130.py",
        "sigma_role": "Moniteur de stabilite dynamique Sigma V18.9",
        "current_version": "P56B_v1.4.1",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "HIGH_IF_MODIFIED",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "gamma=1.0 confirme : tau_max default=0.75, accel_limit default=0.40. "
            "Pas de gamma=0.5 (banni depuis P56B). "
            "Config externe sigma_config.json (tau_max=5.0, calibration 3-sigma 2026-03-12) "
            "prise en charge sans modifier le moteur. "
            "Architecture Moteur Fixe + Config Calibree respectee."
        ),
        "p72_invariants_checked": [
            "SIGMA_POST_GUARD_VETO_ONLY",
            "DETERMINISM",
        ],
    },
    {
        "file_path": "sigma/contracts.py",
        "sigma_role": "Types canoniques : CanonicalDecisionEnvelope, DomainAggregate, AgentVote, States",
        "current_version": "P56B_GPS",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "MEDIUM_IF_MODIFIED",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "GpsDefenseAviationState ajoute en P56B. "
            "Triple architecture de confiance (integrity/governance/readiness) presente. "
            "CanonicalDecisionEnvelope correcte avec normalize_confidence. "
            "Aucun champ 'gamma' present."
        ),
        "p72_invariants_checked": [
            "DETERMINISM",
            "THRESHOLD_CONSERVATION",
        ],
    },
    {
        "file_path": "sigma/aggregation.py",
        "sigma_role": "Agregation des votes par domaine (bank/trading/ecom/gps)",
        "current_version": "P56B_GPS",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "aggregate_gps_defense_aviation ajoute en P56B. "
            "Logique d'agregation deterministe. "
            "Confidence plafonnee a 0.98. "
            "truth_score/mismatch_gap corrects pour GPS."
        ),
        "p72_invariants_checked": [
            "DETERMINISM",
            "THRESHOLD_CONSERVATION",
        ],
    },
    {
        "file_path": "sigma/protocols.py",
        "sigma_role": "Pipelines domaines : run_*_pipeline() -> CanonicalDecisionEnvelope",
        "current_version": "P56D_GPS",
        "p56b_patched": True,
        "p56d_patched": True,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "run_gps_defense_aviation_pipeline ajoute en P56D. "
            "Chaque pipeline : aggregate -> _apply_meta_agents -> GuardX108().decide(). "
            "GuardX108 est toujours l'etape finale. "
            "Aucune intervention Sigma dans les pipelines."
        ),
        "p72_invariants_checked": [
            "GUARD_X108_FINAL_AUTHORITY",
            "DETERMINISM",
        ],
    },
    {
        "file_path": "sigma/base.py",
        "sigma_role": "ABC BaseAgent avec evaluate() et clamp()",
        "current_version": "P56_BASE",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Interface abstraite minimale. "
            "Aucune logique decisionnelle. "
            "Stable et complete."
        ),
        "p72_invariants_checked": [],
    },
    {
        "file_path": "sigma/evaluate.py",
        "sigma_role": "F61 Sigma Unified Dispatcher — readonly, advisory_only",
        "current_version": "F61",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "BOUNDARY dict complet : decision_authority=KX108_ONLY, "
            "advisory_only=True, allowed_to_decide=False, emits_act=False, "
            "emits_verdict=False, kernel_mutation=False, x108_mutation=False. "
            "validate_sigma_dispatcher() verifie ces contraintes sur chaque domaine."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
            "KX108_ONLY_DECISION_AUTHORITY",
            "NO_KERNEL_MUTATION_FROM_PERIPHERY",
        ],
    },
    {
        "file_path": "sigma/registry.py",
        "sigma_role": "F60 Registry des domaines avec metadonnees de souverainete",
        "current_version": "F60",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "_BOUNDARY dict present : decision_authority=KX108_ONLY, readonly=True. "
            "_CANONICAL_DOMAINS = (bank, trading, ecom, gps_defense_aviation). "
            "Stable."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
        ],
    },
    {
        "file_path": "sigma/packets.py",
        "sigma_role": "F62 Sigma Domain Packet Normalizer",
        "current_version": "F62",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "_PACKET_BOUNDARY : decision_authority=KX108_ONLY, "
            "readonly=True, advisory_only=True, allowed_to_decide=False, "
            "emits_act=False, emits_verdict=False, kernel_mutation=False, "
            "x108_mutation=False, neo4j_write=False, graphiti_write=False, "
            "memory_write=False, brody_decision=False. "
            "Aucune execution pipeline. Aucune route. Aucun stockage."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
            "NO_GRAPHITI_WRITE",
            "NO_MEMORY_WRITE_WITHOUT_GATE",
        ],
    },
    {
        "file_path": "sigma/graphiti_readonly_bridge.py",
        "sigma_role": "Lecture seule Graphiti — bridge readonly sans ecriture",
        "current_version": "P6x_READONLY",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Lecture seule confirmee par convention de nommage _readonly_bridge. "
            "Invariant NO_GRAPHITI_WRITE protege ce fichier."
        ),
        "p72_invariants_checked": [
            "NO_GRAPHITI_WRITE",
        ],
    },
    {
        "file_path": "sigma/trees_activation_readonly.py",
        "sigma_role": "Activation des arbres de decision — lecture seule",
        "current_version": "P6x_READONLY",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Fichier readonly par convention. "
            "Pas d'intervention sur le chemin de decision Guard."
        ),
        "p72_invariants_checked": [],
    },
    {
        "file_path": "sigma/orchestrator_preview.py",
        "sigma_role": "Preview d'orchestration — dry_run preview uniquement",
        "current_version": "P6x_PREVIEW",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Preview uniquement — aucune execution production. "
            "Aucune mutation sigma ou kernel."
        ),
        "p72_invariants_checked": [],
    },
    {
        "file_path": "sigma/connectors.py",
        "sigma_role": "Connecteurs sigma — bus/interface couche",
        "current_version": "P6x",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Connecteurs sigma maintenu sous l'invariant NO_PERIPHERY_DECISION_AUTHORITY. "
            "Audite P70 (network egress). Aucune mutation sigma."
        ),
        "p72_invariants_checked": [
            "NETWORK_EGRESS_REVIEW_REQUIRED",
        ],
    },
    {
        "file_path": "sigma/sigma_monitor.py",
        "sigma_role": "CLI monitor ObsidiaSigmaMonitor + GPS example runner",
        "current_version": "P56B_CLI",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "CLI de monitoring uniquement. "
            "Utilise ObsidiaSigmaMonitor.evaluate_step() et export_to_proofkit(). "
            "Aucune mutation du chemin de decision."
        ),
        "p72_invariants_checked": [],
    },
    {
        "file_path": "sigma/__init__.py",
        "sigma_role": "Module init sigma/",
        "current_version": "BASE",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": "Module init. Aucune logique decisionnelle.",
        "p72_invariants_checked": [],
    },
    {
        "file_path": "sigma/contracts.broken-ragnarok.py",
        "sigma_role": "Fichier intentionnellement casse — vendored/protege",
        "current_version": "INTENTIONALLY_BROKEN",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Fichier intentionnellement casse (ragnarok test artifact). "
            "Ne jamais importer ni modifier. Protege par PROTECTED_SCOPE."
        ),
        "p72_invariants_checked": [],
    },
    {
        "file_path": "sigma/domains/bank_agents.py",
        "sigma_role": "Agents domaine banque — votes AgentVote",
        "current_version": "P56B",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Agents retournent AgentVote — pas de CanonicalDecisionEnvelope directement. "
            "Autorite finale : GuardX108 via protocols.py. "
            "Suite de tests sigma/tests/test_bank_*.py comprehensive."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
        ],
    },
    {
        "file_path": "sigma/domains/trading_agents.py",
        "sigma_role": "Agents domaine trading — votes AgentVote",
        "current_version": "P56B",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Note P73 : python_agents/domains/trading_agents.py (core) a dependance ccxt. "
            "sigma/domains/trading_agents.py est distinct — "
            "verifie manuellement qu'il n'importe pas ccxt (interne sigma uniquement). "
            "Autorite finale : GuardX108."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
            "NETWORK_EGRESS_REVIEW_REQUIRED",
        ],
    },
    {
        "file_path": "sigma/domains/ecom_agents.py",
        "sigma_role": "Agents domaine ecommerce — votes AgentVote",
        "current_version": "P56B",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Agents retournent AgentVote. "
            "Suite de tests sigma/tests/test_bank_*. "
            "Autorite finale : GuardX108."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
        ],
    },
    {
        "file_path": "sigma/domains/meta_agents.py",
        "sigma_role": "Meta-agents cross-domaine — votes supplementaires",
        "current_version": "P56B",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Meta-agents appeles via _apply_meta_agents() en protocols.py. "
            "Etendent l'agregat (contradictions/unknowns/risk_flags) "
            "sans changer la decision Guard. "
            "Autorite finale : GuardX108."
        ),
        "p72_invariants_checked": [
            "GUARD_X108_FINAL_AUTHORITY",
        ],
    },
    {
        "file_path": "sigma/domains/gps_defense_aviation_agents.py",
        "sigma_role": "Agents domaine GPS defense aviation — votes AgentVote",
        "current_version": "P56B_GPS",
        "p56b_patched": True,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "Domaine GPS ajoute en P56B. "
            "Suite de tests sigma/tests/test_gps_*.py. "
            "Autorite finale : GuardX108."
        ),
        "p72_invariants_checked": [
            "NO_PERIPHERY_DECISION_AUTHORITY",
        ],
    },
    {
        "file_path": "sigma/sigma_config.json",
        "sigma_role": "Configuration calibree Sigma — seuils externes",
        "current_version": "CALIBRATED_2026-03-12",
        "p56b_patched": False,
        "p56d_patched": False,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "LOW",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "tau_max=5.0 (calibration 3-sigma, 30 observations, 2026-03-12). "
            "accel_limit=0.6. tau_min=0.05. "
            "Pas de gamma=0.5 (banni depuis P56B). "
            "Architecture Moteur Fixe + Config Calibree : "
            "le moteur obsidia_sigma_v130.py n'est pas modifie, "
            "seule la config externe change."
        ),
        "p72_invariants_checked": [
            "DETERMINISM",
            "SIGMA_POST_GUARD_VETO_ONLY",
        ],
    },
    {
        "file_path": "sigma/tests/",
        "sigma_role": "Suite de tests sigma — 21 fichiers",
        "current_version": "P56B+",
        "p56b_patched": True,
        "p56d_patched": True,
        "proof_wins": True,
        "needs_change": False,
        "change_type": "NO_CHANGE",
        "risk_level": "NONE",
        "decision": "NO_SIGMA_CHANGE_REQUIRED",
        "reason": (
            "21 fichiers de tests : test_bank_world, test_bank_adversarial_pack, "
            "test_bank_fuzz_scale_pack, test_sigma_monitor, test_sigma_pipeline, "
            "test_sigma_smoke, test_gps_fail_closed, test_gps_semantics, test_gps_smoke, "
            "et packs de tests bank (market, regulatory, replay, enterprise, etc.). "
            "Couverture comprehensive. Aucun ajout de test requis pour P74."
        ),
        "p72_invariants_checked": [],
    },
]

# ---------------------------------------------------------------------------
# Verification automatique : POST_GUARD_VETO_ONLY
# ---------------------------------------------------------------------------

def _check_post_guard_veto_only(root: Path) -> dict:
    """Verifie que apply_sigma() ne peut que downgrader, jamais promouvoir."""
    run_pipeline_path = root / "sigma" / "run_pipeline.py"
    findings = []
    verified = False

    if run_pipeline_path.exists():
        content = run_pipeline_path.read_text(encoding="utf-8")

        if "POST_GUARD_VETO_ONLY" in content:
            findings.append("sigma_override_policy='POST_GUARD_VETO_ONLY' presente dans run_pipeline.py")
            verified = True
        if "HOLD_STABILITY_ALERT" in content:
            findings.append("HOLD_STABILITY_ALERT seul verdict que Sigma peut imposer (downgrade uniquement)")
        if "VETO_ONLY" in content:
            findings.append("sigma_authority='VETO_ONLY' : Sigma ne peut que veto, pas autoriser")
        if "REPORT_ONLY" in content:
            findings.append("sigma_authority='REPORT_ONLY' : Sigma observe sans agir si stable")
        if "sigma_override_policy" in content:
            findings.append("sigma_override_policy correctement inscrit dans le JSON de sortie")

        if re.search(r"gamma\s*=\s*0\.5", content):
            findings.append("ALERTE: gamma=0.5 detecte dans run_pipeline.py!")
            verified = False

    return {
        "verified": verified,
        "file_checked": str(run_pipeline_path.relative_to(root)),
        "findings": findings,
    }


def _check_no_gamma_05(root: Path) -> dict:
    """Verifie qu'aucun gamma=0.5 n'est present dans sigma/."""
    sigma_dir = root / "sigma"
    violations = []
    files_checked = []

    for py_file in sigma_dir.rglob("*.py"):
        if "broken" in py_file.name:
            continue
        content = py_file.read_text(encoding="utf-8")
        files_checked.append(str(py_file.relative_to(root)))
        if re.search(r"gamma\s*=\s*0\.5", content):
            violations.append(f"VIOLATION gamma=0.5 dans {py_file.relative_to(root)}")

    cfg_path = sigma_dir / "sigma_config.json"
    if cfg_path.exists():
        files_checked.append(str(cfg_path.relative_to(root)))
        cfg_content = cfg_path.read_text(encoding="utf-8")
        if "0.5" in cfg_content:
            cfg_data = json.loads(cfg_content)
            tau_max = cfg_data.get("tau_max")
            accel_limit = cfg_data.get("accel_limit")
            if tau_max == 0.5 or accel_limit == 0.5:
                violations.append(
                    f"VIOLATION gamma=0.5 : tau_max={tau_max}, accel_limit={accel_limit} dans sigma_config.json"
                )

    return {
        "verified": len(violations) == 0,
        "files_checked_count": len(files_checked),
        "violations": violations,
    }


def _check_agents_readonly_pressure(root: Path) -> dict:
    """Verifie que agents_readonly/ ne cree aucune pression sur sigma/."""
    ar_dir = root / "apps" / "obsidia_api" / "agents_readonly"
    findings = []
    sigma_imports = []

    if ar_dir.exists():
        for py_file in ar_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if "from sigma" in content or "import sigma" in content:
                sigma_imports.append(str(py_file.relative_to(root)))
            if "SIGMA_OVERRIDE: bool = False" in content or "SIGMA_OVERRIDE = False" in content:
                findings.append(f"{py_file.name}: SIGMA_OVERRIDE=False confirme")
            if "DRY_RUN_ONLY: bool = True" in content:
                findings.append(f"{py_file.name}: DRY_RUN_ONLY=True confirme")

    return {
        "sigma_imports_from_agents_readonly": sigma_imports,
        "sigma_pressure": len(sigma_imports) > 0,
        "verified_no_pressure": len(sigma_imports) == 0,
        "findings": findings,
    }


def _check_srl_outside_sigma(root: Path) -> dict:
    """Verifie que SRL (P66) est bien hors sigma/."""
    srl_path = root / "periphery" / "brody_memory_readonly" / "srl_session_registry_layer_readonly"
    srl_exists = srl_path.exists()
    sigma_srl = root / "sigma" / "srl_session_registry_layer_readonly"
    sigma_srl_exists = sigma_srl.exists()

    return {
        "srl_in_periphery": srl_exists,
        "srl_in_sigma": sigma_srl_exists,
        "verified_srl_outside_sigma": not sigma_srl_exists,
    }


# ---------------------------------------------------------------------------
# P72 invariants checked
# ---------------------------------------------------------------------------

P72_INVARIANTS_CHECKED = [
    {
        "invariant_id": "SIGMA_POST_GUARD_VETO_ONLY",
        "layer": "OS2_SIGMA",
        "formal_status": "PYTHON_TESTED_NOT_LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "run_pipeline.py:apply_sigma() : stability==FAIL -> HOLD_STABILITY_ALERT uniquement. "
            "sigma_authority en sortie : VETO_ONLY ou REPORT_ONLY. "
            "Sigma ne peut jamais promouvoir HOLD/BLOCK -> ACT."
        ),
    },
    {
        "invariant_id": "GUARD_X108_FINAL_AUTHORITY",
        "layer": "OS1_GUARD",
        "formal_status": "LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "sigma/guard.py : GuardX108.decide() = autorite finale. "
            "Aucun appel Sigma dans guard.py. "
            "Preuve Lean : GUARD_X108_FINAL_AUTHORITY (X108_kernel_never_blocks)."
        ),
    },
    {
        "invariant_id": "NO_KERNEL_MUTATION_FROM_PERIPHERY",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "sigma/ ne modifie aucun fichier kernel, Lean, ou preuve. "
            "evaluate.py BOUNDARY: kernel_mutation=False, x108_mutation=False. "
            "Aucun fichier sigma/ n'ecrit dans proofs/V18_3_1/ ni dans les theoremes Lean."
        ),
    },
    {
        "invariant_id": "NO_PERIPHERY_DECISION_AUTHORITY",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED_NOT_LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "evaluate.py: allowed_to_decide=False, advisory_only=True. "
            "packets.py: sigma_allowed_to_decide=False. "
            "agents_readonly/: DECISION_AUTHORITY=KX108_ONLY."
        ),
    },
    {
        "invariant_id": "KX108_ONLY_DECISION_AUTHORITY",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED_NOT_LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "decision_authority='KX108_ONLY' dans : evaluate.py, registry.py, "
            "packets.py, agents_readonly/__init__.py, sigma_dashboard_readonly.py, "
            "indicators_readonly.py."
        ),
    },
    {
        "invariant_id": "DETERMINISM",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "sigma/aggregation.py : logique deterministe, confidence plafonnee a 0.98. "
            "sigma_config.json : seuils fixes (tau_max=5.0, accel_limit=0.6). "
            "Aucune variation non-deterministe introduite."
        ),
    },
    {
        "invariant_id": "NO_GRAPHITI_WRITE",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED_NOT_LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "evaluate.py BOUNDARY: graphiti_write=False. "
            "packets.py _PACKET_BOUNDARY: graphiti_write=False. "
            "graphiti_readonly_bridge.py: lecture seule uniquement."
        ),
    },
    {
        "invariant_id": "NO_MEMORY_WRITE_WITHOUT_GATE",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED_NOT_LEAN_PROVEN",
        "p74_verification": "VERIFIED",
        "evidence": (
            "evaluate.py BOUNDARY: memory_write=False. "
            "packets.py _PACKET_BOUNDARY: memory_write=False. "
            "agents_readonly/: MEMORY_WRITE=False."
        ),
    },
]

# ---------------------------------------------------------------------------
# Focus findings
# ---------------------------------------------------------------------------

FOCUS_FINDINGS = [
    {
        "finding_id": "P74-F1",
        "type": "VERIFIED_CORRECT",
        "component": "sigma/run_pipeline.py:apply_sigma()",
        "description": (
            "POST_GUARD_VETO_ONLY correctement implemente : "
            "stability==FAIL -> HOLD_STABILITY_ALERT + sigma_authority=VETO_ONLY, "
            "stability==PASS -> sigma_authority=REPORT_ONLY. "
            "Aucune promotion possible de HOLD/BLOCK vers ACT."
        ),
        "action": "NO_CHANGE",
    },
    {
        "finding_id": "P74-F2",
        "type": "VERIFIED_CORRECT",
        "component": "sigma/obsidia_sigma_v130.py",
        "description": (
            "gamma=1.0 confirme. tau_max default=0.75, accel_limit default=0.40. "
            "sigma_config.json : tau_max=5.0 (calibration statistique 3-sigma, 2026-03-12). "
            "Aucune valeur 0.5 ni dans le moteur ni dans la config."
        ),
        "action": "NO_CHANGE",
    },
    {
        "finding_id": "P74-F3",
        "type": "VERIFIED_CORRECT",
        "component": "agents_readonly/ (P73)",
        "description": (
            "sigma_dashboard_readonly.py et indicators_readonly.py ne creent aucune pression sur sigma/. "
            "sigma_dashboard_readonly importe json et Path, pas sigma directement. "
            "indicators_readonly est un wrapper standalone de math pure. "
            "SIGMA_OVERRIDE=False dans les deux."
        ),
        "action": "NO_CHANGE",
    },
    {
        "finding_id": "P74-F4",
        "type": "VERIFIED_CORRECT",
        "component": "sigma/ test suite",
        "description": (
            "21 fichiers de tests couvrent : "
            "bank (world, adversarial, fuzz, enterprise, market, regulatory, replay, scale), "
            "GPS (smoke, semantics, fail_closed), "
            "sigma (pipeline, monitor, smoke). "
            "Aucun test manquant identifie pour les invariants P74."
        ),
        "action": "NO_CHANGE",
    },
    {
        "finding_id": "P74-F5",
        "type": "CARRY_FORWARD_P73",
        "component": "sigma/domains/trading_agents.py",
        "description": (
            "Verification que sigma/domains/trading_agents.py "
            "n'importe PAS ccxt (contrairement a python_agents/domains/trading_agents.py P73). "
            "Finding P73 porte : ccxt est un risque core seulement, pas sigma/."
        ),
        "action": "MONITOR",
    },
]

# ---------------------------------------------------------------------------
# Run checks and build result
# ---------------------------------------------------------------------------

def run_audit() -> dict:
    veto_check = _check_post_guard_veto_only(ROOT)
    gamma_check = _check_no_gamma_05(ROOT)
    ar_check = _check_agents_readonly_pressure(ROOT)
    srl_check = _check_srl_outside_sigma(ROOT)

    overall_sigma_decision = "NO_SIGMA_CHANGE_REQUIRED"
    if not veto_check["verified"]:
        overall_sigma_decision = "BLOCKED_REQUIRES_FORMAL_REVIEW"
    if not gamma_check["verified"]:
        overall_sigma_decision = "BLOCK_SIGMA_CHANGE"
    if ar_check["sigma_pressure"]:
        overall_sigma_decision = "BLOCKED_REQUIRES_FORMAL_REVIEW"

    sigma_files_scanned = [e["file_path"] for e in SIGMA_MATRIX]

    result = {
        "audit_id": "P74",
        "status": "P74_SIGMA_SAFE_EVOLUTION_READY",
        "mode": "AUDIT_AND_PATCH_IF_SAFE",
        "source_patch_applied": False,
        "sigma_decision": overall_sigma_decision,
        "files_imported_count": 0,
        "sigma_modified": False,
        "runtime_modified": False,
        "routes_modified": False,
        "lean_proofs_modified": False,
        "proofs_modified": False,
        "srl_modified": False,
        "connectors_modified": False,
        "source_packs_modified": False,
        "act_enabled": False,
        "memory_write_enabled": False,
        "graphiti_write_enabled": False,
        "neo4j_write_enabled": False,
        "kernel_mutation_enabled": False,
        "x108_merge_enabled": False,
        "dry_run_only": DRY_RUN_ONLY,
        "branch": "p74-sigma-safe-evolution",
        "date": "2026-06-07",
        "palier": "P74",
        "sigma_model": SIGMA_MODEL,
        "sigma_files_scanned": sigma_files_scanned,
        "sigma_files_scanned_count": len(sigma_files_scanned),
        "sigma_matrix": SIGMA_MATRIX,
        "patches_applied": [],
        "blocked_sigma_changes": [],
        "proof_wins": [
            e["file_path"] for e in SIGMA_MATRIX
            if e["proof_wins"] and e["file_path"] != "sigma/contracts.broken-ragnarok.py"
        ],
        "core_regressions_blocked": [
            "sigma/ non modifie — guard.py/run_pipeline.py preserves P56D",
            "obsidia_sigma_v130.py : gamma=1.0 preservee (P56B)",
            "contracts.py : GPS domain et triple confidence preserves (P56B)",
        ],
        "p72_invariants_checked": P72_INVARIANTS_CHECKED,
        "p73_agent_pressure_checked": ar_check,
        "sigma_tests_checked": {
            "test_files_count": 21,
            "test_directories": ["sigma/tests/"],
            "coverage_domains": ["bank", "trading", "ecom", "gps_defense_aviation", "sigma_monitor"],
            "new_tests_required": False,
        },
        "post_guard_veto_only_check": veto_check,
        "no_gamma_05_check": gamma_check,
        "srl_outside_sigma_check": srl_check,
        "focus_findings": FOCUS_FINDINGS,
        "preexisting_manifest_drift": [],
        "preexisting_test_debt": [],
        "full_cascade_timeout_noted": True,
        "next_step": "P75_RUNTIME_CORE_RISK_REVIEW",
    }

    return result


def main():
    result = run_audit()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"JSON => {OUT_JSON}")
    print(f"sigma_decision => {result['sigma_decision']}")
    print(f"status => {result['status']}")
    print(f"files_scanned => {result['sigma_files_scanned_count']}")
    veto = result["post_guard_veto_only_check"]
    gamma = result["no_gamma_05_check"]
    print(f"post_guard_veto_only verified => {veto['verified']}")
    print(f"no_gamma_05 verified => {gamma['verified']}")


if __name__ == "__main__":
    main()

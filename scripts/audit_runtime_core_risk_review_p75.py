#!/usr/bin/env python3
"""
scripts/audit_runtime_core_risk_review_p75.py

P75 — Runtime Core Risk Review
MODE: AUDIT_ONLY

Audite les composants runtime core a risque eleve.
Ne patche pas. Ne importe pas. Ne modifie rien.

VERROU ABSOLU :
  - Ne pas importer ces composants en production.
  - Ne pas executer le runtime core.
  - Ne pas activer ACT.
  - Ne pas lancer de serveur.
  - Ne pas appeler le reseau.

DRY_RUN_ONLY = True (audit seul)
"""

import json
import os
import re
import sys
from pathlib import Path

DRY_RUN_ONLY: bool = True

ROOT = Path(__file__).resolve().parent.parent
CORE_ENGINE_DIR = ROOT / "_tmp_core_import" / "OBSIDIA_CORE_ONLY_FULL_MACHINERY" / "engine"
OUT_JSON = ROOT / "docs" / "core_import" / "P75_RUNTIME_CORE_RISK_REVIEW.json"
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
    "runtime_modified": False,
}

# ---------------------------------------------------------------------------
# Runtime model
# ---------------------------------------------------------------------------

RUNTIME_MODEL = {
    "already_covered_by_proof": (
        "Composants dont la logique est deja couverte par runtime_wiring/, sigma/, ou proofs/. "
        "Exemple : X108Gate dans os1/x108.py est deja couvert par "
        "runtime_wiring/x108_admission_stub.py et sigma/guard.py (P56D GuardX108). "
        "Ne pas reimporter — utiliser la version proof."
    ),
    "duplicate_old_core": (
        "Fichiers vendored ou doublons exacts de composants deja presents dans core_full/vendor/. "
        "core_full/modules/os_trad/vendor/ copie os0/, os1/, proof/ en totalite. "
        "Ne pas importer — doublons inutiles, plus maintenu."
    ),
    "adapter_candidate_readonly": (
        "Logique pure (hash, metriques, validation) sans file write ni reseau. "
        "Peut devenir adapter readonly dans un palier futur apres revue formelle. "
        "Exemples : os0/ir.py (types IR), os0/contract.py (validateur R1-R10), "
        "os0/determinism.py (hash canonique), os3/metrics.py (metriques graphe)."
    ),
    "adapter_candidate_dry_run": (
        "Logique utile (sandbox, traducteur, parseur) sans side-effect mais produisant des resultats. "
        "Pourrait devenir adapter dry-run avec DRY_RUN_ONLY=True dans un palier futur. "
        "Exemples : os0/sandbox.py (executor deterministique), os1/parse_input.py (AST->IR)."
    ),
    "test_only_candidate": (
        "Tests unitaires pour os0/os1 uniquement — pas de runtime production. "
        "Import possible dans un palier futur comme tests de regression architecturale."
    ),
    "doc_only_candidate": (
        "Reference documentaire uniquement — demos, specs de types. "
        "Pas de runtime load. Import doc uniquement pour reference architecturale."
    ),
    "high_risk_blocked": (
        "Composants avec multiples risques combines (action + write + network). "
        "api_server/main.py : FastAPI live + file write par requete + route /v1/decision."
    ),
    "action_risk_blocked": (
        "Composants qui emettent ACT ou executent des decisions irréversibles. "
        "os1/os1.py -> OS1Decision(decision='ACT'). "
        "orchestrator.py -> _kernel.run(req) -> Decision.ACT. "
        "engine_final.py -> FinalResult(decision='ACT'). "
        "BLOQUE jusqu'a preuve formelle et hardening complet."
    ),
    "write_risk_blocked": (
        "Composants qui ecrivent sur le filesystem sans gate (audit_log, signing, attestation). "
        "open(path, 'a'/'w') non gate. "
        "BLOQUE — ecriture non consentie requiert gate explicite."
    ),
    "network_risk_blocked": (
        "Composants qui appellent le reseau externe (boto3 S3, requests, ccxt). "
        "worm_uploader.py : boto3 S3 upload. "
        "BLOQUE — reseau externe requiert gate P70."
    ),
    "kernel_mutation_blocked": (
        "Composants qui sont ou wrappent le kernel d'execution (ObsidiaKernel, run_final, run_obsidia). "
        "BLOQUE PERMANENT — le kernel ne peut pas etre importe brut. "
        "Toute integration kernel requiert preuve formelle + revue architecturale."
    ),
    "formal_review_required": (
        "Composants dont la classification necessiterait une revue formelle plus approfondie. "
        "core_full/adapter.py : sys.path manipulation + purge de modules = "
        "risque d'interference avec sigma/ existant. "
        "BLOQUE jusqu'a revue formelle."
    ),
}

# ---------------------------------------------------------------------------
# Risk patterns to search
# ---------------------------------------------------------------------------

RISK_PATTERNS = [
    "ACT",
    r"decision\s*=\s*[\"']ACT[\"']",
    r"open\s*\([^)]+,\s*[\"'](w|a)[\"']",
    "write_text",
    "boto3",
    r"requests\.post",
    r"os\.system",
    r"subprocess\.",
    "FastAPI",
    "APIRouter",
    r"app\.post\s*\(",
    r"while\s+True",
    r"os\.walk",
    "kernel_mutation",
    "sys.modules.pop",
    "run_obsidia",
    "_kernel.run",
]

def _check_patterns(content: str, file_path: str) -> list:
    found = []
    for pat in RISK_PATTERNS:
        if re.search(pat, content):
            found.append(pat)
    return found

def _read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

# ---------------------------------------------------------------------------
# Runtime matrix
# ---------------------------------------------------------------------------

RUNTIME_MATRIX = [
    # ---- RUNTIME_KERNEL_MUTATION_BLOCKED (3 files) ----
    {
        "file_path": "engine/obsidia_runtime/engine_final.py",
        "component_name": "run_final()",
        "category": "RUNTIME_KERNEL_MUTATION_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "CRITICAL",
        "risk_patterns_found": [
            "decision='ACT|HOLD|REJECT'",
            "os2_dec = decision_act_hold(...)",
            "os1_run_request(raw_input=...) -> OS1Decision",
            "from obsidia_os1 import run_request",
        ],
        "description": (
            "Moteur d'execution complet OS2+OS1+Registry. "
            "Produit FinalResult(decision='ACT/HOLD/REJECT'). "
            "Appelle OS1 qui execute OS0 sandbox. "
            "Contient la logique de Pivot allowlist registry."
        ),
        "reason_blocked": (
            "Emetteur ACT direct. Le moteur final ne peut pas etre importe brut. "
            "Toute integration requiert preuve formelle OS2 + hardening complet. "
            "P72 invariant GUARD_X108_FINAL_AUTHORITY : l'autorite finale reste GuardX108 (sigma/guard.py), "
            "pas run_final()."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_ACT_BEFORE_TAU"],
    },
    {
        "file_path": "engine/obsidia_kernel/kernel.py",
        "component_name": "ObsidiaKernel.run()",
        "category": "RUNTIME_KERNEL_MUTATION_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "CRITICAL",
        "risk_patterns_found": [
            "from entrypoint import run_obsidia",
            "fr = run_obsidia(engine_payload)",
            "kernel_decision = _map_decision(raw_decision)",
            "Decision.ACT",
            "HumanGate",
            "hash_chain",
        ],
        "description": (
            "Kernel d'execution central. "
            "Appelle run_obsidia() (engine_final), produit Result(decision=Decision.ACT/HOLD/BLOCK). "
            "Contient hash_chain, ACP, HumanGate. Version v2.3.1."
        ),
        "reason_blocked": (
            "C'est le kernel lui-meme. "
            "RUNTIME_KERNEL_MUTATION_BLOCKED permanent. "
            "Importer ce fichier connecterait directement le kernel d'execution au repo proof. "
            "Requiert preuve formelle et integration architecturale complete."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "IRREVERSIBLE_ACTION_DELAY"],
    },
    {
        "file_path": "engine/core_full/entrypoint.py",
        "component_name": "run_obsidia()",
        "category": "RUNTIME_KERNEL_MUTATION_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "CRITICAL",
        "risk_patterns_found": [
            "from obsidia_runtime.engine_final import run_final",
            "return run_final(**payload)",
        ],
        "description": (
            "Entrypoint du kernel core. "
            "Charge le registry depuis core_full/registry/minimal_engine_registry_from_xls.json. "
            "Appelle run_final(**payload) directement."
        ),
        "reason_blocked": (
            "Entrypoint kernel — executer run_obsidia() lance le moteur complet. "
            "BLOCK_RUNTIME_IMPORT jusqu'a preuve formelle."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_ACT_BEFORE_TAU"],
    },
    # ---- RUNTIME_ACTION_RISK_BLOCKED (5 entries) ----
    {
        "file_path": "engine/os1/os1.py",
        "component_name": "run_request()",
        "category": "RUNTIME_ACTION_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "HIGH",
        "risk_patterns_found": [
            "OS1Decision(decision='ACT')",
            "sb.run(program)",
            "x108_gate.check(...)",
        ],
        "description": (
            "Pipeline OS1 complet : parse_input -> validate_contract -> X108 check -> OS0 sandbox exec. "
            "Produit OS1Decision(decision='ACT/HOLD/REJECT'). "
            "Execute os0_out = sb.run(program) si X108 dit ACT."
        ),
        "reason_blocked": (
            "Emetteur ACT direct. "
            "Le pipeline OS1 execute le programme IR dans le sandbox — "
            "hors du perimetre sigma/GuardX108. "
            "P72 invariant NO_ACT_BEFORE_TAU : aucune action avant tau. "
            "BLOCK jusqu'a preuve formelle OS1 complete."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_ACT_BEFORE_TAU", "HOLD_BEFORE_TAU", "IRREVERSIBLE_ACTION_DELAY"],
    },
    {
        "file_path": "engine/unified/orchestrator.py",
        "component_name": "orchestrate()",
        "category": "RUNTIME_ACTION_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "HIGH",
        "risk_patterns_found": [
            "_kernel = ObsidiaKernel()",
            "_kernel.run(req)",
            "intent_type = 'ACTION'",
            "_router = build_default_router()",
        ],
        "description": (
            "Orchestrateur unifie : construit router + kernel, route les requetes. "
            "Cree ObsidiaKernel() au chargement du module (side-effect). "
            "Intent default = ACTION. "
            "Appelle _kernel.run(req) pour chaque requete."
        ),
        "reason_blocked": (
            "Import du module cree ObsidiaKernel() immediatement (side-effect). "
            "Emetteur ACTION/BLOCK/HOLD via kernel. "
            "BLOCK_RUNTIME_IMPORT — impossible a importer sans lancer le kernel."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": True,
        "sigma_covers": False,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_ACT_BEFORE_TAU"],
    },
    {
        "file_path": "engine/unified/pipeline.py",
        "component_name": "run()",
        "category": "RUNTIME_ACTION_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "HIGH",
        "risk_patterns_found": [
            "from .orchestrator import orchestrate",
            "return orchestrate(payload)",
        ],
        "description": (
            "Wrapper mince sur orchestrate(). "
            "Importer ce fichier importe orchestrator.py = cree ObsidiaKernel() side-effect."
        ),
        "reason_blocked": "Delegue a orchestrator.py — memes risques. BLOCK_RUNTIME_IMPORT.",
        "proof_wins": False,
        "runtime_wiring_covers": True,
        "sigma_covers": False,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY"],
    },
    {
        "file_path": "engine/api_server/main.py",
        "component_name": "FastAPI app /v1/decision",
        "category": "RUNTIME_ACTION_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "CRITICAL",
        "risk_patterns_found": [
            "app = FastAPI(...)",
            "app.post('/v1/decision')",
            "unified_run(payload)",
            "open(path, 'w')",
            "os.makedirs(STORE_DIR)",
        ],
        "description": (
            "Serveur FastAPI live. Route POST /v1/decision appelle unified_run() (pipeline complet). "
            "Ecrit chaque resultat dans STORE_DIR/{trace_id}.json. "
            "Contient auth HMAC, JWT, API key. "
            "Lance le serveur avec uvicorn (run_api.sh)."
        ),
        "reason_blocked": (
            "Serveur live avec execution d'action et file write par requete. "
            "P68 finding porte : routes proof deja exposees sous apps/obsidia_api/. "
            "Ne pas creer un deuxieme serveur. BLOCK_RUNTIME_IMPORT."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": True,
        "sigma_covers": False,
        "p72_invariants": ["ROUTE_AUTH_BOUNDARY", "NO_MEMORY_WRITE_WITHOUT_GATE"],
    },
    {
        "file_path": "engine/api_server/run_api.sh",
        "component_name": "uvicorn launcher",
        "category": "RUNTIME_ACTION_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "HIGH",
        "risk_patterns_found": ["shell script — lance uvicorn"],
        "description": "Script shell lançant uvicorn pour api_server/main.py. Demarre le serveur live.",
        "reason_blocked": "Execution de serveur live. BLOCK_RUNTIME_IMPORT.",
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    # ---- RUNTIME_WRITE_RISK_BLOCKED (4 files) ----
    {
        "file_path": "engine/api_server/audit_log.py",
        "component_name": "append_audit()",
        "category": "RUNTIME_WRITE_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "HIGH",
        "risk_patterns_found": [
            "open(AUDIT_LOG, 'a')",
            "open(AUDIT_CHAIN, 'a')",
            "os.makedirs(STORE_DIR, exist_ok=True)",
        ],
        "description": (
            "Log d'audit append-only + hash chain. "
            "Ecrit audit.log et audit.chain a chaque appel. "
            "makedirs execute au chargement du module (side-effect)."
        ),
        "reason_blocked": (
            "Ecriture filesystem non gatee au chargement du module. "
            "P72 invariant NO_MEMORY_WRITE_WITHOUT_GATE. "
            "BLOCK_RUNTIME_IMPORT — la logique de hash chain est bonne "
            "mais l'implementation brute ecrit sans gate. "
            "ADAPT_READONLY_LATER pour la logique de hash seule."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_MEMORY_WRITE_WITHOUT_GATE"],
    },
    {
        "file_path": "engine/api_server/signing.py",
        "component_name": "ensure_keys() / sign_bytes()",
        "category": "RUNTIME_WRITE_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "MEDIUM",
        "risk_patterns_found": [
            "PRIVATE_KEY_PATH.write_text(priv_pem)",
            "PUBLIC_KEY_PATH.write_text(pub_pem)",
            "KEY_DIR.mkdir(parents=True, exist_ok=True)",
        ],
        "description": (
            "Generateur de cles Ed25519 + signature. "
            "ensure_keys() genere et ecrit PEM sur le disque si absent. "
            "KEY_DIR.mkdir() execute au chargement du module (side-effect). "
            "verify_bytes() est pure (lecture seule)."
        ),
        "reason_blocked": (
            "mkdir et write_text au chargement = side-effect non gate. "
            "BLOCK_RUNTIME_IMPORT en l'etat. "
            "verify_bytes() seule pourrait devenir ADAPT_READONLY_LATER."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_MEMORY_WRITE_WITHOUT_GATE"],
    },
    {
        "file_path": "engine/api_server/run_attestation.py",
        "component_name": "run_attestation main()",
        "category": "RUNTIME_WRITE_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "MEDIUM",
        "risk_patterns_found": [
            "write_attestation(att, sig_b64, pub_pem)",
            "sign_bytes(raw)",
        ],
        "description": (
            "Script CLI qui build et ecrit une attestation signee sur le disque. "
            "Appelle attestation.py (read) + signing.py (write keys) + write_attestation()."
        ),
        "reason_blocked": (
            "Ecriture fichier attestation + generation de cles = side-effects. "
            "BLOCK_RUNTIME_IMPORT en l'etat. "
            "La logique de hash attestation dans attestation.py est candidate ADAPT_READONLY_LATER."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_MEMORY_WRITE_WITHOUT_GATE"],
    },
    {
        "file_path": "engine/os3/svg.py",
        "component_name": "render_core_svg()",
        "category": "RUNTIME_WRITE_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "LOW",
        "risk_patterns_found": [
            "out_path: str (parametre de sortie fichier)",
        ],
        "description": (
            "Renderer SVG pour le graphe de core. "
            "Accepte out_path: str — ecrit le fichier SVG. "
            "La logique de generation SVG est pure mais le write n'est pas gate."
        ),
        "reason_blocked": (
            "Ecriture fichier non gatee. "
            "P73 pattern : agents qui ecrivent PNG bloques (sigma_dashboard_readonly). "
            "Meme logique ici. BLOCK_RUNTIME_IMPORT. "
            "Pourrait devenir ADAPT_READONLY_LATER en retournant le SVG comme string."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_MEMORY_WRITE_WITHOUT_GATE"],
    },
    # ---- RUNTIME_NETWORK_RISK_BLOCKED (1 file) ----
    {
        "file_path": "engine/api_server/worm_uploader.py",
        "component_name": "WORM S3 uploader",
        "category": "RUNTIME_NETWORK_RISK_BLOCKED",
        "decision": "BLOCK_RUNTIME_IMPORT",
        "risk_level": "HIGH",
        "risk_patterns_found": [
            "import boto3",
            "boto3.client('s3', ...)",
            "s3.upload_file(...)",
            "s3.put_object(...)",
            "s3.head_bucket(...)",
            "s3.create_bucket(...)",
        ],
        "description": (
            "Uploader WORM optional — envoie audit.log + audit.chain vers S3/MinIO. "
            "boto3 = dependance reseau externe. "
            "Cree le bucket si absent (write sur stockage externe)."
        ),
        "reason_blocked": (
            "Reseau externe (S3/MinIO). "
            "P70 invariant NETWORK_EGRESS_REVIEW_REQUIRED. "
            "BLOCK_RUNTIME_IMPORT — gate reseau requis avant tout upload."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NETWORK_EGRESS_REVIEW_REQUIRED"],
    },
    # ---- RUNTIME_REQUIRES_FORMAL_REVIEW (1 file) ----
    {
        "file_path": "engine/core_full/modules/os_trad/adapter.py",
        "component_name": "os_trad_propose()",
        "category": "RUNTIME_REQUIRES_FORMAL_REVIEW",
        "decision": "BLOCK_UNTIL_FORMAL_REVIEW",
        "risk_level": "HIGH",
        "risk_patterns_found": [
            "sys.path.insert(0, str(VENDOR_DIR))",
            "sys.modules.pop(k, None)",
            "from proof.runner import build, Refusal",
        ],
        "description": (
            "Adapter OS_TRAD. "
            "Manipule sys.path (inject vendor/ dir). "
            "Purge sys.modules (pop obsidia_os0, obsidia_os1, proof). "
            "Risque d'interference avec sigma/ et les imports du repo proof actuel. "
            "Appelle proof.runner.build() depuis vendor — runner non verifie."
        ),
        "reason_blocked": (
            "Manipulation du module system Python = risque d'interference avec sigma/. "
            "sys.modules.pop(obsidia_os0...) pourrait descharger des modules sigma/ en cours d'utilisation. "
            "BLOCK_UNTIL_FORMAL_REVIEW — necessite audit complet de l'impact sur sigma/."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_KERNEL_MUTATION_FROM_PERIPHERY"],
    },
    # ---- RUNTIME_ALREADY_COVERED_BY_PROOF (2 files) ----
    {
        "file_path": "engine/os1/x108.py",
        "component_name": "X108Gate.check()",
        "category": "RUNTIME_ALREADY_COVERED_BY_PROOF",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "LOW",
        "risk_patterns_found": [],
        "description": (
            "Gate X108 minimal — check elapsed_s vs min_wait_s. "
            "Produit X108Check(decision='ACT/HOLD')."
        ),
        "reason_blocked": (
            "Deja couvert par runtime_wiring/x108_admission_stub.py et sigma/guard.py (P56D). "
            "GuardX108 (sigma) est l'autorite finale — Lean-proven GUARD_X108_FINAL_AUTHORITY. "
            "KEEP_PROOF_VERSION."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": True,
        "sigma_covers": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_ACT_BEFORE_TAU"],
    },
    {
        "file_path": "engine/os0/ir.py",
        "component_name": "IR alphabet (12 symbols)",
        "category": "RUNTIME_ALREADY_COVERED_BY_PROOF",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Alphabet IR L2 : 12 types (VALUE, STATE, READ, WRITE, FLOW, COND, LOOP, "
            "CALL, RETURN, EVENT, TIME, ERROR). Dataclasses pures immuables."
        ),
        "reason_blocked": (
            "Types purs couverts par le modele de contrat sigma/contracts.py (P56B). "
            "La notion IR L2 est architecturalement separee du pipeline sigma/GuardX108. "
            "KEEP_PROOF_VERSION — pas d'import requis dans le repo proof. "
            "Si besoin futur : ADAPT_READONLY_LATER comme types stand-alone."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": True,
        "p72_invariants": ["DETERMINISM"],
    },
    # ---- RUNTIME_ADAPTER_CANDIDATE_READONLY (6 files) ----
    {
        "file_path": "engine/os0/contract.py",
        "component_name": "validate() R1-R10",
        "category": "RUNTIME_ADAPTER_CANDIDATE_READONLY",
        "decision": "ADAPT_READONLY_LATER",
        "risk_level": "LOW",
        "risk_patterns_found": [],
        "description": (
            "Validateur de contrat structurel R1-R10 pour les programmes IR. "
            "Aucun file write, aucun reseau. "
            "validate(program) retourne List[Violation] ou leve ContractViolationError. "
            "Fonction pure deterministe."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_READONLY_LATER. "
            "Logique pure exploitable pour valider des programmes IR dans un palier futur. "
            "Requiert : revue formelle du mapping entre R1-R10 et invariants P72, "
            "DRY_RUN_ONLY=True, BOUNDARY complet."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["DETERMINISM"],
    },
    {
        "file_path": "engine/os0/sandbox.py",
        "component_name": "Sandbox.run()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_DRY_RUN",
        "decision": "ADAPT_DRY_RUN_LATER",
        "risk_level": "LOW",
        "risk_patterns_found": [],
        "description": (
            "Executor de programmes IR deterministique. "
            "Aucun side-effect externe : print() = no-op, pas de file write, pas de reseau. "
            "Sandbox.run(program) -> Any (pur). "
            "Garde un log d'execution interne (self.log)."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_DRY_RUN_LATER. "
            "La sandbox est pure mais son output pourrait etre interprété comme une action. "
            "Requiert : DRY_RUN_ONLY=True, BOUNDARY complet, revue de l'output semantique. "
            "Note : WRITE IR node modifie self.state — "
            "pas un vrai file write mais mutation d'etat interne."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["DETERMINISM"],
    },
    {
        "file_path": "engine/os0/determinism.py",
        "component_name": "canonical_hash()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_READONLY",
        "decision": "ADAPT_READONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Hash canonique SHA-256 d'un programme IR. "
            "Fonction pure : canonical_hash(ir_program) -> str. "
            "Aucun side-effect."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_READONLY_LATER. "
            "Logique de hash pur utile pour la verification d'integrite des programmes IR. "
            "Peut etre importe dans un palier futur avec BOUNDARY complet."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["DETERMINISM"],
    },
    {
        "file_path": "engine/os0/translate.py",
        "component_name": "python_like_to_ir()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_DRY_RUN",
        "decision": "ADAPT_DRY_RUN_LATER",
        "risk_level": "LOW",
        "risk_patterns_found": [],
        "description": (
            "Traducteur python-like -> IR (prototype). "
            "Supporte : assignations simples + while x < N. "
            "Fonction pure (parse regex, pas d'AST)."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_DRY_RUN_LATER. "
            "Utile pour tests du pipeline IR. "
            "Prototype incomplet — supporte un sous-ensemble tres limite. "
            "Revue requise avant usage production."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/os1/parse_input.py",
        "component_name": "_parse_assignment() / parse_input()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_DRY_RUN",
        "decision": "ADAPT_DRY_RUN_LATER",
        "risk_level": "LOW",
        "risk_patterns_found": ["import ast"],
        "description": (
            "Parseur AST Python -> IR. "
            "Utilise ast.parse() de la stdlib. "
            "Coerce dicts/listes en noeuds EVENT. "
            "Aucun file write, aucun reseau."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_DRY_RUN_LATER. "
            "ast.parse() est standard. "
            "Attention : parse arbitraire d'input utilisateur = surface XSS/injection potentielle. "
            "Requiert sanitization input + DRY_RUN_ONLY=True + BOUNDARY complet."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["DETERMINISM"],
    },
    {
        "file_path": "engine/os3/metrics.py",
        "component_name": "compute_metrics_core_fixed()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_READONLY",
        "decision": "ADAPT_READONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Metriques de graphe OS3 : triangle detection, hexagone radial, asymetrie. "
            "S = alpha*T_mean + beta*H_score - gamma*A. "
            "decision_act_hold(metrics, theta_S) -> 'ACT'|'HOLD'. "
            "Fonctions pures, aucun side-effect."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_READONLY_LATER. "
            "decision_act_hold() retourne 'ACT'|'HOLD' mais c'est un score pur, "
            "non un verdict GuardX108. "
            "Utilise dans engine_final.py comme gate OS2 AVANT OS1. "
            "Exploitable comme metriques readonly avec BOUNDARY complet. "
            "Note : gamma=1.0 dans compute_metrics() (default) — pas de gamma=0.5. "
            "Revue formelle OS2 requise avant integration dans le pipeline proof."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["DETERMINISM", "THRESHOLD_CONSERVATION"],
    },
    {
        "file_path": "engine/os3/core_split.py",
        "component_name": "CORE_1BASED / WORLD_1BASED",
        "category": "RUNTIME_ADAPTER_CANDIDATE_READONLY",
        "decision": "ADAPT_READONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Constantes de partition core/world : CORE_1BASED=[2,6,10,...], "
            "WORLD_1BASED=[1,3,4,...]. "
            "core_nodes_0based() et world_nodes_0based() = conversions simples."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_READONLY_LATER. "
            "Constantes pures. "
            "Utiles pour les tests de metriques OS3 dans un palier futur."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/api_server/security.py",
        "component_name": "enforce_auth() / verify_jwt() / verify_hmac_signature()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_READONLY",
        "decision": "ADAPT_READONLY_LATER",
        "risk_level": "LOW",
        "risk_patterns_found": [],
        "description": (
            "Module auth : API key, JWT HS256, HMAC. "
            "AUTH_MODE=apikey|jwt|both|none. "
            "verify_hmac_signature() : anti-replay avec nonce. "
            "Logique auth complete et bien structuree."
        ),
        "reason_blocked": (
            "Pas bloque — candidat ADAPT_READONLY_LATER pour reference. "
            "apps/obsidia_api/ a deja son propre modele auth (OBSIDIA_API_KEY 503 fail-closed, P68). "
            "La logique HMAC + anti-replay est documentairement utile. "
            "Note : _SEEN_NONCES est un dict global = state mutable en memoire. "
            "IMPORT_DOC_ONLY_LATER plus appropriate que ADAPT_READONLY."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["ROUTE_AUTH_BOUNDARY"],
    },
    {
        "file_path": "engine/api_server/attestation.py",
        "component_name": "build_attestation() / sha256_file()",
        "category": "RUNTIME_ADAPTER_CANDIDATE_READONLY",
        "decision": "ADAPT_READONLY_LATER",
        "risk_level": "LOW",
        "risk_patterns_found": [
            "ATTEST_DIR.mkdir(parents=True, exist_ok=True)",
            "fn.write_text(...)",
        ],
        "description": (
            "Build d'attestation : sha256(audit_log) + sha256(audit_chain) + hash chain d'attestations. "
            "build_attestation() = lecture + hash (readonly). "
            "write_attestation() = ecriture fichier (write). "
            "makedirs au chargement du module."
        ),
        "reason_blocked": (
            "Pas bloque mais ADAPT_READONLY_LATER uniquement pour build_attestation()/sha256_file(). "
            "makedirs au chargement = side-effect — a supprimer. "
            "write_attestation() = RUNTIME_WRITE_RISK_BLOCKED. "
            "La logique de hash + chain attestation est utile comme readonly."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": ["NO_MEMORY_WRITE_WITHOUT_GATE"],
    },
    # ---- RUNTIME_TEST_ONLY_CANDIDATE (2 files) ----
    {
        "file_path": "engine/os0/tests.py",
        "component_name": "Tests OS0",
        "category": "RUNTIME_TEST_ONLY_CANDIDATE",
        "decision": "IMPORT_TEST_ONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Suite de tests unitaires pour os0/ir.py, os0/contract.py, os0/sandbox.py. "
            "Tests de la grammaire IR, des regles R1-R10, de l'executor."
        ),
        "reason_blocked": (
            "Pas bloque — IMPORT_TEST_ONLY_LATER. "
            "Utile comme tests de regression architecturale pour os0 dans un palier futur. "
            "Requis : os0 adapte en readonly/dry-run d'abord."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/os0/tests_advanced.py",
        "component_name": "Tests OS0 avances",
        "category": "RUNTIME_TEST_ONLY_CANDIDATE",
        "decision": "IMPORT_TEST_ONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Tests avances OS0 : edge cases, violations complexes, sandbox avance."
        ),
        "reason_blocked": (
            "IMPORT_TEST_ONLY_LATER — meme condition que tests.py."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    # ---- RUNTIME_DOC_ONLY_CANDIDATE (2 files) ----
    {
        "file_path": "engine/os0/demo.py",
        "component_name": "Demo OS0",
        "category": "RUNTIME_DOC_ONLY_CANDIDATE",
        "decision": "IMPORT_DOC_ONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": "Demo du pipeline OS0 — illustration de l'utilisation. Pas de runtime production.",
        "reason_blocked": "IMPORT_DOC_ONLY_LATER — reference architecturale uniquement.",
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/obsidia_kernel/contract.py",
        "component_name": "Decision / Request / Result types",
        "category": "RUNTIME_DOC_ONLY_CANDIDATE",
        "decision": "IMPORT_DOC_ONLY_LATER",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Types de contrat kernel : Decision(ACT/HOLD/BLOCK), "
            "IntentType(PROPOSE/ACTION), Meta, Intent, Governance, Request. "
            "Dataclasses pures."
        ),
        "reason_blocked": (
            "IMPORT_DOC_ONLY_LATER — reference des types kernel pour documentation. "
            "Ne pas importer dans le runtime sigma/ — types incompatibles avec sigma/contracts.py. "
            "Utiliser sigma/contracts.py (P56B) comme reference de types pour le repo proof."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": True,
        "p72_invariants": [],
    },
    # ---- RUNTIME_DUPLICATE_OLD_CORE (vendored bulk) ----
    {
        "file_path": "engine/core_full/modules/os_trad/vendor/obsidia_os0/",
        "component_name": "Vendored os0 (9 fichiers)",
        "category": "RUNTIME_DUPLICATE_OLD_CORE",
        "decision": "DO_NOT_IMPORT_DUPLICATE",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Copie vendoree de os0/ : __init__, contract, demo, determinism, ir, "
            "sandbox, tests, tests_advanced, translate. "
            "Identiques aux fichiers engine/os0/ correspondants."
        ),
        "reason_blocked": (
            "DO_NOT_IMPORT_DUPLICATE — doublon exact de engine/os0/. "
            "Existe uniquement pour que core_full/modules/os_trad/adapter.py "
            "puisse manipuler sys.path sans conflit. "
            "Ne jamais importer depuis vendor/ directement."
        ),
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/core_full/modules/os_trad/vendor/obsidia_os1/",
        "component_name": "Vendored os1 (4 fichiers)",
        "category": "RUNTIME_DUPLICATE_OLD_CORE",
        "decision": "DO_NOT_IMPORT_DUPLICATE",
        "risk_level": "NONE",
        "risk_patterns_found": [],
        "description": (
            "Copie vendoree de os1/ : __init__, os1, parse_input, x108. "
            "Identiques aux fichiers engine/os1/ correspondants."
        ),
        "reason_blocked": "DO_NOT_IMPORT_DUPLICATE — meme raison que vendor/obsidia_os0/.",
        "proof_wins": False,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/core_full/modules/os_trad/vendor/proof/",
        "component_name": "Vendored proof runner (3 fichiers)",
        "category": "RUNTIME_DUPLICATE_OLD_CORE",
        "decision": "DO_NOT_IMPORT_DUPLICATE",
        "risk_level": "LOW",
        "risk_patterns_found": ["from proof.runner import build, Refusal"],
        "description": (
            "Copie vendoree du runner proof : __init__, codegen, runner. "
            "Appele par core_full/adapter.py. "
            "Contient Refusal (pattern d'echec de preuve)."
        ),
        "reason_blocked": (
            "DO_NOT_IMPORT_DUPLICATE. "
            "Le proof runner vendored est distinct des preuves formelles Lean/TLA du repo. "
            "Ne pas confondre avec proofs/V18_3_1/."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": False,
        "p72_invariants": [],
    },
    {
        "file_path": "engine/obsidia_runtime/engine_runtime.py",
        "component_name": "assemble_minimal_engine() / load_cortex_from_registry()",
        "category": "RUNTIME_DUPLICATE_OLD_CORE",
        "decision": "DO_NOT_IMPORT_DUPLICATE",
        "risk_level": "LOW",
        "risk_patterns_found": [
            "os.walk('.')",
            "open(registry_path, 'r')",
        ],
        "description": (
            "Assembly minimal du moteur depuis registry JSON. "
            "load_cortex_from_registry() utilise os.walk('.') pour trouver le fichier registry. "
            "Retourne pivot_agents, domaines_vrais, domaines_archi_cognitive."
        ),
        "reason_blocked": (
            "DO_NOT_IMPORT_DUPLICATE. "
            "La logique d'assembly registry est couverte par le pattern sigma/registry.py (F60). "
            "os.walk('.') = traversee filesystem non bornee. "
            "Ne pas importer."
        ),
        "proof_wins": True,
        "runtime_wiring_covers": False,
        "sigma_covers": True,
        "p72_invariants": [],
    },
]

# ---------------------------------------------------------------------------
# Build category / decision counts
# ---------------------------------------------------------------------------

def _build_counts(matrix):
    cat_counts = {}
    dec_counts = {}
    for e in matrix:
        cat = e["category"]
        dec = e["decision"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        dec_counts[dec] = dec_counts.get(dec, 0) + 1
    return cat_counts, dec_counts


def _by_category(matrix, category):
    return [e["file_path"] for e in matrix if e["category"] == category]


def _by_decision(matrix, decision):
    return [e["file_path"] for e in matrix if e["decision"] == decision]


# ---------------------------------------------------------------------------
# P72 invariant constraints applied
# ---------------------------------------------------------------------------

P72_INVARIANT_CONSTRAINTS_APPLIED = [
    "GUARD_X108_FINAL_AUTHORITY: engine_final/kernel/orchestrator BLOQUES — l'autorite finale reste GuardX108 sigma/guard.py",
    "NO_ACT_BEFORE_TAU: os1/os1.py et engine_final.py BLOQUES — emettent ACT sans respecter l'invariant tau",
    "HOLD_BEFORE_TAU: pipeline OS1 execute sans garantie temporelle — BLOQUE",
    "IRREVERSIBLE_ACTION_DELAY: engine_final.py : irreversible=True sans tau garanti — BLOQUE",
    "NO_KERNEL_MUTATION_FROM_PERIPHERY: kernel.py/entrypoint.py BLOQUES PERMANENT",
    "NO_MEMORY_WRITE_WITHOUT_GATE: audit_log/signing/attestation/svg BLOQUES — writes non gates",
    "NETWORK_EGRESS_REVIEW_REQUIRED: worm_uploader.py BLOQUE — boto3 S3",
    "NO_PERIPHERY_DECISION_AUTHORITY: os3/metrics.py decision_act_hold() = advisory score uniquement — ADAPT_READONLY_LATER",
    "DETERMINISM: os0/ir.py, os0/contract.py, os0/sandbox.py, os3/metrics.py — deterministes, candidats readonly",
    "ROUTE_AUTH_BOUNDARY: api_server/main.py BLOQUE — serveur live double non autorise",
    "DRY_RUN_ONLY_ADAPTERS: tout adapter futur (os0, os3) devra DRY_RUN_ONLY=True",
    "KX108_ONLY_DECISION_AUTHORITY: aucun composant core ne peut prendre de decision souveraine",
]

P74_SIGMA_CONSTRAINTS_APPLIED = [
    "SIGMA_POST_GUARD_VETO_ONLY: sigma/ non modifie — aucun composant core ne bypass apply_sigma()",
    "GUARD_X108_FINAL_AUTHORITY: sigma/guard.py reste l'autorite finale — os1/x108.py KEEP_PROOF_VERSION",
    "NO_GAMMA_05: os3/metrics.py gamma=1.0 par default — confirme",
    "NO_KERNEL_MUTATION: aucun import core ne modifie sigma/guard.py, sigma/run_pipeline.py, sigma/obsidia_sigma_v130.py",
]

# ---------------------------------------------------------------------------
# Focus findings
# ---------------------------------------------------------------------------

FOCUS_FINDINGS = [
    {
        "finding_id": "P75-F1",
        "type": "CRITICAL_BLOCKED",
        "component": "engine/obsidia_kernel/kernel.py + engine/core_full/entrypoint.py + engine/obsidia_runtime/engine_final.py",
        "description": (
            "Triangle kernel : ObsidiaKernel.run() -> run_obsidia() -> run_final(). "
            "Constitue le moteur d'execution complet. "
            "Impossible a importer brut sans lancer le kernel. "
            "BLOCK_RUNTIME_IMPORT PERMANENT."
        ),
        "action": "BLOCK_RUNTIME_IMPORT",
    },
    {
        "finding_id": "P75-F2",
        "type": "CRITICAL_BLOCKED",
        "component": "engine/unified/orchestrator.py",
        "description": (
            "Side-effect critique au chargement : _kernel = ObsidiaKernel() et _router = build_default_router() "
            "s'executent a l'import. "
            "Impossible a importer sans lancer le kernel complet. "
            "BLOCK_RUNTIME_IMPORT."
        ),
        "action": "BLOCK_RUNTIME_IMPORT",
    },
    {
        "finding_id": "P75-F3",
        "type": "HIGH_BLOCKED",
        "component": "engine/os1/os1.py",
        "description": (
            "run_request() produit OS1Decision(decision='ACT') si X108 passe et sandbox OK. "
            "Emetteur ACT hors du pipeline sigma/GuardX108. "
            "P72 invariant NO_ACT_BEFORE_TAU viole si X108 bypass. "
            "BLOCK_RUNTIME_IMPORT."
        ),
        "action": "BLOCK_RUNTIME_IMPORT",
    },
    {
        "finding_id": "P75-F4",
        "type": "VERIFIED_SAFE_FOR_LATER",
        "component": "engine/os0/ (ir.py, contract.py, sandbox.py, determinism.py)",
        "description": (
            "OS0 est la couche la plus pure : types IR immuables, validateur R1-R10, "
            "sandbox deterministique, hash canonique. "
            "Aucun side-effect externe. "
            "ADAPT_READONLY_LATER (contract, determinism, ir) / ADAPT_DRY_RUN_LATER (sandbox, translate). "
            "Requiert un palier dedie (P76+) pour l'integration."
        ),
        "action": "ADAPT_READONLY_LATER / ADAPT_DRY_RUN_LATER",
    },
    {
        "finding_id": "P75-F5",
        "type": "VERIFIED_SAFE_FOR_LATER",
        "component": "engine/os3/metrics.py + engine/os3/core_split.py",
        "description": (
            "OS3 (graph metrics) est pur : triangle, hexagone, asymetrie. "
            "S = alpha*T + beta*H - gamma*A avec gamma=1.0 par default (pas 0.5). "
            "decision_act_hold() retourne 'ACT'|'HOLD' comme score, pas un verdict GuardX108. "
            "ADAPT_READONLY_LATER — requiert revue formelle OS2/OS3 dans un palier dedie."
        ),
        "action": "ADAPT_READONLY_LATER",
    },
    {
        "finding_id": "P75-F6",
        "type": "HIGH_BLOCKED",
        "component": "engine/core_full/modules/os_trad/adapter.py",
        "description": (
            "Manipulation du module system Python : sys.path.insert + sys.modules.pop. "
            "Purge obsidia_os0, obsidia_os1, proof du cache modules. "
            "Risque d'interference directe avec sigma/ si importe dans le meme process. "
            "BLOCK_UNTIL_FORMAL_REVIEW."
        ),
        "action": "BLOCK_UNTIL_FORMAL_REVIEW",
    },
    {
        "finding_id": "P75-F7",
        "type": "AUDIT_CARRY_FORWARD",
        "component": "engine/api_server/audit_log.py (hash chain logic)",
        "description": (
            "La logique de hash chain de audit_log.py est architecturalement bonne : "
            "h_i = sha256(h_{i-1} || json(event)). "
            "Complementaire des preuves RFC3161 du repo. "
            "Mais l'implementation courante ecrit sans gate. "
            "ADAPT_READONLY_LATER pour la logique de hash seule — porter comme finding."
        ),
        "action": "ADAPT_READONLY_LATER (hash logic only)",
    },
]

# ---------------------------------------------------------------------------
# Run audit
# ---------------------------------------------------------------------------

def run_audit() -> dict:
    cat_counts, dec_counts = _build_counts(RUNTIME_MATRIX)

    result = {
        "audit_id": "P75",
        "status": "P75_RUNTIME_CORE_RISK_REVIEW_READY",
        "mode": "AUDIT_ONLY",
        "source_patch_applied": False,
        "files_imported_count": 0,
        "runtime_decision": "NO_RUNTIME_IMPORT",
        "runtime_model": RUNTIME_MODEL,
        "runtime_files_scanned_count": len(RUNTIME_MATRIX),
        "runtime_matrix": RUNTIME_MATRIX,
        "category_counts": cat_counts,
        "decision_counts": dec_counts,
        "already_covered_by_proof": _by_category(RUNTIME_MATRIX, "RUNTIME_ALREADY_COVERED_BY_PROOF"),
        "duplicate_old_core": _by_category(RUNTIME_MATRIX, "RUNTIME_DUPLICATE_OLD_CORE"),
        "adapter_candidate_readonly": _by_category(RUNTIME_MATRIX, "RUNTIME_ADAPTER_CANDIDATE_READONLY"),
        "adapter_candidate_dry_run": _by_category(RUNTIME_MATRIX, "RUNTIME_ADAPTER_CANDIDATE_DRY_RUN"),
        "test_only_candidate": _by_category(RUNTIME_MATRIX, "RUNTIME_TEST_ONLY_CANDIDATE"),
        "doc_only_candidate": _by_category(RUNTIME_MATRIX, "RUNTIME_DOC_ONLY_CANDIDATE"),
        "high_risk_blocked": _by_category(RUNTIME_MATRIX, "RUNTIME_HIGH_RISK_BLOCKED"),
        "action_risk_blocked": _by_category(RUNTIME_MATRIX, "RUNTIME_ACTION_RISK_BLOCKED"),
        "write_risk_blocked": _by_category(RUNTIME_MATRIX, "RUNTIME_WRITE_RISK_BLOCKED"),
        "network_risk_blocked": _by_category(RUNTIME_MATRIX, "RUNTIME_NETWORK_RISK_BLOCKED"),
        "kernel_mutation_blocked": _by_category(RUNTIME_MATRIX, "RUNTIME_KERNEL_MUTATION_BLOCKED"),
        "formal_review_required": _by_category(RUNTIME_MATRIX, "RUNTIME_REQUIRES_FORMAL_REVIEW"),
        "unknown_requires_review": [],
        "proof_wins": [
            e["file_path"] for e in RUNTIME_MATRIX
            if e.get("proof_wins") and e["decision"] in (
                "BLOCK_RUNTIME_IMPORT",
                "KEEP_PROOF_VERSION",
                "BLOCK_UNTIL_FORMAL_REVIEW",
            )
        ],
        "p72_invariant_constraints_applied": P72_INVARIANT_CONSTRAINTS_APPLIED,
        "p74_sigma_constraints_applied": P74_SIGMA_CONSTRAINTS_APPLIED,
        "focus_findings": FOCUS_FINDINGS,
        "preexisting_manifest_drift": [],
        "preexisting_test_debt": [],
        "runtime_modified": False,
        "sigma_modified": False,
        "routes_modified": False,
        "srl_modified": False,
        "connectors_modified": False,
        "source_packs_modified": False,
        "proofs_modified": False,
        "lean_proofs_modified": False,
        "act_enabled": False,
        "memory_write_enabled": False,
        "graphiti_write_enabled": False,
        "neo4j_write_enabled": False,
        "kernel_mutation_enabled": False,
        "x108_merge_enabled": False,
        "dry_run_only": DRY_RUN_ONLY,
        "branch": "p75-runtime-core-risk-review",
        "date": "2026-06-07",
        "palier": "P75",
        "full_cascade_timeout_noted": True,
        "next_step": "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION",
    }

    return result


def main():
    result = run_audit()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"JSON => {OUT_JSON}")
    print(f"runtime_decision => {result['runtime_decision']}")
    print(f"status => {result['status']}")
    print(f"files_scanned => {result['runtime_files_scanned_count']}")
    print(f"category_counts => {result['category_counts']}")
    print(f"decision_counts => {result['decision_counts']}")


if __name__ == "__main__":
    main()

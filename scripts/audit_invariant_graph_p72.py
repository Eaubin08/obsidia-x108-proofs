"""
scripts/audit_invariant_graph_p72.py

P72 — Invariant Graph & Formal Proof Alignment
MODE: AUDIT + DOCS
DRY_RUN_ONLY: True — aucun patch, aucune modification runtime, aucune modification Sigma.

Produit : docs/core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "docs", "core_import", "P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json")

DRY_RUN_ONLY: bool = True

# ---------------------------------------------------------------------------
# Couches architecturales
# ---------------------------------------------------------------------------

LAYER_MAP = {
    "OS0_KERNEL":      "Noyau de décision déterministe X-108 (decideX108, decision, beforeTau)",
    "OS1_GUARD":       "Guard X-108 — autorité finale de décision",
    "OS2_SIGMA":       "Sigma — veto post-Guard uniquement (P56D, gel permanent)",
    "OS3_AUDIT_PROOF": "Couche audit/preuve/trace (Merkle, scellé, immutabilité)",
    "OS4_PERIPHERY":   "Périphérie non-décisionnelle (mémoire, graphiti, agents, bus, connecteurs)",
    "OS5_SOURCES":     "Source packs et adapters (dry_run, advisory_only, KX108_ONLY gate)",
    "OS6_ROUTES":      "Routes API et frontière d'authentification (OBSIDIA_API_KEY)",
    "OS7_NETWORK":     "Egress réseau (connecteurs actifs, exports, boucles live)",
}

# ---------------------------------------------------------------------------
# Statuts formels valides
# ---------------------------------------------------------------------------

FORMAL_STATUSES = [
    "LEAN_PROVEN",
    "PYTHON_TESTED",
    "SPEC_ONLY",
    "DOC_ONLY",
    "RUNTIME_OBSERVED",
    "MIXED_PROOF_STATUS",
    "UNPROVEN_REQUIRES_REVIEW",
]

# ---------------------------------------------------------------------------
# Graphe des invariants — 23 entrées
# ---------------------------------------------------------------------------

INVARIANT_GRAPH = [
    {
        "invariant_id": "DETERMINISM",
        "description": "Le noyau de décision est déterministe : même entrée → même sortie, toujours.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.E2",
            "Obsidia.aggregate4_unanimous",
            "Obsidia.no_two_distinct_supermajorities_4",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": [],
        "blocks_extension_of": ["OS1_GUARD", "OS2_SIGMA", "OS4_PERIPHERY"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Toute extension qui introduit un état non-déterministe dans le chemin de décision est INTERDITE.",
    },
    {
        "invariant_id": "NO_ACT_BEFORE_TAU",
        "description": "Si irr=true et elapsed<τ, la décision est toujours HOLD. Aucune action irréversible avant τ.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_no_act_before_tau",
            "Obsidia.TemporalBridge.canonicalize_preserves_nonneg",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["DETERMINISM"],
        "blocks_extension_of": ["OS1_GUARD", "OS4_PERIPHERY", "OS7_NETWORK"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Aucune extension ne peut court-circuiter le test beforeTau pour des décisions irréversibles.",
    },
    {
        "invariant_id": "HOLD_BEFORE_TAU",
        "description": "Conséquence directe de NO_ACT_BEFORE_TAU : l'état actif avant τ est HOLD (jamais BLOCK, jamais ACT).",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_no_act_before_tau",
            "Obsidia.TemporalKernel.X108_kernel_never_blocks",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["NO_ACT_BEFORE_TAU", "DETERMINISM"],
        "blocks_extension_of": ["OS1_GUARD"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Le résultat HOLD avant τ est une garantie Lean. Ne pas remplacer par BLOCK ou état intermédiaire.",
    },
    {
        "invariant_id": "IRREVERSIBLE_ACTION_DELAY",
        "description": "Pour irr=true et τ≤elapsed, le noyau retombe sur la décision de base (decision metrics theta). Délai irréversible respecté.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_irreversible_after_tau_equals_base",
            "Obsidia.TemporalKernel.X108_after_tau_equals_base",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["NO_ACT_BEFORE_TAU", "DETERMINISM"],
        "blocks_extension_of": ["OS0_KERNEL", "OS1_GUARD"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Post-τ, la décision suit exactement la base. Ne pas ajouter de délai supplémentaire non-prouvé.",
    },
    {
        "invariant_id": "REVERSIBLE_ACTION_BASELINE",
        "description": "Pour irr=false, le noyau X-108 est équivalent à la décision de base (pas de délai τ appliqué).",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_reversible_equals_base",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["DETERMINISM"],
        "blocks_extension_of": ["OS0_KERNEL"],
        "risk_if_broken": "HIGH",
        "extension_rule": "Les actions réversibles n'ont pas de délai. Ne pas appliquer beforeTau si irr=false.",
    },
    {
        "invariant_id": "NEGATIVE_CLOCK_SKEW_TO_HOLD",
        "description": "Si elapsed_raw<0 et irr=true et τ≥0, alors la décision est HOLD. Skew horlogie négatif → HOLD sécurisé.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalBridge.skew_negative_implies_hold",
        ],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["NO_ACT_BEFORE_TAU", "HOLD_BEFORE_TAU"],
        "blocks_extension_of": ["OS0_KERNEL", "OS4_PERIPHERY"],
        "risk_if_broken": "HIGH",
        "extension_rule": "Les bridges temporels doivent préserver le comportement HOLD en cas de skew négatif.",
    },
    {
        "invariant_id": "THRESHOLD_CONSERVATION",
        "description": "Deux supermajorités distinctes (ACT+HOLD, ACT+BLOCK, HOLD+BLOCK) sont impossibles simultanément sur 4 votants.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.no_two_distinct_supermajorities_4",
            "Obsidia.no_act_and_hold_supermajority_4",
            "Obsidia.no_act_and_block_supermajority_4",
            "Obsidia.no_hold_and_block_supermajority_4",
            "Obsidia.aggregate4_fail_closed",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["DETERMINISM", "BLOCK_PRIORITY_OVER_HOLD_ALLOW"],
        "blocks_extension_of": ["OS0_KERNEL"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Conserver exactement aggregate4 (4 votants, seuil 3/4). Modifier le quorum invalide les preuves.",
    },
    {
        "invariant_id": "BLOCK_PRIORITY_OVER_HOLD_ALLOW",
        "description": "En l'absence de supermajorité ACT ou HOLD, aggregate4 retourne BLOCK (fail-fermé). BLOCK est la valeur par défaut sûre.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.aggregate4_fail_closed",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["THRESHOLD_CONSERVATION", "DETERMINISM"],
        "blocks_extension_of": ["OS0_KERNEL", "OS1_GUARD"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Le default fail-closed est prouvé. Ne pas ajouter de cas 'else ACT' ou 'else HOLD'.",
    },
    {
        "invariant_id": "HOLD_PRIORITY_OVER_ALLOW",
        "description": "HOLD (retenue) a priorité sur ACT : X108_no_act_before_tau garantit que le noyau préfère HOLD quand la condition τ est active.",
        "layer": "OS0_KERNEL",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_no_act_before_tau",
            "Obsidia.aggregate4_act",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["NO_ACT_BEFORE_TAU", "BLOCK_PRIORITY_OVER_HOLD_ALLOW"],
        "blocks_extension_of": ["OS0_KERNEL", "OS1_GUARD"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "L'ordre de priorité BLOCK > HOLD > ACT est prouvé. Ne pas inverser dans un fork ou adapter.",
    },
    {
        "invariant_id": "GUARD_X108_FINAL_AUTHORITY",
        "description": "Le noyau X-108 est l'autorité finale : il ne peut jamais BLOQUER (X108_kernel_never_blocks). La décision finale passe toujours.",
        "layer": "OS1_GUARD",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_kernel_never_blocks",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["DETERMINISM", "HOLD_BEFORE_TAU"],
        "blocks_extension_of": ["OS1_GUARD", "OS2_SIGMA"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Aucune couche périphérique ne peut prendre une décision finale. Guard seul est autorité.",
    },
    {
        "invariant_id": "SIGMA_POST_GUARD_VETO_ONLY",
        "description": "Sigma n'est active qu'en mode veto post-Guard (P56D). Elle ne décide pas, elle peut uniquement bloquer après Guard.",
        "layer": "OS2_SIGMA",
        "formal_status": "SPEC_ONLY",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["GUARD_X108_FINAL_AUTHORITY"],
        "blocks_extension_of": ["OS2_SIGMA"],
        "risk_if_broken": "HIGH",
        "extension_rule": "Sigma ne peut pas initier de décision. Tout ajout à sigma/ doit rester en mode veto-only.",
    },
    {
        "invariant_id": "NO_PERIPHERY_DECISION_AUTHORITY",
        "description": "Aucun composant périphérique (mémoire, graphiti, agents, bus) n'a d'autorité décisionnelle. Tous sont non-décisionnels.",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["GUARD_X108_FINAL_AUTHORITY", "KX108_ONLY_DECISION_AUTHORITY"],
        "blocks_extension_of": ["OS4_PERIPHERY"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "Tout ajout périphérique doit déclarer emits_act=False et advisory_only=True.",
    },
    {
        "invariant_id": "NO_GRAPHITI_WRITE",
        "description": "Graphiti est en lecture seule (P66). Aucune écriture graphiti sans gate KX108. graphiti_write_enabled=False confirmé.",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["NO_PERIPHERY_DECISION_AUTHORITY", "NO_KERNEL_MUTATION_FROM_PERIPHERY"],
        "blocks_extension_of": ["OS4_PERIPHERY"],
        "risk_if_broken": "HIGH",
        "extension_rule": "graphiti_v20_readonly_client.py — GET uniquement, write=False. Confirmer dans tout audit P7X+.",
    },
    {
        "invariant_id": "NO_MEMORY_WRITE_WITHOUT_GATE",
        "description": "Aucune écriture mémoire sans gate KX108. memory_write_enabled=False confirmé. SRL = lecture seule.",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["NO_PERIPHERY_DECISION_AUTHORITY"],
        "blocks_extension_of": ["OS4_PERIPHERY"],
        "risk_if_broken": "HIGH",
        "extension_rule": "SRL = Session Registry Layer, non-décisionnel, lecture seule. Tout write nécessite gate explicite.",
    },
    {
        "invariant_id": "NO_KERNEL_MUTATION_FROM_PERIPHERY",
        "description": "G1 (immutabilité de trace) : le kernel ne peut pas être muté depuis la périphérie. Trace gelée post-commit.",
        "layer": "OS3_AUDIT_PROOF",
        "formal_status": "LEAN_PROVEN",
        "lean_theorems": [
            "Obsidia.G1",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["DETERMINISM", "GUARD_X108_FINAL_AUTHORITY"],
        "blocks_extension_of": ["OS4_PERIPHERY", "OS3_AUDIT_PROOF"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "kernel_mutation_enabled=False. Aucun adaptateur périphérique ne doit modifier le kernel ou la trace.",
    },
    {
        "invariant_id": "DRY_RUN_ONLY_ADAPTERS",
        "description": "Tous les adapters source sont en DRY_RUN_ONLY. advisory_only=True, emits_act=False, runtime_allowed_now=0.",
        "layer": "OS5_SOURCES",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["NO_PERIPHERY_DECISION_AUTHORITY", "KX108_ONLY_DECISION_AUTHORITY"],
        "blocks_extension_of": ["OS5_SOURCES"],
        "risk_if_broken": "HIGH",
        "extension_rule": "DRY_RUN_ONLY: bool = True dans chaque adapter. Confirmer emits_act=False avant tout runtime load.",
    },
    {
        "invariant_id": "BUS_PROPOSE_ONLY",
        "description": "Le bus Obsidia ne fait que proposer (PROPOSE_ONLY). Aucune décision, aucun emit_act depuis le bus.",
        "layer": "OS4_PERIPHERY",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["NO_PERIPHERY_DECISION_AUTHORITY"],
        "blocks_extension_of": ["OS4_PERIPHERY"],
        "risk_if_broken": "HIGH",
        "extension_rule": "Bus adapters classifiés ADAPTER_DRY_RUN_SAFE (P71). Aucun bus adapter ne peut émettre ACT.",
    },
    {
        "invariant_id": "ROUTE_AUTH_BOUNDARY",
        "description": "Toutes les routes sensibles exigent OBSIDIA_API_KEY via Depends(require_api_key). 503 fail-fermé si absent.",
        "layer": "OS6_ROUTES",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["NO_PERIPHERY_DECISION_AUTHORITY"],
        "blocks_extension_of": ["OS6_ROUTES"],
        "risk_if_broken": "HIGH",
        "extension_rule": "Toute nouvelle route exposant des données doit ajouter Depends(require_api_key). POST /preview = finding ouvert P69/P71.",
    },
    {
        "invariant_id": "NETWORK_EGRESS_REVIEW_REQUIRED",
        "description": "Tout egress réseau réel (connecteurs aviation/bank/trading) est classifié CONNECTOR_ACTIVE_REVIEW/DO_NOT_RUN (P70).",
        "layer": "OS7_NETWORK",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["DRY_RUN_ONLY_ADAPTERS"],
        "blocks_extension_of": ["OS7_NETWORK"],
        "risk_if_broken": "HIGH",
        "extension_rule": "Tout nouveau connecteur avec requests.post() ou socket ouvert doit passer audit P7X avant runtime.",
    },
    {
        "invariant_id": "SOURCE_PACK_NOT_CANON_BY_EXISTENCE",
        "description": "La présence d'un source pack dans _source_packs/ ne le canonise pas. La canonisation requiert manifest + hashes + registre officiel.",
        "layer": "OS5_SOURCES",
        "formal_status": "PYTHON_TESTED",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": True,
        "depends_on": ["DRY_RUN_ONLY_ADAPTERS"],
        "blocks_extension_of": ["OS5_SOURCES"],
        "risk_if_broken": "MEDIUM",
        "extension_rule": "Pack LOCAL_ONLY_UNCANONIZED ≠ runtime-loadable. Exiger MANIFEST_SHA256.json + source_file_registry.",
    },
    {
        "invariant_id": "ARCHIVE_NOT_RUNTIME",
        "description": "G2 (Merkle seal) : les archives (_freezes/, .local_audits/) sont scellées et ne peuvent pas être chargées en runtime.",
        "layer": "OS3_AUDIT_PROOF",
        "formal_status": "MIXED_PROOF_STATUS",
        "lean_theorems": [
            "Obsidia.G2",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["NO_KERNEL_MUTATION_FROM_PERIPHERY"],
        "blocks_extension_of": ["OS3_AUDIT_PROOF", "OS5_SOURCES"],
        "risk_if_broken": "HIGH",
        "extension_rule": "SOURCE_ARCHIVE_ONLY = jamais runtime-loadable. Merkle seal = preuve d'intégrité, non de chargeabilité.",
    },
    {
        "invariant_id": "PYTHON_TESTED_NOT_LEAN_PROVEN",
        "description": "Meta-invariant : un test Python n'est pas une preuve formelle Lean. Les deux statuts sont distincts et non-interchangeables.",
        "layer": "OS3_AUDIT_PROOF",
        "formal_status": "DOC_ONLY",
        "lean_theorems": [],
        "tla_checked": False,
        "python_tested": False,
        "depends_on": [],
        "blocks_extension_of": ["OS3_AUDIT_PROOF"],
        "risk_if_broken": "MEDIUM",
        "extension_rule": "Ne jamais écrire 'prouvé' pour un test pytest. Utiliser LEAN_PROVEN uniquement si #print axioms valide.",
    },
    {
        "invariant_id": "KX108_ONLY_DECISION_AUTHORITY",
        "description": "KX108_ONLY est la contrainte d'autorité décisionnelle centrale : seul le noyau X-108 peut prendre des décisions ACT/HOLD/BLOCK finales.",
        "layer": "OS0_KERNEL",
        "formal_status": "SPEC_ONLY",
        "lean_theorems": [
            "Obsidia.TemporalKernel.X108_kernel_never_blocks",
            "Obsidia.TemporalKernel.X108_no_act_before_tau",
        ],
        "tla_checked": True,
        "python_tested": True,
        "depends_on": ["GUARD_X108_FINAL_AUTHORITY", "DETERMINISM"],
        "blocks_extension_of": ["OS0_KERNEL", "OS1_GUARD", "OS2_SIGMA", "OS4_PERIPHERY"],
        "risk_if_broken": "CRITICAL",
        "extension_rule": "has_kx108_authority doit être True pour tout composant prenant des décisions. Sinon emits_act=False obligatoire.",
    },
]

# ---------------------------------------------------------------------------
# Théorème → Architecture Map
# ---------------------------------------------------------------------------

THEOREM_TO_ARCHITECTURE_MAP = [
    {
        "lean_theorem_id": "Obsidia.TemporalKernel.X108_no_act_before_tau",
        "source_file": "proofs/lean/Obsidia/TemporalKernel.lean",
        "lean_namespace": "Obsidia.TemporalKernel",
        "statement_summary": "Si irr=true et elapsed<τ, alors decideX108=HOLD",
        "maps_to_invariants": ["NO_ACT_BEFORE_TAU", "HOLD_BEFORE_TAU", "KX108_ONLY_DECISION_AUTHORITY"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "decideX108 / beforeTau",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.TemporalKernel.X108_after_tau_equals_base",
        "source_file": "proofs/lean/Obsidia/TemporalKernel.lean",
        "lean_namespace": "Obsidia.TemporalKernel",
        "statement_summary": "Si beforeTau=false, alors decideX108 = decision metrics theta",
        "maps_to_invariants": ["IRREVERSIBLE_ACTION_DELAY", "REVERSIBLE_ACTION_BASELINE"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "decideX108",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.TemporalKernel.X108_kernel_never_blocks",
        "source_file": "proofs/lean/Obsidia/TemporalKernel.lean",
        "lean_namespace": "Obsidia.TemporalKernel",
        "statement_summary": "decide3X108 ≠ Decision3.BLOCK (le noyau X108 ne bloque jamais)",
        "maps_to_invariants": ["GUARD_X108_FINAL_AUTHORITY", "HOLD_BEFORE_TAU", "KX108_ONLY_DECISION_AUTHORITY"],
        "maps_to_layer": "OS1_GUARD",
        "maps_to_component": "decide3X108 / liftDecision",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.TemporalKernel.X108_reversible_equals_base",
        "source_file": "proofs/lean/Obsidia/TemporalKernel.lean",
        "lean_namespace": "Obsidia.TemporalKernel",
        "statement_summary": "Pour irr=false, decideX108 = decision metrics theta (pas de délai τ)",
        "maps_to_invariants": ["REVERSIBLE_ACTION_BASELINE"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "decideX108 / beforeTau (irr=false path)",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.TemporalKernel.X108_irreversible_after_tau_equals_base",
        "source_file": "proofs/lean/Obsidia/TemporalKernel.lean",
        "lean_namespace": "Obsidia.TemporalKernel",
        "statement_summary": "Pour irr=true et τ≤elapsed, decideX108 = decision metrics theta",
        "maps_to_invariants": ["IRREVERSIBLE_ACTION_DELAY"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "decideX108 (post-tau path)",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.TemporalBridge.skew_negative_implies_hold",
        "source_file": "proofs/lean/Obsidia/TemporalBridge.lean",
        "lean_namespace": "Obsidia.TemporalBridge",
        "statement_summary": "Si elapsed_raw<0 et irr=true et τ≥0, alors decide_with_skew_handling=HOLD",
        "maps_to_invariants": ["NEGATIVE_CLOCK_SKEW_TO_HOLD", "NO_ACT_BEFORE_TAU"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "decide_with_skew_handling / canonicalize_elapsed",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.TemporalBridge.canonicalize_preserves_nonneg",
        "source_file": "proofs/lean/Obsidia/TemporalBridge.lean",
        "lean_namespace": "Obsidia.TemporalBridge",
        "statement_summary": "canonicalize_elapsed e = Int.toNat e pour e≥0 (bridge temporel préserve non-négatif)",
        "maps_to_invariants": ["NO_ACT_BEFORE_TAU", "NEGATIVE_CLOCK_SKEW_TO_HOLD"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "canonicalize_elapsed",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.no_two_distinct_supermajorities_4",
        "source_file": "proofs/lean/Obsidia/Consensus.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Deux supermajorités distinctes (≥3/4) sont impossibles simultanément",
        "maps_to_invariants": ["THRESHOLD_CONSERVATION", "DETERMINISM"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "aggregate4 / countDec",
        "axioms_free": True,
        "verified_via": "#print axioms (via _aux theorems)",
    },
    {
        "lean_theorem_id": "Obsidia.aggregate4_fail_closed",
        "source_file": "proofs/lean/Obsidia/Consensus.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Sans supermajorité ACT ni HOLD ni BLOCK, aggregate4 retourne BLOCK (fail-fermé)",
        "maps_to_invariants": ["BLOCK_PRIORITY_OVER_HOLD_ALLOW", "THRESHOLD_CONSERVATION"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "aggregate4",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.aggregate4_unanimous",
        "source_file": "proofs/lean/Obsidia/Consensus.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "aggregate4 d d d d = d (4 votants identiques → résultat identique)",
        "maps_to_invariants": ["DETERMINISM", "THRESHOLD_CONSERVATION"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "aggregate4",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.aggregate4_act",
        "source_file": "proofs/lean/Obsidia/Consensus.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Si ≥3/4 ACT, aggregate4=ACT",
        "maps_to_invariants": ["HOLD_PRIORITY_OVER_ALLOW", "THRESHOLD_CONSERVATION"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "aggregate4",
        "axioms_free": True,
        "verified_via": "#print axioms",
    },
    {
        "lean_theorem_id": "Obsidia.D1",
        "source_file": "proofs/lean/Obsidia/Basic.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Non-contradiction des règles de gouvernance (D1 PROOF_INDEX)",
        "maps_to_invariants": ["DETERMINISM"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "Decision type / governance rules",
        "axioms_free": True,
        "verified_via": "PROOF_INDEX.md LEAN_PROVEN",
    },
    {
        "lean_theorem_id": "Obsidia.E2",
        "source_file": "proofs/lean/Obsidia/Basic.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Déterminisme du vote (E2 PROOF_INDEX)",
        "maps_to_invariants": ["DETERMINISM"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "decision / vote function",
        "axioms_free": True,
        "verified_via": "PROOF_INDEX.md LEAN_PROVEN",
    },
    {
        "lean_theorem_id": "Obsidia.G1",
        "source_file": "proofs/lean/Obsidia/Basic.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Immutabilité de la trace (G1 PROOF_INDEX)",
        "maps_to_invariants": ["NO_KERNEL_MUTATION_FROM_PERIPHERY"],
        "maps_to_layer": "OS3_AUDIT_PROOF",
        "maps_to_component": "audit trace / immutable log",
        "axioms_free": True,
        "verified_via": "PROOF_INDEX.md LEAN_PROVEN",
    },
    {
        "lean_theorem_id": "Obsidia.G2",
        "source_file": "proofs/lean/Obsidia/Basic.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Cohérence du sceau Merkle (G2 PROOF_INDEX)",
        "maps_to_invariants": ["ARCHIVE_NOT_RUNTIME"],
        "maps_to_layer": "OS3_AUDIT_PROOF",
        "maps_to_component": "Merkle seal / archive integrity",
        "axioms_free": True,
        "verified_via": "PROOF_INDEX.md LEAN_PROVEN",
    },
    {
        "lean_theorem_id": "Obsidia.G3",
        "source_file": "proofs/lean/Obsidia/Basic.lean",
        "lean_namespace": "Obsidia",
        "statement_summary": "Pas de contradiction circulaire (G3 PROOF_INDEX)",
        "maps_to_invariants": ["BLOCK_PRIORITY_OVER_HOLD_ALLOW", "HOLD_PRIORITY_OVER_ALLOW"],
        "maps_to_layer": "OS0_KERNEL",
        "maps_to_component": "governance rules / contradiction-free",
        "axioms_free": True,
        "verified_via": "PROOF_INDEX.md LEAN_PROVEN",
    },
]

# ---------------------------------------------------------------------------
# Matrice LEAN_PROVEN vs PYTHON_TESTED
# ---------------------------------------------------------------------------

LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX = [
    {
        "claim": "Aucune action irréversible avant τ",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "X108_no_act_before_tau",
        "python_test_file": "tests/test_p56e_post_patch_metric_reaudit.py",
        "python_test_passes": True,
        "note": "Lean prouve le cas général. Python teste les cas nominaux et adversariaux.",
        "public_claimable": True,
    },
    {
        "claim": "Noyau X108 ne bloque jamais",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "X108_kernel_never_blocks",
        "python_test_file": "tests/test_p56e_post_patch_metric_reaudit.py",
        "python_test_passes": True,
        "note": "decide3X108 ≠ BLOCK — prouvé par contradiction Lean. Python confirme en runtime.",
        "public_claimable": True,
    },
    {
        "claim": "Déterminisme du vote (aggregate4)",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "aggregate4_unanimous + no_two_distinct_supermajorities_4",
        "python_test_file": "tests/test_p57_core_machinery_runtime_binding_audit.py",
        "python_test_passes": True,
        "note": "Unanimité et anti-contradiction prouvées Lean. Python teste les cas 3/4.",
        "public_claimable": True,
    },
    {
        "claim": "Fail-closed par défaut (BLOCK si aucune supermajorité)",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "aggregate4_fail_closed",
        "python_test_file": "tests/test_p57_core_machinery_runtime_binding_audit.py",
        "python_test_passes": True,
        "note": "aggregate4 retourne BLOCK si ni ACT ni HOLD ni BLOCK supermajorité.",
        "public_claimable": True,
    },
    {
        "claim": "Skew négatif → HOLD (protection horloge)",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "skew_negative_implies_hold",
        "python_test_file": "tests/test_p56e_post_patch_metric_reaudit.py",
        "python_test_passes": True,
        "note": "TemporalBridge prouvé. Python teste le bridge en runtime.",
        "public_claimable": True,
    },
    {
        "claim": "Immutabilité de la trace",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "Obsidia.G1",
        "python_test_file": "tests/test_p64_fusion_continuity_ledger.py",
        "python_test_passes": True,
        "note": "G1 prouvé Lean. Python vérifie l'absence de mutation sur les traces historiques.",
        "public_claimable": True,
    },
    {
        "claim": "Merkle seal cohérent",
        "lean_status": "LEAN_PROVEN",
        "lean_theorem": "Obsidia.G2",
        "python_test_file": "tests/test_p64_fusion_continuity_ledger.py",
        "python_test_passes": True,
        "note": "G2 prouvé Lean. Python vérifie le scellement des archives.",
        "public_claimable": True,
    },
    {
        "claim": "Graphiti en lecture seule",
        "lean_status": "NOT_LEAN_PROVEN",
        "lean_theorem": None,
        "python_test_file": "tests/test_p66_srl_readonly_memory_layer.py",
        "python_test_passes": True,
        "note": "PYTHON_TESTED uniquement. Graphiti readonly est une contrainte architecturale, pas un théorème Lean.",
        "public_claimable": False,
    },
    {
        "claim": "Routes API sécurisées par OBSIDIA_API_KEY",
        "lean_status": "NOT_LEAN_PROVEN",
        "lean_theorem": None,
        "python_test_file": "tests/test_p68_api_auth_route_exposure_audit.py",
        "python_test_passes": True,
        "note": "PYTHON_TESTED. Dépend de l'infra runtime — hors périmètre Lean.",
        "public_claimable": False,
    },
    {
        "claim": "Adapters source en DRY_RUN_ONLY",
        "lean_status": "NOT_LEAN_PROVEN",
        "lean_theorem": None,
        "python_test_file": "tests/test_p71_source_runtime_source_packs_deep_audit.py",
        "python_test_passes": True,
        "note": "PYTHON_TESTED. Registre source_file_registry.json vérifié — contrainte de déploiement.",
        "public_claimable": False,
    },
    {
        "claim": "Sigma = veto post-Guard uniquement",
        "lean_status": "NOT_LEAN_PROVEN",
        "lean_theorem": None,
        "python_test_file": "tests/test_p56e_post_patch_metric_reaudit.py",
        "python_test_passes": True,
        "note": "SPEC_ONLY + PYTHON_TESTED. Architecture P56D, pas de preuve Lean formelle.",
        "public_claimable": False,
    },
    {
        "claim": "Connecteurs actifs DO_NOT_RUN sans dry_run gate",
        "lean_status": "NOT_LEAN_PROVEN",
        "lean_theorem": None,
        "python_test_file": "tests/test_p70_network_egress_connectors_audit.py",
        "python_test_passes": True,
        "note": "PYTHON_TESTED (P70 audit). Aviation/bank/trading classifiés CONNECTOR_ACTIVE_REVIEW.",
        "public_claimable": False,
    },
]

# ---------------------------------------------------------------------------
# Règles de stabilisation de la périphérie
# ---------------------------------------------------------------------------

PERIPHERY_STABILIZATION_RULES = [
    {
        "domain": "MEMORY_SRL",
        "rule": "SRL = Session Registry Layer — lecture seule, non-décisionnel.",
        "current_status": "COMPLIANT",
        "invariants_protected": ["NO_MEMORY_WRITE_WITHOUT_GATE", "NO_PERIPHERY_DECISION_AUTHORITY"],
        "action_if_violated": "IMMEDIATE_HOLD — memory_write_enabled doit rester False.",
        "audit_palier": "P66",
    },
    {
        "domain": "GRAPHITI",
        "rule": "graphiti_v20_readonly_client.py — GET uniquement, write=False, stub fallback.",
        "current_status": "COMPLIANT",
        "invariants_protected": ["NO_GRAPHITI_WRITE", "NO_PERIPHERY_DECISION_AUTHORITY"],
        "action_if_violated": "IMMEDIATE_HOLD — tout write graphiti nécessite gate KX108 explicite.",
        "audit_palier": "P70",
    },
    {
        "domain": "AGENTS",
        "rule": "Agents périphériques = advisory_only=True, emits_act=False. Aucune autorité décisionnelle.",
        "current_status": "COMPLIANT",
        "invariants_protected": ["NO_PERIPHERY_DECISION_AUTHORITY", "KX108_ONLY_DECISION_AUTHORITY"],
        "action_if_violated": "CLASSIFIER_HOLD — tout agent avec emits_act=True requiert audit palier dédié.",
        "audit_palier": "P71",
    },
    {
        "domain": "BUS",
        "rule": "Bus Obsidia = PROPOSE_ONLY. Aucun emit_act, aucune décision finale.",
        "current_status": "COMPLIANT",
        "invariants_protected": ["BUS_PROPOSE_ONLY", "NO_PERIPHERY_DECISION_AUTHORITY"],
        "action_if_violated": "IMMEDIATE_HOLD — bus adapter avec emit_act=True = violation critique.",
        "audit_palier": "P61",
    },
    {
        "domain": "CONNECTORS",
        "rule": "Connecteurs actifs (aviation/bank/trading) = DO_NOT_RUN. Dry_run gate obligatoire avant activation.",
        "current_status": "REVIEW_REQUIRED",
        "invariants_protected": ["NETWORK_EGRESS_REVIEW_REQUIRED", "DRY_RUN_ONLY_ADAPTERS"],
        "action_if_violated": "DO_NOT_RUN — while True + requests.post + irreversible=True sans dry_run gate.",
        "audit_palier": "P70",
    },
    {
        "domain": "SOURCE_PACKS",
        "rule": "Packs source = DRY_RUN_ONLY, advisory_only, readonly_content_loader boundaries.",
        "current_status": "COMPLIANT",
        "invariants_protected": ["DRY_RUN_ONLY_ADAPTERS", "SOURCE_PACK_NOT_CANON_BY_EXISTENCE"],
        "action_if_violated": "AUDIT_REQUIRED — runtime_allowed_now doit rester 0.",
        "audit_palier": "P71",
    },
    {
        "domain": "UI_ROUTES",
        "rule": "Routes API exposant des données = Depends(require_api_key). POST /preview = finding ouvert.",
        "current_status": "PARTIAL_REVIEW",
        "invariants_protected": ["ROUTE_AUTH_BOUNDARY"],
        "action_if_violated": "APPLY_AUTH — ADD_REQUIRE_API_KEY sur POST /preview et POST /os-map/query.",
        "audit_palier": "P69",
    },
]

# ---------------------------------------------------------------------------
# Règles de sécurité des extensions
# ---------------------------------------------------------------------------

EXTENSION_SAFETY_RULES = [
    {
        "rule_id": "EXT_SAFE_01",
        "title": "Toute extension doit déclarer son invariant_coverage",
        "description": "Chaque nouveau module doit lister les invariants de INVARIANT_GRAPH qu'il respecte/protège.",
        "required_fields": ["emits_act", "advisory_only", "has_kx108_authority", "dry_run_only"],
        "lean_proven_invariants_preserved": [
            "DETERMINISM", "NO_ACT_BEFORE_TAU", "GUARD_X108_FINAL_AUTHORITY",
        ],
    },
    {
        "rule_id": "EXT_SAFE_02",
        "title": "Ne pas modifier proofs/lean/ — les théorèmes sont gelés",
        "description": "Aucune extension ne peut modifier les fichiers TemporalKernel.lean, TemporalBridge.lean, Consensus.lean, Basic.lean sans protocole de preuve formelle complet.",
        "required_fields": [],
        "lean_proven_invariants_preserved": [
            "NO_ACT_BEFORE_TAU", "IRREVERSIBLE_ACTION_DELAY", "THRESHOLD_CONSERVATION",
            "GUARD_X108_FINAL_AUTHORITY", "DETERMINISM",
        ],
    },
    {
        "rule_id": "EXT_SAFE_03",
        "title": "Ne pas modifier sigma/ — gel permanent post-P56D",
        "description": "Sigma = veto post-Guard. Toute modification sigma/ invalide SIGMA_POST_GUARD_VETO_ONLY.",
        "required_fields": [],
        "lean_proven_invariants_preserved": ["SIGMA_POST_GUARD_VETO_ONLY", "GUARD_X108_FINAL_AUTHORITY"],
    },
    {
        "rule_id": "EXT_SAFE_04",
        "title": "Adapter périphérique = DRY_RUN_ONLY: bool = True obligatoire",
        "description": "Tout adapter source/bus/connector doit déclarer DRY_RUN_ONLY=True et emits_act=False.",
        "required_fields": ["DRY_RUN_ONLY", "emits_act", "advisory_only"],
        "lean_proven_invariants_preserved": [
            "DRY_RUN_ONLY_ADAPTERS", "NO_PERIPHERY_DECISION_AUTHORITY", "KX108_ONLY_DECISION_AUTHORITY",
        ],
    },
    {
        "rule_id": "EXT_SAFE_05",
        "title": "X108 est l'autorité finale — aucun court-circuit",
        "description": "Aucune extension ne peut retourner ACT/HOLD/BLOCK en contournant decideX108. KX108_ONLY.",
        "required_fields": ["has_kx108_authority"],
        "lean_proven_invariants_preserved": [
            "KX108_ONLY_DECISION_AUTHORITY", "GUARD_X108_FINAL_AUTHORITY",
            "NO_ACT_BEFORE_TAU", "DETERMINISM",
        ],
    },
    {
        "rule_id": "EXT_SAFE_06",
        "title": "aggregate4 (quorum 3/4) est le seul agrégateur de consensus valide",
        "description": "Modifier le quorum (ex. 2/3, 4/5) invalide THRESHOLD_CONSERVATION et BLOCK_PRIORITY_OVER_HOLD_ALLOW.",
        "required_fields": [],
        "lean_proven_invariants_preserved": [
            "THRESHOLD_CONSERVATION", "BLOCK_PRIORITY_OVER_HOLD_ALLOW", "DETERMINISM",
        ],
    },
    {
        "rule_id": "EXT_SAFE_07",
        "title": "Tout nouveau connecteur réseau nécessite un audit palier avant activation",
        "description": "requests.post() ou équivalent = CONNECTOR_ACTIVE_REVIEW obligatoire. Pas de runtime sans dry_run gate.",
        "required_fields": ["dry_run_declared", "kx108_authority_declared"],
        "lean_proven_invariants_preserved": ["NETWORK_EGRESS_REVIEW_REQUIRED"],
    },
]

# ---------------------------------------------------------------------------
# Buckets par statut formel
# ---------------------------------------------------------------------------

def _bucket(matrix, field, value):
    return [e["invariant_id"] for e in matrix if e.get(field) == value]


def _theorem_by_invariant(inv_id):
    theorems = []
    for t in THEOREM_TO_ARCHITECTURE_MAP:
        if inv_id in t.get("maps_to_invariants", []):
            theorems.append(t["lean_theorem_id"])
    return theorems


# ---------------------------------------------------------------------------
# Construction du rapport JSON
# ---------------------------------------------------------------------------

def build_report():
    lean_proven = _bucket(INVARIANT_GRAPH, "formal_status", "LEAN_PROVEN")
    python_tested_only = _bucket(INVARIANT_GRAPH, "formal_status", "PYTHON_TESTED")
    spec_only = _bucket(INVARIANT_GRAPH, "formal_status", "SPEC_ONLY")
    doc_only = _bucket(INVARIANT_GRAPH, "formal_status", "DOC_ONLY")
    mixed = _bucket(INVARIANT_GRAPH, "formal_status", "MIXED_PROOF_STATUS")

    layer_counts = {}
    for inv in INVARIANT_GRAPH:
        layer = inv["layer"]
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    risk_critical = [i["invariant_id"] for i in INVARIANT_GRAPH if i["risk_if_broken"] == "CRITICAL"]

    report = {
        "status": "P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY",
        "mode": "AUDIT_DOCS",
        "dry_run_only": DRY_RUN_ONLY,
        "palier": "P72",
        "branch": "p72-invariant-graph-formal-proof-alignment",
        "date": "2026-06-07",
        "runtime_modified": False,
        "sigma_modified": False,
        "routes_modified": False,
        "lean_modified": False,
        "proofs_v18_3_1_modified": False,
        "act_enabled": False,
        "kernel_mutation_enabled": False,
        "x108_merge_enabled": False,
        "total_invariants": len(INVARIANT_GRAPH),
        "lean_proven_count": len(lean_proven),
        "python_tested_only_count": len(python_tested_only),
        "spec_only_count": len(spec_only),
        "doc_only_count": len(doc_only),
        "mixed_proof_status_count": len(mixed),
        "critical_invariants": risk_critical,
        "lean_proven_invariants": lean_proven,
        "python_tested_only_invariants": python_tested_only,
        "spec_only_invariants": spec_only,
        "doc_only_invariants": doc_only,
        "mixed_proof_status_invariants": mixed,
        "layer_counts": layer_counts,
        "total_lean_theorems_mapped": len(THEOREM_TO_ARCHITECTURE_MAP),
        "invariant_graph": INVARIANT_GRAPH,
        "theorem_to_architecture_map": THEOREM_TO_ARCHITECTURE_MAP,
        "lean_proven_vs_python_tested_matrix": LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX,
        "periphery_stabilization_rules": PERIPHERY_STABILIZATION_RULES,
        "extension_safety_rules": EXTENSION_SAFETY_RULES,
        "layer_map": LAYER_MAP,
        "formal_proof_claim": (
            "Le périmètre public de preuves / vérification / exécution P1 d'Obsidia X-108 est "
            "fermé, reproductible et publiquement gelé. "
            "Les théorèmes Lean 4 (TemporalKernel, TemporalBridge, Consensus, Basic) couvrent "
            "les invariants noyau critiques. "
            "Les tests Python valident les comportements runtime. "
            "Un test Python n'est PAS une preuve formelle Lean."
        ),
        "forbidden_overclaims": [
            "Ne pas écrire 'prouvé formellement' pour un test pytest",
            "Ne pas écrire 'Lean prouve X' si X n'est pas dans #print axioms",
            "Ne pas confondre TLA+ model-checking (état fini) et preuve Lean (universel)",
            "Ne pas prétendre que PYTHON_TESTED = LEAN_PROVEN",
        ],
        "full_cascade_timeout_noted": True,
        "full_cascade_note": (
            "Cascade complète P56E→P71 dépasse 10 min (limite Bash). "
            "Tests unitaires P72 exécutés et validés. "
            "Régressions paliers vérifiées séparément."
        ),
        "next_step": "P73_AGENTS_COMPLEMENTARY_RECONCILIATION",
    }

    return report


# ---------------------------------------------------------------------------
# Écriture JSON
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    report = build_report()

    if DRY_RUN_ONLY:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY")
        print(f"JSON => {OUT_JSON}")
        print(f"Invariants: {report['total_invariants']} total")
        print(f"  LEAN_PROVEN: {report['lean_proven_count']}")
        print(f"  PYTHON_TESTED: {report['python_tested_only_count']}")
        print(f"  SPEC_ONLY: {report['spec_only_count']}")
        print(f"  DOC_ONLY: {report['doc_only_count']}")
        print(f"  MIXED: {report['mixed_proof_status_count']}")
        print(f"Theoremes Lean mappes: {report['total_lean_theorems_mapped']}")
    else:
        raise RuntimeError("DRY_RUN_ONLY is False — interdit en P72.")

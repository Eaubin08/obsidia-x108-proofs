"""
Brody Tree Policy
=================
Source : T13_T34_SIGNAL_DISCOVERY_READONLY_20260514_025500
Signal retenu : PATH_SLUG (n.path CONTAINS slug)
22 arbres T13-T34, 117 candidats safe, 81 bloqués.
"""
from __future__ import annotations
from typing import Any

# ── Tree registries ────────────────────────────────────────────────────────────
SAFE_TREES: dict[str, str] = {
    "T13": "Arbre de l'Art",
    "T14": "Arbre de la Philosophie",
    "T15": "Arbre de la Spiritualite",
    "T16": "Arbre de la Relation",
    "T17": "Arbre du Collectif",
    "T18": "Arbre de la Transmission",
    "T19": "Arbre de la Culture",
    "T23": "Arbre du Temps",
    "T25": "Arbre de l'Histoire",
    "T26": "Arbre de la Coherence",
    "T27": "Arbre de la Verite",
    "T28": "Arbre de la Valeur",
    "T29": "Arbre de la Finalite",
}

BLOCKED_ACTION_TREES: dict[str, str] = {
    "T20": "Arbre de l'Action",
    "T21": "Arbre de la Creation",
    "T22": "Arbre de la Transformation",
}

BLOCKED_MEMORY_TREE: dict[str, str] = {
    "T24": "Arbre de la Memoire",
}

BLOCKED_AGI_TREES: dict[str, str] = {
    "T30": "Arbre Cognitif Global",
    "T31": "Arbre des Flux",
    "T32": "Arbre des Connexions",
    "T33": "Arbre de l'Optimisation",
    "T34": "Arbre de la Stabilite",
}

SAFE_DOC_COUNT   = 117  # 13 trees × 9 docs
BLOCKED_DOC_COUNT = 81  # 9 trees × 9 docs
TOTAL_TREES      = 22
SIGNAL_METHOD    = "PATH_SLUG"


def get_tree_policy_snapshot() -> dict[str, Any]:
    """Return a full snapshot of the tree policy."""
    return {
        "safe_trees": list(SAFE_TREES.keys()),
        "safe_tree_names": SAFE_TREES,
        "safe_count": len(SAFE_TREES),
        "safe_docs": SAFE_DOC_COUNT,
        "blocked_action_trees": list(BLOCKED_ACTION_TREES.keys()),
        "blocked_action_tree_names": BLOCKED_ACTION_TREES,
        "blocked_action_reason": "BLOCKED_ACTION_TRIGGER — V_ACTION_TRANSFORMATION. Pas de déclencheur d'action.",
        "blocked_memory_trees": list(BLOCKED_MEMORY_TREE.keys()),
        "blocked_memory_tree_names": BLOCKED_MEMORY_TREE,
        "blocked_memory_reason": "BLOCKED_DIRECT_MEMORY_WRITE — T24 ne peut pas déclencher d'écriture Graphiti/Neo4j.",
        "blocked_agi_trees": list(BLOCKED_AGI_TREES.keys()),
        "blocked_agi_tree_names": BLOCKED_AGI_TREES,
        "blocked_agi_reason": "BLOCKED_AGI_LAYER — VIII_OBSIDIA_AGI. Pas d'activation couche décisionnelle.",
        "blocked_total": len(BLOCKED_ACTION_TREES) + len(BLOCKED_MEMORY_TREE) + len(BLOCKED_AGI_TREES),
        "blocked_docs": BLOCKED_DOC_COUNT,
        "total_trees": TOTAL_TREES,
        "signal_method": SIGNAL_METHOD,
        "source": "T13_T34_SIGNAL_DISCOVERY_READONLY_20260514_025500",
    }


def get_tree_usage_note(tree_id: str | None = None) -> str:
    """Get a human-readable policy note for a specific tree or general summary."""
    if tree_id and tree_id in BLOCKED_ACTION_TREES:
        return (
            f"{tree_id} ({BLOCKED_ACTION_TREES[tree_id]}) est bloqué comme déclencheur d'action "
            f"(V_ACTION_TRANSFORMATION). Je peux le citer comme signal contextuel readonly, "
            f"mais pas l'utiliser pour déclencher une action."
        )
    if tree_id and tree_id in BLOCKED_MEMORY_TREE:
        return (
            f"{tree_id} ({BLOCKED_MEMORY_TREE[tree_id]}) est bloqué pour écriture mémoire directe. "
            f"Je peux le citer pour contexte, mais pas déclencher d'écriture Graphiti/Neo4j via cet arbre."
        )
    if tree_id and tree_id in BLOCKED_AGI_TREES:
        return (
            f"{tree_id} ({BLOCKED_AGI_TREES[tree_id]}) est bloqué — couche AGI VIII_OBSIDIA_AGI. "
            f"Je peux l'évoquer pour contexte conceptuel, mais pas l'activer comme couche décisionnelle."
        )
    if tree_id and tree_id in SAFE_TREES:
        return (
            f"{tree_id} ({SAFE_TREES[tree_id]}) est safe. "
            f"Je peux l'utiliser comme signal contextuel et source de navigation readonly."
        )
    # General summary
    safe_list = ", ".join(list(SAFE_TREES.keys())[:7]) + f"... ({len(SAFE_TREES)} total)"
    blocked_list = ", ".join(
        list(BLOCKED_ACTION_TREES.keys())
        + list(BLOCKED_MEMORY_TREE.keys())
        + list(BLOCKED_AGI_TREES.keys())
    )
    return (
        f"Arbres safe (signal/contexte readonly) : {safe_list}\n"
        f"Arbres bloqués (action/mémoire/AGI) : {blocked_list}\n"
        "Les arbres bloqués peuvent être cités, pas activés comme déclencheurs."
    )


def is_tree_safe(tree_id: str) -> bool:
    return tree_id in SAFE_TREES


def is_tree_blocked(tree_id: str) -> bool:
    return tree_id in BLOCKED_ACTION_TREES or \
           tree_id in BLOCKED_MEMORY_TREE or \
           tree_id in BLOCKED_AGI_TREES

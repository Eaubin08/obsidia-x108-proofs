"""
Cognitive Tree Registry — 34 canonical cognitive trees.
TreeSpace = R^34, a_i ∈ [0,1].
Output is context signal only. Never a decision.
Restored from Freeze Candidate Matrix - Canonical Version.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_TREES: list[dict] = [
    {"id": 1,  "name": "ARBRE_01__Arbre_de_l_Humain",         "domain": "I_FONDAMENTAUX"},
    {"id": 2,  "name": "ARBRE_02__Arbre_de_la_Conscience",     "domain": "I_FONDAMENTAUX"},
    {"id": 3,  "name": "ARBRE_03__Arbre_de_la_Perception",     "domain": "I_FONDAMENTAUX"},
    {"id": 4,  "name": "ARBRE_04__Arbre_du_Sens",              "domain": "I_FONDAMENTAUX"},
    {"id": 5,  "name": "ARBRE_05__Arbre_de_l_Identite",          "domain": "I_FONDAMENTAUX"},
    {"id": 6,  "name": "ARBRE_06__Arbre_de_la_Comprehension",   "domain": "COGNITION"},
    {"id": 7,  "name": "ARBRE_07__Arbre_de_l_Organisation",     "domain": "COGNITION"},
    {"id": 8,  "name": "ARBRE_08__Arbre_de_la_Pensee",           "domain": "COGNITION"},
    {"id": 9,  "name": "ARBRE_09__Arbre_de_l_Intelligence",     "domain": "COGNITION"},
    {"id": 10, "name": "ARBRE_10__Arbre_du_Langage",           "domain": "COGNITION"},
    {"id": 11, "name": "ARBRE_11__Arbre_de_la_Science",          "domain": "EPISTEMICS"},
    {"id": 12, "name": "ARBRE_12__Arbre_de_la_Technique",        "domain": "EPISTEMICS"},
    {"id": 13, "name": "ARBRE_13__Arbre_de_l_Art",               "domain": "EPISTEMICS"},
    {"id": 14, "name": "ARBRE_14__Arbre_de_la_Philosophie",      "domain": "EPISTEMICS"},
    {"id": 15, "name": "ARBRE_15__Arbre_de_la_Spiritualite",     "domain": "EPISTEMICS"},
    {"id": 16, "name": "ARBRE_16__Arbre_de_la_Relation",         "domain": "SOCIAL"},
    {"id": 17, "name": "ARBRE_17__Arbre_du_Collectif",          "domain": "SOCIAL"},
    {"id": 18, "name": "ARBRE_18__Arbre_de_la_Transmission",     "domain": "SOCIAL"},
    {"id": 19, "name": "ARBRE_19__Arbre_de_la_Culture",          "domain": "SOCIAL"},
    {"id": 20, "name": "ARBRE_20__Arbre_de_l_Action",            "domain": "PLANNING"},
    {"id": 21, "name": "ARBRE_21__Arbre_de_la_Creation",          "domain": "PLANNING"},
    {"id": 22, "name": "ARBRE_22__Arbre_de_la_Transformation",    "domain": "PLANNING"},
    {"id": 23, "name": "ARBRE_23__Arbre_du_Temps",               "domain": "TEMPORAL"},
    {"id": 24, "name": "ARBRE_24__Arbre_de_la_Memoire",             "domain": "TEMPORAL"},
    {"id": 25, "name": "ARBRE_25__Arbre_de_l_Histoire",            "domain": "TEMPORAL"},
    {"id": 26, "name": "ARBRE_26__Arbre_de_la_Coherence",           "domain": "GOVERNANCE"},
    {"id": 27, "name": "ARBRE_27__Arbre_de_la_Verite",              "domain": "GOVERNANCE"},
    {"id": 28, "name": "ARBRE_28__Arbre_de_la_Valeur",              "domain": "GOVERNANCE"},
    {"id": 29, "name": "ARBRE_29__Arbre_de_la_Finalite",            "domain": "GOVERNANCE"},
    {"id": 30, "name": "ARBRE_30__Arbre_Cognitif_Global",          "domain": "META"},
    {"id": 31, "name": "ARBRE_31__Arbre_des_Flux",               "domain": "INFRASTRUCTURE"},
    {"id": 32, "name": "ARBRE_32__Arbre_des_Connexions",         "domain": "INFRASTRUCTURE"},
    {"id": 33, "name": "ARBRE_33__Arbre_de_l_Optimisation",       "domain": "INFRASTRUCTURE"},
    {"id": 34, "name": "ARBRE_34__Arbre_de_la_Stabilite",          "domain": "INFRASTRUCTURE"},
]

@dataclass
class TreeEntry:
    id: int
    name: str
    domain: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "domain": self.domain}

def get_all_trees() -> list[TreeEntry]:
    return [TreeEntry(**t) for t in _TREES]

def get_tree_by_id(tree_id: int) -> TreeEntry | None:
    for t in _TREES:
        if t["id"] == tree_id:
            return TreeEntry(**t)
    return None

def get_trees_by_domain(domain: str) -> list[TreeEntry]:
    return [TreeEntry(**t) for t in _TREES if t["domain"] == domain]

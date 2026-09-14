#!/usr/bin/env python3
"""
obsidure_math_memory_provider.py
Readonly provider — charge MATH_MEMORY_INDEX.json et repond aux requetes d'Obsidure.

READONLY = True
kernel_mutation = False
decision_authority = KX108_ONLY
emits_act = False
memory_write = False
graphiti_write = False
neo4j_write = False
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Optional

DECISION_AUTHORITY = "KX108_ONLY"
READONLY = True
EMITS_ACT = False
KERNEL_MUTATION = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False

MISSING_CONTEXT = "MISSING_CONTEXT"

_INDEX_PATH = (
    Path(__file__).resolve().parents[2]
    / "periphery"
    / "obsidure_math_memory_readonly"
    / "MATH_MEMORY_INDEX.json"
)


class ObsidureMathMemoryProvider:
    """
    Provider en lecture seule de la memoire mathematique d'Obsidure.

    Ce provider ne modifie aucun fichier, ne declenche aucune action,
    n'ecrit pas dans Graphiti ni Neo4j. Il charge l'index JSON et repond
    aux requetes d'Obsidure sur les pepites, metriques et dependances.
    """

    def __init__(self, index_path: Path = _INDEX_PATH) -> None:
        self._data: dict = {}
        self._items: dict[str, dict] = {}
        if index_path.exists():
            self._data = json.loads(index_path.read_text(encoding="utf-8"))
            for item in self._data.get("items", []):
                self._items[item["id"]] = item

    def get_pepite(self, pepite_id: str) -> dict | str:
        """
        Retourne l'item correspondant a l'id, ou MISSING_CONTEXT si absent ou si
        le statut de l'item est MISSING_CONTEXT (concept non documenté lisiblement).

        Utiliser cette methode avant toute tentative de preuve ou d'axiomatisation.
        Si le retour est MISSING_CONTEXT, ne pas inventer le concept.
        """
        item = self._items.get(pepite_id)
        if item is None:
            return MISSING_CONTEXT
        if item.get("status") == MISSING_CONTEXT:
            return MISSING_CONTEXT
        return item

    def get_metric(self, metric_name: str) -> dict | str:
        """
        Cherche une metrique par nom dans le champ related_metrics de chaque item.
        Retourne le premier item contenant cette metrique, ou MISSING_CONTEXT.
        """
        for item in self._items.values():
            if metric_name in item.get("related_metrics", []):
                return item
        return MISSING_CONTEXT

    def get_missing_dependencies(self, pepite_id: str) -> list[str] | str:
        """
        Retourne la liste des dependances manquantes pour un item.
        Retourne MISSING_CONTEXT si l'item n'existe pas.
        """
        item = self._items.get(pepite_id)
        if item is None:
            return MISSING_CONTEXT
        return item.get("missing_dependencies", [])

    def can_use_for_proof(self, pepite_id: str) -> bool:
        """
        Retourne True ssi l'item peut etre utilise dans une chaine de preuve formelle.
        False par defaut si l'item est absent.
        Un axiome HYPOTHESE_TEMPORAIRE n'est pas une preuve — can_be_used_for_proof=False.
        """
        item = self._items.get(pepite_id)
        if item is None:
            return False
        return bool(item.get("can_be_used_for_proof", False))

    def get_status(self, pepite_id: str) -> str:
        """
        Retourne le statut de l'item (CANONICAL_CANDIDATE, PROVISIONAL, etc.)
        ou MISSING_CONTEXT si l'item n'existe pas.
        """
        item = self._items.get(pepite_id)
        if item is None:
            return MISSING_CONTEXT
        return item.get("status", MISSING_CONTEXT)

    def list_ids(self) -> list[str]:
        """Retourne la liste de tous les ids connus."""
        return list(self._items.keys())

    def research_context(self, objective: str) -> dict | None:
        normalized = objective.casefold().replace('\\_', '_').replace('-', '_')
        if 'navier' not in normalized and 'ns_anti_pumping' not in normalized:
            return None
        from periphery.agents.obsidure_research_sources import load_navier_context
        return load_navier_context()

    def explain_boundary(self) -> dict:
        """
        Retourne les proprietes de securite de ce provider.
        Utile pour l'introspection et les tests.
        """
        return {
            "readonly": READONLY,
            "decision_authority": DECISION_AUTHORITY,
            "emits_act": EMITS_ACT,
            "kernel_mutation": KERNEL_MUTATION,
            "memory_write": MEMORY_WRITE,
            "graphiti_write": GRAPHITI_WRITE,
            "neo4j_write": NEO4J_WRITE,
        }

    # Proprietes de securite — lecture seule, pas de setters

    @property
    def kernel_mutation(self) -> bool:
        """Toujours False — ce provider ne modifie jamais le kernel."""
        return False

    @property
    def emits_act(self) -> bool:
        """Toujours False — ce provider ne declenche jamais d'action."""
        return False

    @property
    def memory_write(self) -> bool:
        """Toujours False — ce provider n'ecrit jamais en memoire."""
        return False


# Singleton module-level
_provider: Optional[ObsidureMathMemoryProvider] = None


def get_provider() -> ObsidureMathMemoryProvider:
    """
    Retourne l'instance singleton du provider.
    Cree l'instance au premier appel.
    """
    global _provider
    if _provider is None:
        _provider = ObsidureMathMemoryProvider()
    return _provider

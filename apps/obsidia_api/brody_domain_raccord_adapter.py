"""Brody domain raccord adapter.

Phase 12E4-B.

Readonly/advisory raccord between already-present Obsidia domains and
Brody true voice / machination payload.

It does not decide, act, write memory, write Graphiti, write Neo4j,
mutate the kernel, or mutate X108.
"""
from __future__ import annotations

from typing import Any
import re
import unicodedata


BOUNDARY = {
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "emits_act": False,
    "emits_verdict": False,
    "decision_authority": "KX108_ONLY",
}


def _fold(text: str) -> str:
    text = text or ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def _has_any(low: str, terms: tuple[str, ...]) -> bool:
    return any(t in low for t in terms)


def _negated_near(low: str, verbs: tuple[str, ...]) -> bool:
    negators = (
        "sans ", "ne pas ", "n' ", "n’ ", "no ", "without ",
        "pas de ", "aucune ", "aucun ", "non "
    )
    for verb in verbs:
        idx = low.find(verb)
        if idx < 0:
            continue
        window = low[max(0, idx - 32):idx + len(verb) + 32]
        if any(n in window for n in negators):
            return True
    return False


def has_negated_mutation(text: str) -> bool:
    low = _fold(text)
    return (
        _has_any(low, ("sans remplacer", "sans modifier", "ne pas remplacer", "ne pas modifier", "without replacing", "without modifying"))
        or _negated_near(low, ("remplacer", "replace", "modifier", "modify", "patcher", "patch", "muter", "mutate"))
    )


def has_negated_action(text: str) -> bool:
    low = _fold(text)
    return (
        _has_any(low, ("sans autoriser act", "sans act", "sans agir", "no act", "without act", "without acting", "sans executer", "sans lancer"))
        or _negated_near(low, ("autoriser", "authorize", "act", "agir", "executer", "execute", "lancer"))
    )


def has_memory_write_request(text: str) -> bool:
    low = _fold(text)
    write_terms = ("ecris", "ecrit", "write", "inscris", "enregistre", "sauvegarde", "save", "store")
    memory_terms = ("memoire", "memory", "graphiti", "neo4j", "canon", "canonical", "valide", "valider", "promotion", "freeze")
    if has_negated_action(text):
        # "sans écrire" is a boundary statement, not a request.
        if _negated_near(low, write_terms):
            return False
    return _has_any(low, write_terms) and _has_any(low, memory_terms)


def adjust_risk_flags(text: str, flags: list[str]) -> list[str]:
    values = list(dict.fromkeys(str(f) for f in (flags or []) if f))

    if has_negated_mutation(text):
        values = [f for f in values if f != "mutation_request"]

    if has_negated_action(text):
        values = [f for f in values if f != "action_request"]

    if has_memory_write_request(text):
        for f in ("write_request", "memory_write_request", "graphiti_write_request", "canon_promotion_request"):
            if f not in values:
                values.append(f)

    return values


def _domain_text_fr(domains: list[str], text: str) -> str:
    parts: list[str] = []

    if "MEMORY_WRITE_CANON_FREEZE" in domains:
        parts.append(
            "La demande touche une écriture mémoire / Graphiti / canonisation. "
            "Brody ne peut pas écrire, valider canon, promouvoir un freeze ou modifier Graphiti. "
            "Le raccord actif doit rester une projection readonly : signaler la demande, exposer le refus, "
            "et laisser toute autorité à KX108/humain."
        )

    if "NEGATION_GUARD" in domains:
        parts.append(
            "La formulation contient une négation structurante : « sans remplacer / sans modifier ». "
            "Ce n'est pas une demande de mutation, c'est une contrainte de non-contournement. "
            "Le rôle du garde anti-mismatch est de ne pas confondre mention d'une frontière avec tentative de la franchir."
        )

    if "FRICTION" in domains:
        parts.append(
            "La friction est un signal de calibration : elle indique qu'un raccord manque ou qu'une réponse masque une faille. "
            "Elle ne doit pas être traitée comme bruit émotionnel ; elle oriente le diagnostic vers cohérence, contexte et frontière X108."
        )

    if "THERMODYNAMICS" in domains:
        parts.append(
            "La couche thermodynamique sert à lire la dissipation, l'entropie et la stabilité d'un système. "
            "Dans Brody, elle reste métrique/advisory : elle peut expliquer une tension ou une perte de cohérence, jamais autoriser ACT."
        )

    if "ENERGY_SIGMA" in domains:
        parts.append(
            "Énergie / sigma / truth_score forment un raccord d'évaluation : détecter l'écart entre forme cohérente et vérité structurelle. "
            "Ils renforcent la lecture, mais ne deviennent pas décisionnaires."
        )

    if "ANTI_MISMATCH" in domains:
        parts.append(
            "Anti-mismatch sert à détecter les réponses belles mais fausses : false_on, decorative_coherence, collapse_disguised. "
            "Si la surface répond bien mais contredit le contrat, Brody doit ralentir et signaler la divergence."
        )

    if "REGIMES" in domains:
        parts.append(
            "Les régimes CRISTAL / TRANSITION / NÉANT servent à qualifier l'état de réponse : "
            "CRISTAL quand la structure est stable, TRANSITION quand la matière enrichit mais reste partielle, "
            "NÉANT quand le signal est insuffisant. Ces régimes sont des états de voix, pas des décisions."
        )

    if "TIME_TEMPORALITY" in domains:
        parts.append(
            "Le temps/X108 reste le verrou de passage : Brody peut lire le passé, répondre au présent, projeter le futur, "
            "mais ne franchit pas l'irréversibilité."
        )

    if "COHERENCE" in domains:
        parts.append(
            "La cohérence est la règle de non-contradiction : si le texte dit « sans modifier », "
            "le système doit préserver cette contrainte au lieu de déclencher une alerte mutation."
        )

    if not parts:
        return ""

    return "\n\n".join(parts)


def build_domain_raccord_snapshot(user_message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    text = user_message or ""
    low = _fold(text)

    domains: list[str] = []

    if _has_any(low, ("friction", "saoule", "perdu", "bloque", "bug", "faille", "raccord manque")):
        domains.append("FRICTION")

    if _has_any(low, ("thermodynamique", "thermodynamic", "entropie", "entropy", "dissipation", "temperature", "chaleur", "heat")):
        domains.append("THERMODYNAMICS")

    if _has_any(low, ("temps", "temporal", "x108", "x-108", "hold", "irreversible", "irreversibilite", "tau")):
        domains.append("TIME_TEMPORALITY")

    if _has_any(low, ("coherence", "cohérence", "non-contradiction", "contradiction", "coherence_loop")):
        domains.append("COHERENCE")

    if _has_any(low, ("energie", "énergie", "energy", "sigma", "sigma_score", "truth_score", "balance exponentielle")):
        domains.append("ENERGY_SIGMA")

    if _has_any(low, ("anti_mismatch", "anti-mismatch", "mismatch", "false_on", "decorative_coherence", "collapse_disguised")):
        domains.append("ANTI_MISMATCH")

    if _has_any(low, ("cristal", "transition", "neant", "néant", "autosort", "sovereignsealer", "reflexreducer", "frictionengine")):
        domains.append("REGIMES")

    if has_memory_write_request(text):
        domains.append("MEMORY_WRITE_CANON_FREEZE")

    if has_negated_mutation(text):
        domains.append("NEGATION_GUARD")

    # Deduplicate but preserve order.
    domains = list(dict.fromkeys(domains))

    boundary_required = "MEMORY_WRITE_CANON_FREEZE" in domains
    structural_answer = _domain_text_fr(domains, text)

    mode = "DOMAIN_RACCORD"
    if boundary_required:
        mode = "DOMAIN_RACCORD_BOUNDARY"
    elif "NEGATION_GUARD" in domains:
        mode = "DOMAIN_RACCORD_NEGATION_GUARD"
    elif domains:
        mode = "DOMAIN_RACCORD_STRUCTURAL"

    return {
        "source": "BRODY_DOMAIN_RACCORD_ADAPTER_V1",
        "status": "DOMAIN_RACCORD_READY" if domains else "NO_DOMAIN_RACCORD",
        "domains": domains,
        "voice_mode": mode,
        "structural_answer_available": bool(structural_answer),
        "structural_answer": structural_answer,
        "memory_dependency": "NONE",
        "memory_enrichment": "OPTIONAL",
        "boundary_required": boundary_required,
        "negation_guard_active": "NEGATION_GUARD" in domains,
        "write_boundary_required": boundary_required,
        "risk_flags_patch": adjust_risk_flags(text, []),
        **BOUNDARY,
    }

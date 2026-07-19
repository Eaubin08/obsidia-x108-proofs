"""OBSIDIA TERMINAL GUIDANCE VOCABULARY V0.

Lexique du terminal `obsidia`. NON SOUVERAIN.

Ce module N'EST PAS Sigma Core. Il n'importe rien depuis sigma/, ne definit
aucun X108Gate, n'emet aucune decision. C'est un dictionnaire ferme des mots
que le terminal a le droit de prononcer, et de ceux qu'il n'a pas le droit
de prononcer.

Regle absolue :
    decision_authority = KX108_ONLY
    Le terminal recommande, guide, refuse localement (POLICY_DENY).
    Il ne decide jamais. HOLD_RECOMMENDED n'est pas X108Gate.HOLD.
"""

from __future__ import annotations

# --- Sorties possibles du terminal (types de reponse, pas des decisions) ---
TERMINAL_OUTPUTS = (
    "EXECUTE",       # readonly direct autorise (doctor/status HTTP GET uniquement)
    "COMMANDS",      # le terminal affiche les commandes exactes, ne les lance pas
    "GUIDE",         # demande floue mais dans le perimetre : orientation
    "POLICY_DENY",   # refus local terminal/policy (PAS un BLOCK X108)
    "STOP_UNKNOWN",  # intention non reconnue : on s'arrete, on demande
)

# --- Verbes de guidance autorises (recommandations non souveraines) ---
GUIDANCE_ACTIONS = (
    "CONTINUE",
    "SLOW_DOWN",
    "RELAUNCH_LAYER",
    "REQUEST_CONTEXT",
    "REQUEST_TRACE",
    "REQUEST_REPLAY",
    "REQUEST_TEST",
    "REQUEST_PROOF",
    "CHECK_INVARIANT",
    "STOP_UNKNOWN",
    "HOLD_RECOMMENDED",
)

# --- Mots que le terminal ne doit JAMAIS emettre comme resultat ---
FORBIDDEN_TERMINAL_ACTIONS = (
    "ACT",
    "ALLOW",
    "BLOCK",          # reserve a X108. Le terminal dit POLICY_DENY.
    "HOLD",           # reserve a X108. Le terminal dit HOLD_RECOMMENDED.
    "WRITE_MEMORY",
    "MUTATE_KERNEL",
    "AUTO_APPLY",
    "COMMIT",
    "DEPLOY",
)

# --- Champs non souverains obligatoires sur chaque receipt terminal ---
NON_SOVEREIGN_RECEIPT_DEFAULTS = {
    "receipt_type": "terminal_non_sovereign",
    "authority": "NONE",
    "sovereign": False,
    "gate_emitted": None,
    "decision_authority": "KX108_ONLY",
}


def is_forbidden(word: str) -> bool:
    """Vrai si le mot est interdit en sortie terminal."""
    return word.strip().upper() in FORBIDDEN_TERMINAL_ACTIONS


def assert_output_allowed(output: str) -> str:
    """Valide qu'une sortie terminal appartient au lexique. Leve sinon."""
    up = output.strip().upper()
    if up in FORBIDDEN_TERMINAL_ACTIONS:
        raise ValueError(
            f"Sortie interdite pour le terminal: {up}. "
            f"Le terminal n'emet jamais de decision souveraine (KX108_ONLY)."
        )
    if up not in TERMINAL_OUTPUTS and up not in GUIDANCE_ACTIONS:
        raise ValueError(f"Sortie hors lexique terminal V0: {up}")
    return up

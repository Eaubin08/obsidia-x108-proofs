"""
Fichier périphérique cible pour la session synthétique OBSIDURE_BOUNDED_APPLY_V1.
Ce fichier est modifié par Obsidure lors de la session E2E.
"""

PERIPHERAL_VERSION = "v0"

def peripheral_status() -> dict:
    return {"version": PERIPHERAL_VERSION, "status": "ORIGINAL"}

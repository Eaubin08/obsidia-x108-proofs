"""
Source Classifier — Obsidia X-108 Sovereign Ingestion.
Determines if a document belongs to the canonical matrix or requires quarantine.
Restored from V4.3 Audit Checklist.
"""
from __future__ import annotations

# Les sources sacrées issues de ton architecture et de tes audits de gel
_CANONICAL_TRUSTED_SOURCES = {
    "checklist_v4.md",
    "doca_taxonomie_canonique_statuts.md",
    "docb_mapping_17blocs_161pepites.md",
    "docc_matrice_v3_recalee.md",
    "docd_readme_corpus.md",
    "rapport_161_pepites_integral_final.md",
    "src_40spec.txt",
    "internal_audit",
    "proofkit",
    "verified_feed",
    "sigma_output"
}

# La matière R&D hétérogène ou brute qui doit passer par un sas de quarantaine/validation G4
_QUARANTINE_SOURCES = {
    "src_branche149.txt",
    "user_upload",
    "web_scrape",
    "unknown"
}

def classify_source(source: str) -> str:
    """
    Classifie la source pour forcer l'alignement du pipeline d'ingestion.
    """
    clean_source = source.lower().strip()
    
    # Validation des briques de ton infrastructure réelle
    if clean_source in _CANONICAL_TRUSTED_SOURCES or any(trusted in clean_source for trusted in _CANONICAL_TRUSTED_SOURCES):
        return "TRUSTED"
        
    # Isolation de la matière hétérogène (Branche 149, etc.)
    if clean_source in _QUARANTINE_SOURCES or any(quarantine in clean_source for quarantine in _QUARANTINE_SOURCES):
        return "UNTRUSTED"
        
    return "UNCLASSIFIED"

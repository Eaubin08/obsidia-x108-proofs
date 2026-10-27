def map_reason_code(code):
    return {"RC_CONTEXT_ONLY":"Projection contexte uniquement","RC_X108_REQUIRED":"Décision requiert X-108"}.get(code, "Raison non cartographiée")

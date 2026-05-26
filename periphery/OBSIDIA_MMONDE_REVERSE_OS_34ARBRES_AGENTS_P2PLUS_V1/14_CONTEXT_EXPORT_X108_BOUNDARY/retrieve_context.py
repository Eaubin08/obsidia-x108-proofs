# Context retrieval minimal, non décisionnel
def retrieve(query):
    return {
        "query": query,
        "events": [],
        "activated_trees": {},
        "calibrated_links": [],
        "projection": {},
        "confidence": 0.0,
        "non_decision": True,
        "export_target": "X-108"
    }

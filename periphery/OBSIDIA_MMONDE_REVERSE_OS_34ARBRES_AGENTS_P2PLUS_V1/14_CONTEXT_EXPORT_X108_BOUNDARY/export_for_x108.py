# Export context to X-108 boundary, no decision
def export(packet):
    out = dict(packet)
    out["non_decision"] = True
    out["export_target"] = "X-108"
    out.pop("decision", None)
    out.pop("ACT", None)
    return out

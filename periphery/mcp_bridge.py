# MCP Bridge minimal, non décisionnel
def convert_request(request):
    return {
        "intent": request.get("intent", ""),
        "domain": request.get("domain", ""),
        "scope": request.get("scope", ""),
        "cost": request.get("cost", 0.0),
        "risk": request.get("risk", 0.0),
        "tool_request": request.get("tool_request"),
        "policy_scope": request.get("policy_scope", "READONLY_CONTEXT"),
        "tree_vector": request.get("tree_vector", [0.0]*34),
        "non_decision": True
    }

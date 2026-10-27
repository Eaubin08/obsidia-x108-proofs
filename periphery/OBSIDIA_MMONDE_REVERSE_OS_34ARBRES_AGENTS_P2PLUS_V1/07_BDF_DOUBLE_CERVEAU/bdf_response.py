# BDF minimal, non décisionnel
def compute_response(alpha, beta, llm_output, diffusion_output):
    return alpha * llm_output + beta * diffusion_output

def compute_bdf(alpha=0.5, beta=0.5, llm_output=0.0, diffusion_output=0.0):
    return {"response_value": compute_response(alpha, beta, llm_output, diffusion_output), "non_decision": True, "explanation": "BDF proposal only"}

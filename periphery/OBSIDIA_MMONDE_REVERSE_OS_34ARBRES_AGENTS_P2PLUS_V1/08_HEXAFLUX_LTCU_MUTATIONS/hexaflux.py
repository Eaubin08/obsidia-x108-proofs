# HexaFlux minimal, non décisionnel
def mutate(input_data):
    return input_data

def symbolic_mutation(value, role="transition"):
    return {"original_value": value, "mutated_value": value, "transition_role": role, "non_decision": True}

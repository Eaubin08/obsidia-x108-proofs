
# Reduction cognitive active

def reduce(activation, threshold=0.15):
    return {i: v for i, v in enumerate(activation) if v > threshold}


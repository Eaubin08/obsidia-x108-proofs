def filter_dominant(activation, threshold=0.15):
    return {k: v for k, v in activation.items() if v > threshold}

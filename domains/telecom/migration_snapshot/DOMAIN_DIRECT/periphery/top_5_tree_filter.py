
# Filter top 5 trees placeholder

def filter_top5(activations):
    return sorted(activations.items(), key=lambda x: x[1], reverse=True)[:5]


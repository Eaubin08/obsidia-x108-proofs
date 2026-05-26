# Shazam Cognitif minimal, non décisionnel
from spectral_hash import extract_features

KEYWORDS = {
    0: ["humain","personne","vie"],
    1: ["conscience","présence","perception"],
    2: ["voir","sentir","perception"],
    3: ["sens","meaning","direction"],
    4: ["identité","moi","nom"],
    5: ["comprendre","comprehension","analyse"],
    6: ["organiser","structure","plan"],
    7: ["pensée","idée","raisonnement"],
    8: ["intelligence","ia","agent"],
    9: ["langage","mot","texte"],
    10: ["science","preuve","test"],
    11: ["technique","code","outil"],
    12: ["art","image","création"],
    13: ["philosophie","concept","vérité"],
    14: ["spiritualité","symbolique","résonance"],
    15: ["relation","lien","contact"],
    16: ["collectif","groupe","communauté"],
    17: ["transmission","mémoire","héritage"],
    18: ["culture","histoire","tradition"],
    19: ["action","agir","exécuter"],
    20: ["création","forge","build"],
    21: ["transformation","mutation","changement"],
    22: ["temps","chronologie","frise"],
    23: ["mémoire","trace","souvenir"],
    24: ["histoire","passé","événement"],
    25: ["cohérence","alignement","stable"],
    26: ["vérité","preuve","réel"],
    27: ["valeur","score","poids"],
    28: ["finalité","objectif","but"],
    29: ["global","cognitif","système"],
    30: ["flux","pipeline","stream"],
    31: ["connexion","graphe","lien"],
    32: ["optimisation","améliorer","performance"],
    33: ["stabilité","robuste","freeze"],
}

def shazam(payload, threshold=0.15):
    text = payload.decode("utf-8", errors="ignore").lower() if isinstance(payload, (bytes, bytearray)) else str(payload).lower()
    features = extract_features(payload)
    activations = {}
    for idx in range(34):
        keys = KEYWORDS.get(idx, [])
        hit = sum(1 for k in keys if k in text)
        base = 0.05 + min(0.8, hit * 0.25)
        boost = 0.1 * features["tension"] + 0.05 * features["urgency"]
        activations[idx] = round(min(1.0, base + boost), 4)
    dominant = {k:v for k,v in activations.items() if v > threshold}
    return {
        "spectral_hash": features,
        "tree_activation": activations,
        "dominant_trees": dominant,
        "metadata": {"shazam_trees": list(dominant.keys()), "non_decision": True},
        "non_decision": True
    }

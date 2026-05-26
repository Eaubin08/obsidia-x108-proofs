import re
with open('periphery/brody_bridge.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Ajout du print de debug pour voir le topic reçu
new_code = code.replace(
    'if env.topic != "GENCOIN_TRAD_CONTEXT":', 
    'if env.topic != "GENCOIN_TRAD_CONTEXT":\n            print(f"[DEBUG] REJETÉ: topic {env.topic} reçu, attendu GENCOIN_TRAD_CONTEXT")\n            return'
)
with open('periphery/brody_bridge.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Bridge patché avec debug.")

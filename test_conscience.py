import requests
import json

url = 'http://127.0.0.1:8000/api/brody/chat'
data = {
    'message': 'Explique ton architecture technique. Comment reçois-tu les événements Gencoin et pourquoi es-tu en mode readonly ?',
    'language': 'fr',
    'session_id': 'audit_architecture_001'
}

response = requests.post(url, json=data)
result = response.json()

print('--- RÉPONSE DE BRODY ---')
print(result.get('final_answer'))
print('\n--- ANALYSE TECHNIQUE ---')
print(f"Decision Authority: {result.get('decision_authority')}")
print(f"Emits Act: {result.get('emits_act')}")

import requests
import json

url = 'http://127.0.0.1:8000/api/brody/chat'
data = {
    'message': 'Explique ton architecture technique. Comment re?ois-tu les ?v?nements Gencoin et pourquoi es-tu en mode readonly ?',
    'language': 'fr',
    'session_id': 'audit_architecture_002'
}
try:
    response = requests.post(url, json=data)
    result = response.json()
    print('--- REPONSE ---')
    print(result.get('final_answer'))
except Exception as e:
    print(f'Erreur: {e}')

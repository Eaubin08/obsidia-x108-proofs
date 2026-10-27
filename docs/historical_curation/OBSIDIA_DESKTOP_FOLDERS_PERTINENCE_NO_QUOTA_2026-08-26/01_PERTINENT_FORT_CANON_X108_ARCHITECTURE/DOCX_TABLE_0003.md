
## DOCX_TABLE_0003
| Col1 | Col2 | Col3 | Col4 | Col5 |
|---|---|---|---|---|
| Bloc / Outil Google | Ce que ça fait (résumé) | Déjà présent dans Obsidia ? | Utile ou non ? | Pourquoi / Comment l’intégrer |
| TensorFlow | Framework général de deep learning | ❌ (pas directement utilisé) | ⚠️ Optionnel | Redondant avec LLMs pré-entraînés, sauf si on veut entraîner en local une sous-brique d’Obsidia |
| JAX | NumPy + autograd + XLA (training rapide) | ❌ | ✅ Pour Cortex Obsidia Light | Ultra utile si on veut entraîner des micro-modèles internes (ex. agents éphémères adaptatifs, simulateurs internes) |
| MediaPipe | Détection visage/main/pose (vision) | ❌ | ⚠️ Pas prioritaire | Utile si Obsidia a besoin d’un module sensoriel visuel (ex : assistant en live ou robot interactif) |
| LiteRT | Inférence IA sur mobile / edge | ❌ | ✅ Si on vise embedded Obsidia | Idéal pour une version offline d’Obsidia (ex : module AGI embarqué dans une clé, Raspberry, etc.) |
| ADK (Agent Dev Kit) | Kit pour créer et piloter des agents | ✅ / 🧪 partiellement recréé | ⚠️ Intéressant à benchmarker | Obsidia a sa propre architecture d’agents (Master, éphémères…), mais pourrait s’inspirer du routing d’ADK |
| A2A Protocol | Protocole agent ↔ agent interopérable | ❌ | ✅ à fond | Potentiel d’intégration énorme pour la version Obsidia ↔ ObsidiaSeed ↔ autres AGI |
| Google Research | Repo d’expérimentations IA | 🔍 utilisé comme veille, pas intégré | ✅ | Idéal pour benchmark ou intégration modulaire d’expériences de recherche (nouveau préprocesseur, etc.) |
| Kubeflow | Plateforme MLOps sur Kubernetes | ❌ | ⚠️ Peu utile sauf industrialisation | Trop lourd sauf si on lance du multi-expérimentations ou entraînement distribué |
| Magenta | IA pour créer de la musique / art | ❌ | ✅ Si Clio ou l’univers Obsidia a besoin d’art expressif | Parfait pour une expression poétique générée par agent Obsidia ou IA artistique |
| Cirq | IA quantique (programmation Qubit) | ❌ | 🧠 Futur stratégique | Aligné avec ta vision long terme Obsidia x quantum. On ne l’active pas maintenant mais c’est une veille prioritaire. |

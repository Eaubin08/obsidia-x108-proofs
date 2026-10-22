# M42 B11 Compétence & Calibration — Spécification Fail-Closed V1

## 1. Statut et autorité

- **Chapitre :** M42 — B11 Compétence et Calibration.
- **Couche :** Cognition / Pré-forge / Gouvernance périphérique.
- **Phase :** Spécification de la politique fail-closed sur preuves non authentifiées et sécurité passive intégrale (`SPEC_AUTHORED_HARDENED_TOTAL_PASSIVE`).
- **Base :** Diagnostic forensic `AUTHENTICATED_EXECUTION_EVIDENCE=NOT_AVAILABLE` dans les chemins d'exécution d'agents.
- **Principe directeur :** Refus absolu de simuler une source de confiance inexistante. En l'absence d'ancrage indépendant vérifiable, B11 retombe impérativement en `UNKNOWN_COMPETENCE` (`UNKNOWN != INCAPACITY`).
- **Principe de passivité totale (Anti-Descriptor Gate & Total Passive Boundary) :**
  - Conteneurs : seuls `list` ou `tuple` natifs (`type in (tuple, list)`) sont admis pour `evidence_records`, `target_resources` et `conditions`. Tout générateur ou itérateur personnalisé est rejeté avant itération (`INVALID_CONTAINER_STRUCTURE_REJECTED`).
  - Enregistrements : seuls les `dict` natifs (`type(record) is dict`) sont traités. Tout mapping personnalisé ou objet est rejeté sans appel de méthode (`INVALID_RECORD_STRUCTURE_REJECTED`).
  - Valeurs : aucun appel implicite à `str(obj)`, `bool(obj)` ou comparaison dunder `__eq__`. Seuls les types scalaires natifs attendus (`str`, `bool`) sont vérifiés par type exact avant tout traitement.

---

## 2. Règles du contrat Fail-Closed (FC-01 à FC-13)

1. **Règle FC-01 : Rejet du hash auto-signé non ancré**
   Un payload déclarant `outcome="SUCCESS"`, même muni d'un condensat SHA-256 parfaitement cohérent calculé sur lui-même, ne confère jamais `EVIDENCED_COMPETENCE` en l'absence d'ancrage dans un registre d'audit indépendant. Le profil produit est impérativement `UNKNOWN_COMPETENCE` (`confidence_score=0.0`, `reliability_score=None`) avec le code d'inconnue standard `EVIDENCE_UNANCHORED`.

2. **Règle FC-02 : Rejet de la self-attestation**
   Aucun indicateur déclaratif fourni par l'appelant (`is_verified=True`, `is_authenticated=True` ou équivalent) n'est accepté comme substitut d'authentification. Toute tentative est consignée dans `risk_indicators=("SELF_ATTESTATION_REJECTED",)` et la preuve est ignorée, laissant le profil en `UNKNOWN_COMPETENCE`.

3. **Règle FC-03 : Non-étanchéité du statut B9**
   `CognitivePath.path_id` (B9) scelle uniquement `(subject, goal, steps)` et ne scelle pas `_status`. Un chemin B9 sans reçu d'exécution externe scellé ne peut pas attester du succès opérationnel mondial d'une tâche. Le profil retombe en `UNKNOWN_COMPETENCE` avec `unknowns=("B9_PATH_STATUS_UNSEALED",)`.

4. **Règle FC-04 : Distinction B7 REJECT vs Incompétence technique**
   Un verdict `B7 REJECT` (non-conformité syntaxique de rôle ou violation de frontière cognitive locale en mémoire de travail) est consigné dans `contradictions=("B7_ROLE_NON_CONFORMANCE",)`. Il n'est jamais converti automatiquement en `EVIDENCED_INCOMPETENCE` permanente (`TECHNICAL_INCOMPETENCE != SYNTACTIC_REJECT`).

5. **Règle FC-05 : Distinction GuardX108 BLOCK vs Incompétence technique**
   Un blocage par la porte de sécurité `GuardX108` (`x108_gate="BLOCK"`) relève du contrôle d'accès (`COMPETENCE != AUTHORITY`). Il est consigné dans `risk_indicators=("ACCESS_GATE_BLOCKED",)`, mais ne constitue pas une preuve d'incapacité technique de l'organe. Le profil reste en `UNKNOWN_COMPETENCE`.

6. **Règle FC-06 : Traitement de l'absence totale de preuves**
   En l'absence totale de preuves recevables, l'évaluateur produit `UNKNOWN_COMPETENCE`, `confidence_score=0.0`, `reliability_score=None`, avec `unknowns=("NO_HISTORICAL_EVIDENCE",)`. L'absence de preuve n'est jamais assimilée à une incapacité (`UNKNOWN != FALSE`).

7. **Règle FC-07 : Frontières constitutionnelles absolues**
   L'évaluateur est une fonction pure sans effet de bord, conforme à `B11_EFFECTS` :
   - `memory_write=False` (aucune persistance durable dans B10)
   - `emits_act=False` (aucune émission d'acte)
   - `kernel_mutation=False` (aucune altération du noyau)
   - `decision_authority="KX108_ONLY"` (décision réservée au noyau)
   - `advisory_only=True` (caractère strictement consultatif)
   - `b12_selection=False` (aucune sélection d'organe / agent, prérogative B12/M43)

8. **Règle FC-08 : Rejet des descripteurs dynamiques et propriétés d'objets**
   Tout objet personnalisé injecté dans `evidence_records` est refoulé sans exécution de `@property` ni `__getattr__` (`INVALID_RECORD_STRUCTURE_REJECTED`).

9. **Règle FC-09 : Rejet des sous-classes de Mapping personnalisées**
   Toute sous-classe de mapping surchargeant `.get()` ou `__getitem__` est refoulée sans appel de méthode (`INVALID_RECORD_STRUCTURE_REJECTED`).

10. **Règle FC-10 : Rejet des identifiants non-scalaires (Anti-`__str__` dunder)**
    Tout `evidence_id` qui n'est pas strictement un `str` natif est rejeté sans appel à `str(obj)` (`INVALID_EVIDENCE_ID_REJECTED`).

11. **Règle FC-11 : Rejet des itérables et générateurs hostiles (Anti-`__iter__`/`__next__`)**
    Si `evidence_records` n'est pas un `tuple` ou `list` natif, aucune itération n'est tentée (`INVALID_CONTAINER_STRUCTURE_REJECTED`).

12. **Règle FC-12 : Rejet des valeurs à comparaison hostile (Anti-`__eq__` dunder)**
    Aucune comparaison `== "SUCCESS"`, `== "REJECT"`, `== "BLOCK"` n'est effectuée sur un objet non-`str` natif.

13. **Règle FC-13 : Rejet des ressources et conditions non-scalaires (Anti-`__str__` arguments)**
    Toute ressource ou condition non-`str` natif est écartée sans appel à `str(obj)` (`INVALID_RESOURCE_STRUCTURE_REJECTED`, `INVALID_CONDITION_STRUCTURE_REJECTED`).

---

## 3. Matrice des statuts d'admissibilité et codes diagnostiques stables

| Règle | Signal d'entrée | Diagnostic / Statut B11 | Champ cible | Régime produit | Scores |
|---|---|---|---|---|---|
| **FC-01** | Payload `SUCCESS` avec hash cohérent sans ancrage | `EVIDENCE_UNANCHORED` | `unknowns` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-02** | Payload avec `is_verified=True` / `is_authenticated=True` | `SELF_ATTESTATION_REJECTED` | `risk_indicators` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-03** | B9 `CognitivePath` avec `status=SUCCEEDED` sans reçu | `B9_PATH_STATUS_UNSEALED` | `unknowns` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-04** | B7 `CognitiveValidationVerdict.REJECT` | `B7_ROLE_NON_CONFORMANCE` | `contradictions` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-05** | GuardX108 `x108_gate="BLOCK"` | `ACCESS_GATE_BLOCKED` | `risk_indicators` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-06** | Zéro preuve recevable | `NO_HISTORICAL_EVIDENCE` | `unknowns` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-07** | Toute invocation | Respect de `B11_EFFECTS` | `B11_EFFECTS` | N/A | Profil consultatif pur |
| **FC-08/09** | Enregistrement non `dict` natif | `INVALID_RECORD_STRUCTURE_REJECTED` | `risk_indicators` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-10** | `evidence_id` non `str` natif | `INVALID_EVIDENCE_ID_REJECTED` | `risk_indicators` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-11** | `evidence_records` non `tuple`/`list` natif | `INVALID_CONTAINER_STRUCTURE_REJECTED` | `risk_indicators` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-12** | Valeur outcome/verdict non `str` natif | Ignoré sans appel `__eq__` | N/A | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |
| **FC-13** | Ressource ou condition non `str` natif | `INVALID_RESOURCE/CONDITION_STRUCTURE_REJECTED` | `risk_indicators` | `UNKNOWN_COMPETENCE` | `rel=None`, `conf=0.0` |

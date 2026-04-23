# P2 BANK - COMPTE-RENDU CANONIQUE DE CORRECTION

## Statut

Correction appliquee, executee, testee et committee.

## Probleme initial

Le probleme observe n'etait pas situe dans X-108 guard, mais en amont, au niveau du contrat d'entree et de la construction de l'etat bank.

Des payloads invalides pouvaient etre acceptes comme etats legitimes, puis transformes par les agents en signaux trop permissifs, jusqu'a produire des `GUARD_ALLOW` non surs.

## Cause racine

### 1. Construction permissive de l'etat

`run_pipeline.py` chargeait le JSON brut puis construisait directement :

```python
BankState(**state_data)
```

sans validation metier/schema prealable.

### 2. Contrat `BankState` insuffisamment durci

`BankState` ne portait pas de validation stricte a l'initialisation.

Consequences possibles :
- `amount < 0`
- `fraud_score < 0`
- `device_trust_score > 1`
- types incoherents
- champs critiques absents ou compenses par defaut permissif

### 3. Defaut favorable sur `device_trust_score`

Le champ `device_trust_score` avait un defaut `= 1.0`, ce qui pouvait etre interprete comme une confiance parfaite si le champ etait absent.

### 4. Effet systemique sur les agents bank

Des valeurs invalides pouvaient ensuite reduire artificiellement les signaux de risque et conduire a un verdict permissif en aval.

## Chaine causale resumee

1. JSON bank brut accepte
2. Construction directe `BankState(**state_data)`
3. Absence de validation d'entree stricte
4. Propagation de valeurs invalides dans les agents
5. Reduction artificielle des signaux de risque
6. `GUARD_ALLOW` possible sur etat non legitime

## Correctif applique

### A. Durcissement du contrat `BankState`

Ajout d'un `__post_init__` dans `sigma/contracts.py` avec validation explicite :

- chaines non vides
- booleens stricts
- entiers non negatifs
- nombres finis
- bornes minimales et maximales
- scores bornes dans `[0,1]`
- `amount > 0`
- `policy_limit > 0`
- `elapsed_s >= 0`
- `min_required_elapsed_s >= 0`

### B. Validation explicite du payload bank avant construction

Ajout dans `sigma/run_pipeline.py` de :

- `REQUIRED_BANK_FIELDS`
- `ALLOWED_BANK_FIELDS`
- `validate_bank_payload(state_data)`

Effets :
- rejet si champ requis manquant
- rejet si champ inconnu
- rejet si le payload n'est pas un objet JSON bank valide

### C. Positionnement correct de la membrane

Le correctif a ete applique au bon endroit :

- en amont du guard
- au niveau du contrat d'entree
- avant construction d'etat
- sans deplacer artificiellement la logique de surete dans `guard.py`

## Fichiers modifies

- `sigma/contracts.py`
- `sigma/run_pipeline.py`

## Preuve d'execution reelle

Pack execute avec succes :

- runner Python : OK
- tests `pytest` : OK
- script PowerShell pack : OK

### Resultat runner

- `total_cases = 74`
- `failed_cases = 0`
- `unsafe_allow_count = 0`
- `clean_rejection_count = 23`
- `safe_non_allow_count = 50`
- `replay_stable_count = 1`

### Repartition des outcomes

- `CLEAN_REJECTION = 23`
- `SAFE_NON_ALLOW = 50`
- `REPLAY_STABLE = 1`

### Repartition des gates

- `HOLD = 2`
- `BLOCK = 49`

## Validation test

Suite executee :

```text
python -W ignore -m pytest .\sigma\tests\test_bank_security_fuzz_extended_pack.py -v
```

Resultat :

- `6 passed`

Tests valides :
- `test_extended_fuzz_runner_passes`
- `test_total_case_count_is_expected`
- `test_no_unsafe_allow`
- `test_many_clean_rejections_exist`
- `test_many_safe_non_allow_exist`
- `test_replay_stability_present`

## Garantie obtenue

Apres correction :

- les payloads bank invalides ne traversent plus la membrane comme etats legitimes
- les champs manquants critiques sont rejetes explicitement
- les champs inconnus sont rejetes explicitement
- les types incoherents et bornes invalides sont rejetes
- plus aucun `UNSAFE_ALLOW` n'est observe sur le pack extended fuzz
- le guard n'est plus alimente par un etat faux
- le pack extended fuzz teste desormais la vraie membrane de surete et non une fuite de plomberie d'entree

## Limite de portee

Cette correction demontre la fermeture de la breche identifiee sur le perimetre bank teste par le pack `P2 BANK / SECURITY FUZZ EXTENDED`.

Elle ne pretend pas, a elle seule, demontrer la surete universelle de tous les domaines, mais elle apporte une preuve executable et verifiee sur le perimetre concerne.

## Commits associes

- `86ae408` - `Harden BankState contract and validate bank payloads before pipeline construction`
- `01b793d` - `Add extended bank security fuzz failure extraction and report`

## Conclusion canonique

Le defaut n'etait pas dans le guard, mais dans l'acceptation permissive de l'etat avant pipeline.

Le correctif applique durcit le contrat bank, valide explicitement le payload avant construction, supprime la possibilite de faux `ALLOW` issus d'etats invalides et retablit une membrane de surete coherente avec l'intention structurelle du systeme.

# Procédure de l'opérateur de recevabilité — curriculum V0.4

**L'opérateur** est désigné par le fondateur. Il est distinct du rédacteur et de l'auteur du modèle (Claude). Il travaille hors session Claude.

**Indépendance :** deux sous-agents lancés par Claude sous le même compte Windows ne constituent **pas** une indépendance garantie. Le rédacteur et l'opérateur doivent être des personnes, ou un dispositif hors de portée de Claude ; c'est le fondateur qui le qualifie.

## Entrées

- le fichier JSON du rédacteur, avec son SHA-256 annoncé ;
- le schéma complet `CURRICULUM_V04_SCHEMA.md` ;
- le curriculum V0 (`tests/education_pilot/_pilot_data.py`) ;
- l'accès aux examens privés du RED V0.3, **uniquement pour le contrôle de recoupement**.

## Contrôles

| Code | Contrôle |
|---|---|
| CV-HASH-IN | le SHA-256 du fichier reçu est égal à celui annoncé par le rédacteur |
| CV-SCHEMA | JSON valide ; champs obligatoires ; `kind` et `sense` cohérents |
| CV-IDS | identifiants uniques ; versions entières ≥ 1 ; `exercise_id` et `contrasts_with` résolus |
| CV-QUOTA | au moins 5 leçons par sens (F1–F7, C1, C2, R1, R2) ; au moins 2 exercices par sens de « force » ; au moins 3 items ambigus ; paires voisines présentes |
| CV-PEDAGO | ordre croissant par sens ; corrections au format attendu (un code positif = sens de l'exercice, au plus un « pas », code négatif connu) |
| CV-DUP-INT | aucune phrase dupliquée ou quasi dupliquée **dans** le curriculum (Jaccard des mots pleins > 0,8 entre deux items) |
| CV-DISJ-V0 | aucune phrase identique au curriculum V0 |
| CV-DISJ-RED | aucune phrase identique et aucune quasi-copie (Jaccard > 0,5) d'une phrase d'examen du RED V0.3 privé |
| CV-NO-TABLE | aucune phrase contenant « table » |
| CV-PROV | `provenance` renseignée pour chaque item et chaque correction |
| CV-HASH-OUT | SHA-256 final consigné ; le fichier devient immuable |

## Ce que l'opérateur transmet à l'auteur du modèle

**Uniquement :**
- `ACCEPT` ou `REJECT` ;
- le **code** des contrôles en échec (par exemple `CV-QUOTA`, `CV-DISJ-RED`) ;
- pour les contrôles de forme, l'identifiant de l'item concerné, **jamais** pour CV-DISJ-RED.

Il ne transmet **jamais** de phrase d'examen, de clé ni de résultat de recoupement détaillé. En cas de `REJECT`, l'opérateur renvoie au **rédacteur** les identifiants à reprendre.

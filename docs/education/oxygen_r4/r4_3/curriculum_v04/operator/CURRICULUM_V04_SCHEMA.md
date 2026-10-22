# Curriculum V0.4 — schéma d'entrée et protocole de recevabilité

## 1. Distinction des jeux

| Jeu | Rôle | Statut |
|---|---|---|
| Curriculum initial **V0** | leçons, exercices et corrections de `_pilot_data.py` (`E_LESSONS`, `E_EXERCISES`, `C_CORRECTIONS`, `CONCURRENT_LESSONS`, `CONTRADICTION`) | **figé, conservé**, jamais écrasé |
| Curriculum enrichi **V0.4** | nouveau fichier JSON, **distinct**, hors banc RED V0.3 | rédigé par un rédacteur non exposé |
| Exercices et corrections | intégrés au curriculum (champ `kind`) | enseignement |
| Évaluations de **développement** | RED V0.3 (examens privés) | inchangées, contaminées (l'auteur les a lues) |
| Évaluations **prospectives** | futur jeu indépendant | inchangées, HOLD_INDEPENDENCE |

## 2. Schéma JSON

```json
{
  "schema": "OXYGEN_CURRICULUM_V04",
  "version": "1.0",
  "author_role": "...",
  "created": "YYYY-MM-DD",
  "items": [
    {
      "id": "CV4-F1-001",
      "version": 1,
      "word": "force",
      "sense": "F1",
      "kind": "lesson | exercise | ambiguous",
      "text": "...",
      "construction": "court libellé libre (ex. « nom + de + infinitif »)",
      "contrasts_with": ["CV4-F2-004"],
      "order": 1,
      "provenance": "rédigée par …, date"
    }
  ],
  "corrections": [
    {
      "id": "CV4-C-001",
      "version": 1,
      "exercise_id": "CV4-F1-101",
      "text": "« … » … (F1), pas … (F2).",
      "status": "active | withdrawn",
      "provenance": "…"
    }
  ]
}
```

**Règles :**
- `id` est unique et stable, jamais réutilisé ; toute modification passe par `version + 1` ;
- `sense` appartient à l'inventaire ; il vaut `AMBIGU` si et seulement si `kind = ambiguous` ;
- `contrasts_with` renvoie à des `id` existants d'un **autre** sens ;
- `exercise_id` renvoie à un item de `kind = exercise`.

## 3. Recevabilité (avant toute utilisation)

Elle est exécutée par l'**opérateur**. Le résultat transmis à l'auteur se limite aux **noms de contrôles et OK/KO**.

| Contrôle | Règle |
|---|---|
| CV-SCHEMA | conformité au schéma, identifiants uniques |
| CV-QUOTA | au moins 5 leçons par sens ; au moins 2 exercices par sens de « force » ; au moins 3 items ambigus ; paires voisines présentes |
| CV-DISJ-V0 | aucune phrase identique au curriculum V0 (empreinte normalisée) |
| CV-DISJ-RED | aucune phrase, ni quasi-copie (Jaccard des mots pleins > 0,5), du **RED V0.3 privé**. Exécuté **par l'opérateur** ; l'auteur ne voit que OK/KO. |
| CV-DISJ-HOLDOUT | idem contre le futur jeu prospectif, s'il existe |
| CV-NO-TABLE | aucune phrase avec « table » |
| CV-CORR-FORMAT | chaque correction contient exactement un code positif égal au sens de l'exercice, au plus un « pas » et un code négatif connu |
| CV-NOCOPY | contrôle de non-recopie d'un dictionnaire : aucune séquence de 8 tokens ou plus en commun avec l'export lexical V1 (Littré exclu de l'export) |
| CV-HASH | empreinte SHA-256 consignée **avant** le premier usage, puis fichier immuable |

## 4. Données qui ne sont jamais utilisées pour fabriquer le curriculum

Les anciennes questions d'examen, leurs réponses, les scores item par item, les heuristiques des élèves.

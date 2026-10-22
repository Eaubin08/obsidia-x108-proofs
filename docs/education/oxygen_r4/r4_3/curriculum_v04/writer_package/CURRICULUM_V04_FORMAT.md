# Format du fichier de curriculum V0.4 (pour le rédacteur)

```json
{
  "schema": "OXYGEN_CURRICULUM_V04",
  "version": "1.0",
  "author_role": "votre rôle (pas votre nom si vous préférez)",
  "created": "AAAA-MM-JJ",
  "items": [
    {"id": "CV4-F1-001", "version": 1, "word": "force", "sense": "F1",
     "kind": "lesson", "text": "…votre phrase…",
     "construction": "description libre de la construction (ex. « nom + de + infinitif »)",
     "contrasts_with": [], "order": 1, "provenance": "rédigée par …, date"}
  ],
  "corrections": [
    {"id": "CV4-C-001", "version": 1, "exercise_id": "CV4-F1-101",
     "text": "« segment clé » explication (F1), pas explication (F2).",
     "status": "active", "provenance": "…"}
  ]
}
```

**Champs :**
- `kind` vaut `lesson`, `exercise` ou `ambiguous` ;
- pour `ambiguous`, `sense` vaut `"AMBIGU"` ;
- `contrasts_with` contient les `id` d'items **d'un autre sens** qui forment une paire proche avec celui-ci ;
- `order` donne l'ordre pédagogique, croissant dans chaque sens ;
- les `id` sont uniques ; toute modification d'un item incrémente `version` sans changer l'`id` ;
- chaque `exercise` a exactement une correction `active`.

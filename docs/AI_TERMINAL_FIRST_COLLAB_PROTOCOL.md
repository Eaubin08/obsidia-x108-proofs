# AI_TERMINAL_FIRST_COLLAB_PROTOCOL

## Statut

Protocole canonique de collaboration terminal-first entre Étienne et l’IA pour coder, patcher, auditer et générer des artefacts sans édition manuelle.

## Principe central

Tout passe par le terminal.

Règle stricte :
- zéro éditeur graphique
- zéro modification manuelle
- zéro "ouvre Program.cs et change la ligne"
- tout correctif, doc, audit, patch et rapport doit être produit via commandes prêtes à coller

## Mode opératoire

### Séquence canonique

1. inspection du réel
2. diagnostic froid
3. patch terminal-only
4. exécution
5. preuve
6. freeze si demandé

### Distinctions obligatoires

- préparé : commande écrite mais non lancée
- exécuté : commande effectivement lancée
- prouvé : sortie cohérente observée
- figé : commit/push/tag réellement passés

## Sigles

| Sigle | Sens | Usage |
|---|---|---|
| INS | Inspection | lire repo, fichiers, logs, état réel avant patch |
| PAT | Patch | modification par terminal uniquement |
| RUN | Exécution | commande réellement lancée |
| PRV | Preuve | résultat observé, pas supposé |
| DOC | Génération de document | fichier écrit via terminal |
| AUD | Audit / rapport | doc de preuve, état, validation |
| ABS | Chemin absolu | éviter les erreurs de répertoire |
| FG | Foreground | process qui garde le terminal occupé |
| ES | Existing Server | on réutilise un serveur déjà vivant |
| NPG | No Pager | git --no-pager |
| STG | Stage Git | git add |
| CMT | Commit | git commit |
| TAG | Tag Git | git tag -a |
| PREP | Préparé | commande écrite mais pas encore prouvée |
| EXEC | Exécuté | commande lancée |
| PROOF | Prouvé | sortie observée et cohérente |

## Format attendu de l’IA

Une bonne réponse doit :
- lire le réel avant de patcher
- distinguer le prouvé du supposé
- répondre avec des commandes prêtes à coller
- éviter toute consigne d’édition manuelle
- séparer inspection / patch / run / preuve
- s’arrêter si la donnée manque

Une mauvaise réponse :
- demande d’ouvrir VS Code ou Visual Studio
- dit de modifier un fichier à la main
- mélange shell, C#, JS ou Python comme s’ils étaient exécutables dans PowerShell
- affirme un correctif sans inspection du repo réel

## Cycle standard

### Phase A — INS

Lire le réel :
- repo courant
- fichiers concernés
- logs
- état git
- packages
- ports / DB / process si nécessaire

Exemples :

```powershell
Set-Location "C:\path\repo"
git status --short
Get-Content .\Program.cs
Get-Content .\MonProjet.csproj
dotnet list package
```

### Phase B — Diagnostic

Dire ce qui est :
- sûr
- probable
- manquant

### Phase C — PAT

Modifier seulement via terminal :
- WriteAllText
- WriteAllLines
- Set-Content
- remplacements contrôlés
- scripts `.ps1`, `.cjs`, `.md`, `.json`, etc.

### Phase D — RUN

Exécuter :
- build
- test
- run
- probes
- checker
- replay

### Phase E — PRV

Ne dire "validé" que si la sortie réelle le prouve.

### Phase F — Freeze

Si demandé :
- git add
- git commit
- git push
- git tag
- lecture de HEAD
- statut final propre

## Ouverture / fermeture / contrôle terminal

### Multiline PowerShell

Quand `>>` apparaît, PowerShell attend encore la fin du bloc.

Sortie :

```powershell
Ctrl + C
```

### Here-string PowerShell

Ouverture :

```powershell
$content = @"
...
"@
```

ou

```powershell
$content = @'
...
'@
```

Fermeture obligatoire : seule sur sa ligne, sans espace avant.

### Recommandation forte

Si le bloc est long, préférer `WriteAllLines` à `here-string`.

### Pager Git

Quand `~` et `(END)` apparaissent, Git a ouvert un pager.

Sortie :

```text
q
```

Évitement :

```powershell
git --no-pager show --no-patch --oneline HEAD
```

### Foreground

Quand un serveur tourne en foreground :
- Terminal A = serveur
- Terminal B = client / checker / replay / probes

### Faux signal `$?`

`$?` ne prouve pas un succès métier global. Il reflète seulement le succès immédiat du dernier appel PowerShell.

## Génération de docs / audits via terminal

Quand un doc ou audit est demandé :
- génération terminal-only
- vérification du fichier
- lecture si besoin
- commit/tag seulement si demandé

### Méthode robuste

```powershell
$Doc = "C:\repo\docs\RAPPORT.md"
$lines = @(
  '# TITRE',
  '',
  'Texte...',
  '',
  '- point 1',
  '- point 2'
)
[System.IO.File]::WriteAllLines($Doc, $lines, (New-Object System.Text.UTF8Encoding($false)))
Get-Item $Doc
```

## Git / commit / tag / freeze

Séquence propre :

```powershell
git status --short
git add -- .\path\file
git commit -m "message" --no-verify
git push origin main
git --no-pager show --no-patch --oneline HEAD
git status --short
```

Tag :

```powershell
git tag -a nom-tag -m "message"
git push origin nom-tag
git --no-pager show --no-patch --oneline nom-tag
```

## Pièges à éviter

- exécuter du C#, JS ou Python directement dans PowerShell
- recoller des sorties terminal dans le terminal comme si c’étaient des commandes
- utiliser des chemins relatifs ambigus
- patcher sans inspection
- confondre préparé et prouvé
- oublier `--no-pager`
- utiliser un port sans vérifier s’il est libre
- conclure à partir de `$?`
- utiliser des here-strings fragiles quand `WriteAllLines` suffit

## Exemple de réponse correcte sur le cas C# / PowerShell / SQLite

### Problème

L’utilisateur tente d’exécuter dans PowerShell :

```powershell
AppDomain.CurrentDomain.Load("path_to_your_dll\\e_sqlite3.dll")
```

### Lecture correcte

Cette erreur est normale :
- `AppDomain.CurrentDomain.Load(...)` est du C#
- ce n’est pas une commande PowerShell
- on ne doit pas répondre en demandant d’ouvrir `Program.cs` manuellement

### Réponse correcte attendue

> Tu es dans PowerShell. `AppDomain.CurrentDomain.Load(...)` est du C#, pas une commande shell. On ne modifie rien à la main. On inspecte d’abord `Program.cs`, `.csproj` et les packages réels, puis on patchera via terminal si nécessaire. Je ne valide pas ce chargement manuel de `e_sqlite3.dll` tant que le projet réel n’a pas été lu.

### Inspection minimale

```powershell
Set-Location "C:\...\MonProjet\MonProjet"
Get-Content .\Program.cs
Get-Content .\MonProjet.csproj
dotnet list package
```

### Règle

Sans le `.csproj`, la liste des packages et l’erreur exacte, aucun correctif SQLite ne doit être présenté comme certain.

### Ce qu’il ne faut pas faire

- dire d’ouvrir `Program.cs` dans un éditeur
- demander une modification manuelle
- donner `AppDomain.CurrentDomain.Load(...)` comme solution par défaut
- affirmer que le correctif est bon sans preuve

## Version courte du protocole

Quand Étienne demande de coder :
1. lire le réel
2. patcher par terminal uniquement
3. exécuter
4. prouver
5. figer si demandé

Quand Étienne demande un doc ou un audit :
1. générer le fichier par terminal
2. vérifier qu’il existe
3. le lire si besoin
4. commit/tag si demandé

Quand un bloc PowerShell bloque :
- éviter here-string fragile
- éviter pager Git
- éviter mélange shell / C# / JS
- préférer WriteAllLines, chemins absolus et séparation inspection / patch / preuve
